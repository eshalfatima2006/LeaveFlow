"""Small independently authored foundation checks, not full FR/BR coverage."""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import connection
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from leave.models import LeaveBalance, LeaveRequest, Team, User
from tests.team.fixtures.leave_data import (
    TEST_PASSWORD, build_overapproval_scenario, build_people,
    build_reference_fixture, logical_snapshot, make_request,
)
from tests.team.runner import record_snapshot
from tests.team.safety import PROFILE, TEST_NAME, validate_database_config


class FoundationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fixture = build_reference_fixture()

    def test_synthetic_identity_and_balance_relationships(self):
        """FND-001; FR-W1-01, FR-W2-01; BR-04: synthetic roles/teams/balances."""
        p = self.fixture.people
        self.assertEqual(Team.objects.count(), 2)
        self.assertEqual(User.objects.count(), 6)
        self.assertEqual(LeaveBalance.objects.count(), 6)
        self.assertEqual((p.e1.role, p.e2.role), (User.Role.EMPLOYEE,) * 2)
        self.assertEqual((p.e1.team_id, p.e2.team_id, p.m1.team_id), (p.team_a.pk,) * 3)
        self.assertEqual(p.m2.team_id, p.team_b.pk)
        self.assertEqual((p.m1.role, p.m2.role), (User.Role.MANAGER,) * 2)
        self.assertEqual(p.admin.role, User.Role.ADMIN)
        self.assertIsNone(p.teamless_manager.team_id)
        self.assertEqual(p.e1.leave_balance.user_id, p.e1.pk)
        self.assertEqual(p.e1.leave_balance.allowance, 10)

    def test_pending_record_and_approved_only_consumption(self):
        """FND-002; FR-W1-03/05/06; BR-01/03/05: persisted pending and totals."""
        item = LeaveRequest.objects.get(pk=self.fixture.pending.pk)
        self.assertEqual(connection.settings_dict["NAME"], TEST_NAME)
        self.assertEqual(item.employee_id, self.fixture.people.e1.pk)
        self.assertEqual(item.status, LeaveRequest.Status.PENDING)
        self.assertEqual((item.start_date, item.end_date), (date(2026, 12, 14), date(2026, 12, 16)))
        self.assertIsNone(item.decided_by_id)
        self.assertIsNone(item.decided_at)
        self.assertEqual((item.business_days, self.fixture.approved.business_days), (3, 2))
        balance = LeaveBalance.objects.get(user=item.employee)
        self.assertEqual((balance.approved_days, balance.available_days), (2, 8))
        self.assertEqual(LeaveRequest.objects.count(), 3)

    def test_real_login_and_token_authenticated_dashboard(self):
        """FND-003; FR-W1-01/05, FR-W2-01; BR-03/04: real DRF token lookup."""
        client = APIClient()
        self.assertEqual(client.get("/api/dashboard/").status_code, 401)
        login = client.post("/api/auth/login/", {
            "username": self.fixture.people.e1.username, "password": TEST_PASSWORD,
        }, format="json")
        self.assertEqual(login.status_code, 200)
        # Never print, snapshot or compare the raw credential in assertion output.
        client.credentials(HTTP_AUTHORIZATION="Token " + login.data["token"])
        me = client.get("/api/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["id"], self.fixture.people.e1.pk)
        self.assertEqual(me.data["team"], self.fixture.people.team_a.name)
        response = client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["balance"], {"allowance": 10, "used": 2, "available": 8})
        self.assertEqual(response.data["counts"], {"total": 3, "pending": 1, "approved": 1})
        self.assertEqual({r["id"] for r in response.data["recent"]}, {
            self.fixture.pending.pk, self.fixture.approved.pk, self.fixture.rejected.pk,
        })

    def test_reference_logical_snapshot(self):
        """FND-004; FR-W1-06, FR-W2-01; BR-03/04/05: stable logical fixture."""
        snapshot = logical_snapshot()
        self.assertEqual(snapshot["teams"], ["sqe-A", "sqe-B"])
        self.assertEqual(len(snapshot["users"]), 6)
        self.assertEqual(len(snapshot["balances"]), 6)
        self.assertEqual([r["days"] for r in snapshot["requests"]], [2, 3, 1])
        self.assertEqual([r["status"] for r in snapshot["requests"]], ["approved", "pending", "rejected"])
        self.assertEqual(snapshot["token_count"], 0)
        record_snapshot("reference", snapshot)

    def test_zero_missing_and_exact_balance_fixture_variants(self):
        """FND-005; FR-W1-05; BR-03: reusable zero/missing/exact allowance setups."""
        p = build_people("variants", allowances={"e1": 3, "m1": 3}, missing_balance_for=("e2",))
        make_request(p.e1, status=LeaveRequest.Status.APPROVED, decided_by=p.m1)
        balance = LeaveBalance.objects.get(user=p.e1)
        self.assertEqual((balance.allowance, balance.approved_days, balance.available_days), (3, 3, 0))
        self.assertFalse(LeaveBalance.objects.filter(user=p.e2).exists())
        exact = make_request(p.m1)
        self.assertEqual(exact.business_days, p.m1.leave_balance.available_days)
        self.assertEqual(p.m1.leave_balance.available_days, 3)  # pending reserves nothing

    def test_overlap_requires_explicit_fixture_opt_in(self):
        """FND-006; FR-W1-04; BR-02: invalid fixture setup is deliberate only."""
        count = LeaveRequest.objects.count()
        with self.assertRaises(ValidationError):
            make_request(self.fixture.people.e1)
        self.assertEqual(LeaveRequest.objects.count(), count)
        overlap = make_request(self.fixture.people.e1, allow_overlap=True)
        self.assertNotEqual(overlap.pk, self.fixture.pending.pk)
        self.assertEqual(overlap.start_date, self.fixture.pending.start_date)

    def test_prepare_future_overapproval_scenario_without_deciding(self):
        """FND-007; FR-W1-05/06; BR-03/05: prepare future regression, no W2 call."""
        p, first, second = build_overapproval_scenario()
        self.assertNotEqual(first.pk, second.pk)
        self.assertLess(first.end_date, second.start_date)
        self.assertEqual((first.business_days, second.business_days), (4, 4))
        self.assertEqual((first.status, second.status), ("pending", "pending"))
        self.assertEqual(p.e1.leave_balance.available_days, 5)
        self.assertIsNone(first.decided_at)
        self.assertIsNone(second.decided_by_id)


class FixtureIsolationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fixture = build_reference_fixture("isolation")
        cls.initial = logical_snapshot()

    def test_01_mutate_own_records(self):
        """FND-008; FR-W1-06; BR-03/05: mutate inside this test's savepoint."""
        self.assertEqual(logical_snapshot(), self.initial)
        record_snapshot("isolation_before", logical_snapshot())
        LeaveBalance.objects.filter(user=self.fixture.people.e1).update(allowance=99)
        LeaveRequest.objects.filter(pk=self.fixture.pending.pk).update(note="A2.0 isolation mutation")
        Team.objects.create(name="sqe-transient")
        mutated = logical_snapshot()
        self.assertNotEqual(mutated, self.initial)
        self.assertEqual(len(mutated["teams"]), 3)
        record_snapshot("isolation_mutated", mutated)

    def test_02_independent_test_starts_clean(self):
        """FND-009; FR-W1-06; BR-03/05: prior test's mutations rolled back."""
        self.assertEqual(logical_snapshot(), self.initial)
        self.assertEqual(Team.objects.count(), 2)
        self.assertEqual(LeaveBalance.objects.get(user=self.fixture.people.e1).allowance, 10)
        self.assertEqual(LeaveRequest.objects.get(pk=self.fixture.pending.pk).note, "Synthetic fixture")
        record_snapshot("isolation_next_test", logical_snapshot())


class SafetyGuardTests(SimpleTestCase):
    def config(self, **changes):
        config = {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:", "TEST": {"NAME": ":memory:"}}
        return config | changes

    def test_unknown_profiles_are_refused(self):
        """FND-010; infrastructure: an explicit safe profile is mandatory."""
        for profile in (None, "development", "sqe-memory-v2"):
            with self.subTest(profile=profile), self.assertRaises(RuntimeError):
                validate_database_config(self.config(), profile)

    def test_file_external_and_custom_test_targets_are_refused(self):
        """FND-011; infrastructure: reject dev SQLite, unknown files/URIs and PG."""
        bad = [
            self.config(NAME="backend/db.sqlite3"),
            self.config(NAME="/tmp/test.sqlite3"),
            self.config(NAME="file:unknown?mode=memory&cache=shared"),
            self.config(ENGINE="django.db.backends.postgresql", NAME="test_external"),
            self.config(TEST={"NAME": "test_file.sqlite3"}),
            self.config(TEST={"NAME": ":memory:", "MIRROR": "production"}),
        ]
        for config in bad:
            with self.subTest(engine=config["ENGINE"], name=config["NAME"]), self.assertRaises(RuntimeError):
                validate_database_config(config, PROFILE)

    def test_fixture_requires_active_django_memory_target(self):
        """FND-012; infrastructure: refuse fixture work before test DB selection."""
        with self.assertRaises(RuntimeError):
            validate_database_config(self.config(), PROFILE, active=True)
        validate_database_config(self.config(NAME=TEST_NAME), PROFILE, active=True)
