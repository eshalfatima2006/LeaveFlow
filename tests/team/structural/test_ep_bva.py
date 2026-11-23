# =============================================================================
# A2.3 — EQUIVALENCE PARTITIONING (EP) and THREE-POINT BOUNDARY VALUE ANALYSIS (BVA)
# Endpoints: W1 POST /api/requests/ ; W2 POST /api/requests/{id}/decision/
#
# EP rule: every valid and invalid class gets its own test; each invalid test
# changes exactly ONE input from a valid base payload.
#
# W1 partitions (valid base: vacation, Mon 2026-12-14..Tue 12-15, short note,
# employee with allowance 10 and a real token)
#   leave_type     valid {vacation, permit, personal}   invalid {empty, unknown string, numeric}
#   start_date     valid {future weekday, today}        invalid {missing, non-date string, null}
#   end_date       valid {same as start, after start}   invalid {before start, missing}
#   note           valid {empty, 1 char, within limit}  invalid {over 280 chars}
#   authentication valid {valid token}                  invalid {no token, wrong token}
#
# W2 partitions (valid base: decision value "approved" by an authorised actor
# on a visible, pending, non-own request)
#   status (body)  valid {approved, rejected}           invalid {empty, "pending", random string}
#   request_id     valid {existing pending visible}     invalid {nonexistent, already decided}
#   role           valid {manager same team, admin}     invalid {employee, manager of other team}
#
# Representatives: the note classes use 0, 1 and 200 characters (valid) and 400
# characters (invalid). The class edges 279/280/281 are executed once, in BVA.
#
# BVA (three points per limit; HTTP status AND database readback each time)
#   note length        279 | 280 | 281                     -> 201 | 201 | 400
#   days vs available  A-1 | A   | A+1  (A = 5)           -> 201 | 201 | 400
#                      (A-1 spans a weekend: 4 business / 6 calendar days)
#   date range         end = start-1 | start | start+1     -> 400 | 201 (1 day) | 201 (2 days)
#   overlap with pending Tue 12-08..Thu 12-10 (inclusive):
#     start limit      Mon 12-07 | Tue 12-08 | Wed 12-09   -> 201 | 400 | 400
#     end limit        Wed 12-09 | Thu 12-10 | Fri 12-11   -> (12-09 shared, executed once) | 400 | 201
#
# Counting: each executable case is counted once at the API level. These cases
# use input combinations not repeated elsewhere in this suite. Where an A2.1 test
# exercises the same class at the same level (API-W1-002.*, API-W1-003.01/.02,
# API-W1-004.01, API-W1-005.01, API-W2-002.*, API-W2-003.01), report the pair as
# one case: the structural suite is the technique catalogue, not extra coverage.
# Observed (not desired) baseline: "today" and past dates are accepted (no rule);
# another team's manager gets 404 (scoped lookup), not 403.
# =============================================================================
"""A2.3 EP and three-point BVA on W1/W2 through real API calls."""

from datetime import date

from django.utils import timezone
from rest_framework.test import APIClient

from leave.models import LeaveRequest, User
from tests.team.api.support import add_member, payload, row_state
from tests.team.fixtures.leave_data import TEST_PASSWORD, build_people, make_request
from tests.team.structural.support import (
    DECIDED, END_BEFORE_START, FORBIDDEN, INSUFFICIENT, INVALID, OVERLAP, StructuralTestCase,
)


