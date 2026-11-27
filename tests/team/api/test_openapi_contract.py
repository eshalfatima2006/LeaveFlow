# =============================================================================
# A2.4 — OPENAPI CONTRACT VERIFICATION (RTM GEN-001 "compare actual contract drift")
#
# Every documented (operation, status) pair of docs/sqe/openapi/leaveflow-api.yaml
# is produced by a real API call, and the response's status, media type and body
# are validated against the spec (tests/team/api/contract.py). Pairs are declared
# with @covers; test_every_documented_response_is_exercised fails when the spec
# documents a response that no test produces.
#
# Scope: response structure. Business effects are asserted by the A2.1-A2.3 suites.
# The KnownDeviation tests pin baseline responses that contradict the contract;
# they are characterizations of defects, not approved behaviour.
# =============================================================================
"""A2.4: real responses conform to the OpenAPI response contract."""

from datetime import date
import hashlib

from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from leave.models import LeaveRequest, User
from tests.team.api.contract import CONTRACT, SPEC_PATH, errors, response_errors
from tests.team.api.support import (
    LOGIN_URL, REQUESTS_URL, add_member, all_rows, decision_url, payload, token_client,
)
from tests.team.fixtures.leave_data import TEST_PASSWORD, build_people, make_request
from tests.team.generated import test_generated_api


def covers(operation_id, status):
    def mark(method):
        method.covers = (operation_id, status)
        return method
    return mark


def invalid_token_client():
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + "0" * 40)
    return client


class ContractTestCase(TestCase):
    def setUp(self):
        self.p = build_people("ctr")
        self.pending = make_request(self.p.e1, start=date(2026, 12, 14), end=date(2026, 12, 15))
        self.approved = make_request(
            self.p.e1, start=date(2026, 12, 21), end=date(2026, 12, 22),
            status=LeaveRequest.Status.APPROVED, decided_by=self.p.m1,
        )

    def assert_conforms(self, response):
        operation_id, status = getattr(self, self._testMethodName).covers
        self.assertEqual(response.status_code, status, getattr(response, "data", None))
        self.assertEqual(response_errors(operation_id, response), [])
        return response


class LoginContractTests(ContractTestCase):
    def credentials(self):
        return {"username": self.p.e1.username, "password": TEST_PASSWORD}

    @covers("login", 200)
    def test_login_200(self):
        """Contract login 200: token and user object."""
        self.assert_conforms(APIClient().post(LOGIN_URL, self.credentials(), format="json"))

    @covers("login", 400)
    def test_login_400_credentials(self):
        """Contract login 400: wrong password."""
        self.assert_conforms(APIClient().post(LOGIN_URL, {**self.credentials(), "password": "wrong"}, format="json"))

    @covers("login", 400)
    def test_login_400_malformed_json(self):
        """Contract login 400: malformed JSON."""
        self.assert_conforms(APIClient().post(LOGIN_URL, "{", content_type="application/json"))

    @covers("login", 401)
    def test_login_401_invalid_authorization_header(self):
        """Contract login 401: an invalid token header is refused even with valid credentials."""
        self.assert_conforms(invalid_token_client().post(LOGIN_URL, self.credentials(), format="json"))

    @covers("login", 415)
    def test_login_415(self):
        """Contract login 415: text/plain body."""
        self.assert_conforms(APIClient().post(LOGIN_URL, "x", content_type="text/plain"))


