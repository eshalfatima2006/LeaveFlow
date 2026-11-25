# =============================================================================
# A2.3 — DECISION TABLES, PART 2 (RTM DT-002, DT-003, DT-004, DT-005)
# Complements test_decision_table.py (code tables DT1 and DT2). Every table lists
# the combinations of its atomic conditions; infeasible ones are justified.
#
# DT-002 overlap predicate        LeaveRequest.clean, models.py:83-90
# DT-003 request visibility       views.visible_requests, views.py:46-51
# DT-004 event recipients         events.build_leave_event, events.py:18-29
# DT-005 upcoming team leave      views.team_view (next_leave query)
#
# Counting: one executable case per test method. DT-002 R1 (pending), the
# other-employee, rejected and neighbour rows repeat case classes of API-W1-004
# and DT1 R2 with other data, as do four of the five DT-003 rows with
# API-W2-001.01: report each such class once at the API level. DT-004 and DT-005
# have no earlier team test.
# =============================================================================
"""A2.3 decision tables for overlap, visibility, event recipients and upcoming leave."""

from datetime import date
from unittest import mock

from django.core.exceptions import ValidationError

from leave.events import build_leave_event
from leave.models import LeaveRequest, User
from tests.team.api.support import add_member
from tests.team.fixtures.leave_data import build_people, make_request
from tests.team.structural.support import (
    OVERLAP, REQUESTS_URL, StructuralTestCase, payload, token_client,
)

Status = LeaveRequest.Status


