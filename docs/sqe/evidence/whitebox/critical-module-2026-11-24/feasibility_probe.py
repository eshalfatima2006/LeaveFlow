#!/usr/bin/env python3
"""Critical-module feasibility probe (decision record DR-001). Analysis tool, not a team test.

Runs every executable truth row of
  D1  serializers.py:37  `balance and instance.business_days > balance.available_days`
  H   serializers.py:35  `exc.message_dict if hasattr(exc, 'message_dict') else exc.messages`
  D2  views.py:49        `user.role == User.Role.MANAGER and user.team_id`
against the disposable in-memory test database (profile sqe-memory-v1, fail-closed
guard). LeaveBalance.available_days is wrapped in-process only to count how often
the right operand of D1 is evaluated; no source file is modified.

Usage (repository root): .venv/bin/python docs/sqe/evidence/whitebox/critical-module-2026-11-24/feasibility_probe.py <output.json>
"""

from datetime import date
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
sys.dont_write_bytecode = True
os.environ["DJANGO_SETTINGS_MODULE"] = "tests.team.settings"


def dev_db():
    path = ROOT / "backend" / "db.sqlite3"
    if not path.exists():
        return None
    st = path.stat()
    return {"size": st.st_size, "mtime_ns": st.st_mtime_ns, "inode": st.st_ino}


def main(output):
    before = dev_db()
    from tests.team.safety import assert_disposable_database

    assert_disposable_database()
    import django

    django.setup()
    from django.db import connection
    from django.test.utils import setup_test_environment

    setup_test_environment()
    connection.creation.create_test_db(verbosity=0, autoclobber=True, keepdb=False)
    assert_disposable_database(active=True)

    from leave.models import LeaveBalance, LeaveRequest, Team, User
    from leave.serializers import LeaveRequestSerializer
    from leave.views import visible_requests

    calls = {"available_days": 0}
    original = LeaveBalance.available_days

    def counted(self):
        calls["available_days"] += 1
        return original.fget(self)

    LeaveBalance.available_days = property(counted)

    def submit(user, start, end):
        calls["available_days"] = 0
        serializer = LeaveRequestSerializer(
            data={"leave_type": "vacation", "start_date": start, "end_date": end},
            context={"request": SimpleNamespace(user=user)},
        )
        valid = serializer.is_valid()
        errors = {k: [str(m) for m in v] for k, v in serializer.errors.items()}
        return {"valid": valid, "errors": errors, "available_days_evaluations": calls["available_days"]}

    team_a = Team.objects.create(name="Probe A")
    no_balance = User.objects.create_user("probe-nobalance", role="employee", team=team_a)
    with_balance = User.objects.create_user("probe-balance5", role="employee", team=team_a)
    LeaveBalance.objects.create(user=with_balance, allowance=5)

    d1 = [
        {"row": "B=F, E=masked", "fixture": "no LeaveBalance; 2027-03-01..05 (D=5)", **submit(no_balance, "2027-03-01", "2027-03-05")},
        {"row": "B=T, E=F", "fixture": "A=5; 2027-03-01..05 (D=5)", **submit(with_balance, "2027-03-01", "2027-03-05")},
        {"row": "B=T, E=T", "fixture": "A=5; 2027-03-01..08 (D=6)", **submit(with_balance, "2027-03-01", "2027-03-08")},
    ]
    balance = getattr(no_balance, "leave_balance", None)
    try:
        balance.available_days  # noqa: B018 - demonstrates E is undefined without a balance
        undefined = "unexpected: E evaluable"
    except AttributeError as exc:
        undefined = f"AttributeError: {exc}"
    d1_infeasible = {
        "rows": ["B=F, E=T", "B=F, E=F"],
        "reason": "With B=F there is no LeaveBalance object, so available_days (and therefore E) has no domain value; "
                  "Python short-circuit also skips E. Attempting to evaluate E: " + undefined,
    }

    LeaveRequest.objects.create(employee=with_balance, start_date=date(2027, 4, 5), end_date=date(2027, 4, 9))
    h = [
        {"row": "H=T (dict-shaped ValidationError)", "fixture": "end before start", **submit(with_balance, "2027-03-10", "2027-03-09")},
        {"row": "H=F (list-shaped ValidationError)", "fixture": "overlap with pending 2027-04-05..09", **submit(with_balance, "2027-04-07", "2027-04-07")},
    ]

    team_b = Team.objects.create(name="Probe B")
    users = {
        "admin": User.objects.create_user("probe-admin", role="admin"),
        "manager+team": User.objects.create_user("probe-mgr-team", role="manager", team=team_a),
        "manager-noteam": User.objects.create_user("probe-mgr-noteam", role="manager"),
        "employee+team": User.objects.create_user("probe-emp-team", role="employee", team=team_a),
        "employee-noteam": User.objects.create_user("probe-emp-noteam", role="employee"),
        "outsider": User.objects.create_user("probe-outsider", role="employee", team=team_b),
    }
    own = {}
    for key, user in users.items():
        own[key] = LeaveRequest.objects.create(employee=user, start_date=date(2027, 5, 3), end_date=date(2027, 5, 3)).id
    team_a_ids = sorted(LeaveRequest.objects.filter(employee__team=team_a).values_list("id", flat=True))
    all_ids = sorted(LeaveRequest.objects.values_list("id", flat=True))

    def outcome(ids):
        if ids == all_ids:
            return "all requests (admin bypass)"
        if ids == team_a_ids:
            return "team A requests (D2 true)"
        if len(ids) == 1:
            return "own requests only (D2 false / fallback)"
        return "unexpected"

    d2 = []
    for key, m, t in (("admin", None, None), ("manager+team", "T", "T"), ("manager-noteam", "T", "F"),
                      ("employee+team", "F", "T"), ("employee-noteam", "F", "F")):
        ids = sorted(visible_requests(users[key]).values_list("id", flat=True))
        d2.append({"actor": key, "M": m, "T": t, "visible_ids": ids, "outcome": outcome(ids)})

    LeaveBalance.available_days = original
    result = {
        "profile": "sqe-memory-v1",
        "database": connection.settings_dict["NAME"],
        "D1": d1, "D1_infeasible": d1_infeasible, "H": h, "D2": d2,
        "development_database_unchanged": before == dev_db(),
    }
    connection.creation.destroy_test_db(":memory:", verbosity=0)
    Path(output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["development_database_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