class ReadContractTests(ContractTestCase):
    @covers("me", 200)
    def test_me_200(self):
        """Contract me 200: profile with a team."""
        self.assert_conforms(token_client(self.p.e1).get("/api/me/"))

    @covers("me", 200)
    def test_me_200_without_team(self):
        """Contract me 200: team is null for a user without a team."""
        response = self.assert_conforms(token_client(self.p.teamless_manager).get("/api/me/"))
        self.assertIsNone(response.json()["team"])

    @covers("me", 401)
    def test_me_401(self):
        """Contract me 401: no token."""
        self.assert_conforms(APIClient().get("/api/me/"))

    @covers("listRequests", 200)
    def test_list_200(self):
        """Contract listRequests 200: pending and approved rows."""
        response = self.assert_conforms(token_client(self.p.m1).get(REQUESTS_URL))
        self.assertEqual({r["status"] for r in response.json()}, {"pending", "approved"})

    @covers("listRequests", 401)
    def test_list_401(self):
        """Contract listRequests 401: invalid token."""
        self.assert_conforms(invalid_token_client().get(REQUESTS_URL))

    @covers("dashboard", 200)
    def test_dashboard_200(self):
        """Contract dashboard 200: six visible requests, at most five recent."""
        for day in (7, 8, 9, 10):
            make_request(self.p.e2, start=date(2026, 12, day), end=date(2026, 12, day))
        response = self.assert_conforms(token_client(self.p.m1).get("/api/dashboard/"))
        self.assertEqual((response.json()["counts"]["total"], len(response.json()["recent"])), (6, 5))

    @covers("dashboard", 401)
    def test_dashboard_401(self):
        """Contract dashboard 401: no token."""
        self.assert_conforms(APIClient().get("/api/dashboard/"))

    @covers("team", 200)
    def test_team_200(self):
        """Contract team 200: members with and without an upcoming leave, and without a balance.

        The approved leave lies far in the future, so it stays upcoming.
        """
        make_request(self.p.e2, start=date(2099, 12, 7), end=date(2099, 12, 8),
                     status=LeaveRequest.Status.APPROVED, decided_by=self.p.m1)
        add_member("ctr", "nobal", User.Role.EMPLOYEE, self.p.team_a, allowance=None)
        response = self.assert_conforms(token_client(self.p.e1).get("/api/team/"))
        upcoming = {m["username"]: m["next_leave"] for m in response.json()}
        self.assertEqual(upcoming["ctr_e2"], {"start_date": "2099-12-07", "end_date": "2099-12-08"})
        self.assertIsNone(upcoming["ctr_nobal"])

    @covers("team", 200)
    def test_team_200_without_team(self):
        """Contract team 200: empty list for a caller without a team."""
        response = self.assert_conforms(token_client(self.p.teamless_manager).get("/api/team/"))
        self.assertEqual(response.json(), [])

    @covers("team", 401)
    def test_team_401(self):
        """Contract team 401: no token."""
        self.assert_conforms(APIClient().get("/api/team/"))


class SubmitContractTests(ContractTestCase):
    def submit(self, body, **kwargs):
        return token_client(self.p.e1).post(REQUESTS_URL, body, **(kwargs or {"format": "json"}))

    @covers("submitRequest", 201)
    def test_submit_201(self):
        """Contract submitRequest 201: created LeaveRequest."""
        self.assert_conforms(self.submit(payload()))

    @covers("submitRequest", 400)
    def test_submit_400_fields(self):
        """Contract submitRequest 400: several field errors."""
        self.assert_conforms(self.submit({"leave_type": "none", "note": None}))

    @covers("submitRequest", 400)
    def test_submit_400_end_before_start(self):
        """Contract submitRequest 400: end_date error (BR-01)."""
        self.assert_conforms(self.submit(payload("2026-12-08", "2026-12-07")))

    @covers("submitRequest", 400)
    def test_submit_400_overlap(self):
        """Contract submitRequest 400: non_field_errors (BR-02)."""
        self.assert_conforms(self.submit(payload("2026-12-14", "2026-12-14")))

    @covers("submitRequest", 400)
    def test_submit_400_balance(self):
        """Contract submitRequest 400: non_field_errors (BR-03)."""
        self.assert_conforms(self.submit(payload("2027-01-04", "2027-01-29")))

    @covers("submitRequest", 400)
    def test_submit_400_malformed_json(self):
        """Contract submitRequest 400: malformed JSON gives detail, not field errors."""
        response = self.assert_conforms(self.submit("{", content_type="application/json"))
        self.assertEqual(set(response.json()), {"detail"})

    @covers("submitRequest", 400)
    def test_submit_400_body_not_object(self):
        """Contract submitRequest 400: a JSON list body is refused."""
        self.assert_conforms(self.submit("[]", content_type="application/json"))

    @covers("submitRequest", 401)
    def test_submit_401(self):
        """Contract submitRequest 401: no token."""
        self.assert_conforms(APIClient().post(REQUESTS_URL, payload(), format="json"))

    @covers("submitRequest", 415)
    def test_submit_415(self):
        """Contract submitRequest 415: text/plain body."""
        self.assert_conforms(self.submit("x", content_type="text/plain"))