class OverlapDecisionTable(StructuralTestCase):
    """DT-002 — does an existing row block a new request?

    Conditions (existing row X, candidate N):
      E  same employee              S  X.status in {pending, approved}
      L  X.start <= N.end           R  X.end >= N.start
      P  X.pk != N.pk               Action: block iff E and S and L and R and P

    32 combinations. L=F with R=F is infeasible for ordered intervals
    (X.start > N.end >= N.start > X.end contradicts X.start <= X.end): 8 rows out.
    P=F is unreachable through W1, because a new candidate has no pk; those 12
    feasible rows run at model level on the saved row itself (TestCase method
    test_dt002_pk_excluded_rows). The 12 feasible P=T rows run through the API:

        Rule  R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12
        E     T  T  T  T  T  T  F  F  F  F   F   F
        S     T  T  T  F  F  F  T  T  T  F   F   F
        L     T  F  T  T  F  T  T  F  T  T   F   T
        R     T  T  F  T  T  F  T  T  F  T   T   F
        HTTP  400 ----------------- 201 ------------------
    """

    # Candidate intervals against X = Tue 12-08 .. Thu 12-10, keyed by (L, R).
    INTERVALS = {
        (True, True): ("2026-12-09", "2026-12-09"),
        (False, True): ("2026-12-07", "2026-12-07"),
        (True, False): ("2026-12-11", "2026-12-11"),
    }

    def setUp(self):
        self.p = build_people("dtt")

    def existing(self, status):
        return make_request(
            self.p.e1, start=date(2026, 12, 8), end=date(2026, 12, 10), status=status,
            decided_by=None if status == Status.PENDING else self.p.m1,
        )

    def check_row(self, e, s, left, right, *, status=None):
        status = status or (Status.PENDING if s else Status.REJECTED)
        self.existing(status)
        body = payload(*self.INTERVALS[left, right])
        candidate = self.p.e1 if e else self.p.e2
        if e and s and left and right:
            self.assert_w1_rejected(candidate, body, 400, "non_field_errors", message=OVERLAP)
        else:
            self.assert_w1_created(candidate, body, days=1)

    def test_dt002_r1_pending_blocks(self):
        """DT-002 R1: E,S,L,R all true, X pending → 400 overlap, no row."""
        self.check_row(True, True, True, True)

    def test_dt002_r1_approved_blocks(self):
        """DT-002 R1: E,S,L,R all true, X approved (second value of S) → 400 overlap, no row."""
        self.check_row(True, True, True, True, status=Status.APPROVED)

    def test_dt002_r2(self):
        """DT-002 R2: only L false (candidate ends before X starts) → 201."""
        self.check_row(True, True, False, True)

    def test_dt002_r3(self):
        """DT-002 R3: only R false (candidate starts after X ends) → 201."""
        self.check_row(True, True, True, False)

    def test_dt002_r4(self):
        """DT-002 R4: only S false (X rejected) → 201."""
        self.check_row(True, False, True, True)

    def test_dt002_r5(self):
        """DT-002 R5: S and L false → 201."""
        self.check_row(True, False, False, True)

    def test_dt002_r6(self):
        """DT-002 R6: S and R false → 201."""
        self.check_row(True, False, True, False)

    def test_dt002_r7(self):
        """DT-002 R7: only E false (X belongs to a colleague) → 201."""
        self.check_row(False, True, True, True)

    def test_dt002_r8(self):
        """DT-002 R8: E and L false → 201."""
        self.check_row(False, True, False, True)

    def test_dt002_r9(self):
        """DT-002 R9: E and R false → 201."""
        self.check_row(False, True, True, False)

    def test_dt002_r10(self):
        """DT-002 R10: E and S false → 201."""
        self.check_row(False, False, True, True)

    def test_dt002_r11(self):
        """DT-002 R11: E, S and L false → 201."""
        self.check_row(False, False, False, True)

    def test_dt002_r12(self):
        """DT-002 R12: E, S and R false → 201."""
        self.check_row(False, False, True, False)

    def test_dt002_pk_excluded_rows(self):
        """DT-002 P=F, 12 rows (model level): the saved row never blocks itself, whatever E,S,L,R are.

        The saved row is changed in memory only, so the query compares the stored
        row with the candidate values while the pk stays equal. Control: the same
        all-true values as an unsaved copy (P=T) do block.
        """
        for s in (True, False):
            stored = self.existing(Status.PENDING if s else Status.REJECTED)
            for e in (True, False):
                for (left, right), (start, end) in self.INTERVALS.items():
                    with self.subTest(E=e, S=s, L=left, R=right):
                        item = LeaveRequest.objects.get(pk=stored.pk)
                        item.employee = self.p.e1 if e else self.p.e2
                        item.start_date, item.end_date = date.fromisoformat(start), date.fromisoformat(end)
                        item.clean()  # must not raise
            if s:
                twin = LeaveRequest(employee=self.p.e1, start_date=date(2026, 12, 9), end_date=date(2026, 12, 9))
                with self.assertRaises(ValidationError):
                    twin.clean()
                stored.status, stored.decided_by = Status.REJECTED, self.p.m1
                stored.save()


