"""A2.1 Group C: W2 visibility, decision authorization, value validation and final states.

Case IDs expand planned RTM families API-W2-001..006. Guard order verified from
backend/leave/views.py: authentication -> role -> decision value -> visible lookup
-> not self -> pending. Every denied call asserts unchanged persisted rows.
Same-record W1->W2 cross-workflow integration is deliberately left to A2.2.
"""

from datetime import date

from django.test import TestCase
from django.utils import timezone

from leave.models import LeaveRequest, User
from tests.team.api.support import (
    REQUEST_FIELDS, REQUESTS_URL, add_member, all_rows, balance_view, decision_url, row_state, token_client,
)
from tests.team.fixtures.leave_data import build_reference_fixture, make_request

FORBIDDEN = {"detail": "Operazione non consentita."}
INVALID = {"detail": "Decisione non valida."}
SELF = {"detail": "Non puoi decidere una tua richiesta."}
DECIDED = {"detail": "La richiesta è già stata decisa."}


class DecisionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fx = build_reference_fixture("w2")
        p = cls.p = cls.fx.people
        cls.eb = add_member("w2", "eb", User.Role.EMPLOYEE, p.team_b)
        span = {"start": date(2026, 12, 14), "end": date(2026, 12, 15)}
        cls.e2_pending = make_request(p.e2, **span)
        cls.eb_pending = make_request(cls.eb, **span)
        cls.m1_pending = make_request(p.m1, **span)
        cls.admin_pending = make_request(p.admin, **span)
        cls.teamless_pending = make_request(p.teamless_manager, **span)

    def decide(self, actor, request_id, body):
        return token_client(actor).post(decision_url(request_id), body, format="json")

    def assert_denied(self, actor, request_id, body, status_code, data=None):
        before = all_rows()
        response = self.decide(actor, request_id, body)
        self.assertEqual(response.status_code, status_code, response.data)
        if data is not None:
            self.assertEqual(response.data, data)
        self.assertEqual(set(response.data), {"detail"})  # no request data exposed
        self.assertEqual(all_rows(), before)
        return response

    def assert_decided(self, actor, item, decision):
        before = row_state(item.pk)
        count = LeaveRequest.objects.count()
        started = timezone.now()
        response = self.decide(actor, item.pk, {"status": decision})
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(set(response.data), REQUEST_FIELDS)
        self.assertNotIn("decided_by", response.data)  # audit fields stored but not serialized (FR-W2-06 note)
        self.assertEqual((response.data["id"], response.data["status"]), (item.pk, decision))
        self.assertEqual(response.data["employee"]["id"], item.employee_id)
        after = row_state(item.pk)
        self.assertEqual(after["decided_by_id"], actor.pk)
        self.assertTrue(started <= after["decided_at"] <= timezone.now())
        unchanged = ("id", "employee_id", "leave_type", "start_date", "end_date", "note", "created_at")
        self.assertEqual({k: after[k] for k in unchanged}, {k: before[k] for k in unchanged})
        self.assertEqual((before["status"], after["status"]), ("pending", decision))
        self.assertEqual(LeaveRequest.objects.count(), count)
        return response, after


class VisibilityTests(DecisionTestCase):
    def test_request_list_and_dashboard_scope_by_role(self):
        """API-W2-001.01; FR-W2-01; BR-04: employee own, team manager team, teamless own, admin all."""
        fx = self.fx
        e1_own = {fx.pending.pk, fx.approved.pk, fx.rejected.pk}
        team_a = e1_own | {self.e2_pending.pk, self.m1_pending.pk, self.admin_pending.pk}
        expected = {
            self.p.e1: e1_own,
            self.p.e2: {self.e2_pending.pk},
            self.eb: {self.eb_pending.pk},
            self.p.m1: team_a,
            self.p.m2: {self.eb_pending.pk},
            self.p.teamless_manager: {self.teamless_pending.pk},
            self.p.admin: set(LeaveRequest.objects.values_list("pk", flat=True)),
        }
        self.assertEqual(len(expected[self.p.admin]), 8)
        for user, ids in expected.items():
            with self.subTest(user=user.username):
                client = token_client(user)
                listed = client.get(REQUESTS_URL)
                self.assertEqual(listed.status_code, 200)
                self.assertEqual({r["id"] for r in listed.data}, ids)
                self.assertEqual(len(listed.data), len(ids))  # no duplicates
                for item in listed.data:
                    self.assertEqual(item["employee"]["id"], LeaveRequest.objects.get(pk=item["id"]).employee_id)
                counts = client.get("/api/dashboard/").data["counts"]
                rows = LeaveRequest.objects.filter(pk__in=ids)
                self.assertEqual(counts, {
                    "total": len(ids),
                    "pending": rows.filter(status="pending").count(),
                    "approved": rows.filter(status="approved").count(),
                })


