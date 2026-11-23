"""A2.1 Group B: W1 leave-request submission through POST /api/requests/.

Case IDs expand planned RTM families API-W1-001..006. Docstrings marked
CHARACTERIZATION pin current baseline behaviour whose business policy is still
unresolved (TEST-BASIS GAP IDs); they are not claims that the policy is approved.
"""

from datetime import date

from django.test import TestCase

from leave.models import LeaveBalance, LeaveRequest, User
from tests.team.api.support import (
    REQUEST_FIELDS, REQUESTS_URL, all_rows, balance_view, payload, rolled_back, row_state, token_client,
)
from tests.team.fixtures.leave_data import build_people, make_request

INSUFFICIENT = ["Saldo ferie insufficiente."]


class SubmissionTestCase(TestCase):
    prefix = "w1"

    @classmethod
    def setUpTestData(cls):
        cls.p = build_people(cls.prefix)

    def setUp(self):
        self.client = token_client(self.p.e1)

    def submit(self, body, client=None):
        return (client or self.client).post(REQUESTS_URL, body, format="json")

    def assert_rejected_without_insert(self, body, error_key, client=None):
        before = all_rows()
        response = self.submit(body, client)
        self.assertEqual(response.status_code, 400, response.data)
        self.assertIn(error_key, response.data)
        self.assertNotIn("id", response.data)
        self.assertEqual(all_rows(), before)
        return response

    def assert_created(self, body, owner, client=None):
        count = LeaveRequest.objects.count()
        response = self.submit(body, client)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(set(response.data), REQUEST_FIELDS)
        self.assertEqual(LeaveRequest.objects.count(), count + 1)
        row = row_state(response.data["id"])
        self.assertEqual(row["employee_id"], owner.pk)
        self.assertEqual(row["status"], "pending")
        self.assertIsNone(row["decided_by_id"])
        self.assertIsNone(row["decided_at"])
        self.assertEqual(response.data["employee"]["id"], owner.pk)
        return response, row


