"""A2.2: events are published only after commit, through a fake Redis client (RTM DT-004, EC-03 event part).

``REDIS_URL`` is set only around the call under test and ``leave.events.Redis`` is
replaced, so no Redis server is contacted. ``captureOnCommitCallbacks`` separates
the moment of commit from the call. Worker, gateway and browser delivery stay out
of scope (UC-07, decision D-2).
"""

from contextlib import contextmanager
from datetime import date
import json
from unittest import mock

from django.test import TestCase, override_settings

from leave.events import STREAM_NAME, publish_leave_event
from tests.team.api.support import REQUESTS_URL, all_rows, decision_url, payload, token_client
from tests.team.fixtures.leave_data import build_people, make_request


class EventPublicationTests(TestCase):
    def setUp(self):
        self.p = build_people("evt")
        self.pending = make_request(self.p.e1, start=date(2026, 12, 14), end=date(2026, 12, 15))
        # Clients are built before REDIS_URL is set: the fixture guard requires it to be empty.
        self.e1, self.e2, self.m1 = (token_client(u) for u in (self.p.e1, self.p.e2, self.p.m1))

    @contextmanager
    def publishing(self):
        with override_settings(REDIS_URL="redis://fake.invalid:1/0"), mock.patch("leave.events.Redis") as redis:
            yield redis.from_url.return_value.xadd

    def assert_published_after_commit(self, call, status, kind, recipients):
        with self.publishing() as xadd:
            with self.captureOnCommitCallbacks() as callbacks:
                response = call()
            self.assertEqual(response.status_code, status)
            self.assertEqual((len(callbacks), xadd.call_count), (1, 0))  # nothing before commit
            callbacks[0]()
        self.assertEqual(xadd.call_count, 1)
        stream, fields = xadd.call_args.args
        event = json.loads(fields["payload"])
        self.assertEqual((stream, event["type"], event["request"]["id"]), (STREAM_NAME, kind, response.data["id"]))
        self.assertEqual((event["request"]["status"], set(event["recipients"])), (response.data["status"], recipients))

    def decide(self, client, value):
        return client.post(decision_url(self.pending.pk), {"status": value}, format="json")

    def test_submission_is_published_after_commit(self):
        """DT-004; FR-W1-06: W1 registers one event and publishes it only at commit, to admin and team manager."""
        self.assert_published_after_commit(
            lambda: self.e1.post(REQUESTS_URL, payload(), format="json"), 201, "leave.requested",
            {self.p.admin.pk, self.p.m1.pk})

    def test_approval_is_published_after_commit(self):
        """DT-004; FR-W2-05: approval is published only at commit, to the owner."""
        self.assert_published_after_commit(lambda: self.decide(self.m1, "approved"), 200, "leave.approved", {self.p.e1.pk})

    def test_rejection_is_published_after_commit(self):
        """DT-004; FR-W2-06: rejection is published only at commit, to the owner."""
        self.assert_published_after_commit(lambda: self.decide(self.m1, "rejected"), 200, "leave.rejected", {self.p.e1.pk})

    def test_refused_calls_register_no_event(self):
        """DT-004: W1 400, W2 403 and W2 400 register no commit callback."""
        with self.publishing() as xadd, self.captureOnCommitCallbacks(execute=True) as callbacks:
            statuses = [
                self.e1.post(REQUESTS_URL, payload("2026-12-14", "2026-12-14"), format="json").status_code,
                self.decide(self.e2, "approved").status_code,
                self.decide(self.m1, "pending").status_code,
            ]
        self.assertEqual((statuses, callbacks, xadd.call_count), ([400, 403, 400], [], 0))

    def test_rolled_back_decision_publishes_nothing(self):
        """BR-05: a failure after the event was registered rolls the decision back and drops the event."""
        before = all_rows()

        def publish_then_fail(*args):
            publish_leave_event(*args)
            raise RuntimeError("synthetic failure inside the decision transaction")

        self.m1.raise_request_exception = False
        with self.publishing() as xadd, self.captureOnCommitCallbacks(execute=True) as callbacks:
            with mock.patch("leave.views.publish_leave_event", side_effect=publish_then_fail):
                with self.assertLogs("django.request", level="ERROR"):
                    response = self.decide(self.m1, "approved")
        self.assertEqual((response.status_code, callbacks, xadd.call_count), (500, [], 0))
        self.assertEqual(all_rows(), before)

    def test_redis_failure_does_not_undo_the_decision(self):
        """BR-05: Redis failing at publication is logged; the committed decision stands."""
        with self.publishing() as xadd:
            xadd.side_effect = ConnectionError("synthetic outage")
            with self.assertLogs("leave.events", level="ERROR"), self.captureOnCommitCallbacks(execute=True):
                response = self.decide(self.m1, "approved")
        self.assertEqual(response.status_code, 200)
        self.pending.refresh_from_db()
        self.assertEqual((self.pending.status, self.pending.decided_by_id), ("approved", self.p.m1.pk))
