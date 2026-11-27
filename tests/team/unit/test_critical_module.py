"""White-box tests for the DR-001 W1 validation chain.

The tests deliberately exercise each predicate outcome rather than relying only
on end-to-end API scenarios.  The test IDs map to the four assignment rules:

* BR-01: an interval must be ordered and count weekdays inclusively;
* BR-02: an active request must not overlap another active request;
* BR-03: approved-only consumption and submission allowance enforcement.

Shared BR-04 is authorization, BR-05 is pending-only decisions and BR-06 is
field domains; their API and view tests are mapped in the MCC evidence.

The current source keeps the missing-balance path permissive.  That behavior is
characterized as GAP-07 until the product owner confirms a different policy.
"""

from datetime import date
import json
from unittest.mock import patch

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from leave.models import LeaveBalance, LeaveRequest
from leave.serializers import LeaveRequestSerializer
from leave.views import health_view, team_view
from tests.team.fixtures.leave_data import build_people, build_reference_fixture, make_request
from tests.team.api.support import token_client


class BusinessDaysAndCleaningTests(TestCase):
    """BR-01 and BR-02 predicate/branch coverage."""

    @classmethod
    def setUpTestData(cls):
        cls.fx = build_reference_fixture("wbclean")
        cls.people = cls.fx.people

    def test_business_days_covers_weekend_weekday_and_mixed_interval(self):
        cases = [
            (date(2026, 12, 12), date(2026, 12, 13), 0),  # weekend only
            (date(2026, 12, 14), date(2026, 12, 14), 1),  # one weekday
            (date(2026, 12, 14), date(2026, 12, 18), 5),  # inclusive work week
        ]
        for start, end, expected in cases:
            with self.subTest(start=start, end=end):
                item = LeaveRequest(employee=self.people.e2, start_date=start, end_date=end)
                self.assertEqual(item.business_days, expected)

    def test_model_string_and_display_helpers_are_deterministic(self):
        self.assertEqual(str(self.fx.people.team_a), "wbclean-A")
        self.assertEqual(self.people.e1.display_name, "Synthetic e1")
        self.assertIn("wbclean_e1", str(self.fx.pending))

    def test_clean_rejects_reversed_dates_with_field_error(self):
        item = LeaveRequest(
            employee=self.people.e2,
            start_date=date(2026, 12, 18),
            end_date=date(2026, 12, 14),
        )
        with self.assertRaises(DjangoValidationError) as raised:
            item.clean()
        self.assertEqual(raised.exception.message_dict["end_date"], [
            "La data finale non può precedere quella iniziale."
        ])

    def test_clean_accepts_nonoverlap_and_rejects_pending_and_approved_overlap(self):
        nonoverlap = LeaveRequest(
            employee=self.people.e1,
            start_date=date(2026, 12, 28),
            end_date=date(2026, 12, 29),
        )
        nonoverlap.clean()

        for existing in (self.fx.pending, self.fx.approved):
            with self.subTest(existing_status=existing.status):
                candidate = LeaveRequest(
                    employee=self.people.e1,
                    start_date=existing.start_date,
                    end_date=existing.end_date,
                )
                with self.assertRaises(DjangoValidationError) as raised:
                    candidate.clean()
                self.assertEqual(raised.exception.messages, [
                    "Esiste già una richiesta sovrapposta."
                ])

    def test_clean_ignores_rejected_requests_and_excludes_self(self):
        rejected = LeaveRequest(
            employee=self.people.e2,
            start_date=date(2026, 12, 14),
            end_date=date(2026, 12, 16),
            status=LeaveRequest.Status.REJECTED,
        )
        rejected.save()
        candidate = LeaveRequest(
            employee=self.people.e2,
            start_date=rejected.start_date,
            end_date=rejected.end_date,
        )
        candidate.clean()

        self.fx.pending.clean()