class AuthorizedDecisionTests(DecisionTestCase):
    def test_same_team_manager_approves_pending_and_balance_is_derived(self):
        """API-W2-002.02, API-W2-005.01; FR-W2-02, FR-W2-04, FR-W2-05; BR-03/04/05: 200, actor/time, used +D."""
        self.assertEqual(balance_view(self.p.e1), (10, 2, 8))
        response, _ = self.assert_decided(self.p.m1, self.fx.pending, "approved")
        self.assertEqual(response.data["status_label"], "Approvata")
        self.assertEqual(balance_view(self.p.e1), (10, 5, 5))  # pending had 3 business days

    def test_same_team_manager_rejects_pending_without_charging_allowance(self):
        """API-W2-006.01; FR-W2-02, FR-W2-04, FR-W2-06; BR-03/04/05: 200 rejected, used unchanged."""
        self.assertEqual(balance_view(self.p.e2), (10, 0, 10))
        response, _ = self.assert_decided(self.p.m1, self.e2_pending, "rejected")
        self.assertEqual(response.data["status_label"], "Rifiutata")
        self.assertEqual(balance_view(self.p.e2), (10, 0, 10))

    def test_admin_decides_requests_of_any_team(self):
        """API-W2-002.03; FR-W2-02, FR-W2-05, FR-W2-06; BR-04/05: admin approves Team B, rejects Team A."""
        self.assert_decided(self.p.admin, self.eb_pending, "approved")
        self.assert_decided(self.p.admin, self.e2_pending, "rejected")
        self.assertEqual(balance_view(self.eb), (10, 2, 8))

    def test_extra_body_keys_cannot_override_audit_or_content(self):
        """API-W2-003.03; FR-W2-03, FR-W2-05; BR-05/06: injected decider/time/owner/note are ignored."""
        before = row_state(self.fx.pending.pk)
        response = self.decide(self.p.m1, self.fx.pending.pk, {
            "status": "approved", "decided_by": self.p.m2.pk, "decided_at": "2020-01-01T00:00:00Z",
            "employee": self.p.e2.pk, "note": "tampered", "end_date": "2026-12-31",
        })
        self.assertEqual(response.status_code, 200)
        after = row_state(self.fx.pending.pk)
        self.assertEqual(after["decided_by_id"], self.p.m1.pk)
        self.assertGreater(after["decided_at"].year, 2020)
        for key in ("employee_id", "note", "end_date", "start_date"):
            self.assertEqual(after[key], before[key])


class DeniedDecisionTests(DecisionTestCase):
    def test_employee_role_cannot_decide(self):
        """API-W2-002.01; FR-W2-02; BR-04: employee -> 403 for teammate's and own requests, unchanged."""
        for target in (self.e2_pending, self.fx.pending):
            for decision in ("approved", "rejected"):
                with self.subTest(target=target.pk, decision=decision):
                    self.assert_denied(self.p.e1, target.pk, {"status": decision}, 403, FORBIDDEN)

    def test_out_of_scope_managers_receive_404(self):
        """API-W2-002.04; FR-W2-01, FR-W2-02; BR-04: other-team and teamless managers cannot reach target."""
        cases = [
            (self.p.m2, self.fx.pending), (self.p.m2, self.admin_pending), (self.p.m2, self.m1_pending),
            (self.p.m1, self.eb_pending), (self.p.teamless_manager, self.fx.pending),
            (self.p.teamless_manager, self.eb_pending),
        ]
        for actor, target in cases:
            with self.subTest(actor=actor.username, target=target.pk):
                self.assert_denied(actor, target.pk, {"status": "approved"}, 404)

    def test_self_decision_forbidden_for_every_privileged_role(self):
        """API-W2-002.05; FR-W2-02; BR-04/05: own pending request -> 403 for manager, admin, teamless manager."""
        for actor, own in ((self.p.m1, self.m1_pending), (self.p.admin, self.admin_pending),
                           (self.p.teamless_manager, self.teamless_pending)):
            for decision in ("approved", "rejected"):
                with self.subTest(actor=actor.username, decision=decision):
                    self.assert_denied(actor, own.pk, {"status": decision}, 403, SELF)

    def test_nonexistent_and_unroutable_ids(self):
        """API-W2-002.07; FR-W2-02; BR-04: absent IDs -> 404 even for admin; non-integer path does not route."""
        missing = LeaveRequest.objects.order_by("-pk").values_list("pk", flat=True).first() + 1000
        for request_id in (missing, 0):
            with self.subTest(request_id=request_id):
                self.assert_denied(self.p.admin, request_id, {"status": "approved"}, 404)
        before = all_rows()
        client = token_client(self.p.admin)
        for path in ("/api/requests/abc/decision/", "/api/requests/-1/decision/"):
            with self.subTest(path=path):
                self.assertEqual(client.post(path, {"status": "approved"}, format="json").status_code, 404)
        self.assertEqual(all_rows(), before)


