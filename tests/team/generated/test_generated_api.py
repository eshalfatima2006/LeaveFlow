# =============================================================================
# GENERATED FILE - DO NOT EDIT BY HAND.
# Generator: scripts/sqe/generate_api_tests.py
# Spec:      docs/sqe/openapi/leaveflow-api.yaml
# Spec SHA-256: 00167b42eee65d5ae1ae55c1e56c6efff110aebea8fe50444a25fa48eb7fb61a
# Command:   python3 scripts/sqe/generate_api_tests.py docs/sqe/openapi/leaveflow-api.yaml --output tests/team/generated/test_generated_api.py
#
# Test design (from the spec's constraints, one input varied per test, all
# other inputs at the operation's example values):
#   EP  valid: each enum value / the declared type / omitted optional field;
#       invalid: wrong type, out-of-enum, invalid format, null, missing required
#       field, over-max-length, x-invalid-examples, missing/unknown token.
#   BVA 3-point (limit-1, limit, limit+1) for maxLength/minLength/minimum/
#       maximum, x-relational and x-rule-boundaries constraints.
# Identical requests are generated once; the docstring lists every
# class the test covers (count each executable case once).
# Tests: 68
# =============================================================================
"""OpenAPI-generated EP/BVA API tests (A2.4). Regenerate instead of editing."""

from datetime import date

from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from leave.models import LeaveRequest
from tests.team.api.support import token_client
from tests.team.fixtures.leave_data import TEST_PASSWORD, build_people, make_request

SPEC_SHA256 = '00167b42eee65d5ae1ae55c1e56c6efff110aebea8fe50444a25fa48eb7fb61a'
FIXTURE = {'allowance': 10, 'pending': {'start': '2026-12-15', 'end': '2026-12-16'}}


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

    def setUp(self):
        # x-sqe-fixture: every allowance, and the W2 target / overlap interval, a
        # pending team A request of e1 that m1 may decide.
        self.people = build_people("gen", allowance=FIXTURE["allowance"])
        self.pending = make_request(
            self.people.e1, start=date.fromisoformat(FIXTURE["pending"]["start"]),
            end=date.fromisoformat(FIXTURE["pending"]["end"]),
        )

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

    def url(self, path):
        return self.PATH.format(**{**{k: self.ref(v) for k, v in self.PATH_PARAMS.items()}, **path})

    def client_for(self, auth):
        if auth == "actor" and self.ACTOR:
            return token_client(self.ref(self.ACTOR))
        client = APIClient()
        if auth == "invalid":
            client.credentials(HTTP_AUTHORIZATION="Token " + "0" * 40)
        return client

    def snapshot(self):
        if self.READBACK == "created":
            return LeaveRequest.objects.filter(employee=self.ref(self.ACTOR)).count()
        if self.READBACK == "decided":
            return LeaveRequest.objects.filter(pk=self.pending.pk).values("status", "decided_by_id").get()
        return Token.objects.count()

    def check(self, body, *, status, path=None, auth="actor", error=None):
        """One real API call with one generated request; assert status, error key and persisted outcome."""
        client = self.client_for(auth)
        body = self.resolve(body)
        before = self.snapshot()
        response = getattr(client, self.METHOD)(self.url(path or {}), body, format="json")
        data = getattr(response, "data", None)
        shown = "(login body hidden)" if self.READBACK == "token" else repr(data)
        detail = f"{self.METHOD.upper()} {self.PATH} -> {response.status_code}, expected {status}: {shown}"
        self.assertEqual(response.status_code, status, detail)
        valid = status == self.SUCCESS
        if error is not None:
            self.assertEqual(set(data), {error}, detail)
        after = self.snapshot()
        if self.READBACK == "created":
            self.assertEqual(after - before, 1 if valid else 0, "LeaveRequest rows created")
        elif self.READBACK == "decided":
            expected = {"status": body["status"], "decided_by_id": self.ref(self.ACTOR).pk} if valid else before
            self.assertEqual(after, expected, "decision persisted state")
        else:
            self.assertEqual("token" in data, valid, "token in response")
            self.assertEqual(after - before, 1 if valid else 0, "tokens created")
        return response


