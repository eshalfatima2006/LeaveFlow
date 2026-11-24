"""Fail-closed checks for the browser harness (profile sqe-browser-v1).

The Playwright suite needs a database shared by two processes (the live Django
server and the fixture/readback CLI), so it cannot use the in-memory A2.0
profile. The only accepted target is ``browser.sqlite3`` inside a run directory
that ``scripts/sqe/browser_harness.py init`` created directly under the system
temporary directory and marked. The development database, any path inside the
repository and any other engine are refused. These checks are pure: a rejected
configuration never opens a connection.
"""

import os
import tempfile
from pathlib import Path

PROFILE = "sqe-browser-v1"
RUN_DIR_PREFIX = "leaveflow-sqe-browser-"
MARKER = ".sqe-browser-run"
DB_NAME = "browser.sqlite3"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEVELOPMENT_DATABASE = REPO_ROOT / "backend" / "db.sqlite3"


def validate_run_dir(run_dir):
    run_dir = Path(run_dir)
    temp_root = Path(tempfile.gettempdir()).resolve()
    if run_dir.parent != temp_root or not run_dir.name.startswith(RUN_DIR_PREFIX):
        raise RuntimeError("Refusing run directory: not a harness-created temporary directory.")
    if REPO_ROOT == run_dir or REPO_ROOT in run_dir.parents:
        raise RuntimeError("Refusing run directory inside the repository.")
    if not run_dir.is_dir() or not (run_dir / MARKER).is_file():
        raise RuntimeError("Refusing run directory without the harness marker.")
    return run_dir


def run_dir_from_environment():
    raw = os.environ.get("SQE_BROWSER_RUN_DIR", "")
    if not raw or not Path(raw).is_absolute():
        raise RuntimeError("SQE_BROWSER_RUN_DIR must be an absolute harness run directory.")
    return validate_run_dir(Path(raw).resolve())


def database_path(run_dir):
    database = (Path(run_dir) / DB_NAME).resolve()
    if database.parent != Path(run_dir).resolve() or database == DEVELOPMENT_DATABASE.resolve():
        raise RuntimeError("Refusing database path outside the harness run directory.")
    return database


def validate_database_config(config, profile, run_dir):
    name = config.get("NAME")
    if (
        profile != PROFILE
        or config.get("ENGINE") != "django.db.backends.sqlite3"
        or not name
        or Path(str(name)).resolve() != database_path(run_dir)
        or config.get("TEST", {}).get("MIRROR")
    ):
        raise RuntimeError("Refusing database: the sqe-browser-v1 profile is required.")


def assert_browser_database():
    from django.conf import settings
    from django.db import connections

    if set(settings.DATABASES) != {"default"}:
        raise RuntimeError("Refusing additional database aliases.")
    if settings.REDIS_URL:
        raise RuntimeError("Browser harness requires Redis publication disabled.")
    validate_database_config(
        connections["default"].settings_dict,
        getattr(settings, "TEAM_TEST_PROFILE", None),
        run_dir_from_environment(),
    )
