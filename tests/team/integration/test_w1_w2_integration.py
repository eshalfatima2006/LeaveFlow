"""A2.2 cross-workflow integration: W1 submission → W2 decision on the SAME persisted request.

Every request is created by the employee through the real W1 API
(``POST /api/requests/``) after a real login (``POST /api/auth/login/``), and is
then decided through the real W2 API (``POST /api/requests/{id}/decision/``).
No LeaveRequest is inserted or changed through the ORM; the ORM is used only to
build users/teams/balances in ``setUp`` and to read back persisted state after
each call.

Case IDs are children of the planned RTM objective API-INT-001 (same-record
W1→W2 readback and the approval-overdraw scenario). API-INT-002 (concurrency on
PostgreSQL) is not part of this module.

Database isolation: the sqe-memory-v1 profile (``tests/team/settings.py``) and
its fail-closed guard (``tests/team/safety.py``); run with
``.venv/bin/python scripts/sqe/run_tests.py team tests.team.integration``.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from leave.models import LeaveRequest, User
from tests.team.api.support import (
    LOGIN_URL, REQUESTS_URL, add_member, balance_view, decision_url, payload, row_state,
)
from tests.team.fixtures.leave_data import TEST_PASSWORD, build_people

FORBIDDEN = {"detail": "Operazione non consentita."}
SELF = {"detail": "Non puoi decidere una tua richiesta."}
DECIDED = {"detail": "La richiesta è già stata decisa."}

# Mon 7 – Wed 9 Dec 2026 and Mon 14 – Wed 16 Dec 2026: three business days each.
FIRST = {"start": "2026-12-07", "end": "2026-12-09"}
SECOND = {"start": "2026-12-14", "end": "2026-12-16"}


class CrossWorkflowTestCase(TestCase):
    """Shared setUp and HTTP helpers. Subclasses override ``allowances``."""

    allowances = None
    prefix = "a22"

    def setUp(self):
        self.people = build_people(self.prefix, allowance=10, allowances=self.allowances)
        self.e1, self.m1, self.m2 = self.people.e1, self.people.m1, self.people.m2
        # Team B employee for the cross-team visibility case.
        self.eb = add_member(self.prefix, "eb", User.Role.EMPLOYEE, self.people.team_b)

    # ---- HTTP helpers (real login → real DRF token) -------------------------
    def login(self, user):
        anonymous = APIClient()
        response = anonymous.post(LOGIN_URL, {"username": user.username, "password": TEST_PASSWORD}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["user"]["id"], user.pk)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + response.data["token"])
        return client

    def submit(self, user, dates, note):
        """W1 through HTTP; returns the new request ID after asserting the insert."""
        count = LeaveRequest.objects.count()
        response = self.login(user).post(REQUESTS_URL, payload(dates["start"], dates["end"], note=note), format="json")
        self.assertEqual(response.status_code, 201, response.data)
        request_id = response.data["id"]
        self.assertEqual(LeaveRequest.objects.count(), count + 1)
        row = row_state(request_id)
        self.assertEqual((row["employee_id"], row["status"], row["note"]), (user.pk, LeaveRequest.Status.PENDING, note))
        self.assertEqual((row["decided_by_id"], row["decided_at"]), (None, None))
        return request_id

    def decide(self, actor, request_id, decision):
        return self.login(actor).post(decision_url(request_id), {"status": decision}, format="json")

    def decide_ok(self, actor, request_id, decision):
        """W2 success: same row, new status, actor and timestamp; content and count unchanged."""
        before = row_state(request_id)
        count = LeaveRequest.objects.count()
        started = timezone.now()
        response = self.decide(actor, request_id, decision)
        finished = timezone.now()
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual((response.data["id"], response.data["status"]), (request_id, decision))
        after = row_state(request_id)
        self.assertEqual(after["status"], decision)
        self.assertEqual(after["decided_by_id"], actor.pk)
        self.assertIsNotNone(after["decided_at"])
        self.assertTrue(started <= after["decided_at"] <= finished)
        for field in ("id", "employee_id", "leave_type", "start_date", "end_date", "note", "created_at"):
            self.assertEqual(after[field], before[field], field)
        self.assertEqual(LeaveRequest.objects.count(), count)
        return after

    def decide_denied(self, actor, request_id, decision, status_code, body=None):
        """W2 refusal: exact status (and body) with the persisted row unchanged."""
        before = row_state(request_id)
        count = LeaveRequest.objects.count()
        response = self.decide(actor, request_id, decision)
        self.assertEqual(response.status_code, status_code, response.data)
        self.assertEqual(set(response.data), {"detail"})
        if body is not None:
            self.assertEqual(response.data, body)
        self.assertEqual(row_state(request_id), before)
        self.assertEqual(LeaveRequest.objects.count(), count)

    def listed_ids(self, user):
        response = self.login(user).get(REQUESTS_URL)
        self.assertEqual(response.status_code, 200)
        return {item["id"]: item["status"] for item in response.data}

    def dashboard_balance(self, user):
        response = self.login(user).get("/api/dashboard/")
        self.assertEqual(response.status_code, 200)
        return response.data["balance"]


class SameRecordApprovalTests(CrossWorkflowTestCase):
    def test_w1_submission_then_w2_approval_consumes_allowance(self):
        """API-INT-001.01; FR-W1-06, FR-W2-01, FR-W2-04, FR-W2-05; BR-03, BR-04, BR-05.

        The request created by W1 is the one W2 approves: same primary key, owner
        and content; status approved with decided_by/decided_at set; the employee's
        derived balance drops by exactly the request's business days, seen both in
        the ORM and in the employee's own dashboard and list.
        """
        k = self.submit(self.e1, FIRST, "A22 approval")
        self.assertEqual(balance_view(self.e1), (10, 0, 10))  # pending reserves nothing
        self.assertEqual(self.listed_ids(self.m1).get(k), LeaveRequest.Status.PENDING)

        after = self.decide_ok(self.m1, k, LeaveRequest.Status.APPROVED)

        self.assertEqual(after["employee_id"], self.e1.pk)
        self.assertEqual(balance_view(self.e1), (10, 3, 7))
        self.assertEqual(self.dashboard_balance(self.e1), {"allowance": 10, "used": 3, "available": 7})
        self.assertEqual(self.listed_ids(self.e1), {k: LeaveRequest.Status.APPROVED})


class SameRecordRejectionTests(CrossWorkflowTestCase):
    def test_w1_submission_then_w2_rejection_consumes_nothing(self):
        """API-INT-001.02; FR-W1-04, FR-W1-06, FR-W2-04, FR-W2-06; BR-02, BR-03, BR-05.

        Rejecting the W1-created request records the decision on the same row but
        consumes no allowance, and releases its dates: the employee can submit the
        same dates again as a new request while the rejected row stays rejected.
        """
        k = self.submit(self.e1, FIRST, "A22 rejection")

        self.decide_ok(self.m1, k, LeaveRequest.Status.REJECTED)

        self.assertEqual(balance_view(self.e1), (10, 0, 10))
        self.assertEqual(self.dashboard_balance(self.e1), {"allowance": 10, "used": 0, "available": 10})
        again = self.submit(self.e1, FIRST, "A22 same dates after rejection")
        self.assertNotEqual(again, k)
        self.assertEqual(row_state(k)["status"], LeaveRequest.Status.REJECTED)
        self.assertEqual(balance_view(self.e1), (10, 0, 10))


class ApprovalOverdrawTests(CrossWorkflowTestCase):
    allowances = {"e1": 5}

    def test_second_approval_overdraws_allowance_characterization(self):
        """API-INT-001.03 — CHARACTERIZATION of a known SUT defect (TEST-BASIS GAP-01, risk PR-01).

        Allowance 5; two three-day requests both pass W1 because pending requests
        reserve nothing (FR-W1-05). Approving the first leaves 2 days. W2 has no
        approval-time balance check (views.py decide_request), so approving the
        second ALSO succeeds and the derived available balance becomes −1.

        This test pins the observed baseline behaviour so it is reported, not
        fixed. It is not an approved oracle: the desired rejection contract is
        undecided (blocked regression objective OBJ-UC02-01 / EC-01). When an
        approved fix lands, this test must be replaced by the agreed regression.
        """
        first = self.submit(self.e1, FIRST, "A22 overdraw first")
        second = self.submit(self.e1, SECOND, "A22 overdraw second")
        self.assertEqual(balance_view(self.e1), (5, 0, 5))

        self.decide_ok(self.m1, first, LeaveRequest.Status.APPROVED)
        self.assertEqual(balance_view(self.e1), (5, 3, 2))

        # Observed baseline: the second approval is accepted although D (3) > available (2).
        self.decide_ok(self.m1, second, LeaveRequest.Status.APPROVED)
        self.assertEqual(balance_view(self.e1), (5, 6, -1))
        self.assertEqual(self.dashboard_balance(self.e1), {"allowance": 5, "used": 6, "available": -1})
        self.assertEqual(
            {row_state(first)["status"], row_state(second)["status"]}, {LeaveRequest.Status.APPROVED}
        )


class CrossWorkflowAuthorizationTests(CrossWorkflowTestCase):
    def test_requester_cannot_decide_own_w1_request(self):
        """API-INT-001.04; FR-W2-02; BR-04, BR-05.

        An employee who submitted a request through W1 cannot decide it (role guard,
        403), whichever decision is sent. A manager who submits their own request
        through W1 is also refused by the self-decision guard (403). The persisted
        rows stay pending with no decider.
        """
        k = self.submit(self.e1, FIRST, "A22 employee own")
        self.decide_denied(self.e1, k, LeaveRequest.Status.APPROVED, 403, FORBIDDEN)
        self.decide_denied(self.e1, k, LeaveRequest.Status.REJECTED, 403, FORBIDDEN)

        own = self.submit(self.m1, SECOND, "A22 manager own")
        self.decide_denied(self.m1, own, LeaveRequest.Status.APPROVED, 403, SELF)
        self.assertEqual(row_state(k)["status"], LeaveRequest.Status.PENDING)
        self.assertEqual(row_state(own)["status"], LeaveRequest.Status.PENDING)

    def test_other_team_request_is_invisible_to_manager(self):
        """API-INT-001.05; FR-W2-01, FR-W2-02; BR-04.

        A request submitted through W1 by a team B employee does not appear in team
        A's manager's list, and that manager's decision on it returns 404 with no
        change. Positive control: team B's manager sees it and can approve it.
        """
        kb = self.submit(self.eb, FIRST, "A22 team B")

        self.assertNotIn(kb, self.listed_ids(self.m1))
        self.decide_denied(self.m1, kb, LeaveRequest.Status.APPROVED, 404)

        self.assertEqual(self.listed_ids(self.m2).get(kb), LeaveRequest.Status.PENDING)
        after = self.decide_ok(self.m2, kb, LeaveRequest.Status.APPROVED)
        self.assertEqual(after["decided_by_id"], self.m2.pk)


class InvalidTransitionTests(CrossWorkflowTestCase):
    def test_decision_on_approved_request_conflicts(self):
        """API-INT-001.06; FR-W2-04; BR-03, BR-05.

        After a W1-created request is approved through W2, approving it again or
        rejecting it returns 409. The original decider and timestamp are preserved
        and the allowance is consumed only once.
        """
        k = self.submit(self.e1, FIRST, "A22 approved twice")
        decided = self.decide_ok(self.m1, k, LeaveRequest.Status.APPROVED)

        self.decide_denied(self.m1, k, LeaveRequest.Status.APPROVED, 409, DECIDED)
        self.decide_denied(self.m1, k, LeaveRequest.Status.REJECTED, 409, DECIDED)

        self.assertEqual(row_state(k), decided)
        self.assertEqual(balance_view(self.e1), (10, 3, 7))

    def test_decision_on_rejected_request_conflicts(self):
        """API-INT-001.07; FR-W2-04, FR-W2-06; BR-03, BR-05.

        After a W1-created request is rejected through W2, rejecting it again or
        approving it returns 409. The rejection record is preserved and no
        allowance is consumed by the refused approval.
        """
        k = self.submit(self.e1, FIRST, "A22 rejected twice")
        decided = self.decide_ok(self.m1, k, LeaveRequest.Status.REJECTED)

        self.decide_denied(self.m1, k, LeaveRequest.Status.REJECTED, 409, DECIDED)
        self.decide_denied(self.m1, k, LeaveRequest.Status.APPROVED, 409, DECIDED)

        self.assertEqual(row_state(k), decided)
        self.assertEqual(balance_view(self.e1), (10, 0, 10))


class RepeatedSubmissionTests(CrossWorkflowTestCase):
    def test_identical_submission_repeated_while_pending(self):
        """API-INT-001.08; FR-W1-04, FR-W1-06; BR-02, BR-03: immediate repeat → overlap 400, one row, balance unchanged."""
        first = self.submit(self.e1, FIRST, "A22 repeat")
        before = row_state(first)
        response = self.login(self.e1).post(
            REQUESTS_URL, payload(FIRST["start"], FIRST["end"], note="A22 repeat"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"non_field_errors": ["Esiste già una richiesta sovrapposta."]})
        self.assertEqual(list(LeaveRequest.objects.values_list("pk", flat=True)), [first])
        self.assertEqual(row_state(first), before)
        self.assertEqual(balance_view(self.e1), (10, 0, 10))


class ExitCriterionScenarioTests(CrossWorkflowTestCase):
    allowances = {"e1": 5}

    def test_ec01_two_four_day_requests_characterization(self):
        """API-INT-001.09 — CHARACTERIZATION of the EC-01 scenario (GAP-01, PR-01), not an approved oracle.

        Allowance 5, two pending four-day requests. EC-01 expects the second
        approval to be refused with 1 day remaining. The baseline accepts it and
        the balance becomes −3. Replace this test when the rejection contract is agreed.
        """
        first = self.submit(self.e1, {"start": "2026-12-07", "end": "2026-12-10"}, "A22 EC-01 first")
        second = self.submit(self.e1, {"start": "2026-12-14", "end": "2026-12-17"}, "A22 EC-01 second")
        self.decide_ok(self.m1, first, LeaveRequest.Status.APPROVED)
        self.assertEqual(balance_view(self.e1), (5, 4, 1))  # the EC-01 target
        charged = row_state(first)

        self.decide_ok(self.m1, second, LeaveRequest.Status.APPROVED)  # EC-01 expects a refusal here
        self.assertEqual(balance_view(self.e1), (5, 8, -3))
        self.assertEqual(row_state(first), charged)