class SuccessfulSubmissionTests(SubmissionTestCase):
    def test_valid_employee_submission_persists_one_pending_owned_row(self):
        """API-W1-006.01; FR-W1-01, FR-W1-06; BR-04/05/06: 201, returned k readable, balance unchanged."""
        response, row = self.assert_created(payload("2026-12-07", "2026-12-08", note="Family visit"), self.p.e1)
        data = response.data
        self.assertEqual(
            {k: data[k] for k in ("leave_type", "leave_type_label", "start_date", "end_date",
                                  "note", "status", "status_label", "business_days")},
            {"leave_type": "vacation", "leave_type_label": "Ferie", "start_date": "2026-12-07",
             "end_date": "2026-12-08", "note": "Family visit", "status": "pending",
             "status_label": "In attesa", "business_days": 2},
        )
        self.assertEqual(data["employee"]["username"], "w1_e1")
        self.assertEqual((row["start_date"], row["end_date"], row["note"]),
                         (date(2026, 12, 7), date(2026, 12, 8), "Family visit"))
        # Pending reserves nothing; allowance row is untouched.
        self.assertEqual(balance_view(self.p.e1), (10, 0, 10))
        listed = self.client.get(REQUESTS_URL).data
        self.assertEqual([r["id"] for r in listed], [data["id"]])
        dashboard = self.client.get("/api/dashboard/").data
        self.assertEqual(dashboard["counts"], {"total": 1, "pending": 1, "approved": 0})
        self.assertEqual(dashboard["balance"], {"allowance": 10, "used": 0, "available": 10})

    def test_manager_and_admin_self_submission_is_owned_by_caller(self):
        """API-W1-001.06; FR-W1-01, FR-W1-06; BR-04. CHARACTERIZATION (FR-W1-01 note): role is not restricted."""
        for user in (self.p.m1, self.p.admin, self.p.teamless_manager):
            with self.subTest(user=user.username):
                response, _ = self.assert_created(payload("2026-12-09", "2026-12-09"), user, token_client(user))
                self.assertEqual(response.data["employee"]["role"], user.role)

    def test_read_only_and_unknown_fields_cannot_set_owner_or_state(self):
        """API-W1-001.07; FR-W1-01, FR-W1-02; BR-04/05/06: injected employee/status/id/days are ignored."""
        body = payload(
            "2026-12-07", "2026-12-08", employee=self.p.e2.pk, status="approved", id=987654,
            decided_by=self.p.m1.pk, business_days=99, status_label="Approvata", unknown_field="x",
        )
        response, row = self.assert_created(body, self.p.e1)
        self.assertNotEqual(response.data["id"], 987654)
        self.assertEqual((response.data["status"], response.data["business_days"]), ("pending", 2))
        self.assertNotIn("unknown_field", response.data)
        self.assertFalse(LeaveRequest.objects.filter(employee=self.p.e2).exists())

    def test_each_leave_type_and_omitted_default(self):
        """API-W1-002.01; FR-W1-02; BR-06: vacation/permit/personal accepted; omitted defaults to vacation."""
        cases = [
            ("2026-12-07", {"leave_type": "vacation"}, "vacation", "Ferie"),
            ("2026-12-08", {"leave_type": "permit"}, "permit", "Permesso"),
            ("2026-12-09", {"leave_type": "personal"}, "personal", "Personale"),
            ("2026-12-10", {"omit": ("leave_type",)}, "vacation", "Ferie"),
        ]
        for day, extra, stored, label in cases:
            with self.subTest(case=extra):
                response, row = self.assert_created(payload(day, day, **extra), self.p.e1)
                self.assertEqual(row["leave_type"], stored)
                self.assertEqual(response.data["leave_type_label"], label)
        self.assertEqual(LeaveRequest.objects.filter(employee=self.p.e1).count(), 4)

    def test_note_optional_blank_and_length_boundaries(self):
        """API-W1-002.02; FR-W1-02; BR-06: omitted/blank/whitespace -> '', trimmed 279/280 ok, 281 -> 400."""
        accepted = [
            ("2026-12-07", {"omit": ("note",)}, ""),
            ("2026-12-08", {"note": ""}, ""),
            ("2026-12-09", {"note": "   "}, ""),
            ("2026-12-10", {"note": "n" * 279}, "n" * 279),
            ("2026-12-11", {"note": "n" * 280}, "n" * 280),
            ("2026-12-14", {"note": "  " + "n" * 280 + "  "}, "n" * 280),  # trimmed before length check
        ]
        for day, extra, stored in accepted:
            with self.subTest(note_len=len(extra.get("note", ""))):
                response, row = self.assert_created(payload(day, day, **extra), self.p.e1)
                self.assertEqual(row["note"], stored)
                self.assertEqual(response.data["note"], stored)
        self.assert_rejected_without_insert(payload("2026-12-15", "2026-12-15", note="n" * 281), "note")


