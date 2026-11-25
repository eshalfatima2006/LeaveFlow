"""Core test profile: never select a file database or an external service."""

from config.settings import *  # noqa: F403 - retain the application's configuration

TEAM_TEST_PROFILE = "sqe-memory-v1"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {"NAME": ":memory:"},
    }
}
REDIS_URL = ""
DEBUG = True
SECURE_SSL_REDIRECT = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
TEST_RUNNER = "tests.team.runner.SafeDiscoverRunner"
# Disposable synthetic accounts only; the browser profile uses the same fast hasher.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
