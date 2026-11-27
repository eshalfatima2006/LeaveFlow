"""Fail closed before test database setup and before fixture ORM operations."""

from django.conf import settings
from django.db import connections

from .postgres_safety import PROFILE as POSTGRES_PROFILE, assert_disposable_postgres

PROFILE = "sqe-memory-v1"
TEST_NAME = "file:memorydb_default?mode=memory&cache=shared"


def validate_database_config(config, profile, *, active=False):
    """Accept only this named profile and Django's exact in-memory targets.

    No paths, arbitrary SQLite URIs, mirrors or external databases are supported.
    This is a pure check: even rejected configurations never open a connection.
    """
    allowed_names = {TEST_NAME} if active else {":memory:", TEST_NAME}
    test = config.get("TEST", {})
    if (
        profile != PROFILE
        or config.get("ENGINE") != "django.db.backends.sqlite3"
        or config.get("NAME") not in allowed_names
        or test.get("NAME") != ":memory:"
        or test.get("MIRROR")
    ):
        raise RuntimeError("Refusing database: the sqe-memory-v1 profile is required.")


def assert_disposable_database(*, active=False):
    if getattr(settings, "TEAM_TEST_PROFILE", None) == POSTGRES_PROFILE:
        return assert_disposable_postgres(active=active)
    if set(settings.DATABASES) != {"default"}:
        raise RuntimeError("Refusing additional database aliases.")
    if settings.REDIS_URL:
        raise RuntimeError("Core fixture tests require Redis publication disabled.")
    validate_database_config(
        connections["default"].settings_dict,
        getattr(settings, "TEAM_TEST_PROFILE", None),
        active=active,
    )
