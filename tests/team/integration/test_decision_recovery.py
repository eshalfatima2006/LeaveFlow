"""W2 rolls back the write on failure and the same request can be retried once."""

from datetime import date
from unittest.mock import patch

from django.db import OperationalError
from django.test import TransactionTestCase

from leave.models import LeaveRequest
from tests.team.api.support import all_rows, balance_view, decision_url, row_state, token_client
from tests.team.fixtures.leave_data import build_people, make_request


class DecisionRecoveryTest(TransactionTestCase):
    def test_write_failure_rolls_back_and_retry_charges_once(self):
        people = build_people("recovery", allowance=5)
        item = make_request(people.e1, start=date(2027, 4, 5), end=date(2027, 4, 7))
        client = token_client(people.m1)
        client.raise_request_exception = False
        url = decision_url(item.pk)
        before = all_rows()
        original_save = LeaveRequest.save

        def write_then_fail(instance, *args, **kwargs):
            original_save(instance, *args, **kwargs)
            raise OperationalError("SQE controlled failure before commit")

        with patch.object(LeaveRequest, "save", write_then_fail):
            failed = client.post(url, {"status": "approved"}, format="json")
        self.assertEqual(failed.status_code, 500)
        self.assertEqual(all_rows(), before)
        self.assertEqual(balance_view(people.e1), (5, 0, 5))

        retry = client.post(url, {"status": "approved"}, format="json")
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(retry.json()["id"], item.pk)
        after = row_state(item.pk)
        self.assertEqual(after["status"], LeaveRequest.Status.APPROVED)
        self.assertEqual(after["decided_by_id"], people.m1.pk)
        self.assertIsNotNone(after["decided_at"])
        self.assertEqual(len(all_rows()), len(before))
        self.assertEqual(balance_view(people.e1), (5, 3, 2))

        duplicate = client.post(url, {"status": "approved"}, format="json")
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(all_rows(), [after])
        self.assertEqual(balance_view(people.e1), (5, 3, 2))
