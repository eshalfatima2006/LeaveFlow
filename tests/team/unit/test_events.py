"""Focused tests for LeaveFlow's event payload and Redis publication boundary."""

from datetime import datetime, timezone as datetime_timezone
import json
from unittest.mock import patch
from uuid import UUID

from django.test import TestCase, override_settings

from leave.events import STREAM_NAME, build_leave_event, publish_leave_event
from tests.team.fixtures.leave_data import build_reference_fixture


class LeaveEventTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fixture = build_reference_fixture("events")
        cls.people = cls.fixture.people

    def test_requested_event_contains_recipients_and_complete_payload(self):
        occurred_at = datetime(2026, 12, 15, 9, 30, tzinfo=datetime_timezone.utc)
        event_id = UUID("11111111-1111-4111-8111-111111111111")

        with patch("leave.events.uuid4", return_value=event_id), patch(
            "leave.events.timezone.now", return_value=occurred_at
        ):
            event = build_leave_event(self.fixture.pending, "leave.requested", self.people.e1)

        self.assertEqual(event["id"], str(event_id))
        self.assertEqual(event["type"], "leave.requested")
        self.assertEqual(event["occurred_at"], occurred_at.isoformat())
        self.assertEqual(set(event["recipients"]), {self.people.m1.id, self.people.admin.id})
        self.assertNotIn(self.people.m2.id, event["recipients"])
        self.assertEqual(event["actor"], {"id": self.people.e1.id, "display_name": self.people.e1.display_name})
        self.assertEqual(
            event["request"],
            {
                "id": self.fixture.pending.id,
                "employee_id": self.people.e1.id,
                "employee_name": self.people.e1.display_name,
                "leave_type": self.fixture.pending.leave_type,
                "start_date": self.fixture.pending.start_date.isoformat(),
                "end_date": self.fixture.pending.end_date.isoformat(),
                "status": self.fixture.pending.status,
            },
        )

    def test_decision_event_targets_only_the_employee(self):
        event = build_leave_event(self.fixture.approved, "leave.approved", self.people.m1)

        self.assertEqual(event["recipients"], [self.people.e1.id])
        self.assertEqual(event["type"], "leave.approved")
        self.assertEqual(event["actor"], {"id": self.people.m1.id, "display_name": self.people.m1.display_name})

    @override_settings(REDIS_URL="")
    def test_publish_returns_without_registering_commit_when_redis_is_disabled(self):
        with patch("leave.events.build_leave_event") as build, patch("leave.events.transaction.on_commit") as on_commit:
            publish_leave_event(self.fixture.pending, "leave.requested", self.people.e1)

        build.assert_not_called()
        on_commit.assert_not_called()

    @override_settings(REDIS_URL="redis://redis:6379/0")
    def test_publish_registers_commit_and_serializes_payload(self):
        payload = {"id": "event-1", "type": "leave.requested"}
        callbacks = []
        client = patch("leave.events.Redis.from_url").start()
        on_commit = patch("leave.events.transaction.on_commit", side_effect=callbacks.append).start()
        build = patch("leave.events.build_leave_event", return_value=payload).start()
        self.addCleanup(patch.stopall)

        publish_leave_event(self.fixture.pending, "leave.requested", self.people.e1)

        build.assert_called_once_with(self.fixture.pending, "leave.requested", self.people.e1)
        on_commit.assert_called_once()
        client.assert_not_called()
        self.assertEqual(len(callbacks), 1)

        callbacks[0]()

        client.assert_called_once_with("redis://redis:6379/0", decode_responses=True)
        client.return_value.xadd.assert_called_once_with(
            STREAM_NAME,
            {"payload": json.dumps(payload)},
            maxlen=10_000,
            approximate=True,
        )

    @override_settings(REDIS_URL="redis://redis:6379/0")
    def test_publish_logs_and_swallows_redis_failure(self):
        callbacks = []
        client = patch("leave.events.Redis.from_url").start()
        client.return_value.xadd.side_effect = RuntimeError("redis unavailable")
        patch("leave.events.transaction.on_commit", side_effect=callbacks.append).start()
        patch("leave.events.build_leave_event", return_value={"id": "event-2"}).start()
        logger = patch("leave.events.logger.exception").start()
        self.addCleanup(patch.stopall)

        publish_leave_event(self.fixture.pending, "leave.approved", self.people.m1)
        callbacks[0]()

        logger.assert_called_once_with("Unable to publish LeaveFlow event %s", "event-2")