class PayloadValidationTests(SubmissionTestCase):
    def test_missing_and_null_fields_rejected_without_insert(self):
        """API-W1-002.03; FR-W1-02; BR-06: omitted/null required dates, null type/note -> 400 on that field."""
        response = self.assert_rejected_without_insert({}, "start_date")
        self.assertEqual(set(response.data), {"start_date", "end_date"})
        cases = [
            (payload(omit=("start_date",)), "start_date"),
            (payload(omit=("end_date",)), "end_date"),
            (payload(start_date=None), "start_date"),
            (payload(end_date=None), "end_date"),
            (payload(leave_type=None), "leave_type"),
            (payload(note=None), "note"),
        ]
        for body, key in cases:
            with self.subTest(body=body):
                response = self.assert_rejected_without_insert(body, key)
                self.assertEqual(set(response.data), {key})

    def test_invalid_date_type_and_note_values_rejected(self):
        """API-W1-002.04; FR-W1-02; BR-06: unparseable/impossible dates, unknown types, nonstring note -> 400."""
        cases = [
            (payload(start_date="07/12/2026"), "start_date"),
            (payload(start_date="2026-13-01"), "start_date"),
            (payload(start_date="2026-02-29", end_date="2026-03-02"), "start_date"),  # not a leap year
            (payload(end_date=""), "end_date"),
            (payload(end_date="tomorrow"), "end_date"),
            (payload(start_date=20261207), "start_date"),
            (payload(leave_type="Vacation"), "leave_type"),
            (payload(leave_type="sick"), "leave_type"),
            (payload(leave_type=""), "leave_type"),
            (payload(leave_type=1), "leave_type"),
            (payload(leave_type=["vacation"]), "leave_type"),
            (payload(note=["structured"]), "note"),
        ]
        for body, key in cases:
            with self.subTest(field=key, value=body[key]):
                self.assert_rejected_without_insert(body, key)

    def test_malformed_json_and_unsupported_media_type(self):
        """API-W1-002.05; FR-W1-02; BR-06: protocol partitions -> 400 parse error / 415, no insert."""
        before = all_rows()
        bad_json = self.client.post(REQUESTS_URL, data='{"start_date": ', content_type="application/json")
        self.assertEqual(bad_json.status_code, 400)
        self.assertEqual(set(bad_json.data), {"detail"})
        plain = self.client.post(REQUESTS_URL, data="start_date=2026-12-07", content_type="text/plain")
        self.assertEqual(plain.status_code, 415)
        self.assertEqual(all_rows(), before)


class DateRuleTests(SubmissionTestCase):
    def test_end_before_start_rejected_on_end_date(self):
        """API-W1-003.01; FR-W1-03; BR-01: end one day before start -> 400 end_date, no row."""
        response = self.assert_rejected_without_insert(payload("2026-12-07", "2026-12-06"), "end_date")
        self.assertEqual(set(response.data), {"end_date"})

    def test_inclusive_weekday_counts(self):
        """API-W1-003.02; FR-W1-03, FR-W1-06; BR-01: server business_days equals independent counts."""
        cases = [
            ("2026-12-08", "2026-12-08", 1),  # same weekday (Tue)
            ("2026-12-07", "2026-12-11", 5),  # Mon..Fri
            ("2026-12-11", "2026-12-11", 1),  # Fri (weekday index 4)
            ("2026-12-11", "2026-12-14", 2),  # Fri..Mon spans a weekend
            ("2026-12-07", "2026-12-14", 6),  # Mon..Mon
            ("2026-12-31", "2027-01-04", 3),  # cross-year Thu, Fri, Mon
            ("2028-02-29", "2028-02-29", 1),  # leap day (Tue)
        ]
        for start, end, days in cases:
            with self.subTest(start=start, end=end), rolled_back():
                response, row = self.assert_created(payload(start, end), self.p.e1)
                self.assertEqual(response.data["business_days"], days)
                self.assertEqual(LeaveRequest.objects.get(pk=row["id"]).business_days, days)

    def test_weekend_only_request_is_accepted_with_zero_days(self):
        """API-W1-003.03; FR-W1-03; BR-01. CHARACTERIZATION (no positive-day minimum; policy open)."""
        for start, end in (("2026-12-12", "2026-12-12"), ("2026-12-13", "2026-12-13"), ("2026-12-12", "2026-12-13")):
            with self.subTest(start=start, end=end), rolled_back():
                response, _ = self.assert_created(payload(start, end), self.p.e1)
                self.assertEqual(response.data["business_days"], 0)
                self.assertEqual(balance_view(self.p.e1), (10, 0, 10))

    def test_past_dates_are_accepted(self):
        """API-W1-003.04; FR-W1-03; BR-01. CHARACTERIZATION (no date-relative-to-today rule; policy open)."""
        response, row = self.assert_created(payload("2020-01-06", "2020-01-06"), self.p.e1)
        self.assertEqual((response.data["business_days"], row["start_date"]), (1, date(2020, 1, 6)))