class DecideContractTests(ContractTestCase):
    def decide(self, actor, request_id, value="approved"):
        return token_client(actor).post(decision_url(request_id), {"status": value}, format="json")

    @covers("decideRequest", 200)
    def test_decide_200_approved(self):
        """Contract decideRequest 200: approved LeaveRequest."""
        self.assert_conforms(self.decide(self.p.m1, self.pending.pk))

    @covers("decideRequest", 200)
    def test_decide_200_rejected(self):
        """Contract decideRequest 200: rejected LeaveRequest."""
        self.assert_conforms(self.decide(self.p.m1, self.pending.pk, "rejected"))

    @covers("decideRequest", 400)
    def test_decide_400_value(self):
        """Contract decideRequest 400: invalid decision value."""
        self.assert_conforms(self.decide(self.p.m1, self.pending.pk, "pending"))

    @covers("decideRequest", 400)
    def test_decide_400_malformed_json(self):
        """Contract decideRequest 400: malformed JSON."""
        self.assert_conforms(token_client(self.p.m1).post(
            decision_url(self.pending.pk), "{", content_type="application/json"))

    @covers("decideRequest", 401)
    def test_decide_401(self):
        """Contract decideRequest 401: no token."""
        self.assert_conforms(APIClient().post(decision_url(self.pending.pk), {"status": "approved"}, format="json"))

    @covers("decideRequest", 403)
    def test_decide_403_role(self):
        """Contract decideRequest 403: employee."""
        self.assert_conforms(self.decide(self.p.e2, self.pending.pk))

    @covers("decideRequest", 403)
    def test_decide_403_self(self):
        """Contract decideRequest 403: manager's own request."""
        own = make_request(self.p.m1, start=date(2026, 12, 7), end=date(2026, 12, 8))
        self.assert_conforms(self.decide(self.p.m1, own.pk))

    @covers("decideRequest", 404)
    def test_decide_404_json(self):
        """Contract decideRequest 404: request of another team (JSON)."""
        self.assert_conforms(self.decide(self.p.m2, self.pending.pk))

    @covers("decideRequest", 404)
    def test_decide_404_html(self):
        """Contract decideRequest 404: a non-numeric id does not match the route (HTML)."""
        response = self.assert_conforms(self.decide(self.p.m1, "abc"))
        self.assertTrue(response["Content-Type"].startswith("text/html"))

    @covers("decideRequest", 409)
    def test_decide_409(self):
        """Contract decideRequest 409: already decided."""
        self.assert_conforms(self.decide(self.p.m1, self.approved.pk))

    @covers("decideRequest", 415)
    def test_decide_415(self):
        """Contract decideRequest 415: text/plain body."""
        self.assert_conforms(token_client(self.p.m1).post(
            decision_url(self.pending.pk), "x", content_type="text/plain"))


