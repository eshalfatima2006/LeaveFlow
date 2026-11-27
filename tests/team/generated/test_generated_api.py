# =============================================================================
# GENERATED FILE - DO NOT EDIT BY HAND.
# Generator: scripts/sqe/generate_api_tests.py
# Spec:      docs/sqe/openapi/leaveflow-api.yaml
# Spec SHA-256: 939d1303b296138c872a55f84823eeb15d0370925cc840fe5f14c6064fcd0b41
# Command:   python3 scripts/sqe/generate_api_tests.py docs/sqe/openapi/leaveflow-api.yaml --output tests/team/generated/test_generated_api.py
#
# One input varies per test; the rest is the operation's example request.
# EP and 3-point BVA classes: see the generator's module docstring. Identical
# requests are generated once; the docstring lists every class the test covers
# (count each executable case once).
# Tests: 127
# =============================================================================
"""OpenAPI-generated EP/BVA API tests (A2.4). Regenerate instead of editing."""

from datetime import date
from urllib.parse import urlencode

from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from leave.models import LeaveRequest
from tests.team.api.contract import response_errors
from tests.team.api.support import all_rows, balance_view, token_client
from tests.team.fixtures.leave_data import TEST_PASSWORD, build_people, make_request

SPEC_SHA256 = '939d1303b296138c872a55f84823eeb15d0370925cc840fe5f14c6064fcd0b41'
FIXTURE = {'allowance': 10, 'pending': {'start': '2026-12-15', 'end': '2026-12-16'}}


class F:
    """Fixture-bound value, resolved inside the test."""

    def __init__(self, ref):
        self.ref = ref


