"""Fixed-date synthetic builders; no deletes, resets or production seed command."""

from dataclasses import dataclass
from datetime import date, datetime, timezone
import re

from django.db import transaction
from rest_framework.authtoken.models import Token

from leave.models import LeaveBalance, LeaveRequest, Team, User
from tests.team.safety import assert_disposable_database

TEST_PASSWORD = "sqe-local-fixture-only"
DECIDED_AT = datetime(2026, 12, 1, 10, tzinfo=timezone.utc)


@dataclass
class People:
    team_a: Team
    team_b: Team
    e1: User
    e2: User
    m1: User
    m2: User
    admin: User
    teamless_manager: User


@dataclass
class ReferenceFixture:
    people: People
    pending: LeaveRequest
    approved: LeaveRequest
    rejected: LeaveRequest


def build_people(prefix="sqe", *, allowance=10, allowances=None, missing_balance_for=()):
    """Create two teams/six users. Overrides concern fixtures, not API fields."""
    assert_disposable_database(active=True)
    keys = {"e1", "e2", "m1", "m2", "admin", "teamless_manager"}
    overrides = dict(allowances or {})
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,19}", prefix):
        raise ValueError("Use a short lowercase synthetic prefix.")
    if not set(overrides) <= keys or not set(missing_balance_for) <= keys:
        raise ValueError("Unknown fixture identity.")
    with transaction.atomic():
        team_a = Team.objects.create(name=f"{prefix}-A")
        team_b = Team.objects.create(name=f"{prefix}-B")
        specs = {
            "e1": (User.Role.EMPLOYEE, team_a),
            "e2": (User.Role.EMPLOYEE, team_a),
            "m1": (User.Role.MANAGER, team_a),
            "m2": (User.Role.MANAGER, team_b),
            "admin": (User.Role.ADMIN, team_a),
            "teamless_manager": (User.Role.MANAGER, None),
        }
        users = {}
        for key, (role, team) in specs.items():
            user = User.objects.create_user(
                username=f"{prefix}_{key}",
                password=TEST_PASSWORD,
                first_name="Synthetic",
                last_name=key,
                email=f"{prefix}_{key}@example.invalid",
                role=role,
                team=team,
                is_staff=key == "admin",
                is_superuser=key == "admin",
            )
            user.full_clean()
            users[key] = user
            if key not in missing_balance_for:
                balance = LeaveBalance(user=user, allowance=overrides.get(key, allowance), year=2026)
                balance.full_clean()
                balance.save()
    return People(team_a, team_b, **users)


def make_request(
    employee,
    *,
    start=date(2026, 12, 14),
    end=date(2026, 12, 16),
    status=LeaveRequest.Status.PENDING,
    leave_type=LeaveRequest.Type.VACATION,
    note="Synthetic fixture",
    decided_by=None,
    allow_overlap=False,
):
    """Validate fixture invariants before insertion; overlap bypass is explicit.

    Direct history construction does not run the decision API. This builder's
    nonnegative allowance check is a fixture safeguard, not a claim of a W2 guard.
    """
    assert_disposable_database(active=True)
    if end < start:
        raise ValueError("Fixture dates must be ordered.")
    final = status in {LeaveRequest.Status.APPROVED, LeaveRequest.Status.REJECTED}
    if final:
        if (
            decided_by is None
            or decided_by.pk == employee.pk
            or decided_by.role not in {User.Role.MANAGER, User.Role.ADMIN}
            or (decided_by.role == User.Role.MANAGER and (
                not decided_by.team_id or decided_by.team_id != employee.team_id
            ))
        ):
            raise ValueError("Final fixture records need an authorized non-self decider.")
    elif decided_by is not None:
        raise ValueError("Pending fixtures cannot already have a decider.")
    item = LeaveRequest(
        employee=employee, start_date=start, end_date=end, status=status,
        leave_type=leave_type, note=note, decided_by=decided_by,
        decided_at=DECIDED_AT if final else None,
    )
    item.clean_fields()
    if not allow_overlap:
        item.clean()
    balance = LeaveBalance.objects.filter(user=employee).first()
    if status != LeaveRequest.Status.REJECTED and balance and item.business_days > balance.available_days:
        raise ValueError("Fixture exceeds its known available allowance.")
    item.validate_unique()
    item.validate_constraints()
    item.save()
    return item


def build_reference_fixture(prefix="sqe"):
    assert_disposable_database(active=True)
    with transaction.atomic():
        people = build_people(prefix)
        approved = make_request(
            people.e1, start=date(2026, 12, 7), end=date(2026, 12, 8),
            status=LeaveRequest.Status.APPROVED, decided_by=people.m1,
        )
        pending = make_request(people.e1)
        rejected = make_request(
            people.e1, start=date(2026, 12, 21), end=date(2026, 12, 21),
            status=LeaveRequest.Status.REJECTED, leave_type=LeaveRequest.Type.PERMIT,
            decided_by=people.m1,
        )
    return ReferenceFixture(people, pending, approved, rejected)


def build_overapproval_scenario(prefix="overapproval"):
    """Prepare two valid pending four-day requests; do NOT approve either here."""
    assert_disposable_database(active=True)
    with transaction.atomic():
        people = build_people(prefix, allowances={"e1": 5})
        first = make_request(people.e1, start=date(2026, 12, 7), end=date(2026, 12, 10))
        second = make_request(people.e1, start=date(2026, 12, 14), end=date(2026, 12, 17))
    return people, first, second


def logical_snapshot():
    """Canonical initial state: omit IDs, random tokens/passwords and wall clocks."""
    assert_disposable_database(active=True)
    return {
        "teams": list(Team.objects.order_by("name").values_list("name", flat=True)),
        "users": [
            {"username": u.username, "role": u.role, "team": u.team.name if u.team else None}
            for u in User.objects.select_related("team").order_by("username")
        ],
        "balances": [
            {"user": b.user.username, "allowance": b.allowance, "year": b.year,
             "used": b.approved_days, "available": b.available_days}
            for b in LeaveBalance.objects.select_related("user").order_by("user__username")
        ],
        "requests": [
            {"employee": r.employee.username, "type": r.leave_type,
             "start": r.start_date.isoformat(), "end": r.end_date.isoformat(),
             "status": r.status, "note": r.note, "days": r.business_days,
             "decider": r.decided_by.username if r.decided_by else None}
            for r in LeaveRequest.objects.select_related("employee", "decided_by").order_by(
                "employee__username", "start_date", "end_date", "status"
            )
        ],
        "token_count": Token.objects.count(),
    }
