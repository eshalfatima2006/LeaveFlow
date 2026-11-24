"""Guard Django setup/teardown and retain actual unittest outcomes."""

from contextvars import ContextVar
from copy import deepcopy
from unittest import TextTestResult

from django.db import connections
from django.test.runner import DiscoverRunner

from .safety import assert_disposable_database

_snapshots = ContextVar("foundation_snapshots", default=None)


def record_snapshot(name, value):
    """Collect logical evidence without writing files or sharing state between runs."""
    target = _snapshots.get()
    if target is not None:
        if name in target:
            raise RuntimeError(f"Duplicate evidence snapshot: {name}")
        target[name] = deepcopy(value)


class RecordingResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = []

    def record(self, test, outcome, method_id=None):
        # method_id: the owning test method, so subtest failures count once per method.
        self.cases.append({
            "id": test.id(), "description": test.shortDescription(), "outcome": outcome,
            "method_id": method_id or test.id(),
        })

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "failed")

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "error")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "skipped")

    def addSubTest(self, test, subtest, err):
        # Table-driven cases: unittest reports failed subtests outside
        # addFailure/addError, so record them explicitly to keep per-case evidence.
        super().addSubTest(test, subtest, err)
        if err is not None:
            failed = issubclass(err[0], test.failureException)
            self.record(subtest, "failed" if failed else "error", method_id=test.id())


class SafeDiscoverRunner(DiscoverRunner):
    last_result = None
    database_observations = None

    def get_resultclass(self):
        return RecordingResult

    def setup_databases(self, **kwargs):
        assert_disposable_database()
        config = super().setup_databases(**kwargs)
        if kwargs.get("aliases"):
            assert_disposable_database(active=True)
        self.database_observations = {
            "engine": connections["default"].settings_dict["ENGINE"],
            "active_name": connections["default"].settings_dict["NAME"],
            "redis_disabled": True,
        }
        return config

    def teardown_databases(self, old_config, **kwargs):
        assert_disposable_database()
        return super().teardown_databases(old_config, **kwargs)

    def run_suite(self, suite, **kwargs):
        self.snapshots = {}
        token = _snapshots.set(self.snapshots)
        try:
            self.last_result = super().run_suite(suite, **kwargs)
        finally:
            _snapshots.reset(token)
        return self.last_result