class OverlapTests(SubmissionTestCase):
    prefix = "ov"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.existing = make_request(cls.p.e1, start=date(2026, 12, 7), end=date(2026, 12, 11))

    def test_inclusive_boundaries_against_pending_request(self):
        """API-W1-004.01; FR-W1-04; BR-02: existing pending 12-07..11; touching endpoints block, neighbours pass."""
        cases = [
            ("2026-12-06", "2026-12-06", True),   # day before start
            ("2026-12-07", "2026-12-07", False),  # equals start
            ("2026-12-08", "2026-12-08", False),
            ("2026-12-10", "2026-12-10", False),
            ("2026-12-11", "2026-12-11", False),  # equals end
            ("2026-12-12", "2026-12-12", True),   # day after end
            ("2026-12-04", "2026-12-14", False),  # encloses existing
            ("2026-12-04", "2026-12-07", False),  # end touches start
        ]
        for start, end, allowed in cases:
            with self.subTest(start=start, end=end), rolled_back():
                if allowed:
                    self.assert_created(payload(start, end), self.p.e1)
                else:
                    response = self.assert_rejected_without_insert(payload(start, end), "non_field_errors")
                    self.assertEqual(response.data["non_field_errors"], ["Esiste già una richiesta sovrapposta."])
        self.assertEqual(row_state(self.existing.pk)["status"], "pending")

    def test_approved_request_blocks_and_neighbour_passes(self):
        """API-W1-004.02; FR-W1-04; BR-02/05: approved interval still blocks overlap."""
        approved = make_request(self.p.e1, start=date(2026, 12, 14), end=date(2026, 12, 15),
                                status=LeaveRequest.Status.APPROVED, decided_by=self.p.m1)
        self.assert_rejected_without_insert(payload("2026-12-15", "2026-12-15"), "non_field_errors")
        self.assert_created(payload("2026-12-16", "2026-12-16"), self.p.e1)
        self.assertEqual(row_state(approved.pk)["status"], "approved")

    def test_rejected_request_dates_can_be_reused_as_new_row(self):
        """API-W1-004.03; FR-W1-04; BR-02/05: rejected history does not block; a NEW row is created."""
        rejected = make_request(self.p.e1, start=date(2026, 12, 21), end=date(2026, 12, 22),
                                status=LeaveRequest.Status.REJECTED, decided_by=self.p.m1)
        before = row_state(rejected.pk)
        response, row = self.assert_created(payload("2026-12-21", "2026-12-22"), self.p.e1)
        self.assertNotEqual(row["id"], rejected.pk)
        self.assertEqual(row_state(rejected.pk), before)

    def test_other_employee_may_request_same_dates(self):
        """API-W1-004.04; FR-W1-04, FR-W1-01; BR-02/04: overlap is per employee only."""
        response, row = self.assert_created(payload("2026-12-07", "2026-12-11"), self.p.e2, token_client(self.p.e2))
        self.assertEqual(response.data["business_days"], 5)
        self.assertEqual(row_state(self.existing.pk)["employee_id"], self.p.e1.pk)