class KnownDeviationCharacterizationTests(ContractTestCase):
    """Baseline defects: 500 responses that the contract does not document (x-known-deviations).

    CHARACTERIZATION only. When the application is fixed these tests must be
    replaced by contract tests expecting 400 (or, for the date, 400 or 201).
    """

    def assert_undocumented_500(self, operation_id, client, url, body, **kwargs):
        before = all_rows()
        client.raise_request_exception = False
        with self.assertLogs("django.request", level="ERROR"):
            response = client.post(url, body, **kwargs)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_errors(operation_id, response), [f"{operation_id}: undocumented status 500"])
        self.assertEqual(all_rows(), before)  # nothing was written

    def test_login_non_object_json_characterization(self):
        """Deviation: login with a JSON list body → 500 (contract: 400)."""
        self.assert_undocumented_500("login", APIClient(), LOGIN_URL, "[]", content_type="application/json")

    def test_decide_non_object_json_characterization(self):
        """Deviation: W2 with a JSON list body → 500 (contract: 400); the request stays pending."""
        self.assert_undocumented_500(
            "decideRequest", token_client(self.p.m1), decision_url(self.pending.pk), "[]", content_type="application/json")

    def test_submit_maximum_date_characterization(self):
        """Deviation: W1 with end_date 9999-12-31 → 500 (date overflow in business_days); no row."""
        self.assert_undocumented_500(
            "submitRequest", token_client(self.p.e1), REQUESTS_URL, payload("9999-12-30", "9999-12-31"), format="json")


class ContractIntegrityTests(SimpleTestCase):
    def test_every_documented_response_is_exercised(self):
        """Every documented (operation, status) has a contract test, and no test names an undocumented one."""
        documented = {
            (name, int(code)) for name, op in CONTRACT["operations"].items() for code in op["responses"]
        }
        suites = (LoginContractTests, ReadContractTests, SubmitContractTests, DecideContractTests)
        exercised = {getattr(suite, n).covers for suite in suites for n in dir(suite) if n.startswith("test_")}
        self.assertEqual(exercised, documented)

    def test_generated_artifacts_match_the_current_spec(self):
        """The exported contract and the generated tests come from the spec as it is now (else: regenerate)."""
        sha = hashlib.sha256(SPEC_PATH.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        self.assertEqual({CONTRACT["spec_sha256"], test_generated_api.SPEC_SHA256}, {sha})

    def test_validator_detects_violations(self):
        """The validator reports each kind of violation (a validator that accepts everything proves nothing)."""
        schema = {
            "type": "object", "required": ["id", "kind"],
            "properties": {
                "id": {"type": "integer", "minimum": 0},
                "kind": {"type": "string", "enum": ["a", "b"], "maxLength": 1},
                "day": {"type": "string", "format": "date"},
                "note": {"type": "string", "nullable": True},
                "list": {"type": "array", "maxItems": 1, "items": {"type": "integer"}},
            },
        }
        good = {"id": 1, "kind": "a", "day": "2026-12-07", "note": None, "list": [1]}
        self.assertEqual(errors(good, schema), [])
        for change, expected in (
            ({"id": "1"}, "$.id: expected integer, got str"),
            ({"id": True}, "$.id: expected integer, got bool"),
            ({"id": -1}, "$.id: below 0"),
            ({"id": None}, "$.id: null is not allowed"),
            ({"kind": "c"}, "$.kind: 'c' not in enum"),
            ({"day": "07/12/2026"}, "$.day: not a date"),
            ({"list": [1, 2]}, "$.list: more than 1 items"),
            ({"list": ["x"]}, "$.list[0]: expected integer, got str"),
            ({"extra": 1}, "$.extra: undocumented property"),
        ):
            with self.subTest(change=change):
                self.assertEqual(errors({**good, **change}, schema), [expected])
        self.assertEqual(errors({"id": 1}, schema), ["$.kind: missing"])
        one_of = {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        self.assertEqual((errors("x", one_of), len(errors([], one_of))), ([], 1))
        with self.assertRaises(NotImplementedError):
            errors("x", {"type": "string", "pattern": "a"})
