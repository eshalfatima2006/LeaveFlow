# =============================================================================
# A2.3 — DECISION TABLE TESTING
# Rules with two or more Boolean conditions on W1 and W2, one test per rule.
#
# TABLE 1 — W1 submission validation (LeaveRequestSerializer.validate + LeaveRequest.clean)
#   C1 end_date >= start_date              (models.py:81, checked first)
#   C2 no active (pending/approved) overlap (models.py:83–90, only if C1 = T)
#   C3 a LeaveBalance record exists         (serializers.py:36–37)
#   C4 business_days <= available_days      (serializers.py:37, only if C3 = T: short-circuit)
#   5 rules cover all 16 combinations ("–" = not evaluated / does not matter).
#
# TABLE 2 — W2 decision authorisation and state (views.decide_request, guard order)
#   C1 role in {manager, admin}             (views.py:68)
#   C2 request visible to the actor         (views.py:75–78, only if C1 = T)
#   C3 request.employee != actor            (views.py:79, only if C1, C2 = T)
#   C4 request.status == pending            (views.py:81, only if C1–C3 = T)
#   5 rules cover all 16 combinations. The decision value is held valid
#   ("approved"/"rejected"); invalid values are EP cases in test_ep_bva.py.
#
# Each rule's test sets its don't-care conditions to values that show they are
# not evaluated (e.g. an end-before-start request whose dates also overlap).
# Counting: one executable case per rule, with inputs not repeated elsewhere in
# this suite. A2.1 tests of the same rules (API-W1-003/004/005, API-W2-002/004)
# are the same case classes at the same level: count each pair once.
# =============================================================================
"""A2.3 decision tables for W1 validation and W2 authorisation, through real API calls."""

from datetime import date

from leave.models import LeaveRequest, User
from tests.team.api.support import add_member, balance_view, payload, row_state
from tests.team.fixtures.leave_data import build_people, make_request
from tests.team.structural.support import (
    DECIDED, END_BEFORE_START, FORBIDDEN, INSUFFICIENT, OVERLAP, SELF, StructuralTestCase,
)


class W1ValidationDecisionTable(StructuralTestCase):
    """Decision table 1 — W1 submission validation.

        Rule        R1    R2    R3    R4    R5
        ---------  ----  ----  ----  ----  ----
        C1 end>=st   F     T     T     T     T
        C2 no ovlp   -     F     T     T     T
        C3 balance   -     -     F     T     T
        C4 D <= A    -     -     -     F     T
        ---------  ----  ----  ----  ----  ----
        HTTP        400   400   201   400   201
        Row created  no    no   yes    no   yes
        Error key  end_  non_    -   non_    -
                   date  field       field
        Message    date   over-  -   saldo   -
                   order  lap        insuff.

    R3 is the observed baseline (TEST-BASIS GAP-07): without a balance record the
    balance check is skipped. It is a characterisation, not an approved rule.
    C4 is never evaluated when C3 = F (Python ``and`` short-circuit).
    """

    def setUp(self):
        self.p = build_people("dt1", allowances={"e2": 2})
        self.e1, self.e2 = self.p.e1, self.p.e2
        self.nb = add_member("dt1", "nb", User.Role.EMPLOYEE, self.p.team_a, allowance=None)
        self.e5 = add_member("dt1", "e5", User.Role.EMPLOYEE, self.p.team_a, allowance=5)
        # Approved history: e1 Mon 12-07..Tue 12-08; e5 the same two days (A becomes 3).
        for employee in (self.e1, self.e5):
            make_request(employee, start=date(2026, 12, 7), end=date(2026, 12, 8),
                         status=LeaveRequest.Status.APPROVED, decided_by=self.p.m1)

    def test_dt1_r1(self):
        """DT1 R1: C1=F (C2–C4 not evaluated) → 400 on end_date only, no row.

        End Mon 12-07 before start Tue 12-08; those dates also intersect e1's
        approved request, yet only the date-order error is returned, which shows
        C1 is checked first and C2 is not evaluated.
        """
        response = self.assert_w1_rejected(self.e1, payload("2026-12-08", "2026-12-07"), 400, "end_date", message=END_BEFORE_START)
        self.assertEqual(set(response.data), {"end_date"})

    def test_dt1_r2(self):
        """DT1 R2: C1=T, C2=F (C3/C4 not evaluated) → 400 overlap, no row.

        Tue 12-08..Wed 12-09 intersects e1's APPROVED request (approved requests
        block too, BR-02); e1 has ample balance, so only the overlap error appears.
        """
        response = self.assert_w1_rejected(self.e1, payload("2026-12-08", "2026-12-09"), 400, "non_field_errors", message=OVERLAP)
        self.assertEqual(set(response.data), {"non_field_errors"})

    def test_dt1_r3(self):
        """DT1 R3: C1=T, C2=T, C3=F (C4 masked) → 201 although D is large.

        An employee without a LeaveBalance submits 2026-12-14..2027-01-15 (25
        business days) and is accepted: the balance check is skipped (GAP-07,
        characterisation of baseline behaviour).
        """
        _, row = self.assert_w1_created(self.nb, payload("2026-12-14", "2027-01-15"), days=25)
        self.assertEqual(row["status"], LeaveRequest.Status.PENDING)

    def test_dt1_r4(self):
        """DT1 R4: C1=T, C2=T, C3=T, C4=F → 400 'Saldo ferie insufficiente.', no row.

        Allowance 2, request Mon 12-14..Wed 12-16 = 3 business days > 2.
        """
        self.assert_w1_rejected(self.e2, payload("2026-12-14", "2026-12-16"), 400, "non_field_errors", message=INSUFFICIENT)
        self.assertEqual(balance_view(self.e2), (2, 0, 2))

    def test_dt1_r5(self):
        """DT1 R5: all conditions true → 201 pending row; no allowance consumed.

        Allowance 5 with 2 approved days (available 3); request Mon 12-14..Tue
        12-15 = 2 days ≤ 3. Pending reserves nothing, so the balance stays (5, 2, 3).
        """
        self.assert_w1_created(self.e5, payload("2026-12-14", "2026-12-15"), days=2)
        self.assertEqual(balance_view(self.e5), (5, 2, 3))