class BalanceTests(SubmissionTestCase):
    prefix = "bal"

    def test_requested_days_at_available_boundary(self):
        """API-W1-005.01; FR-W1-05; BR-03/01: A=5 -> D=4 and D=5 accepted, D=6 rejected (three-point BVA)."""
        people = build_people("bva", allowances={"e1": 5})
        client = token_client(people.e1)
        for start, end, days, accepted in (("2026-12-07", "2026-12-10", 4, True),
                                           ("2026-12-07", "2026-12-11", 5, True),
                                           ("2026-12-07", "2026-12-14", 6, False)):
            with self.subTest(days=days), rolled_back():
                if accepted:
                    response, _ = self.assert_created(payload(start, end), people.e1, client)
                    self.assertEqual(response.data["business_days"], days)
                else:
                    response = self.assert_rejected_without_insert(payload(start, end), "non_field_errors", client)
                    self.assertEqual(response.data["non_field_errors"], INSUFFICIENT)
                self.assertEqual(balance_view(people.e1), (5, 0, 5))

    def test_available_counts_approved_history_only(self):
        """API-W1-005.02; FR-W1-05; BR-03: A = 5 - approved 2; pending/rejected consume nothing -> D=3 ok, D=4 400."""
        people = build_people("hist", allowances={"e1": 5})
        make_request(people.e1, start=date(2026, 12, 1), end=date(2026, 12, 2),
                     status=LeaveRequest.Status.APPROVED, decided_by=people.m1)
        make_request(people.e1, start=date(2026, 12, 3), end=date(2026, 12, 4))
        make_request(people.e1, start=date(2026, 11, 30), end=date(2026, 11, 30),
                     status=LeaveRequest.Status.REJECTED, decided_by=people.m1)
        self.assertEqual(balance_view(people.e1), (5, 2, 3))
        client = token_client(people.e1)
        with rolled_back():
            self.assert_created(payload("2026-12-14", "2026-12-16"), people.e1, client)
        response = self.assert_rejected_without_insert(payload("2026-12-14", "2026-12-17"), "non_field_errors", client)
        self.assertEqual(response.data["non_field_errors"], INSUFFICIENT)
        self.assertEqual(client.get("/api/dashboard/").data["balance"], {"allowance": 5, "used": 2, "available": 3})

    def test_zero_and_negative_available(self):
        """API-W1-005.03; FR-W1-05; BR-03. A=0: D=1 400, D=0 accepted. A=-1: even D=0 400 (CHARACTERIZATION, GAP-01)."""
        people = build_people("zero", allowances={"e1": 3})
        make_request(people.e1, start=date(2026, 12, 1), end=date(2026, 12, 3),
                     status=LeaveRequest.Status.APPROVED, decided_by=people.m1)
        client = token_client(people.e1)
        self.assertEqual(balance_view(people.e1), (3, 3, 0))
        self.assert_rejected_without_insert(payload("2026-12-14", "2026-12-14"), "non_field_errors", client)
        with rolled_back():
            response, _ = self.assert_created(payload("2026-12-12", "2026-12-12"), people.e1, client)
            self.assertEqual(response.data["business_days"], 0)
        # Negative available is reachable only through history (e.g. approvals without a guard).
        LeaveBalance.objects.filter(user=people.e1).update(allowance=2)
        self.assertEqual(balance_view(people.e1), (2, 3, -1))
        response = self.assert_rejected_without_insert(payload("2026-12-19", "2026-12-19"), "non_field_errors", client)
        self.assertEqual(response.data["non_field_errors"], INSUFFICIENT)

    def test_missing_balance_record_skips_the_check(self):
        """API-W1-005.04; FR-W1-05; BR-03. CHARACTERIZATION (GAP-07): no balance -> any D accepted, dashboard zeros."""
        people = build_people("nobal", missing_balance_for=("e2",))
        client = token_client(people.e2)
        response, _ = self.assert_created(payload("2026-12-07", "2027-01-08"), people.e2, client)
        self.assertEqual(response.data["business_days"], 25)
        self.assertFalse(LeaveBalance.objects.filter(user=people.e2).exists())
        self.assertEqual(client.get("/api/dashboard/").data["balance"], {"allowance": 0, "used": 0, "available": 0})

    def test_pending_requests_reserve_no_allowance(self):
        """API-W1-005.05; FR-W1-05, FR-W1-06; BR-03. CHARACTERIZATION (GAP-01): two 4-day pendings at A=5 both 201.

        Prepares, but does not perform, the A2.2 approval-time over-allowance regression.
        """
        people = build_people("resv", allowances={"e1": 5})
        client = token_client(people.e1)
        first, _ = self.assert_created(payload("2026-12-07", "2026-12-10"), people.e1, client)
        second, _ = self.assert_created(payload("2026-12-14", "2026-12-17"), people.e1, client)
        self.assertEqual((first.data["business_days"], second.data["business_days"]), (4, 4))
        self.assertEqual(balance_view(people.e1), (5, 0, 5))
        self.assertEqual(
            sorted(LeaveRequest.objects.filter(employee=people.e1).values_list("status", flat=True)),
            ["pending", "pending"],
        )
        self.assertEqual(User.objects.get(pk=people.e1.pk).leave_balance.allowance, 5)
