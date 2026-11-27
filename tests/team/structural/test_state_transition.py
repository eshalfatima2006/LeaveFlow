# =============================================================================
# A2.3 — STATE TRANSITION TESTING (LeaveRequest.status via W2)
#
# States: pending, approved, rejected (no other state exists in the baseline).
# Events: approve, reject (W2 POST /api/requests/{id}/decision/).
# Creation (W1) puts a new request in "pending"; approved and rejected are final.
#
# | Current state | Event   | Next state | Allowed? | Test                               |
# |---------------|---------|------------|----------|------------------------------------|
# | (none)        | submit  | pending    | YES      | test_st_none_submit_pending        |
# | pending       | approve | approved   | YES      | test_st_pending_approve_approved   |
# | pending       | reject  | rejected   | YES      | test_st_pending_reject_rejected    |
# | approved      | approve | -          | NO (409) | test_st_approved_approve_409       |
# | approved      | reject  | -          | NO (409) | test_st_approved_reject_409        |
# | rejected      | approve | -          | NO (409) | test_st_rejected_approve_409       |
# | rejected      | reject  | -          | NO (409) | test_st_rejected_reject_409        |
#
# Coverage (Lecture 15): every valid transition (0-switch) plus every invalid
# cell of the approve/reject events, i.e. "all transitions" for this table. The
# invalid event "pending" from state pending (400) is executed once, as
# test_ep_w2_status_pending in test_ep_bva.py, and is not repeated here.
#
# Counting: one executable case per row. A2.1 FinalStateTests and
# AuthorizedDecisionTests use the same transitions with other data; report each
# pair once at the API level.
# =============================================================================
"""A2.3 state-transition tests for the LeaveRequest status, through real API calls."""

from datetime import date

from leave.models import LeaveRequest
from tests.team.api.support import all_rows, balance_view, payload, row_state
from tests.team.fixtures.leave_data import DECIDED_AT, build_people, make_request
from tests.team.structural.support import DECIDED, StructuralTestCase


class LeaveRequestStateTransitionTests(StructuralTestCase):
    def setUp(self):
        self.p = build_people("st")
        self.e1, self.m1 = self.p.e1, self.p.m1
        self.pending = make_request(self.e1, start=date(2026, 12, 7), end=date(2026, 12, 8)).pk
        self.approved = make_request(
            self.e1, start=date(2026, 12, 14), end=date(2026, 12, 15),
            status=LeaveRequest.Status.APPROVED, decided_by=self.m1,
        ).pk
        self.rejected = make_request(
            self.e1, start=date(2026, 12, 21), end=date(2026, 12, 22),
            status=LeaveRequest.Status.REJECTED, decided_by=self.m1,
        ).pk

    def assert_disallowed(self, request_id, event, original_status):
        """409 with the original status, decider and timestamp unchanged."""
        self.assert_w2_denied(self.m1, request_id, event, 409, DECIDED)
        row = row_state(request_id)
        self.assertEqual((row["status"], row["decided_by_id"], row["decided_at"]), (original_status, self.m1.pk, DECIDED_AT))

    # Allowed transitions ---------------------------------------------------------
    def test_st_pending_approve_approved(self):
        """State transition pending --approve--> approved (allowed, 0-switch edge).

        Expect 200; the same row becomes approved with decided_by = manager and
        decided_at set during the call; the employee's derived balance falls by
        the request's 2 business days (10 → 8, after 2 days already approved).
        """
        self.assertEqual(balance_view(self.e1), (10, 2, 8))
        self.assert_w2_decided(self.m1, self.pending, "approved")
        self.assertEqual(balance_view(self.e1), (10, 4, 6))

    def test_st_pending_reject_rejected(self):
        """State transition pending --reject--> rejected (allowed, 0-switch edge).

        Expect 200; the same row becomes rejected with decided_by/decided_at set;
        no allowance is consumed.
        """
        self.assert_w2_decided(self.m1, self.pending, "rejected")
        self.assertEqual(balance_view(self.e1), (10, 2, 8))

    # Disallowed transitions (final states) -----------------------------------------
    def test_st_approved_approve_409(self):
        """State transition approved --approve--> (disallowed): 409, approved record unchanged, no double charge."""
        self.assert_disallowed(self.approved, "approved", LeaveRequest.Status.APPROVED)
        self.assertEqual(balance_view(self.e1), (10, 2, 8))

    def test_st_approved_reject_409(self):
        """State transition approved --reject--> (disallowed): 409, an approval cannot be reversed."""
        self.assert_disallowed(self.approved, "rejected", LeaveRequest.Status.APPROVED)
        self.assertEqual(balance_view(self.e1), (10, 2, 8))

    def test_st_rejected_approve_409(self):
        """State transition rejected --approve--> (disallowed): 409, the rejection stands and nothing is charged."""
        self.assert_disallowed(self.rejected, "approved", LeaveRequest.Status.REJECTED)
        self.assertEqual(balance_view(self.e1), (10, 2, 8))

    def test_st_rejected_reject_409(self):
        """State transition rejected --reject--> (disallowed): 409, a repeated rejection is refused."""
        self.assert_disallowed(self.rejected, "rejected", LeaveRequest.Status.REJECTED)

    # Creation is not a transition of existing requests -----------------------------
    def test_st_none_submit_pending(self):
        """W1 creation (none --submit--> pending) is independent of other requests' states.

        With requests in pending, approved and rejected states, a new
        non-overlapping submission (Mon 2027-01-04..Tue 01-05) is accepted as a
        new pending row, and the three existing rows keep their states and audit
        fields. Dates overlapping a pending or approved request would still be
        refused by BR-02; that is covered by the overlap BVA cases.
        """
        before = all_rows()
        _, row = self.assert_w1_created(self.e1, payload("2027-01-04", "2027-01-05"), days=2)
        self.assertEqual(row["status"], LeaveRequest.Status.PENDING)
        self.assertEqual([r for r in all_rows() if r["id"] != row["id"]], before)