class VisibilityDecisionTable(StructuralTestCase):
    """DT-003 — which requests does GET /api/requests/ list? (A: admin, M: manager, T: has team)

        Rule   R1   R2   R3   R4   R5
        A      T    F    F    F    F
        M      -    T    T    F    F
        T      -    T    F    T    F
        Scope  all  team own  own  own

    R1 runs for an admin with and without a team (T does not matter). Combinations
    with A=T and M=T are infeasible: role holds a single value.
    """

    def setUp(self):
        self.p = build_people("dtv")
        self.eb = add_member("dtv", "eb", User.Role.EMPLOYEE, self.p.team_b)
        self.lone = add_member("dtv", "lone", User.Role.EMPLOYEE, None)
        self.lone_admin = add_member("dtv", "ladmin", User.Role.ADMIN, None)
        self.ids = {
            key: make_request(user, start=date(2026, 12, 7), end=date(2026, 12, 8)).pk
            for key, user in {
                "e1": self.p.e1, "e2": self.p.e2, "eb": self.eb, "m1": self.p.m1,
                "teamless": self.p.teamless_manager, "lone": self.lone,
            }.items()
        }

    def assert_lists(self, user, *keys):
        response = token_client(user).get(REQUESTS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted(r["id"] for r in response.data), sorted(self.ids[k] for k in keys))

    def test_dt003_r1_admin_with_team(self):
        """DT-003 R1: admin with a team → every request of every team."""
        self.assert_lists(self.p.admin, *self.ids)

    def test_dt003_r1_admin_without_team(self):
        """DT-003 R1: admin without a team → still every request (T does not matter)."""
        self.assert_lists(self.lone_admin, *self.ids)

    def test_dt003_r2_manager_with_team(self):
        """DT-003 R2: M=T, T=T → exactly the team's requests, own included."""
        self.assert_lists(self.p.m1, "e1", "e2", "m1")

    def test_dt003_r3_manager_without_team(self):
        """DT-003 R3: M=T, T=F → own only; another teamless user's request is not listed."""
        self.assert_lists(self.p.teamless_manager, "teamless")

    def test_dt003_r4_employee_with_team(self):
        """DT-003 R4: M=F, T=T → own only; the teammate's request is not listed."""
        self.assert_lists(self.p.e1, "e1")

    def test_dt003_r5_employee_without_team(self):
        """DT-003 R5: M=F, T=F → own only (the row no earlier team test covered)."""
        self.assert_lists(self.lone, "lone")