class DecisionValueTests(DecisionTestCase):
    def test_missing_null_and_invalid_status_values(self):
        """API-W2-003.01; FR-W2-03; BR-05/06: only approved/rejected accepted; others -> 400, unchanged."""
        bodies = [
            {}, {"status": None}, {"status": ""}, {"status": "pending"}, {"status": "Approved"},
            {"status": "approve"}, {"status": "cancelled"}, {"status": 1}, {"status": ["approved"]},
            {"status": {"value": "approved"}}, {"decision": "approved"},
        ]
        for body in bodies:
            with self.subTest(body=body):
                self.assert_denied(self.p.m1, self.fx.pending.pk, body, 400, INVALID)
        self.assertEqual(row_state(self.fx.pending.pk)["status"], "pending")

    def test_guard_precedence(self):
        """API-W2-003.02; FR-W2-02, FR-W2-03; BR-04/05/06: role before value before lookup before self/state."""
        missing = LeaveRequest.objects.order_by("-pk").values_list("pk", flat=True).first() + 1000
        cases = [
            ("employee + invalid value", self.p.e1, self.fx.pending.pk, "bogus", 403, FORBIDDEN),
            ("invalid value + missing id", self.p.m1, missing, "bogus", 400, INVALID),
            ("invalid value + out of scope", self.p.m2, self.fx.pending.pk, "bogus", 400, INVALID),
            ("invalid value + own request", self.p.m1, self.m1_pending.pk, "bogus", 400, INVALID),
            ("invalid value + final state", self.p.m1, self.fx.approved.pk, "bogus", 400, INVALID),
            ("out of scope + final state", self.p.m2, self.fx.approved.pk, "rejected", 404, None),
        ]
        for label, actor, target, value, code, data in cases:
            with self.subTest(case=label):
                self.assert_denied(actor, target, {"status": value}, code, data)


class FinalStateTests(DecisionTestCase):
    def test_approved_and_rejected_requests_cannot_be_decided_again(self):
        """API-W2-004.01; FR-W2-04; BR-05: final states -> 409 for both values; audit and balance preserved."""
        balance = balance_view(self.p.e1)
        for target in (self.fx.approved, self.fx.rejected):
            for actor in (self.p.m1, self.p.admin):
                for decision in ("approved", "rejected"):
                    with self.subTest(state=target.status, actor=actor.username, decision=decision):
                        self.assert_denied(actor, target.pk, {"status": decision}, 409, DECIDED)
        self.assertEqual(row_state(self.fx.approved.pk)["decided_by_id"], self.p.m1.pk)
        self.assertEqual(balance_view(self.p.e1), balance)

    def test_repeat_after_successful_decision_conflicts(self):
        """API-W2-004.02; FR-W2-04; BR-05: pending->approved once; later approve/reject -> 409, same actor/time."""
        _, decided = self.assert_decided(self.p.m1, self.e2_pending, "approved")
        for actor, decision in ((self.p.m1, "approved"), (self.p.m1, "rejected"), (self.p.admin, "rejected")):
            with self.subTest(actor=actor.username, decision=decision):
                self.assert_denied(actor, self.e2_pending.pk, {"status": decision}, 409, DECIDED)
        self.assertEqual(row_state(self.e2_pending.pk), decided)
