# =============================================================================
# GENERATED FILE - DO NOT EDIT BY HAND.
# Generator: scripts/sqe/generate_api_tests.py
# Spec:      docs/sqe/openapi/leaveflow-api.yaml
# Spec SHA-256: 89b9f3a51e73d38e600b342d2c2a16f83b5b2b1393c871a05d9d378d4e3bff74
# Command:   python3 scripts/sqe/generate_api_tests.py docs/sqe/openapi/leaveflow-api.yaml --output tests/team/generated/test_generated_api_v2.py --demo-env SQE_SPEC_CHANGE_DEMO=v2
#
# Test design (from the spec's constraints, one field varied per test, all
# other fields at the operation's example values):
#   EP  valid: each enum value / the declared type; invalid: wrong type,
#       out-of-enum, invalid format, null and missing for required fields,
#       over-max-length.
#   BVA 3-point (limit-1, limit, limit+1) for maxLength/minLength/minimum/
#       maximum and x-relational constraints.
# Identical request bodies are generated once; the docstring lists every
# class the test covers (count each executable case once).
# Tests: 33
#
# DEMONSTRATION MODULE: its tests load only when SQE_SPEC_CHANGE_DEMO=v2.
# It encodes a changed spec and is expected to fail against the unchanged
# application; normal discovery of tests.team loads no tests from it.
# =============================================================================
"""OpenAPI-generated EP/BVA API tests (A2.4). Regenerate instead of editing."""

import os
from datetime import date

from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from leave.models import LeaveRequest
from tests.team.api.support import token_client
from tests.team.fixtures.leave_data import TEST_PASSWORD, build_people, make_request

SPEC_SHA256 = '89b9f3a51e73d38e600b342d2c2a16f83b5b2b1393c871a05d9d378d4e3bff74'
DEMO_ENABLED = os.environ.get('SQE_SPEC_CHANGE_DEMO') == 'v2'


def load_tests(loader, tests, pattern):
    """Load this demonstration module's tests only when explicitly enabled."""
    return tests if DEMO_ENABLED else loader.suiteClass()


class F:
    """Fixture-bound value (x-sqe-test binding), resolved inside the test."""

    def __init__(self, ref):
        self.ref = ref


class GeneratedApiTestCase(TestCase):
    """Runtime harness emitted by the generator; uses the A2.1 fixtures and token clients."""

    METHOD = PATH = READBACK = None
    ACTOR = None
    PATH_PARAMS = {}
    SUCCESS = 200
    ERRORS = ()

    def setUp(self):
        self.people = build_people("gen")
        # The W2 target: a pending team A request of e1 that m1 may decide.
        self.pending = make_request(self.people.e1, start=date(2026, 12, 14), end=date(2026, 12, 15))

    def ref(self, ref):
        root, *attrs = ref.split(".")
        value = {"pending": self.pending, "password": TEST_PASSWORD}.get(root)
        if value is None:
            value = getattr(self.people, root)
        for attr in attrs:
            value = getattr(value, attr)
        return value

    def resolve(self, body):
        return {k: self.ref(v.ref) if isinstance(v, F) else v for k, v in body.items()}

    def url(self):
        return self.PATH.format(**{k: self.ref(v) for k, v in self.PATH_PARAMS.items()})

    def snapshot(self):
        if self.READBACK == "created":
            return LeaveRequest.objects.filter(employee=self.ref(self.ACTOR)).count()
        if self.READBACK == "decided":
            return LeaveRequest.objects.filter(pk=self.pending.pk).values("status", "decided_by_id").get()
        return Token.objects.count()

    def check(self, body, *, valid):
        """One real API call with one generated body; assert status class and persisted outcome."""
        client = token_client(self.ref(self.ACTOR)) if self.ACTOR else APIClient()
        body = self.resolve(body)
        before = self.snapshot()
        response = getattr(client, self.METHOD)(self.url(), body, format="json")
        code = response.status_code
        detail = f"{self.METHOD.upper()} {self.PATH} -> {code} {getattr(response, 'data', None)!r}"
        if valid:
            self.assertTrue(200 <= code < 300, "expected 2xx: " + detail)
            self.assertEqual(code, self.SUCCESS, detail)
        else:
            self.assertTrue(400 <= code < 500, "expected 4xx: " + detail)
            self.assertIn(code, self.ERRORS, "undocumented 4xx: " + detail)
        after = self.snapshot()
        if self.READBACK == "created":
            self.assertEqual(after - before, 1 if valid else 0, "LeaveRequest rows created")
        elif self.READBACK == "decided":
            expected = {"status": body["status"], "decided_by_id": self.ref(self.ACTOR).pk} if valid else before
            self.assertEqual(after, expected, "decision persisted state")
        else:
            self.assertEqual("token" in response.data, valid, "token in response")
        return response