class GeneratedApiTestCase(TestCase):
    """Runtime harness emitted by the generator; uses the A2.1 fixtures and token clients."""

    OPERATION = METHOD = PATH = READBACK = ACTOR = None
    PATH_PARAMS = {}
    DEFAULTS = {}
    SUCCESS = 200

    def setUp(self):
        # x-sqe-fixture: every allowance, and e1's pending request (W2 target, overlap interval).
        self.people = p = build_people("gen", allowance=FIXTURE["allowance"])
        start, end = (date.fromisoformat(FIXTURE["pending"][k]) for k in ("start", "end"))
        self.records = {
            "pending": make_request(p.e1, start=start, end=end),
            "approved": make_request(p.e2, start=date(2026, 12, 21), end=date(2026, 12, 22),
                                     status=LeaveRequest.Status.APPROVED, decided_by=p.m1),
            "rejected": make_request(p.e2, start=date(2026, 12, 23), end=date(2026, 12, 23),
                                     status=LeaveRequest.Status.REJECTED, decided_by=p.m1),
            "other_team": make_request(p.m2, start=start, end=end),
            "own": make_request(p.m1, start=start, end=end),
        }

    def ref(self, ref):
        root, *attrs = ref.split(".")
        value = TEST_PASSWORD if root == "password" else self.records.get(root) or getattr(self.people, root)
        for attr in attrs:
            value = getattr(value, attr)
        return value

    def resolve(self, values):
        return {k: self.ref(v.ref) if isinstance(v, F) else v for k, v in values.items()}

    def client_for(self, auth, actor):
        if auth == "actor" and actor:
            return token_client(self.ref(actor))
        client = APIClient()
        if auth == "invalid":
            client.credentials(HTTP_AUTHORIZATION="Token " + "0" * 40)
        return client

    def balances(self):
        return {user.pk: balance_view(user) for user in vars(self.people).values() if hasattr(user, "role")}

    def state(self):
        return all_rows(), self.balances(), set(Token.objects.values_list("key", flat=True))

    def send(self, client, method, url, body, media, raw):
        call = getattr(client, method)
        if method == "get":
            return call(url)
        if raw is not None:
            return call(url, raw, content_type=media)
        if media == "application/json":
            return call(url, body, format="json")
        if media == "multipart/form-data":
            return call(url, body, format="multipart")
        return call(url, urlencode(body), content_type=media)

    def check(self, body, *, status, path=None, auth="actor", actor=None, method=None,
              media="application/json", raw=None, error=None):
        """One real API call; assert exact status, error key, response schema and stored state."""
        actor, method = actor or self.ACTOR, method or self.METHOD
        client, body = self.client_for(auth, actor), self.resolve(body)
        target = {**{k: self.ref(v) for k, v in self.PATH_PARAMS.items()}, **self.resolve(path or {})}
        before, started = self.state(), timezone.now()
        response = self.send(client, method, self.PATH.format(**target), body, media, raw)
        data = getattr(response, "data", None)
        shown = "(login response hidden)" if self.READBACK == "token" else repr(data)
        self.assertEqual(response.status_code, status, f"{method.upper()} {self.PATH}, expected {status}: {shown}")
        if status != 405:  # OpenAPI documents implemented methods only
            self.assertEqual(response_errors(self.OPERATION, response), [])
        if error is not None:
            self.assertEqual(set(data), {error}, shown)
        after = self.state()
        if status == self.SUCCESS and self.READBACK != "none":
            getattr(self, "assert_" + self.READBACK)(body, before, after, response, actor, target, started)
        else:
            self.assertTrue(after == before, "a refused or read-only call changed stored state")

    def assert_created(self, body, before, after, response, actor, target, started):
        """Exactly one new row, as submitted, pending and owned by the caller; nothing else changed."""
        expected = {**self.DEFAULTS, **body}
        new = [row for row in after[0] if row not in before[0]]
        self.assertEqual((len(new), len(after[0])), (1, len(before[0]) + 1))
        row = new[0]
        self.assertEqual(
            (row["id"], row["employee_id"], row["status"], row["decided_by_id"], row["decided_at"]),
            (response.json()["id"], self.ref(actor).pk, LeaveRequest.Status.PENDING, None, None),
        )
        self.assertEqual(
            (row["leave_type"], row["start_date"].isoformat(), row["end_date"].isoformat(), row["note"]),
            (expected["leave_type"], expected["start_date"], expected["end_date"],
             expected["note"].strip() if expected["note"] else expected["note"]),  # null note (nullable spec)
        )
        self.assertTrue(after[1:] == before[1:], "balance or tokens changed")

    def assert_decided(self, body, before, after, response, actor, target, started):
        """Same row and content, new status, decider and time; only the owner's balance moves, on approval."""
        old = next(row for row in before[0] if row["id"] == target["id"])
        new = next(row for row in after[0] if row["id"] == target["id"])
        self.assertEqual(response.json()["id"], target["id"])
        self.assertTrue(started <= new["decided_at"] <= timezone.now())
        self.assertEqual(new, {**old, "status": body["status"], "decided_by_id": self.ref(actor).pk,
                               "decided_at": new["decided_at"]})
        self.assertEqual([r for r in after[0] if r["id"] != target["id"]], [r for r in before[0] if r["id"] != target["id"]])
        days = LeaveRequest.objects.get(pk=target["id"]).business_days if body["status"] == "approved" else 0
        allowance, used, available = before[1][old["employee_id"]]
        self.assertEqual(after[1], {**before[1], old["employee_id"]: (allowance, used + days, available - days)})
        self.assertTrue(after[2] == before[2], "tokens changed")

    def assert_token(self, body, before, after, response, actor, target, started):
        """One token, returned by the call and bound to the user who logged in; requests unchanged."""
        created = after[2] - before[2]
        self.assertTrue(created == {response.json()["token"]}, "the returned token is the only new one")
        user = Token.objects.get(key=created.pop()).user
        self.assertEqual((user.username, response.json()["user"]["id"]), (body["username"], user.pk))
        self.assertTrue(after[:2] == before[:2], "requests or balances changed")


