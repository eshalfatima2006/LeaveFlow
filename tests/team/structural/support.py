"""Shared base for the A2.3 technique suites (not a test module).

Every action under test is a real HTTP call through DRF's APIClient (a Django
test-client subclass) with a real DRF token. Fixtures (users, teams, balances
and pre-existing requests) are built in ``setUp`` with the A2.0 builders, which
run only on the guarded sqe-memory-v1 test database.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from leave.models import LeaveRequest
from tests.team.api.support import (
    REQUESTS_URL, all_rows, balance_view, decision_url, payload, row_state, token_client,
)

INSUFFICIENT = ["Saldo ferie insufficiente."]
OVERLAP = ["Esiste già una richiesta sovrapposta."]
END_BEFORE_START = ["La data finale non può precedere quella iniziale."]
FORBIDDEN = {"detail": "Operazione non consentita."}
INVALID = {"detail": "Decisione non valida."}
SELF = {"detail": "Non puoi decidere una tua richiesta."}
DECIDED = {"detail": "La richiesta è già stata decisa."}

__all__ = [
    "APIClient", "DECIDED", "END_BEFORE_START", "FORBIDDEN", "INSUFFICIENT", "INVALID", "OVERLAP",
    "REQUESTS_URL", "SELF", "StructuralTestCase", "balance_view", "payload", "row_state",
]


class StructuralTestCase(TestCase):
    """HTTP helpers with persisted-state readback after every call."""

    # ---- W1 ------------------------------------------------------------------
    def post_w1(self, user, body, client=None):
        client = client or token_client(user)
        return client.post(REQUESTS_URL, body, format="json")

    def assert_w1_created(self, user, body, *, days=None, client=None):
        """201, exactly one new pending row owned by ``user`` matching the body."""
        count = LeaveRequest.objects.count()
        response = self.post_w1(user, body, client)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(LeaveRequest.objects.count(), count + 1)
        row = row_state(response.data["id"])
        self.assertEqual((row["employee_id"], row["status"]), (user.pk, LeaveRequest.Status.PENDING))
        self.assertEqual((row["decided_by_id"], row["decided_at"]), (None, None))
        self.assertEqual((row["start_date"].isoformat(), row["end_date"].isoformat()), (body["start_date"], body["end_date"]))
        if days is not None:
            self.assertEqual(response.data["business_days"], days)
            self.assertEqual(LeaveRequest.objects.get(pk=row["id"]).business_days, days)
        return response, row

    def assert_w1_rejected(self, user, body, status_code, error_key=None, *, message=None, client=None):
        """Refusal with the exact status; every persisted row unchanged and none added."""
        before = all_rows()
        response = self.post_w1(user, body, client)
        self.assertEqual(response.status_code, status_code, response.data)
        if error_key is not None:
            self.assertIn(error_key, response.data)
        if message is not None:
            self.assertEqual(response.data[error_key], message)
        self.assertEqual(all_rows(), before)
        return response

    # ---- W2 ------------------------------------------------------------------
    def decide(self, actor, request_id, value):
        return token_client(actor).post(decision_url(request_id), {"status": value}, format="json")

    def assert_w2_decided(self, actor, request_id, value):
        """200 on the same row: new status, actor, timestamp in the call window, content unchanged."""
        before = row_state(request_id)
        count = LeaveRequest.objects.count()
        started = timezone.now()
        response = self.decide(actor, request_id, value)
        finished = timezone.now()
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual((response.data["id"], response.data["status"]), (request_id, value))
        after = row_state(request_id)
        self.assertEqual((after["status"], after["decided_by_id"]), (value, actor.pk))
        self.assertTrue(started <= after["decided_at"] <= finished)
        for field in ("employee_id", "leave_type", "start_date", "end_date", "note", "created_at"):
            self.assertEqual(after[field], before[field], field)
        self.assertEqual(LeaveRequest.objects.count(), count)
        return after

    def assert_w2_denied(self, actor, request_id, value, status_code, body=None):
        """Refusal with exact status (and body); every persisted row unchanged."""
        before = all_rows()
        response = self.decide(actor, request_id, value)
        self.assertEqual(response.status_code, status_code, response.data)
        self.assertEqual(set(response.data), {"detail"})
        if body is not None:
            self.assertEqual(response.data, body)
        self.assertEqual(all_rows(), before)
        return response