class GeneratedLoginTests(GeneratedApiTestCase):
    """POST /api/auth/login/: 7 generated tests."""

    METHOD = 'post'
    PATH = '/api/auth/login/'
    ACTOR = None
    PATH_PARAMS = {}
    READBACK = 'token'
    SUCCESS = 200
    ERRORS = (400,)

    def test_username_ep_valid_string(self):
        """Generated from spec: POST /api/auth/login/ username EP valid string

        Also generated from spec: POST /api/auth/login/ password EP valid string (password)

        Expect 2xx (200).
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, valid=True)

    def test_username_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid wrong type (true)

        Expect 4xx (400,).
        """
        self.check({'username': True, 'password': F('password')}, valid=False)

    def test_username_ep_invalid_null_required(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid null (required)

        Expect 4xx (400,).
        """
        self.check({'username': None, 'password': F('password')}, valid=False)

    def test_username_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid missing (required)

        Expect 4xx (400,).
        """
        self.check({'password': F('password')}, valid=False)

    def test_password_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/auth/login/ password EP invalid wrong type (true)

        Expect 4xx (400,).
        """
        self.check({'username': F('e1.username'), 'password': True}, valid=False)

    def test_password_ep_invalid_null_required(self):
        """Generated from spec: POST /api/auth/login/ password EP invalid null (required)

        Expect 4xx (400,).
        """
        self.check({'username': F('e1.username'), 'password': None}, valid=False)

    def test_password_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/auth/login/ password EP invalid missing (required)

        Expect 4xx (400,).
        """
        self.check({'username': F('e1.username')}, valid=False)


class GeneratedSubmitRequestTests(GeneratedApiTestCase):
    """POST /api/requests/: 20 generated tests."""

    METHOD = 'post'
    PATH = '/api/requests/'
    ACTOR = 'e1'
    PATH_PARAMS = {}
    READBACK = 'created'
    SUCCESS = 201
    ERRORS = (400, 401)

    def test_leave_type_ep_valid_enum_value_vacation(self):
        """Generated from spec: POST /api/requests/ leave_type EP valid enum value 'vacation'

        Also generated from spec: POST /api/requests/ start_date EP valid string (date)
        Also generated from spec: POST /api/requests/ end_date EP valid string (date)
        Also generated from spec: POST /api/requests/ end_date BVA 2026-12-08 (limit+1, end_date >= start_date)
        Also generated from spec: POST /api/requests/ note EP valid string

        Expect 2xx (201).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, valid=True)

    def test_leave_type_ep_valid_enum_value_permit(self):
        """Generated from spec: POST /api/requests/ leave_type EP valid enum value 'permit'

        Expect 2xx (201).
        """
        self.check({'leave_type': 'permit', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, valid=True)

    def test_leave_type_ep_valid_enum_value_personal(self):
        """Generated from spec: POST /api/requests/ leave_type EP valid enum value 'personal'

        Expect 2xx (201).
        """
        self.check({'leave_type': 'personal', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, valid=True)

    def test_leave_type_ep_invalid_out_of_enum_zzz_not_in_enum(self):
        """Generated from spec: POST /api/requests/ leave_type EP invalid out-of-enum 'zzz_not_in_enum'

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'zzz_not_in_enum', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, valid=False)

    def test_leave_type_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/ leave_type EP invalid wrong type (true)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': True, 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, valid=False)

    def test_start_date_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid wrong type (true)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': True, 'end_date': '2026-12-08', 'note': 'Generated test'}, valid=False)

    def test_start_date_ep_invalid_date_format_not_a_date(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid date format ('not-a-date')

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': 'not-a-date', 'end_date': '2026-12-08', 'note': 'Generated test'}, valid=False)

    def test_start_date_ep_invalid_null_required(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid null (required)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': None, 'end_date': '2026-12-08', 'note': 'Generated test'}, valid=False)

    def test_start_date_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid missing (required)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'end_date': '2026-12-08', 'note': 'Generated test'}, valid=False)

    def test_end_date_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid wrong type (true)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': True, 'note': 'Generated test'}, valid=False)

    def test_end_date_ep_invalid_date_format_not_a_date(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid date format ('not-a-date')

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': 'not-a-date', 'note': 'Generated test'}, valid=False)

    def test_end_date_ep_invalid_null_required(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid null (required)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': None, 'note': 'Generated test'}, valid=False)

    def test_end_date_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid missing (required)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'note': 'Generated test'}, valid=False)

    def test_end_date_bva_2026_12_06_below(self):
        """Generated from spec: POST /api/requests/ end_date BVA 2026-12-06 (limit-1, end_date >= start_date)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-06', 'note': 'Generated test'}, valid=False)

    def test_end_date_bva_2026_12_07_at(self):
        """Generated from spec: POST /api/requests/ end_date BVA 2026-12-07 (limit, end_date >= start_date)

        Expect 2xx (201).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-07', 'note': 'Generated test'}, valid=True)

    def test_note_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/ note EP invalid wrong type (true)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': True}, valid=False)

    def test_note_ep_invalid_over_max_length_400_chars_200(self):
        """Generated from spec: POST /api/requests/ note EP invalid over-max-length (400 chars > 200)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 400}, valid=False)

    def test_note_bva_199_below(self):
        """Generated from spec: POST /api/requests/ note BVA 199 (limit-1, maxLength 200)

        Expect 2xx (201).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 199}, valid=True)

    def test_note_bva_200_at(self):
        """Generated from spec: POST /api/requests/ note BVA 200 (limit, maxLength 200)

        Expect 2xx (201).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 200}, valid=True)

    def test_note_bva_201_above(self):
        """Generated from spec: POST /api/requests/ note BVA 201 (limit+1, maxLength 200)

        Expect 4xx (400, 401).
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 201}, valid=False)