class GeneratedLoginTests(GeneratedApiTestCase):
    """POST /api/auth/login/: 19 generated tests."""

    OPERATION = 'login'
    METHOD = 'post'
    PATH = '/api/auth/login/'
    ACTOR = None
    PATH_PARAMS = {}
    DEFAULTS = {}
    READBACK = 'token'
    SUCCESS = 200

    def test_username_ep_valid_string(self):
        """Generated from spec: POST /api/auth/login/ username EP valid string

        Also generated from spec: POST /api/auth/login/ password EP valid string (password)
        Also generated from spec: POST /api/auth/login/ media EP valid application/json

        Expect 200.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=200)

    def test_username_ep_invalid_wrong_type_true(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid wrong type (true)

        Expect 400, error key detail.
        """
        self.check({'username': True, 'password': F('password')}, status=400, error='detail')

    def test_username_ep_invalid_null_not_nullable(self):
        """Generated from spec: POST /api/auth/login/ username EP invalid null (not nullable)

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

    def test_password_ep_invalid_null_not_nullable(self):
        """Generated from spec: POST /api/auth/login/ password EP invalid null (not nullable)

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

    def test_media_ep_valid_application_x_www_form_urlencoded(self):
        """Generated from spec: POST /api/auth/login/ media EP valid application/x-www-form-urlencoded

        Expect 200.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=200, media='application/x-www-form-urlencoded')

    def test_media_ep_valid_multipart_form_data(self):
        """Generated from spec: POST /api/auth/login/ media EP valid multipart/form-data

        Expect 200.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=200, media='multipart/form-data')

    def test_media_ep_invalid_malformed_json(self):
        """Generated from spec: POST /api/auth/login/ media EP invalid malformed JSON

        Expect 400, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=400, raw='{', error='detail')

    def test_media_ep_invalid_text_plain(self):
        """Generated from spec: POST /api/auth/login/ media EP invalid text/plain

        Expect 415, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=415, media='text/plain', raw='x', error='detail')

    def test_method_ep_invalid_get(self):
        """Generated from spec: POST /api/auth/login/ method EP invalid GET

        Expect 405, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=405, method='get', error='detail')

    def test_method_ep_invalid_put(self):
        """Generated from spec: POST /api/auth/login/ method EP invalid PUT

        Expect 405, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=405, method='put', error='detail')

    def test_method_ep_invalid_patch(self):
        """Generated from spec: POST /api/auth/login/ method EP invalid PATCH

        Expect 405, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=405, method='patch', error='detail')

    def test_method_ep_invalid_delete(self):
        """Generated from spec: POST /api/auth/login/ method EP invalid DELETE

        Expect 405, error key detail.
        """
        self.check({'username': F('e1.username'), 'password': F('password')}, status=405, method='delete', error='detail')


class GeneratedMeTests(GeneratedApiTestCase):
    """GET /api/me/: 7 generated tests."""

    OPERATION = 'me'
    METHOD = 'get'
    PATH = '/api/me/'
    ACTOR = 'm1'
    PATH_PARAMS = {}
    DEFAULTS = {}
    READBACK = 'none'
    SUCCESS = 200

    def test_authorization_ep_valid_token(self):
        """Generated from spec: GET /api/me/ Authorization EP valid token

        Expect 200.
        """
        self.check({}, status=200)

    def test_authorization_ep_invalid_no_token(self):
        """Generated from spec: GET /api/me/ Authorization EP invalid no token

        Expect 401, error key detail.
        """
        self.check({}, status=401, auth='none', error='detail')

    def test_authorization_ep_invalid_unknown_token(self):
        """Generated from spec: GET /api/me/ Authorization EP invalid unknown token

        Expect 401, error key detail.
        """
        self.check({}, status=401, auth='invalid', error='detail')

    def test_method_ep_invalid_post(self):
        """Generated from spec: GET /api/me/ method EP invalid POST

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='post', error='detail')

    def test_method_ep_invalid_put(self):
        """Generated from spec: GET /api/me/ method EP invalid PUT

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='put', error='detail')

    def test_method_ep_invalid_patch(self):
        """Generated from spec: GET /api/me/ method EP invalid PATCH

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='patch', error='detail')

    def test_method_ep_invalid_delete(self):
        """Generated from spec: GET /api/me/ method EP invalid DELETE

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='delete', error='detail')


class GeneratedListRequestsTests(GeneratedApiTestCase):
    """GET /api/requests/: 6 generated tests."""

    OPERATION = 'listRequests'
    METHOD = 'get'
    PATH = '/api/requests/'
    ACTOR = 'm1'
    PATH_PARAMS = {}
    DEFAULTS = {}
    READBACK = 'none'
    SUCCESS = 200

    def test_authorization_ep_valid_token(self):
        """Generated from spec: GET /api/requests/ Authorization EP valid token

        Expect 200.
        """
        self.check({}, status=200)

    def test_authorization_ep_invalid_no_token(self):
        """Generated from spec: GET /api/requests/ Authorization EP invalid no token

        Expect 401, error key detail.
        """
        self.check({}, status=401, auth='none', error='detail')

    def test_authorization_ep_invalid_unknown_token(self):
        """Generated from spec: GET /api/requests/ Authorization EP invalid unknown token

        Expect 401, error key detail.
        """
        self.check({}, status=401, auth='invalid', error='detail')

    def test_method_ep_invalid_put(self):
        """Generated from spec: GET /api/requests/ method EP invalid PUT

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='put', error='detail')

    def test_method_ep_invalid_patch(self):
        """Generated from spec: GET /api/requests/ method EP invalid PATCH

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='patch', error='detail')

    def test_method_ep_invalid_delete(self):
        """Generated from spec: GET /api/requests/ method EP invalid DELETE

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='delete', error='detail')