class BalanceAndSerializerTests(TestCase):
    """BR-03 truth-table rows for the validation chain."""

    @classmethod
    def setUpTestData(cls):
        cls.fx = build_reference_fixture("wbserial")
        cls.people = cls.fx.people

    def serializer_for(self, user, *, start="2026-12-28", end="2026-12-29"):
        request = APIRequestFactory().post("/api/requests/", {})
        request.user = user
        return LeaveRequestSerializer(
            data={
                "start_date": start,
                "end_date": end,
                "leave_type": LeaveRequest.Type.VACATION,
                "note": "white-box",
            },
            context={"request": request},
        )

    def test_approved_days_counts_only_approved_and_available_is_remaining(self):
        balance = self.people.e1.leave_balance
        self.assertEqual(balance.approved_days, 2)
        self.assertEqual(balance.available_days, 8)

        make_request(
            self.people.e1,
            start=date(2026, 12, 28),
            end=date(2026, 12, 29),
            status=LeaveRequest.Status.APPROVED,
            decided_by=self.people.m1,
        )
        self.assertEqual(LeaveBalance.objects.get(pk=balance.pk).approved_days, 4)
        self.assertEqual(LeaveBalance.objects.get(pk=balance.pk).available_days, 6)

    def test_serializer_accepts_equal_available_days(self):
        self.people.e2.leave_balance.allowance = 8
        self.people.e2.leave_balance.save(update_fields=["allowance"])
        serializer = self.serializer_for(self.people.e2, start="2026-12-14", end="2026-12-23")
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["start_date"], date(2026, 12, 14))

    def test_serializer_rejects_insufficient_balance(self):
        self.people.e2.leave_balance.allowance = 1
        self.people.e2.leave_balance.save(update_fields=["allowance"])
        serializer = self.serializer_for(self.people.e2, start="2026-12-14", end="2026-12-16")
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["non_field_errors"], ["Saldo ferie insufficiente."])

    def test_mcdc_balance_presence_flips_rejection_for_same_dates(self):
        """MCC-03/MCC-01: B changes, E masked without balance, outcome flips."""
        balance = self.people.e2.leave_balance
        balance.allowance = 1
        balance.save(update_fields=["allowance"])
        limited = self.serializer_for(self.people.e2, start="2026-12-28", end="2026-12-30")
        self.assertFalse(limited.is_valid())
        self.assertEqual(limited.errors["non_field_errors"], ["Saldo ferie insufficiente."])
        balance.delete()
        # Refresh to avoid the reverse OneToOne relation cache retaining the deleted row.
        user = type(self.people.e2).objects.get(pk=self.people.e2.pk)
        unlimited = self.serializer_for(user, start="2026-12-28", end="2026-12-30")
        self.assertTrue(unlimited.is_valid(), unlimited.errors)

    def test_serializer_preserves_field_and_nonfield_clean_errors(self):
        reversed_dates = self.serializer_for(self.people.e2, start="2026-12-18", end="2026-12-14")
        self.assertFalse(reversed_dates.is_valid())
        self.assertEqual(reversed_dates.errors["end_date"], [
            "La data finale non può precedere quella iniziale."
        ])

        overlap = self.serializer_for(
            self.people.e1,
            start=self.fx.pending.start_date.isoformat(),
            end=self.fx.pending.end_date.isoformat(),
        )
        self.assertFalse(overlap.is_valid())
        self.assertEqual(overlap.errors["non_field_errors"], [
            "Esiste già una richiesta sovrapposta."
        ])

    def test_serializer_keeps_current_missing_balance_policy(self):
        people = build_people("wbmissing", missing_balance_for=("e1",))
        serializer = self.serializer_for(people.e1)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class ViewBranchTests(TestCase):
    """Small direct checks for the remaining server-side branch paths."""

    @classmethod
    def setUpTestData(cls):
        cls.people = build_people("wbviews")

    def test_health_returns_ok_when_database_probe_succeeds(self):
        request = APIRequestFactory().get("/health/")
        response = health_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "ok"})

    def test_health_returns_degraded_when_database_probe_fails(self):
        request = APIRequestFactory().get("/health/")
        with patch("leave.views.connection.cursor", side_effect=RuntimeError("probe")):
            response = health_view(request)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(json.loads(response.content), {"status": "degraded"})

    def test_team_view_returns_empty_for_teamless_manager(self):
        response = token_client(self.people.teamless_manager).get("/api/team/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_team_view_reports_members_without_balance_and_next_leave(self):
        self.people.e2.leave_balance.delete()
        make_request(
            self.people.e1,
            start=date(2026, 12, 28),
            end=date(2026, 12, 29),
            status=LeaveRequest.Status.APPROVED,
            decided_by=self.people.m1,
        )
        response = token_client(self.people.m1).get("/api/team/")
        self.assertEqual(response.status_code, 200)
        rows = {row["username"]: row for row in response.data}
        self.assertEqual(rows["wbviews_e2"]["available_days"], 0)
        self.assertEqual(rows["wbviews_e2"]["allowance"], 0)
        self.assertIsNone(rows["wbviews_e2"]["next_leave"])
        self.assertEqual(rows["wbviews_e1"]["next_leave"]["start_date"], date(2026, 12, 28))