class GeneratedDecideRequestTests(GeneratedApiTestCase):
    """POST /api/requests/{id}/decision/: 6 generated tests."""

    METHOD = 'post'
    PATH = '/api/requests/{id}/decision/'
    ACTOR = 'm1'
    PATH_PARAMS = {'id': 'pending.id'}
    READBACK = 'decided'
    SUCCESS = 200
    ERRORS = (400, 401, 403, 404, 409)

    def test_status_ep_valid_enum_value_approved(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP valid enum value 'approved'

        Expect 2xx (200).
        """
        self.check({'status': 'approved'}, valid=True)

    def test_status_ep_valid_enum_value_rejected(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP valid enum value 'rejected'

        Expect 2xx (200).
        """
        self.check({'status': 'rejected'}, valid=True)

    def test_status_ep_invalid_out_of_enum_zzz_not_in_enum(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid out-of-enum 'zzz_not_in_enum'

        Expect 4xx (400, 401, 403, 404, 409).
        """
        self.check({'status': 'zzz_not_in_enum'}, valid=False)

    def test_status_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid wrong type (true)

        Expect 4xx (400, 401, 403, 404, 409).
        """
        self.check({'status': True}, valid=False)

    def test_status_ep_invalid_null_required(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid null (required)

        Expect 4xx (400, 401, 403, 404, 409).
        """
        self.check({'status': None}, valid=False)

    def test_status_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid missing (required)

        Expect 4xx (400, 401, 403, 404, 409).
        """
        self.check({}, valid=False)