class GeneratedSubmitRequestTests(GeneratedApiTestCase):
    """POST /api/requests/: 49 generated tests."""

    OPERATION = 'submitRequest'
    METHOD = 'post'
    PATH = '/api/requests/'
    ACTOR = 'e1'
    PATH_PARAMS = {}
    DEFAULTS = {'leave_type': 'vacation', 'note': ''}
    READBACK = 'created'
    SUCCESS = 201

    def test_leave_type_ep_valid_enum_value_vacation(self):
        """Generated from spec: POST /api/requests/ leave_type EP valid enum value 'vacation'

        Also generated from spec: POST /api/requests/ start_date EP valid string (date)
        Also generated from spec: POST /api/requests/ end_date EP valid string (date)
        Also generated from spec: POST /api/requests/ end_date BVA 2026-12-08 (limit+1, end_date >= start_date)
        Also generated from spec: POST /api/requests/ note EP valid string
        Also generated from spec: POST /api/requests/ Authorization EP valid token
        Also generated from spec: POST /api/requests/ media EP valid application/json

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

    def test_leave_type_ep_invalid_null_not_nullable(self):
        """Generated from spec: POST /api/requests/ leave_type EP invalid null (not nullable)

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

    def test_start_date_ep_invalid_null_not_nullable(self):
        """Generated from spec: POST /api/requests/ start_date EP invalid null (not nullable)

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

    def test_end_date_ep_invalid_null_not_nullable(self):
        """Generated from spec: POST /api/requests/ end_date EP invalid null (not nullable)

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

    def test_note_ep_invalid_null_not_nullable(self):
        """Generated from spec: POST /api/requests/ note EP invalid null (not nullable)

        Expect 400, error key note.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': None}, status=400, error='note')

    def test_note_ep_valid_omitted_optional(self):
        """Generated from spec: POST /api/requests/ note EP valid omitted (optional)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08'}, status=201)

    def test_note_ep_invalid_over_x_trimmed_max_length_560_chars(self):
        """Generated from spec: POST /api/requests/ note EP invalid over x-trimmed-max-length (560 chars)

        Expect 400, error key note.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 560}, status=400, error='note')

    def test_note_bva_279_below(self):
        """Generated from spec: POST /api/requests/ note BVA 279 (limit-1, x-trimmed-max-length 280)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 279}, status=201)

    def test_note_bva_280_at(self):
        """Generated from spec: POST /api/requests/ note BVA 280 (limit, x-trimmed-max-length 280)

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 280}, status=201)

    def test_note_bva_281_above(self):
        """Generated from spec: POST /api/requests/ note BVA 281 (limit+1, x-trimmed-max-length 280)

        Expect 400, error key note.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'n' * 281}, status=400, error='note')

    def test_note_ep_valid_whitespace_only(self):
        """Generated from spec: POST /api/requests/ note EP valid whitespace only

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': '   '}, status=201)

    def test_note_ep_valid_padded_280_chars_after_trim(self):
        """Generated from spec: POST /api/requests/ note EP valid padded 280 chars after trim

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': ' ' + 'n' * 280 + ' '}, status=201)

    def test_note_ep_invalid_padded_281_chars_after_trim(self):
        """Generated from spec: POST /api/requests/ note EP invalid padded 281 chars after trim

        Expect 400, error key note.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': ' ' + 'n' * 281 + ' '}, status=400, error='note')

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

    def test_media_ep_valid_application_x_www_form_urlencoded(self):
        """Generated from spec: POST /api/requests/ media EP valid application/x-www-form-urlencoded

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=201, media='application/x-www-form-urlencoded')

    def test_media_ep_valid_multipart_form_data(self):
        """Generated from spec: POST /api/requests/ media EP valid multipart/form-data

        Expect 201.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=201, media='multipart/form-data')

    def test_media_ep_invalid_malformed_json(self):
        """Generated from spec: POST /api/requests/ media EP invalid malformed JSON

        Expect 400, error key detail.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=400, raw='{', error='detail')

    def test_media_ep_invalid_text_plain(self):
        """Generated from spec: POST /api/requests/ media EP invalid text/plain

        Expect 415, error key detail.
        """
        self.check({'leave_type': 'vacation', 'start_date': '2026-12-07', 'end_date': '2026-12-08', 'note': 'Generated test'}, status=415, media='text/plain', raw='x', error='detail')


