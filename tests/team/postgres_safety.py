"""Fail-closed checks for the disposable PostgreSQL profile (sqe-postgres-v1).

Used only by scripts/sqe/run_concurrency.py, which starts its own throwaway
container. Accepted: one PostgreSQL alias on 127.0.0.1 whose database name starts
with sqe_disposable_ and whose live server reports the random cluster_name that
the harness gave its container. Any other server, including the project's compose
database, is refused before a test database is created.
"""

import os
import re

PROFILE = "sqe-postgres-v1"
NAME = re.compile(r"(test_)?sqe_disposable_[0-9a-f]{12}")
CLUSTER = re.compile(r"leaveflow-sqe-[0-9a-f]{12}")


def validate_database_config(config, profile, cluster, *, active=False):
    """Pure check: a rejected configuration never opens a connection."""
    name = NAME.fullmatch(str(config.get("NAME", "")))
    if (
        profile != PROFILE
        or config.get("ENGINE") != "django.db.backends.postgresql"
        or config.get("HOST") != "127.0.0.1"
        or not str(config.get("PORT", "")).isdigit()
        or not name
        or (active and not name.group(1))
        or config.get("TEST", {}).get("MIRROR")
        or not CLUSTER.fullmatch(cluster or "")
    ):
        raise RuntimeError("Refusing database: the sqe-postgres-v1 profile is required.")


def assert_disposable_postgres(*, active=False):
    from django.conf import settings
    from django.db import connections

    if set(settings.DATABASES) != {"default"} or settings.REDIS_URL:
        raise RuntimeError("Refusing additional database aliases or Redis publication.")
    connection = connections["default"]
    cluster = os.environ.get("SQE_PG_CLUSTER", "")
    validate_database_config(connection.settings_dict, settings.TEAM_TEST_PROFILE, cluster, active=active)
    with connection.cursor() as cursor:
        cursor.execute("SHOW cluster_name")
        if cursor.fetchone()[0] != cluster:
            raise RuntimeError("Refusing PostgreSQL server: not the harness container.")
