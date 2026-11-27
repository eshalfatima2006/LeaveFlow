"""Pytest collection rules for the CI quality gate.

These modules are excluded from the default Django runner by ``load_tests``,
which pytest ignores. Keep this list in step with those hooks:

- ``test_generated_api_v2/v3/v4.py`` are spec-change demonstrations, built to
  fail against the unchanged application (see docs/sqe/openapi/README.md).
- ``test_concurrency.py`` runs only on the disposable PostgreSQL harness
  (``scripts/sqe/run_concurrency.py``) and refuses any other database.
"""

collect_ignore = [
    "team/generated/test_generated_api_v2.py",
    "team/generated/test_generated_api_v3.py",
    "team/generated/test_generated_api_v4.py",
    "team/concurrency/test_concurrency.py",
]
