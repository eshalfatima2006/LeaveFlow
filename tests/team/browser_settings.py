"""Browser-harness profile: a harness-created temporary SQLite file, never backend/db.sqlite3."""

import os

from config.settings import *  # noqa: F403 - retain the application's configuration

from tests.team.browser_safety import NOTIFICATION_REDIS, PROFILE, database_path, run_dir_from_environment

TEAM_TEST_PROFILE = PROFILE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # Fails closed at import time unless the harness run directory is valid.
        "NAME": str(database_path(run_dir_from_environment())),
        "OPTIONS": {"timeout": 30},
    }
}
REDIS_URL = ""
if os.environ.get("SQE_ENABLE_NOTIFICATIONS") == "1":
    REDIS_URL = NOTIFICATION_REDIS
    MIDDLEWARE = [*MIDDLEWARE, "tests.team.notification_fault.NotificationPublishFault"]
DEBUG = True
SECURE_SSL_REDIRECT = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
_ORIGIN = os.environ.get("SQE_BROWSER_ORIGIN", "")
CORS_ALLOWED_ORIGINS = [_ORIGIN] if _ORIGIN else []
# Disposable synthetic accounts only; a fast hasher keeps per-test fixtures quick.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