class GeneratedLoginTests(GeneratedApiTestCase):
    """POST /api/auth/login/: 11 generated tests."""

    METHOD = 'post'
    PATH = '/api/auth/login/'
    ACTOR = None
    PATH_PARAMS = {}
    READBACK = 'token'
    SUCCESS = 200

    def test_username_ep_valid_string(self):
        """Generated from spec: POST /api/auth/login/ username EP valid string

        Also generated from spec: POST /api/auth/login/ password EP valid string (password)

        Expect 200.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=200)

    def test_username_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid wrong type (true)

        Expect 400, error key detail.
        """
        self.check({'username': True, 'password': F('password')}, status=400, error='detail')

    def test_username_ep_invalid_null_required(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid null (required)

        Expect 400, error key detail.
        """
        self.check({'username': None, 'password': F('password')}, status=400, error='detail')

    def test_username_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid missing (required)

        Expect 400, error key detail.
        """
        self.check({'password': F('password')}, status=400, error='detail')

    def test_username_ep_invalid_example_empty(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid example ''

        Expect 400, error key detail.
        """
        self.check({'username': '', 'password': F('password')}, status=400, error='detail')

    def test_username_ep_invalid_example_unknown_user(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid example 'unknown-user'

        Expect 400, error key detail.
        """
        self.check({'username': 'unknown-user', 'password': F('password')}, status=400, error='detail')

    def test_password_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/auth/login/ password EP invalid wrong type (true)

        Expect 400, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': True}, status=400, error='detail')

    def test_password_ep_invalid_null_required(self):
        """Generated from spec: POST /api/auth/login/ password EP invalid null (required)

        Expect 400, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': None}, status=400, error='detail')

    def test_password_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/auth/login/ password EP invalid missing (required)

        Expect 400, error key detail.
        """
        self.check({'username': F('e1.username')}, status=400, error='detail')

    def test_password_ep_invalid_example_empty(self):
        """Generated from spec: POST /api/auth/login/ password EP invalid example ''

        Expect 400, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': ''}, status=400, error='detail')

    def test_password_ep_invalid_example_wrong_password(self):
        """Generated from spec: POST /api/auth/login/ password EP invalid example 'wrong-password'

        Expect 400, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': 'wrong-password'}, status=400, error='detail')


class GeneratedSubmitRequestTests(GeneratedApiTestCase):
    """POST /api/requests/: 42 generated tests."""

    METHOD = 'post'
    PATH = '/api/requests/'
    ACTOR = 'e1'
    PATH_PARAMS = {}
    READBACK = 'created'
    SUCCESS = 201

    def test_leave_type_ep_valid_enum_value_vacation(self):
        """Generated from spec: POST /api/requests/ leave_type EP valid enum value 'vacation'

        Also generated from spec: POST /api/requests/ start_date EP valid string (date)
        Also generated from spec: POST /api/requests/ end_date EP valid string (date)
        Also generated from spec: POST /api/requests/ end_date BVA 2026-12-08 (limit+1, end_date >= start_date)
        Also generated from spec: POST /api/requests/ note EP valid string
        Also generated from spec: POST /api/requests/ Authorization EP valid token

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=201)

    def test_leave_type_ep_valid_enum_value_permit(self):
        """Generated from spec: POST /api/requests/ leave_type EP valid enum value 'permit'

        Expect 201.
        """
        self.check({'leave_type': 'permit', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=201)

    def test_leave_type_ep_valid_enum_value_personal(self):
        """Generated from spec: POST /api/requests/ leave_type EP valid enum value 'personal'

        Expect 201.
        """
        self.check({'leave_type': 'personal', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=201)

    def test_leave_type_ep_invalid_out_of_enum_zzz_not_in_enum(self):
        """Generated from spec: POST /api/requests/ leave_type EP invalid out-of-enum 'zzz_not_in_enum'

        Expect 400, error key leave_type.
        """
        self.check({'leave_type': 'zzz_not_in_enum', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='leave_type')

    def test_leave_type_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/ leave_type EP invalid wrong type (true)

        Expect 400, error key leave_type.
        """
        self.check({'leave_type': True, 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='leave_type')

    def test_leave_type_ep_invalid_null_optional(self):
        """Generated from spec: POST /api/requests/ leave_type EP invalid null (optional)

        Expect 400, error key leave_type.
        """
        self.check({'leave_type': None, 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='leave_type')

    def test_leave_type_ep_valid_omitted_optional(self):
        """Generated from spec: POST /api/requests/ leave_type EP valid omitted (optional)

        Expect 201.
        """
        self.check({'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=201)

    def test_leave_type_ep_invalid_example_empty(self):
        """Generated from spec: POST /api/requests/ leave_type EP invalid example ''

        Expect 400, error key leave_type.
        """
        self.check({'leave_type': '', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='leave_type')

    def test_start_date_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid wrong type (true)

        Expect 400, error key start_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': True, 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='start_date')

    def test_start_date_ep_invalid_date_format_not_a_date(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid date format ('not-a-date')

        Expect 400, error key start_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': 'not-a-date', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='start_date')

    def test_start_date_ep_invalid_null_required(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid null (required)

        Expect 400, error key start_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': None, 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='start_date')

    def test_start_date_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid missing (required)

        Expect 400, error key start_date.
        """
        self.check({'leave_type': 'vacation', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='start_date')

    def test_start_date_ep_invalid_example_empty(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid example ''

        Expect 400, error key start_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': '', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='start_date')

    def test_start_date_ep_invalid_example_2026_02_30(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid example '2026-02-30'

        Expect 400, error key start_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-02-30', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, error='start_date')

    def test_end_date_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid wrong type (true)

        Expect 400, error key end_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': True, 'note': 'Generated test'}, status=400, error='end_date')

    def test_end_date_ep_invalid_date_format_not_a_date(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid date format ('not-a-date')

        Expect 400, error key end_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': 'not-a-date', 'note': 'Generated test'}, status=400, error='end_date')

    def test_end_date_ep_invalid_null_required(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid null (required)

        Expect 400, error key end_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': None, 'note': 'Generated test'}, status=400, error='end_date')

    def test_end_date_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid missing (required)

        Expect 400, error key end_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'note': 'Generated test'}, status=400, error='end_date')

    def test_end_date_ep_invalid_example_empty(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid example ''

        Expect 400, error key end_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '', 'note': 'Generated test'}, status=400, error='end_date')

    def test_end_date_ep_invalid_example_2026_02_30(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid example '2026-02-30'

        Expect 400, error key end_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-02-30', 'note': 'Generated test'}, status=400, error='end_date')

    def test_end_date_bva_2026_12_06_below(self):
        """Generated from spec: POST /api/requests/ end_date BVA 2026-12-06 (limit-1, end_date >= start_date)

        Expect 400, error key end_date.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-06', 'note': 'Generated test'}, status=400, error='end_date')

    def test_end_date_bva_2026_12_07_at(self):
        """Generated from spec: POST /api/requests/ end_date BVA 2026-12-07 (limit, end_date >= start_date)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-07', 'note': 'Generated test'}, status=201)

    def test_note_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/ note EP invalid wrong type (true)

        Expect 400, error key note.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': True}, status=400, error='note')

    def test_note_ep_invalid_null_optional(self):
        """Generated from spec: POST /api/requests/ note EP invalid null (optional)

        Expect 400, error key note.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': None}, status=400, error='note')

    def test_note_ep_valid_omitted_optional(self):
        """Generated from spec: POST /api/requests/ note EP valid omitted (optional)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08'}, status=201)

    def test_note_ep_invalid_over_max_length_560_chars_280(self):
        """Generated from spec: POST /api/requests/ note EP invalid over-max-length (560 chars > 280)

        Expect 400, error key note.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 560}, status=400, error='note')

    def test_note_bva_279_below(self):
        """Generated from spec: POST /api/requests/ note BVA 279 (limit-1, maxLength 280)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 279}, status=201)

    def test_note_bva_280_at(self):
        """Generated from spec: POST /api/requests/ note BVA 280 (limit, maxLength 280)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 280}, status=201)

    def test_note_bva_281_above(self):
        """Generated from spec: POST /api/requests/ note BVA 281 (limit+1, maxLength 280)

        Expect 400, error key note.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 281}, status=400, error='note')

    def test_note_bva_0_at(self):
        """Generated from spec: POST /api/requests/ note BVA 0 (limit, minLength 0)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': ''}, status=201)

    def test_note_bva_1_above(self):
        """Generated from spec: POST /api/requests/ note BVA 1 (limit+1, minLength 0)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n'}, status=201)

    def test_start_date_end_date_bva_9_below_br_03_business_days_10(self):
        """Generated from spec: POST /api/requests/ start_date..end_date BVA 9 (limit-1, BR-03 business days <= 10)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2027-01-04', 'end_date': '2027-01-14', 'note': 'Generated test'}, status=201)

    def test_start_date_end_date_bva_10_at_br_03_business_days_10(self):
        """Generated from spec: POST /api/requests/ start_date..end_date BVA 10 (limit, BR-03 business days <= 10)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2027-01-04', 'end_date': '2027-01-15', 'note': 'Generated test'}, status=201)

    def test_start_date_end_date_bva_11_above_br_03_business_days_10(self):
        """Generated from spec: POST /api/requests/ start_date..end_date BVA 11 (limit+1, BR-03 business days <= 10)

        Expect 400, error key non_field_errors.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2027-01-04', 'end_date': '2027-01-18', 'note': 'Generated test'}, status=400, error='non_field_errors')

    def test_start_date_end_date_ep_invalid_br_03_20_business_days(self):
        """Generated from spec: POST /api/requests/ start_date..end_date EP invalid BR-03 20 business days

        Expect 400, error key non_field_errors.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2027-01-04', 'end_date': '2027-01-29', 'note': 'Generated test'}, status=400, error='non_field_errors')

    def test_start_date_end_date_bva_2026_12_14_below_br_02_existing_start(self):
        """Generated from spec: POST /api/requests/ start_date..end_date BVA 2026-12-14 (limit-1, BR-02 existing start)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-14', 'end_date': '2026-12-14', 'note': 'Generated test'}, status=201)

    def test_start_date_end_date_bva_2026_12_15_at_br_02_existing_start(self):
        """Generated from spec: POST /api/requests/ start_date..end_date BVA 2026-12-15 (limit, BR-02 existing start)

        Also generated from spec: POST /api/requests/ start_date..end_date BVA 2026-12-15 (limit-1, BR-02 existing end)

        Expect 400, error key non_field_errors.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-15', 'end_date': '2026-12-15', 'note': 'Generated test'}, status=400, error='non_field_errors')

    def test_start_date_end_date_bva_2026_12_16_above_br_02_existing_start(self):
        """Generated from spec: POST /api/requests/ start_date..end_date BVA 2026-12-16 (limit+1, BR-02 existing start)

        Also generated from spec: POST /api/requests/ start_date..end_date BVA 2026-12-16 (limit, BR-02 existing end)

        Expect 400, error key non_field_errors.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-16', 'end_date': '2026-12-16', 'note': 'Generated test'}, status=400, error='non_field_errors')

    def test_start_date_end_date_bva_2026_12_17_above_br_02_existing_end(self):
        """Generated from spec: POST /api/requests/ start_date..end_date BVA 2026-12-17 (limit+1, BR-02 existing end)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-17', 'end_date': '2026-12-17', 'note': 'Generated test'}, status=201)

    def test_start_date_end_date_ep_invalid_br_02_encloses_existing(self):
        """Generated from spec: POST /api/requests/ start_date..end_date EP invalid BR-02 encloses existing

        Expect 400, error key non_field_errors.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-14', 'end_date': '2026-12-17', 'note': 'Generated test'}, status=400, error='non_field_errors')

    def test_authorization_ep_invalid_no_token(self):
        """Generated from spec: POST /api/requests/ Authorization EP invalid no token

        Expect 401, error key detail.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=401, auth='none', error='detail')

    def test_authorization_ep_invalid_unknown_token(self):
        """Generated from spec: POST /api/requests/ Authorization EP invalid unknown token

        Expect 401, error key detail.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=401, auth='invalid', error='detail')


class GeneratedDecideRequestTests(GeneratedApiTestCase):
    """POST /api/requests/{id}/decision/: 15 generated tests."""

    METHOD = 'post'
    PATH = '/api/requests/{id}/decision/'
    ACTOR = 'm1'
    PATH_PARAMS = {'id': 'pending.id'}
    READBACK = 'decided'
    SUCCESS = 200

    def test_status_ep_valid_enum_value_approved(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP valid enum value 'approved'

        Also generated from spec: POST /api/requests/{id}/decision/ id EP valid existing record
        Also generated from spec: POST /api/requests/{id}/decision/ Authorization EP valid token

        Expect 200.
        """
        self.check({'status': 'approved'}, status=200)

    def test_status_ep_valid_enum_value_rejected(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP valid enum value 'rejected'

        Expect 200.
        """
        self.check({'status': 'rejected'}, status=200)

    def test_status_ep_invalid_out_of_enum_zzz_not_in_enum(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid out-of-enum 'zzz_not_in_enum'

        Expect 400, error key detail.
        """
        self.check({'status': 'zzz_not_in_enum'}, status=400, error='detail')

    def test_status_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid wrong type (true)

        Expect 400, error key detail.
        """
        self.check({'status': True}, status=400, error='detail')

    def test_status_ep_invalid_null_required(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid null (required)

        Expect 400, error key detail.
        """
        self.check({'status': None}, status=400, error='detail')

    def test_status_ep_invalid_missing_required(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid missing (required)

        Expect 400, error key detail.
        """
        self.check({}, status=400, error='detail')

    def test_status_ep_invalid_example_empty(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid example ''

        Expect 400, error key detail.
        """
        self.check({'status': ''}, status=400, error='detail')

    def test_status_ep_invalid_example_pending(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid example 'pending'

        Expect 400, error key detail.
        """
        self.check({'status': 'pending'}, status=400, error='detail')

    def test_id_ep_invalid_example_0(self):
        """Generated from spec: POST /api/requests/{id}/decision/ id EP invalid example 0

        Expect 404.
        """
        self.check({'status': 'approved'}, status=404, path={'id': 0})

    def test_id_ep_invalid_example_minus_1(self):
        """Generated from spec: POST /api/requests/{id}/decision/ id EP invalid example -1

        Expect 404.
        """
        self.check({'status': 'approved'}, status=404, path={'id': -1})

    def test_id_ep_invalid_example_2147483647(self):
        """Generated from spec: POST /api/requests/{id}/decision/ id EP invalid example 2147483647

        Expect 404.
        """
        self.check({'status': 'approved'}, status=404, path={'id': 2147483647})

    def test_id_ep_invalid_example_abc(self):
        """Generated from spec: POST /api/requests/{id}/decision/ id EP invalid example 'abc'

        Expect 404.
        """
        self.check({'status': 'approved'}, status=404, path={'id': 'abc'})

    def test_id_ep_invalid_example_1_5(self):
        """Generated from spec: POST /api/requests/{id}/decision/ id EP invalid example 1.5

        Expect 404.
        """
        self.check({'status': 'approved'}, status=404, path={'id': 1.5})

    def test_authorization_ep_invalid_no_token(self):
        """Generated from spec: POST /api/requests/{id}/decision/ Authorization EP invalid no token

        Expect 401, error key detail.
        """
        self.check({'status': 'approved'}, status=401, auth='none', error='detail')

    def test_authorization_ep_invalid_unknown_token(self):
        """Generated from spec: POST /api/requests/{id}/decision/ Authorization EP invalid unknown token

        Expect 401, error key detail.
        """
        self.check({'status': 'approved'}, status=401, auth='invalid', error='detail')