class W2DecisionAuthorisationTable(StructuralTestCase):
    """Decision table 2 — W2 decision authorisation and state.

        Rule            R1    R2    R3    R4    R5
        -------------  ----  ----  ----  ----  ----
        C1 mgr/admin     F     T     T     T     T
        C2 visible       -     F     T     T     T
        C3 not own       -     -     F     T     T
        C4 pending       -     -     -     F     T
        -------------  ----  ----  ----  ----  ----
        HTTP            403   404   403   409   200
        Status changed   no    no    no    no   yes
        Error          Oper. Not   Non   già    -
                       non   found puoi  stata
                       cons.       ...   dec.

    Guard order (views.py:68–82): role → decision value → visible lookup → self
    → pending. Admin always has C2 = T (sees all teams).
    """

    def setUp(self):
        self.p = build_people("dt2")
        self.eb = add_member("dt2", "eb", User.Role.EMPLOYEE, self.p.team_b)
        self.pending_a = make_request(self.p.e1, start=date(2026, 12, 7), end=date(2026, 12, 8)).pk
        self.pending_b = make_request(self.eb, start=date(2026, 12, 7), end=date(2026, 12, 8)).pk
        self.own_m1 = make_request(self.p.m1, start=date(2026, 12, 14), end=date(2026, 12, 15)).pk
        self.approved_a = make_request(
            self.p.e1, start=date(2026, 12, 21), end=date(2026, 12, 22),
            status=LeaveRequest.Status.APPROVED, decided_by=self.p.m1,
        ).pk

    def test_dt2_r1(self):
        """DT2 R1: C1=F → 403 'Operazione non consentita.', unchanged.

        A team B employee tries to reject their OWN pending request: C3 would also
        be false, but the role guard answers first (403 role, not the self message).
        """
        self.assert_w2_denied(self.eb, self.pending_b, "rejected", 403, FORBIDDEN)

    def test_dt2_r2(self):
        """DT2 R2: C1=T, C2=F → 404, unchanged.

        A manager with no team sees only their own requests, so a team A request
        is not found by the scoped lookup.
        """
        self.assert_w2_denied(self.p.teamless_manager, self.pending_a, "rejected", 404)

    def test_dt2_r3(self):
        """DT2 R3: C1=T, C2=T, C3=F → 403 'Non puoi decidere una tua richiesta.', unchanged.

        The team A manager approves their own pending request, which is visible to
        them through the team filter.
        """
        self.assert_w2_denied(self.p.m1, self.own_m1, "approved", 403, SELF)

    def test_dt2_r4(self):
        """DT2 R4: C1=T, C2=T, C3=T, C4=F → 409 'La richiesta è già stata decisa.'.

        The admin approves an already approved team A request; the original
        decider and timestamp are preserved (checked by full-row readback).
        """
        before = row_state(self.approved_a)
        self.assert_w2_denied(self.p.admin, self.approved_a, "approved", 409, DECIDED)
        self.assertEqual(row_state(self.approved_a), before)

    def test_dt2_r5(self):
        """DT2 R5: all conditions true → 200; the same row becomes approved by the admin."""
        after = self.assert_w2_decided(self.p.admin, self.pending_b, "approved")
        self.assertEqual(after["employee_id"], self.eb.pk)
