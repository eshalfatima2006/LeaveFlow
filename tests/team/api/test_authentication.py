"""A2.1 Group A: authentication, identity binding and refusal of unauthorized access.

Case IDs expand the planned RTM families (API-W1-001, API-W2-001, API-W2-002).
Token values are compared only by equality; they are never printed or stored.
"""

from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from leave.models import LeaveRequest
from tests.team.api.support import (
    LOGIN_URL, REQUESTS_URL, USER_FIELDS, all_rows, decision_url, payload, token_client,
)
from tests.team.fixtures.leave_data import TEST_PASSWORD, build_reference_fixture, make_request


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fx = build_reference_fixture("auth")
        cls.people = cls.fx.people

    def test_valid_login_returns_token_bound_to_that_user(self):
        """API-W1-001.01; FR-W1-01; BR-04: valid credentials yield the caller's own token."""
        client = APIClient()
        self.assertEqual(Token.objects.count(), 0)
        response = client.post(LOGIN_URL, {"username": "auth_e1", "password": TEST_PASSWORD}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {"token", "user"})
        self.assertEqual(set(response.data["user"]), USER_FIELDS)
        self.assertEqual(response.data["user"]["id"], self.people.e1.pk)
        self.assertEqual(response.data["user"]["role"], "employee")
        self.assertEqual(response.data["user"]["team"], "auth-A")
        stored = Token.objects.get(user=self.people.e1)
        self.assertTrue(response.data["token"] == stored.key, "returned token is not the stored e1 token")
        self.assertEqual(Token.objects.count(), 1)
        # Second login reuses the same token (get_or_create), not a new credential.
        again = client.post(LOGIN_URL, {"username": "auth_e1", "password": TEST_PASSWORD}, format="json")
        self.assertEqual(again.status_code, 200)
        self.assertTrue(again.data["token"] == stored.key)
        self.assertEqual(Token.objects.count(), 1)

    def test_invalid_credentials_are_refused_without_issuing_tokens(self):
        """API-W1-001.02; FR-W1-01; BR-04: wrong/unknown/missing/blank/inactive -> 400, no token."""
        inactive = self.people.e2
        inactive.is_active = False
        inactive.save(update_fields=["is_active"])
        cases = {
            "wrong password": {"username": "auth_e1", "password": "not-the-password"},
            "unknown user": {"username": "auth_nobody", "password": TEST_PASSWORD},
            "missing password": {"username": "auth_e1"},
            "missing both": {},
            "blank both": {"username": "", "password": ""},
            "inactive user": {"username": "auth_e2", "password": TEST_PASSWORD},
        }
        for label, body in cases.items():
            with self.subTest(case=label):
                response = APIClient().post(LOGIN_URL, body, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data, {"detail": "Credenziali non valide."})
                self.assertNotIn("token", response.data)
        self.assertEqual(Token.objects.count(), 0)


class UnauthenticatedAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fx = build_reference_fixture("anon")

    def test_protected_endpoints_return_401_without_credentials(self):
        """API-W1-001.03; FR-W1-01, FR-W2-01, FR-W2-02; BR-04: no token -> 401, nothing exposed or written."""
        before = all_rows()
        client = APIClient()
        cases = [
            ("get", "/api/me/", None),
            ("get", "/api/dashboard/", None),
            ("get", "/api/team/", None),
            ("get", REQUESTS_URL, None),
            ("post", REQUESTS_URL, payload("2026-12-28", "2026-12-28")),
            ("post", decision_url(self.fx.pending.pk), {"status": "approved"}),
        ]
        for method, url, body in cases:
            with self.subTest(method=method, url=url):
                response = getattr(client, method)(url, body, format="json")
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response["WWW-Authenticate"], "Token")
                self.assertEqual(set(response.data), {"detail"})
                self.assertNotIn("results", response.data)
        self.assertEqual(all_rows(), before)

    def test_malformed_and_invalid_tokens_return_401(self):
        """API-W1-001.04; FR-W1-01; BR-04: malformed header/unknown/inactive-user token -> 401, no row."""
        inactive = self.fx.people.e2
        inactive_token = Token.objects.create(user=inactive)
        inactive.is_active = False
        inactive.save(update_fields=["is_active"])
        valid_key = Token.objects.create(user=self.fx.people.e1).key
        before = all_rows()
        headers = {
            "keyword only": "Token",
            "extra token part": "Token abc def",
            "unknown key": "Token " + "0" * 40,
            "inactive user": "Token " + inactive_token.key,
        }
        for label, header in headers.items():
            with self.subTest(case=label):
                client = APIClient()
                client.credentials(HTTP_AUTHORIZATION=header)
                response = client.post(REQUESTS_URL, payload("2026-12-28", "2026-12-28"), format="json")
                self.assertEqual(response.status_code, 401)
                self.assertEqual(set(response.data), {"detail"})
        # A different scheme is not parsed by TokenAuthentication: treated as anonymous -> 401.
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + valid_key)
        self.assertEqual(client.get("/api/me/").status_code, 401)
        self.assertEqual(all_rows(), before)


class IdentityAndOwnershipTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fx = build_reference_fixture("ident")
        cls.p = cls.fx.people
        cls.e2_request = make_request(cls.p.e2, start=cls.fx.pending.start_date, end=cls.fx.pending.end_date)

    def test_token_identity_is_the_authenticated_user_only(self):
        """API-W1-001.05; FR-W1-01, FR-W2-01; BR-04: /me and lists reflect only the token's user."""
        for user in (self.p.e1, self.p.e2, self.p.m1):
            with self.subTest(user=user.username):
                me = token_client(user).get("/api/me/")
                self.assertEqual(me.status_code, 200)
                self.assertEqual(me.data["id"], user.pk)
                self.assertEqual(me.data["username"], user.username)
                self.assertEqual(me.data["role"], user.role)
        e1_ids = {r["id"] for r in token_client(self.p.e1).get(REQUESTS_URL).data}
        self.assertEqual(e1_ids, {self.fx.pending.pk, self.fx.approved.pk, self.fx.rejected.pk})
        self.assertNotIn(self.e2_request.pk, e1_ids)
        e2_list = token_client(self.p.e2).get(REQUESTS_URL).data
        self.assertEqual([r["id"] for r in e2_list], [self.e2_request.pk])
        self.assertEqual(e2_list[0]["employee"]["id"], self.p.e2.pk)

    def test_employee_cannot_decide_or_reach_another_users_request(self):
        """API-W2-002.06; FR-W2-02; BR-04/05: employee decision on a teammate's request -> 403, GET 405, unchanged."""
        before = all_rows()
        client = token_client(self.p.e1)
        for status in ("approved", "rejected"):
            with self.subTest(status=status):
                response = client.post(decision_url(self.e2_request.pk), {"status": status}, format="json")
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.data, {"detail": "Operazione non consentita."})
                self.assertNotIn("employee", response.data)
        # Wrong method on the decision route, authenticated: 405 and still no change.
        self.assertEqual(client.get(decision_url(self.e2_request.pk)).status_code, 405)
        self.assertEqual(all_rows(), before)
        self.assertEqual(LeaveRequest.objects.get(pk=self.e2_request.pk).status, "pending")