class GeneratedDecideRequestTests(GeneratedApiTestCase):
    """POST /api/requests/{id}/decision/: 32 generated tests."""

    OPERATION = 'decideRequest'
    METHOD = 'post'
    PATH = '/api/requests/{id}/decision/'
    ACTOR = 'm1'
    PATH_PARAMS = {'id': 'pending.id'}
    DEFAULTS = {}
    READBACK = 'decided'
    SUCCESS = 200

    def test_status_ep_valid_enum_value_approved(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP valid enum value 'approved'

        Also generated from spec: POST /api/requests/{id}/decision/ id EP valid existing record
        Also generated from spec: POST /api/requests/{id}/decision/ context EP valid manager of the team
        Also generated from spec: POST /api/requests/{id}/decision/ Authorization EP valid token
        Also generated from spec: POST /api/requests/{id}/decision/ media EP valid application/json

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

    def test_status_ep_invalid_null_not_nullable(self):
        """Generated from spec: POST /api/requests/{id}/decision/ status EP invalid null (not nullable)

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

    def test_context_ep_valid_admin(self):
        """Generated from spec: POST /api/requests/{id}/decision/ context EP valid admin

        Expect 200.
        """
        self.check({'status': 'approved'}, status=200, actor='admin')

    def test_context_ep_invalid_employee_owner(self):
        """Generated from spec: POST /api/requests/{id}/decision/ context EP invalid employee owner

        Expect 403, error key detail.
        """
        self.check({'status': 'approved'}, status=403, actor='e1', error='detail')

    def test_context_ep_invalid_employee_teammate(self):
        """Generated from spec: POST /api/requests/{id}/decision/ context EP invalid employee teammate

        Expect 403, error key detail.
        """
        self.check({'status': 'approved'}, status=403, actor='e2', error='detail')

    def test_context_ep_invalid_manager_of_another_team(self):
        """Generated from spec: POST /api/requests/{id}/decision/ context EP invalid manager of another team

        Expect 404, error key detail.
        """
        self.check({'status': 'approved'}, status=404, actor='m2', error='detail')

    def test_context_ep_invalid_manager_without_a_team(self):
        """Generated from spec: POST /api/requests/{id}/decision/ context EP invalid manager without a team

        Expect 404, error key detail.
        """
        self.check({'status': 'approved'}, status=404, actor='teamless_manager', error='detail')

    def test_context_ep_invalid_manager_own_request(self):
        """Generated from spec: POST /api/requests/{id}/decision/ context EP invalid manager own request

        Expect 403, error key detail.
        """
        self.check({'status': 'approved'}, status=403, path={'id': F('own.id')}, error='detail')

    def test_context_ep_invalid_request_out_of_scope(self):
        """Generated from spec: POST /api/requests/{id}/decision/ context EP invalid request out of scope

        Expect 404, error key detail.
        """
        self.check({'status': 'approved'}, status=404, path={'id': F('other_team.id')}, error='detail')

    def test_context_ep_invalid_request_already_approved(self):
        """Generated from spec: POST /api/requests/{id}/decision/ context EP invalid request already approved

        Expect 409, error key detail.
        """
        self.check({'status': 'approved'}, status=409, path={'id': F('approved.id')}, error='detail')

    def test_context_ep_invalid_request_already_rejected(self):
        """Generated from spec: POST /api/requests/{id}/decision/ context EP invalid request already rejected

        Expect 409, error key detail.
        """
        self.check({'status': 'approved'}, status=409, path={'id': F('rejected.id')}, error='detail')

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

    def test_media_ep_valid_application_x_www_form_urlencoded(self):
        """Generated from spec: POST /api/requests/{id}/decision/ media EP valid application/x-www-form-urlencoded

        Expect 200.
        """
        self.check({'status': 'approved'}, status=200, media='application/x-www-form-urlencoded')

    def test_media_ep_valid_multipart_form_data(self):
        """Generated from spec: POST /api/requests/{id}/decision/ media EP valid multipart/form-data

        Expect 200.
        """
        self.check({'status': 'approved'}, status=200, media='multipart/form-data')

    def test_media_ep_invalid_malformed_json(self):
        """Generated from spec: POST /api/requests/{id}/decision/ media EP invalid malformed JSON

        Expect 400, error key detail.
        """
        self.check({'status': 'approved'}, status=400, raw='{', error='detail')

    def test_media_ep_invalid_text_plain(self):
        """Generated from spec: POST /api/requests/{id}/decision/ media EP invalid text/plain

        Expect 415, error key detail.
        """
        self.check({'status': 'approved'}, status=415, media='text/plain', raw='x', error='detail')

    def test_method_ep_invalid_get(self):
        """Generated from spec: POST /api/requests/{id}/decision/ method EP invalid GET

        Expect 405, error key detail.
        """
        self.check({'status': 'approved'}, status=405, method='get', error='detail')

    def test_method_ep_invalid_put(self):
        """Generated from spec: POST /api/requests/{id}/decision/ method EP invalid PUT

        Expect 405, error key detail.
        """
        self.check({'status': 'approved'}, status=405, method='put', error='detail')

    def test_method_ep_invalid_patch(self):
        """Generated from spec: POST /api/requests/{id}/decision/ method EP invalid PATCH

        Expect 405, error key detail.
        """
        self.check({'status': 'approved'}, status=405, method='patch', error='detail')

    def test_method_ep_invalid_delete(self):
        """Generated from spec: POST /api/requests/{id}/decision/ method EP invalid DELETE

        Expect 405, error key detail.
        """
        self.check({'status': 'approved'}, status=405, method='delete', error='detail')


class GeneratedDashboardTests(GeneratedApiTestCase):
    """GET /api/dashboard/: 7 generated tests."""

    OPERATION = 'dashboard'
    METHOD = 'get'
    PATH = '/api/dashboard/'
    ACTOR = 'm1'
    PATH_PARAMS = {}
    DEFAULTS = {}
    READBACK = 'none'
    SUCCESS = 200

    def test_authorization_ep_valid_token(self):
        """Generated from spec: GET /api/dashboard/ Authorization EP valid token

        Expect 200.
        """
        self.check({}, status=200)

    def test_authorization_ep_invalid_no_token(self):
        """Generated from spec: GET /api/dashboard/ Authorization EP invalid no token

        Expect 401, error key detail.
        """
        self.check({}, status=401, auth='none', error='detail')

    def test_authorization_ep_invalid_unknown_token(self):
        """Generated from spec: GET /api/dashboard/ Authorization EP invalid unknown token

        Expect 401, error key detail.
        """
        self.check({}, status=401, auth='invalid', error='detail')

    def test_method_ep_invalid_post(self):
        """Generated from spec: GET /api/dashboard/ method EP invalid POST

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='post', error='detail')

    def test_method_ep_invalid_put(self):
        """Generated from spec: GET /api/dashboard/ method EP invalid PUT

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='put', error='detail')

    def test_method_ep_invalid_patch(self):
        """Generated from spec: GET /api/dashboard/ method EP invalid PATCH

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='patch', error='detail')

    def test_method_ep_invalid_delete(self):
        """Generated from spec: GET /api/dashboard/ method EP invalid DELETE

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='delete', error='detail')


class GeneratedTeamTests(GeneratedApiTestCase):
    """GET /api/team/: 7 generated tests."""

    OPERATION = 'team'
    METHOD = 'get'
    PATH = '/api/team/'
    ACTOR = 'm1'
    PATH_PARAMS = {}
    DEFAULTS = {}
    READBACK = 'none'
    SUCCESS = 200

    def test_authorization_ep_valid_token(self):
        """Generated from spec: GET /api/team/ Authorization EP valid token

        Expect 200.
        """
        self.check({}, status=200)

    def test_authorization_ep_invalid_no_token(self):
        """Generated from spec: GET /api/team/ Authorization EP invalid no token

        Expect 401, error key detail.
        """
        self.check({}, status=401, auth='none', error='detail')

    def test_authorization_ep_invalid_unknown_token(self):
        """Generated from spec: GET /api/team/ Authorization EP invalid unknown token

        Expect 401, error key detail.
        """
        self.check({}, status=401, auth='invalid', error='detail')

    def test_method_ep_invalid_post(self):
        """Generated from spec: GET /api/team/ method EP invalid POST

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='post', error='detail')

    def test_method_ep_invalid_put(self):
        """Generated from spec: GET /api/team/ method EP invalid PUT

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='put', error='detail')

    def test_method_ep_invalid_patch(self):
        """Generated from spec: GET /api/team/ method EP invalid PATCH

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='patch', error='detail')

    def test_method_ep_invalid_delete(self):
        """Generated from spec: GET /api/team/ method EP invalid DELETE

        Expect 405, error key detail.
        """
        self.check({}, status=405, method='delete', error='detail')
