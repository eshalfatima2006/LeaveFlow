# =============================================================================
# API-INT-002 — CONCURRENCY ON DISPOSABLE POSTGRESQL (RTM; PR-03; EC-03)
#
# Run with scripts/sqe/run_concurrency.py only. In the normal in-memory suite this
# module loads no tests, because SQLite cannot show row locks.
#
# Each request runs in its own thread with its own connection. Interleavings are
# forced, not left to chance: a barrier between validation and insert (W1), and a
# held row lock that both deciders are seen waiting for in pg_locks (W2).
# Waits are bounded (lock/statement timeout, barrier and future timeouts).
# =============================================================================
"""API-INT-002: synchronized concurrent requests with full final database state."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
import time
from unittest import mock

from django.conf import settings
from django.db import connection, connections, transaction
from django.test import TransactionTestCase

from leave.models import LeaveRequest
from leave.serializers import LeaveRequestSerializer
from tests.team.api.support import (
    REQUESTS_URL, all_rows, balance_view, decision_url, payload, row_state, token_client,
)
from tests.team.fixtures.leave_data import build_people, make_request
from tests.team.postgres_safety import PROFILE

TIMEOUT = 30


def load_tests(loader, tests, pattern):
    return tests if getattr(settings, "TEAM_TEST_PROFILE", None) == PROFILE else loader.suiteClass()


def in_own_connection(call):
    try:
        return call()
    finally:
        connections.close_all()


class ConcurrencyTestCase(TransactionTestCase):
    def setUp(self):
        self.p = build_people("pg", allowances={"e2": 5})

    def decider(self, actor, request_id, value):
        client = token_client(actor)
        return lambda: client.post(decision_url(request_id), {"status": value}, format="json")

    def run_together(self, *calls, while_running=None):
        with ThreadPoolExecutor(len(calls)) as pool:
            futures = [pool.submit(in_own_connection, call) for call in calls]
            if while_running:
                while_running()
            return [f.result(timeout=TIMEOUT) for f in futures]


class ConcurrentSubmissionTests(ConcurrencyTestCase):
    """CHARACTERIZATION of a baseline defect: the overlap check is query-then-insert without a constraint."""

    def submit_together(self, *intervals):
        barrier = Barrier(len(intervals))
        create = LeaveRequestSerializer.create

        def create_after_both_validated(serializer, data):
            barrier.wait(timeout=TIMEOUT)
            return create(serializer, data)

        client = [token_client(self.p.e1) for _ in intervals]
        with mock.patch.object(LeaveRequestSerializer, "create", create_after_both_validated):
            return self.run_together(*[
                lambda c=c, i=i: c.post(REQUESTS_URL, payload(*i), format="json") for c, i in zip(client, intervals)
            ])

    def assert_both_inserted(self, responses):
        # BR-02 expects one 201 and one overlap 400 with a single row.
        self.assertEqual([r.status_code for r in responses], [201, 201])
        rows = all_rows()
        self.assertEqual(sorted(r["id"] for r in rows), sorted(r.data["id"] for r in responses))
        self.assertEqual({(r["employee_id"], r["status"], r["decided_by_id"]) for r in rows},
                         {(self.p.e1.pk, LeaveRequest.Status.PENDING, None)})
        self.assertEqual(balance_view(self.p.e1), (10, 0, 10))

    def test_overlapping_submissions_characterization(self):
        """API-INT-002.01; FR-W1-04; BR-02: two overlapping submissions both pass the check → two overlapping rows."""
        self.assert_both_inserted(self.submit_together(("2026-12-07", "2026-12-09"), ("2026-12-08", "2026-12-10")))

    def test_identical_submissions_characterization(self):
        """API-INT-002.02; FR-W1-04, FR-W1-06; BR-02: a double submit of one request → two identical rows."""
        self.assert_both_inserted(self.submit_together(("2026-12-07", "2026-12-08"), ("2026-12-07", "2026-12-08")))


class ConcurrentDecisionTests(ConcurrencyTestCase):
    def wait_for_lock_waiters(self, count):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            with connection.cursor() as cursor:
                # pg_stat_activity is cached for the whole transaction; pg_locks is not.
                cursor.execute("SELECT count(DISTINCT pid) FROM pg_locks WHERE NOT granted")
                if cursor.fetchone()[0] == count:
                    return
            time.sleep(0.05)
        self.fail(f"{count} deciders were not seen waiting for the row lock")

    def decide_same_request(self, first, second):
        item = make_request(self.p.e1, start=date(2026, 12, 7), end=date(2026, 12, 8))
        before = row_state(item.pk)
        calls = [self.decider(self.p.m1, item.pk, first), self.decider(self.p.admin, item.pk, second)]
        with ThreadPoolExecutor(2) as pool:
            with transaction.atomic():
                LeaveRequest.objects.select_for_update().get(pk=item.pk)
                futures = [pool.submit(in_own_connection, call) for call in calls]
                self.wait_for_lock_waiters(2)
            responses = [f.result(timeout=TIMEOUT) for f in futures]
        self.assertEqual(sorted(r.status_code for r in responses), [200, 409])
        winner = 0 if responses[0].status_code == 200 else 1
        actor, value = ((self.p.m1, first), (self.p.admin, second))[winner]
        after = row_state(item.pk)
        self.assertEqual(after, {**before, "status": value, "decided_by_id": actor.pk, "decided_at": after["decided_at"]})
        self.assertIsNotNone(after["decided_at"])
        self.assertEqual(len(all_rows()), 1)
        used = 2 if value == "approved" else 0
        self.assertEqual(balance_view(self.p.e1), (10, used, 10 - used))

    def test_approve_and_reject_same_request(self):
        """API-INT-002.03; FR-W2-04; BR-05: approve vs reject under the row lock → one 200, one 409, the winner's audit kept."""
        self.decide_same_request("approved", "rejected")

    def test_approve_same_request_twice(self):
        """API-INT-002.04; FR-W2-04, FR-W2-05; BR-03, BR-05: approve vs approve → one 200, one 409, charged once."""
        self.decide_same_request("approved", "approved")

    def test_distinct_requests_on_one_allowance_characterization(self):
        """API-INT-002.05 — CHARACTERIZATION (GAP-01, PR-01): allowance 5, two 4-day requests approved together → −3.

        EC-01 expects one approval to be refused with 1 day remaining.
        """
        items = [make_request(self.p.e2, start=date(2026, 12, d), end=date(2026, 12, d + 3)) for d in (7, 14)]
        responses = self.run_together(
            self.decider(self.p.m1, items[0].pk, "approved"), self.decider(self.p.admin, items[1].pk, "approved"))
        self.assertEqual([r.status_code for r in responses], [200, 200])
        self.assertEqual([(r["status"], r["decided_by_id"]) for r in all_rows()],
                         [("approved", self.p.m1.pk), ("approved", self.p.admin.pk)])
        self.assertEqual(balance_view(self.p.e2), (5, 8, -3))