class W1EquivalencePartitionTests(StructuralTestCase):
    def setUp(self):
        self.p = build_people("epw1")
        self.e1 = self.p.e1

    # leave_type --------------------------------------------------------------
    def test_ep_w1_leave_type_vacation(self):
        """EP W1 leave_type, valid class {vacation}: 201 and stored as vacation."""
        _, row = self.assert_w1_created(self.e1, payload("2026-12-14", "2026-12-15", leave_type="vacation"), days=2)
        self.assertEqual(row["leave_type"], "vacation")

    def test_ep_w1_leave_type_permit(self):
        """EP W1 leave_type, valid class {permit}: 201 and stored as permit."""
        _, row = self.assert_w1_created(self.e1, payload("2026-12-14", "2026-12-15", leave_type="permit"))
        self.assertEqual(row["leave_type"], "permit")

    def test_ep_w1_leave_type_personal(self):
        """EP W1 leave_type, valid class {personal}: 201 and stored as personal."""
        _, row = self.assert_w1_created(self.e1, payload("2026-12-14", "2026-12-15", leave_type="personal"))
        self.assertEqual(row["leave_type"], "personal")

    def test_ep_w1_leave_type_empty(self):
        """EP W1 leave_type, invalid class {empty string}: 400 keyed leave_type, no insert (not a choice)."""
        self.assert_w1_rejected(self.e1, payload("2026-12-14", "2026-12-15", leave_type=""), 400, "leave_type")

    def test_ep_w1_leave_type_unknown(self):
        """EP W1 leave_type, invalid class {unknown string}: 'sabbatical' → 400 keyed leave_type, no insert."""
        self.assert_w1_rejected(self.e1, payload("2026-12-14", "2026-12-15", leave_type="sabbatical"), 400, "leave_type")

    def test_ep_w1_leave_type_numeric(self):
        """EP W1 leave_type, invalid class {numeric}: JSON number 7 → 400 keyed leave_type, no insert."""
        self.assert_w1_rejected(self.e1, payload("2026-12-14", "2026-12-15", leave_type=7), 400, "leave_type")

    # start_date --------------------------------------------------------------
    def test_ep_w1_start_date_future_weekday(self):
        """EP W1 start_date, valid class {future weekday}: Mon 2027-01-04..Tue 01-05 → 201, 2 business days."""
        self.assert_w1_created(self.e1, payload("2027-01-04", "2027-01-05"), days=2)

    def test_ep_w1_start_date_today(self):
        """EP W1 start_date, valid class {today}: start = end = server local date → 201.

        Baseline has no date-vs-today rule. business_days is 1 on a weekday and 0
        on a weekend, computed independently here.
        """
        today = timezone.localdate()
        expected = 1 if today.weekday() < 5 else 0
        self.assert_w1_created(self.e1, payload(today.isoformat(), today.isoformat()), days=expected)

    def test_ep_w1_start_date_missing(self):
        """EP W1 start_date, invalid class {missing}: field omitted → 400 keyed start_date, no insert."""
        self.assert_w1_rejected(self.e1, payload("2026-12-14", "2026-12-15", omit=("start_date",)), 400, "start_date")

    def test_ep_w1_start_date_non_date(self):
        """EP W1 start_date, invalid class {non-date string}: 'next monday' → 400 keyed start_date, no insert."""
        self.assert_w1_rejected(self.e1, payload("next monday", "2026-12-15"), 400, "start_date")

    def test_ep_w1_start_date_null(self):
        """EP W1 start_date, invalid class {null}: JSON null → 400 keyed start_date, no insert."""
        self.assert_w1_rejected(self.e1, payload(None, "2026-12-15"), 400, "start_date")

    # end_date ----------------------------------------------------------------
    def test_ep_w1_end_date_same_as_start(self):
        """EP W1 end_date, valid class {same as start}: Wed 12-16..12-16 → 201, 1 business day."""
        self.assert_w1_created(self.e1, payload("2026-12-16", "2026-12-16"), days=1)

    def test_ep_w1_end_date_after_start(self):
        """EP W1 end_date, valid class {after start}: Thu 12-17..Tue 12-22 → 201, 4 business days.

        The range spans a weekend (6 calendar days), so it also checks that
        weekends are excluded (BR-01).
        """
        self.assert_w1_created(self.e1, payload("2026-12-17", "2026-12-22"), days=4)

    def test_ep_w1_end_date_before_start(self):
        """EP W1 end_date, invalid class {before start}: Fri 12-18 → Mon 12-14 → 400 on end_date, no insert."""
        self.assert_w1_rejected(self.e1, payload("2026-12-18", "2026-12-14"), 400, "end_date", message=END_BEFORE_START)

    def test_ep_w1_end_date_missing(self):
        """EP W1 end_date, invalid class {missing}: field omitted → 400 keyed end_date, no insert."""
        self.assert_w1_rejected(self.e1, payload("2026-12-14", "2026-12-15", omit=("end_date",)), 400, "end_date")

    # note --------------------------------------------------------------------
    def test_ep_w1_note_empty(self):
        """EP W1 note, valid class {empty}: '' → 201 and stored empty (note is optional)."""
        _, row = self.assert_w1_created(self.e1, payload("2026-12-14", "2026-12-15", note=""))
        self.assertEqual(row["note"], "")

    def test_ep_w1_note_one_char(self):
        """EP W1 note, valid class {1 character}: 'x' → 201 and stored unchanged."""
        _, row = self.assert_w1_created(self.e1, payload("2026-12-14", "2026-12-15", note="x"))
        self.assertEqual(row["note"], "x")

    def test_ep_w1_note_within_limit(self):
        """EP W1 note, valid class {2..280 characters}, representative 200 → 201 stored intact.

        The class edge 280 is executed once, in test_bva_note_length_at.
        """
        _, row = self.assert_w1_created(self.e1, payload("2026-12-14", "2026-12-15", note="n" * 200))
        self.assertEqual(len(row["note"]), 200)

    def test_ep_w1_note_over_limit(self):
        """EP W1 note, invalid class {more than 280 characters}, representative 400 → 400 keyed note, no insert.

        The class edge 281 is executed once, in test_bva_note_length_above.
        """
        self.assert_w1_rejected(self.e1, payload("2026-12-14", "2026-12-15", note="n" * 400), 400, "note")

    # authentication ----------------------------------------------------------
    def test_ep_w1_auth_valid_token(self):
        """EP W1 authentication, valid class {valid token}: token from real login → 201 owned by the caller."""
        login = APIClient().post("/api/auth/login/", {"username": self.e1.username, "password": TEST_PASSWORD}, format="json")
        self.assertEqual(login.status_code, 200)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + login.data["token"])
        self.assert_w1_created(self.e1, payload("2026-12-14", "2026-12-15"), client=client)

    def test_ep_w1_auth_no_token(self):
        """EP W1 authentication, invalid class {no token}: 401 with WWW-Authenticate: Token, no insert."""
        response = self.assert_w1_rejected(self.e1, payload("2026-12-14", "2026-12-15"), 401, "detail", client=APIClient())
        self.assertEqual(response["WWW-Authenticate"], "Token")

    def test_ep_w1_auth_wrong_token(self):
        """EP W1 authentication, invalid class {wrong token}: unknown 40-hex token → 401, no insert."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + "0" * 40)
        self.assert_w1_rejected(self.e1, payload("2026-12-14", "2026-12-15"), 401, "detail", client=client)


class W2EquivalencePartitionTests(StructuralTestCase):
    def setUp(self):
        self.p = build_people("epw2")
        self.eb = add_member("epw2", "eb", User.Role.EMPLOYEE, self.p.team_b)
        self.pending_a = make_request(self.p.e1, start=date(2026, 12, 7), end=date(2026, 12, 8)).pk
        self.pending_b = make_request(self.eb, start=date(2026, 12, 7), end=date(2026, 12, 8)).pk
        self.rejected_a = make_request(
            self.p.e1, start=date(2026, 12, 21), end=date(2026, 12, 21),
            status=LeaveRequest.Status.REJECTED, decided_by=self.p.m1,
        ).pk

    # status --------------------------------------------------------------------
    def test_ep_w2_status_approved(self):
        """EP W2 status, valid class {approved}: admin approves team A pending → 200, approved."""
        self.assert_w2_decided(self.p.admin, self.pending_a, "approved")

    def test_ep_w2_status_rejected(self):
        """EP W2 status, valid class {rejected}: admin rejects team B pending → 200, rejected."""
        self.assert_w2_decided(self.p.admin, self.pending_b, "rejected")

    def test_ep_w2_status_empty(self):
        """EP W2 status, invalid class {empty}: '' → 400 'Decisione non valida.', row unchanged."""
        self.assert_w2_denied(self.p.m1, self.pending_a, "", 400, INVALID)

    def test_ep_w2_status_pending(self):
        """EP W2 status, invalid class {'pending'}: not a decision → 400, row stays pending.

        Also the disallowed event from state pending in the state-transition model.
        """
        self.assert_w2_denied(self.p.m1, self.pending_a, "pending", 400, INVALID)

    def test_ep_w2_status_random(self):
        """EP W2 status, invalid class {random string}: 'maybe' → 400, row unchanged."""
        self.assert_w2_denied(self.p.m1, self.pending_a, "maybe", 400, INVALID)

    # request_id ----------------------------------------------------------------
    def test_ep_w2_request_id_existing_pending(self):
        """EP W2 request_id, valid class {existing pending visible}: team B manager approves team B request → 200."""
        self.assert_w2_decided(self.p.m2, self.pending_b, "approved")

    def test_ep_w2_request_id_nonexistent(self):
        """EP W2 request_id, invalid class {nonexistent}: highest id + 1000 → 404, no row changed."""
        missing = LeaveRequest.objects.order_by("-pk").values_list("pk", flat=True).first() + 1000
        self.assert_w2_denied(self.p.m1, missing, "approved", 404)

    def test_ep_w2_request_id_already_decided(self):
        """EP W2 request_id, invalid class {already decided}: admin rejects a rejected request → 409, audit unchanged."""
        self.assert_w2_denied(self.p.admin, self.rejected_a, "rejected", 409, DECIDED)

    # role ----------------------------------------------------------------------
    def test_ep_w2_role_manager_same_team(self):
        """EP W2 role, valid class {manager of the same team}: team B manager rejects team B request → 200."""
        self.assert_w2_decided(self.p.m2, self.pending_b, "rejected")

    def test_ep_w2_role_admin(self):
        """EP W2 role, valid class {admin}: admin rejects team A request → 200."""
        self.assert_w2_decided(self.p.admin, self.pending_a, "rejected")

    def test_ep_w2_role_employee(self):
        """EP W2 role, invalid class {employee}: teammate employee approves → 403 (role guard), row unchanged."""
        self.assert_w2_denied(self.p.e2, self.pending_a, "approved", 403, FORBIDDEN)

    def test_ep_w2_role_manager_other_team(self):
        """EP W2 role, invalid class {manager of another team}: team B manager on a team A request → 404.

        Observed baseline: the scoped lookup hides the request, so the refusal is
        404 rather than 403. The row is unchanged.
        """
        self.assert_w2_denied(self.p.m2, self.pending_a, "approved", 404)


class BoundaryValueTests(StructuralTestCase):
    def setUp(self):
        self.p = build_people("bva")
        self.e1 = self.p.e1
        self.e5 = add_member("bva", "e5", User.Role.EMPLOYEE, self.p.team_a, allowance=5)
        # Existing pending interval for the overlap limits: Tue 12-08 .. Thu 12-10.
        self.existing = make_request(self.e1, start=date(2026, 12, 8), end=date(2026, 12, 10)).pk

    # note length 279 / 280 / 281 ------------------------------------------------
    def test_bva_note_length_below(self):
        """BVA note length, just below the 280 limit: 279 characters → 201, stored with 279 characters."""
        _, row = self.assert_w1_created(self.e1, payload("2026-12-14", "2026-12-14", note="n" * 279))
        self.assertEqual(len(row["note"]), 279)

    def test_bva_note_length_at(self):
        """BVA note length, exactly at the limit: 280 characters → 201, stored with 280 characters."""
        _, row = self.assert_w1_created(self.e1, payload("2026-12-14", "2026-12-14", note="n" * 280))
        self.assertEqual(len(row["note"]), 280)

    def test_bva_note_length_above(self):
        """BVA note length, just above the limit: 281 characters → 400 keyed note, no row created."""
        self.assert_w1_rejected(self.e1, payload("2026-12-14", "2026-12-14", note="n" * 281), 400, "note")

    # business days vs available (A = 5, no approved history) -------------------
    def test_bva_balance_below(self):
        """BVA days vs available, A-1: Thu 12-17..Tue 12-22 (4 business days, 6 calendar days) with A=5 → 201.

        Spanning a weekend keeps the boundary on business days: counting calendar
        days would push the request over the limit. Allowance is unchanged.
        """
        self.assert_w1_created(self.e5, payload("2026-12-17", "2026-12-22"), days=4)
        self.assertEqual(self.e5.leave_balance.available_days, 5)

    def test_bva_balance_at(self):
        """BVA days vs available, A: Mon 12-14..Fri 12-18 (5 days) with A=5 → 201 (equality is allowed)."""
        self.assert_w1_created(self.e5, payload("2026-12-14", "2026-12-18"), days=5)

    def test_bva_balance_above(self):
        """BVA days vs available, A+1: Mon 12-14..Mon 12-21 (6 days) with A=5 → 400 'Saldo ferie insufficiente.', no row."""
        self.assert_w1_rejected(self.e5, payload("2026-12-14", "2026-12-21"), 400, "non_field_errors", message=INSUFFICIENT)

    # date range: end relative to start (Mon 2026-12-21) ---------------------------
    def test_bva_date_range_below(self):
        """BVA date range, end = start-1: Mon 12-21 → Sun 12-20 → 400 on end_date, no row."""
        self.assert_w1_rejected(self.e1, payload("2026-12-21", "2026-12-20"), 400, "end_date", message=END_BEFORE_START)

    def test_bva_date_range_at(self):
        """BVA date range, end = start: Mon 12-21..12-21 → 201 with 1 business day."""
        self.assert_w1_created(self.e1, payload("2026-12-21", "2026-12-21"), days=1)

    def test_bva_date_range_above(self):
        """BVA date range, end = start+1: Mon 12-21..Tue 12-22 → 201 with 2 business days."""
        self.assert_w1_created(self.e1, payload("2026-12-21", "2026-12-22"), days=2)

    # overlap with the existing pending Tue 12-08..Thu 12-10 ----------------------
    def test_bva_overlap_start_below(self):
        """BVA overlap start limit, one day before: Mon 12-07 (ends the day before 12-08) → 201."""
        self.assert_w1_created(self.e1, payload("2026-12-07", "2026-12-07"), days=1)
        self.assertEqual(row_state(self.existing)["status"], LeaveRequest.Status.PENDING)

    def test_bva_overlap_start_at(self):
        """BVA overlap start limit, at: Tue 12-08 (the existing start day) → 400 overlap, no row (inclusive)."""
        self.assert_w1_rejected(self.e1, payload("2026-12-08", "2026-12-08"), 400, "non_field_errors", message=OVERLAP)

    def test_bva_overlap_start_above(self):
        """BVA overlap start limit, one day after (also the end limit's 'below' point): Wed 12-09 → 400 overlap."""
        self.assert_w1_rejected(self.e1, payload("2026-12-09", "2026-12-09"), 400, "non_field_errors", message=OVERLAP)

    def test_bva_overlap_end_at(self):
        """BVA overlap end limit, at: Thu 12-10 (the existing end day) → 400 overlap, no row (inclusive)."""
        self.assert_w1_rejected(self.e1, payload("2026-12-10", "2026-12-10"), 400, "non_field_errors", message=OVERLAP)

    def test_bva_overlap_end_above(self):
        """BVA overlap end limit, one day after: Fri 12-11 → 201; the existing request is untouched."""
        self.assert_w1_created(self.e1, payload("2026-12-11", "2026-12-11"), days=1)
        self.assertEqual(row_state(self.existing)["status"], LeaveRequest.Status.PENDING)