class EventRecipientDecisionTable(StructuralTestCase):
    """DT-004 — who receives the event of a submission or a decision?

    Conditions for a user U and a submitted request of employee X:
      A  U is admin     M  U is manager     T  U.team == X.team     O  U is X
      Action: notify iff (A or (M and T)) and not O

        Rule    R1  R2  R3  R4  R5  R6  R7  R8  R9
        A       T   T   F   F   F   F   T   F   F
        M       F   F   T   T   F   F   F   T   F
        T       T   F   T   F   T   F   T   T   T
        O       F   F   F   F   F   F   T   T   T
        Notify  yes yes yes no  no  no  no  no  no

    Of the 16 combinations, A=T with M=T (4) is infeasible: one role per user.
    O=T forces T=T (a user's team equals itself), which removes 3 more. The
    remaining 9 are all listed. A decision event ignores this table and notifies
    the request's owner only.

    The request is a real API call. ``leave.views.publish_leave_event`` is replaced
    by a recorder that runs the real ``build_leave_event`` with the arguments the
    view passed, because Redis publication is disabled in this test profile.
    Delivery through Redis, the worker and the gateway is not tested here.
    """

    def setUp(self):
        self.p = build_people("dtr")
        self.team_a_admin = self.p.admin
        self.team_b_admin = add_member("dtr", "admb", User.Role.ADMIN, self.p.team_b)
        self.events = []
        patcher = mock.patch(
            "leave.views.publish_leave_event",
            side_effect=lambda item, kind, actor: self.events.append(build_leave_event(item, kind, actor)),
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def submitted_recipients(self, employee):
        response, _ = self.assert_w1_created(employee, payload("2026-12-07", "2026-12-08"))
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        self.assertEqual((event["type"], event["actor"]["id"]), ("leave.requested", employee.pk))
        self.assertEqual((event["request"]["id"], event["request"]["employee_id"]), (response.data["id"], employee.pk))
        self.assertEqual(len(event["recipients"]), len(set(event["recipients"])))  # no duplicates
        return set(event["recipients"])

    def test_dt004_r1_admin_same_team(self):
        """DT-004 R1: A=T, T=T, O=F → notified."""
        self.assertIn(self.team_a_admin.pk, self.submitted_recipients(self.p.e1))

    def test_dt004_r2_admin_other_team(self):
        """DT-004 R2: A=T, T=F, O=F → notified."""
        self.assertIn(self.team_b_admin.pk, self.submitted_recipients(self.p.e1))

    def test_dt004_r3_manager_same_team(self):
        """DT-004 R3: M=T, T=T, O=F → notified."""
        self.assertIn(self.p.m1.pk, self.submitted_recipients(self.p.e1))

    def test_dt004_r4_manager_other_team(self):
        """DT-004 R4: M=T, T=F, O=F → not notified (other team's and teamless manager)."""
        recipients = self.submitted_recipients(self.p.e1)
        self.assertFalse({self.p.m2.pk, self.p.teamless_manager.pk} & recipients)

    def test_dt004_r5_employee_same_team(self):
        """DT-004 R5: A=F, M=F, T=T, O=F → the teammate is not notified."""
        self.assertNotIn(self.p.e2.pk, self.submitted_recipients(self.p.e1))

    def test_dt004_r6_employee_other_team(self):
        """DT-004 R6: A=F, M=F, T=F, O=F → not notified."""
        eb = add_member("dtr", "eb", User.Role.EMPLOYEE, self.p.team_b)
        self.assertNotIn(eb.pk, self.submitted_recipients(self.p.e1))

    def test_dt004_r7_admin_is_requester(self):
        """DT-004 R7: A=T, O=T → the requesting admin is excluded; exactly the others remain."""
        self.assertEqual(self.submitted_recipients(self.team_a_admin), {self.team_b_admin.pk, self.p.m1.pk})

    def test_dt004_r8_manager_is_requester(self):
        """DT-004 R8: M=T, T=T, O=T → the requesting manager is excluded; exactly the admins remain."""
        self.assertEqual(self.submitted_recipients(self.p.m1), {self.team_a_admin.pk, self.team_b_admin.pk})

    def test_dt004_r9_employee_is_requester(self):
        """DT-004 R9: A=F, M=F, O=T → the requester is excluded; exactly both admins and m1 are notified."""
        self.assertEqual(
            self.submitted_recipients(self.p.e1), {self.team_a_admin.pk, self.team_b_admin.pk, self.p.m1.pk},
        )

    def test_dt004_teamless_requester_characterization(self):
        """DT-004, T with both teams null — CHARACTERIZATION (GAP-08), not an approved oracle.

        A teamless manager is notified about a teamless employee's request
        (``team_id=None`` matches as IS NULL), although visible_requests never
        shows that request to them.
        """
        lone = add_member("dtr", "lone", User.Role.EMPLOYEE, None)
        recipients = self.submitted_recipients(lone)
        self.assertEqual(recipients, {self.team_a_admin.pk, self.team_b_admin.pk, self.p.teamless_manager.pk})

    def assert_decision_notifies_owner_only(self, decision):
        item = make_request(self.p.e1, start=date(2026, 12, 7), end=date(2026, 12, 8))
        self.assert_w2_decided(self.p.m1, item.pk, decision)
        self.assertEqual([(e["type"], e["recipients"], e["actor"]["id"]) for e in self.events],
                         [(f"leave.{decision}", [self.p.e1.pk], self.p.m1.pk)])

    def test_dt004_approval_notifies_owner_only(self):
        """DT-004 decision branch: approval → one leave.approved event to the owner only."""
        self.assert_decision_notifies_owner_only("approved")

    def test_dt004_rejection_notifies_owner_only(self):
        """DT-004 decision branch: rejection → one leave.rejected event to the owner only."""
        self.assert_decision_notifies_owner_only("rejected")

    def test_dt004_refused_calls_publish_nothing(self):
        """DT-004: a refused submission (400) and a refused decision (403) publish no event."""
        item = make_request(self.p.e1, start=date(2026, 12, 7), end=date(2026, 12, 8))
        self.assert_w1_rejected(self.p.e1, payload("2026-12-08", "2026-12-08"), 400, "non_field_errors")
        self.assert_w2_denied(self.p.e2, item.pk, "approved", 403)
        self.assertEqual(self.events, [])


class UpcomingLeaveDecisionTable(StructuralTestCase):
    """DT-005 — which leave does GET /api/team/ show as a member's next_leave?

      P  status == approved     F  end_date >= today

        Rule        R1   R2    R3    R4
        P           T    T     F     F
        F           T    F     T     F
        next_leave  yes  null  null  null

    "Today" is fixed at Wed 2026-12-16, so the F limit is tested at end = today-1,
    today and today+1. Several R1 rows: the earliest start is returned.
    """

    TODAY = date(2026, 12, 16)

    def setUp(self):
        self.p = build_people("dtu")
        patcher = mock.patch("leave.views.timezone.localdate", return_value=self.TODAY)
        patcher.start()
        self.addCleanup(patcher.stop)

    def leave(self, start, end, status=Status.APPROVED):
        return make_request(
            self.p.e1, start=start, end=end, status=status,
            decided_by=None if status == Status.PENDING else self.p.m1,
        )

    def next_leave(self):
        response = token_client(self.p.m1).get("/api/team/")
        self.assertEqual(response.status_code, 200)
        members = {m["id"]: m for m in response.data}
        self.assertEqual(
            set(members), {u.pk for u in (self.p.e1, self.p.e2, self.p.m1, self.p.admin)},
        )
        self.assertIsNone(members[self.p.e2.pk]["next_leave"])  # e1's leave is never shown for a colleague
        return members[self.p.e1.pk]["next_leave"]

    def test_dt005_r1_end_after_today(self):
        """DT-005 R1: approved, end = today+1 (leave in progress) → shown."""
        self.leave(date(2026, 12, 15), date(2026, 12, 17))
        self.assertEqual(self.next_leave(), {"start_date": date(2026, 12, 15), "end_date": date(2026, 12, 17)})

    def test_dt005_r1_end_today(self):
        """DT-005 R1: approved, end = today (inclusive limit) → shown."""
        self.leave(date(2026, 12, 15), self.TODAY)
        self.assertEqual(self.next_leave(), {"start_date": date(2026, 12, 15), "end_date": self.TODAY})

    def test_dt005_r2_end_yesterday(self):
        """DT-005 R2: approved, end = today-1 → null."""
        self.leave(date(2026, 12, 14), date(2026, 12, 15))
        self.assertIsNone(self.next_leave())

    def test_dt005_r3_pending_future(self):
        """DT-005 R3: pending and future → null."""
        self.leave(date(2026, 12, 21), date(2026, 12, 22), Status.PENDING)
        self.assertIsNone(self.next_leave())

    def test_dt005_r3_rejected_future(self):
        """DT-005 R3: rejected and future (second non-approved value of P) → null."""
        self.leave(date(2026, 12, 21), date(2026, 12, 22), Status.REJECTED)
        self.assertIsNone(self.next_leave())

    def test_dt005_r4_pending_past(self):
        """DT-005 R4: pending and past → null."""
        self.leave(date(2026, 12, 14), date(2026, 12, 15), Status.PENDING)
        self.assertIsNone(self.next_leave())

    def test_dt005_no_requests(self):
        """DT-005: a member without any request → null."""
        self.assertIsNone(self.next_leave())

    def test_dt005_earliest_start_selected(self):
        """DT-005: two R1 rows, the later one stored first → the earlier start is returned."""
        self.leave(date(2026, 12, 28), date(2026, 12, 29))
        self.leave(date(2026, 12, 21), date(2026, 12, 22))
        self.leave(date(2026, 12, 14), date(2026, 12, 15))  # past: earliest start overall, but F is false
        self.assertEqual(self.next_leave(), {"start_date": date(2026, 12, 21), "end_date": date(2026, 12, 22)})

    def test_dt005_approval_through_w2_becomes_upcoming(self):
        """DT-005 with W2: pending (null) → manager approves → the same dates appear in /api/team/."""
        item = self.leave(date(2026, 12, 21), date(2026, 12, 22), Status.PENDING)
        self.assertIsNone(self.next_leave())
        self.assert_w2_decided(self.p.m1, item.pk, "approved")
        self.assertEqual(self.next_leave(), {"start_date": date(2026, 12, 21), "end_date": date(2026, 12, 22)})
