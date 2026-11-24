"""Reusable A2.1 API helpers: real token clients, payloads and persisted-state readback.

Helpers never print or snapshot token values. Call them only inside Django
TestCase methods/setUpTestData, after the guarded runner selected the memory DB.
"""

from contextlib import contextmanager

from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from leave.models import LeaveBalance, LeaveRequest, User
from tests.team.fixtures.leave_data import TEST_PASSWORD
from tests.team.safety import assert_disposable_database

REQUESTS_URL = "/api/requests/"
LOGIN_URL = "/api/auth/login/"

# Exact LeaveRequestSerializer output contract at the tested baseline.
REQUEST_FIELDS = {
    "id", "employee", "leave_type", "leave_type_label", "start_date", "end_date",
    "note", "status", "status_label", "business_days", "created_at",
}
USER_FIELDS = {"id", "username", "display_name", "email", "role", "team"}


@contextmanager
def rolled_back():
    """Run one table row in its own savepoint and always roll it back.

    Lets mutually overlapping submission rows each start from the same state.
    """
    assert_disposable_database(active=True)
    with transaction.atomic():
        yield
        transaction.set_rollback(True)


def decision_url(request_id):
    return f"/api/requests/{request_id}/decision/"


def token_client(user):
    """APIClient carrying the user's real DRF token (TokenAuthentication path)."""
    assert_disposable_database(active=True)
    token, _ = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return client


def payload(start="2026-12-07", end="2026-12-08", **extra):
    """Valid W1 body by default; pass ``omit=(...)`` to drop keys entirely."""
    omit = extra.pop("omit", ())
    body = {"start_date": start, "end_date": end, "leave_type": "vacation", "note": "Synthetic A2.1"}
    body.update(extra)
    for key in omit:
        body.pop(key, None)
    return body


def add_member(prefix, key, role, team, *, allowance=10):
    """Extra synthetic account (e.g. a Team B employee) beside build_people()."""
    assert_disposable_database(active=True)
    user = User.objects.create(
        username=f"{prefix}_{key}", password=make_password(TEST_PASSWORD),
        first_name="Synthetic", last_name=key, email=f"{prefix}_{key}@example.invalid",
        role=role, team=team,
    )
    if allowance is not None:
        LeaveBalance.objects.create(user=user, allowance=allowance, year=2026)
    return user


def row_state(request_id):
    """Every persisted LeaveRequest column relevant to W1/W2 oracles."""
    return LeaveRequest.objects.filter(pk=request_id).values(
        "id", "employee_id", "leave_type", "start_date", "end_date", "note",
        "status", "decided_by_id", "decided_at", "created_at",
    ).get()


def all_rows():
    return [row_state(pk) for pk in LeaveRequest.objects.order_by("pk").values_list("pk", flat=True)]


def balance_view(user):
    """(allowance, used, available) derived exactly as the application does."""
    balance = LeaveBalance.objects.get(user=user)
    return balance.allowance, balance.approved_days, balance.available_days
