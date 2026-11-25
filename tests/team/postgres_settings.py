"""Disposable PostgreSQL profile; see postgres_safety. Selected only by run_concurrency.py."""

import os

from tests.team.postgres_safety import PROFILE
from tests.team.settings import *  # noqa: F403 - the core profile with another database

TEAM_TEST_PROFILE = PROFILE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["SQE_PG_NAME"],
        "USER": "sqe",
        "PASSWORD": os.environ["SQE_PG_PASSWORD"],
        "HOST": "127.0.0.1",
        "PORT": os.environ["SQE_PG_PORT"],
        # Bounded waits: a blocked statement fails instead of hanging the run.
        "OPTIONS": {"options": "-c lock_timeout=15000 -c statement_timeout=20000"},
    }
}
