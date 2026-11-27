"""Operation-flow matcher of scripts/sqe/api_coverage.py (TCL7, EC-05).

A flow counts only when its steps return the documented status and meet their
conditions (decision value, same record or dates, acting user). These tests feed
the matcher recorded-call dictionaries, built the way Trace.record builds them, for
the flows exported from the spec (tests/team/generated/api_contract.json). No API
call and no database access is needed.
"""

import json
from pathlib import Path
import sys

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/sqe"))
import api_coverage  # noqa: E402 - tool under test

FLOWS = {f["name"]: f for f in json.loads((ROOT / "tests/team/generated/api_contract.json").read_text(encoding="utf-8"))["flows"]}
EMPLOYEE, MANAGER, OTHER_EMPLOYEE = 11, 21, 12
DATES = ("2026-12-07", "2026-12-08")


def call(operation, status, *, actor, record_id=None, owner=EMPLOYEE, dates=DATES, decision=None, listed=(), leaves=()):
    record = None
    if record_id is not None:
        record = {"id": str(record_id), "owner": owner, "start_date": dates[0], "end_date": dates[1]}
    return {"operation": operation, "status": status, "actor": actor, "record": record,
            "enum_values": {"status": decision} if decision else {}, "listed": list(listed), "leaves": list(leaves)}


def submit(record_id, *, actor=EMPLOYEE, status=201, dates=DATES):
    return call("submitRequest", status, actor=actor, record_id=record_id if status == 201 else None, owner=actor, dates=dates)


def decide(record_id, decision, *, actor=MANAGER, status=200, owner=EMPLOYEE, dates=DATES):
    if status != 200:  # a refused decision knows only the path id
        return call("decideRequest", status, actor=actor, record_id=record_id, owner=None, dates=(None, None), decision=decision)
    return call("decideRequest", status, actor=actor, record_id=record_id, owner=owner, dates=dates, decision=decision)


class RejectThenResubmitFlowTests(SimpleTestCase):
    """'reject then resubmit the dates' = submit 201 → reject 200 (same id, not the owner) → owner resubmits the dates 201."""

    flow = FLOWS["reject then resubmit the dates"]

    def matches(self, calls):
        return api_coverage.match_flow(self.flow["steps"], calls)

    def test_positive_control(self):
        """The real sequence matches, also with an unrelated call between the steps."""
        self.assertTrue(self.matches([submit(1), decide(1, "rejected"), submit(2)]))
        self.assertTrue(self.matches([submit(1), call("me", 200, actor=MANAGER), decide(1, "rejected"), submit(2)]))

    def test_same_endpoints_different_semantics_not_matched(self):
        """Negative: the endpoint sequence submit → decide → submit, but not a rejection and resubmission."""
        cases = {
            "approve then submit (review finding)": [submit(1), decide(1, "approved"), submit(2, dates=("2026-12-14", "2026-12-15"))],
            "approve then submit the same dates": [submit(1), decide(1, "approved"), submit(2)],
            "rejection refused with 409": [submit(1), decide(1, "rejected", status=409), submit(2)],
            "rejection refused with 403 (own request)": [submit(1), decide(1, "rejected", actor=EMPLOYEE, status=403), submit(2)],
            "owner decides the request": [submit(1), decide(1, "rejected", actor=EMPLOYEE), submit(2)],
            "another request is rejected": [submit(1), decide(9, "rejected"), submit(2)],
            "another employee resubmits": [submit(1), decide(1, "rejected"), submit(2, actor=OTHER_EMPLOYEE)],
            "resubmission with other dates": [submit(1), decide(1, "rejected"), submit(2, dates=("2026-12-14", "2026-12-15"))],
            "resubmission refused (400)": [submit(1), decide(1, "rejected"), submit(None, status=400)],
            "steps out of order": [submit(1), submit(2), decide(1, "rejected")],
        }
        for name, calls in cases.items():
            with self.subTest(name):
                self.assertFalse(self.matches(calls))


class OtherFlowConditionTests(SimpleTestCase):
    """Each condition type rejects a call that has the right operation but the wrong meaning."""

    def assert_flow(self, name, good, bad):
        steps = FLOWS[name]["steps"]
        self.assertTrue(api_coverage.match_flow(steps, good), name)
        for label, calls in bad.items():
            with self.subTest(flow=name, case=label):
                self.assertFalse(api_coverage.match_flow(steps, calls))

    def test_decide_then_team_upcoming_leave(self):
        leave = [[EMPLOYEE, *DATES]]
        self.assert_flow("decide then team upcoming leave", [decide(1, "approved"), call("team", 200, actor=MANAGER, leaves=leave)], {
            "rejected, not approved": [decide(1, "rejected"), call("team", 200, actor=MANAGER, leaves=leave)],
            "team view does not show the leave": [decide(1, "approved"), call("team", 200, actor=MANAGER)],
        })

    def test_submit_decide_repeat(self):
        self.assert_flow("submit then decide then repeat the decision",
                         [submit(1), decide(1, "approved"), decide(1, "rejected", status=409)], {
                             "repeat succeeds (200)": [submit(1), decide(1, "approved"), decide(1, "rejected")],
                             "repeat on another request": [submit(1), decide(1, "approved"), decide(2, "rejected", status=409)],
                         })

    def test_owner_dashboard_and_own_list(self):
        self.assert_flow("decide then owner dashboard", [decide(1, "approved"), call("dashboard", 200, actor=EMPLOYEE)], {
            "manager's dashboard": [decide(1, "approved"), call("dashboard", 200, actor=MANAGER)],
        })
        self.assert_flow("submit then own list", [submit(1), call("listRequests", 200, actor=EMPLOYEE, listed=["1"])], {
            "list without the record": [submit(1), call("listRequests", 200, actor=EMPLOYEE, listed=["5"])],
            "someone else's list": [submit(1), call("listRequests", 200, actor=MANAGER, listed=["1"])],
        })

    def test_login_then_profile(self):
        self.assert_flow("login then profile", [call("login", 200, actor=EMPLOYEE), call("me", 200, actor=EMPLOYEE)], {
            "failed login": [call("login", 400, actor=None), call("me", 200, actor=EMPLOYEE)],
            "profile of another user": [call("login", 200, actor=EMPLOYEE), call("me", 200, actor=MANAGER)],
        })

    def test_unknown_condition_is_an_error(self):
        with self.assertRaises(ValueError):
            api_coverage.match_flow([{"operation": "me", "status": 200, "colour": "red"}], [call("me", 200, actor=1)])
