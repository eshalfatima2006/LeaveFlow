"""Deliberate runner self-check, not a product defect or a discovered test.

Run with one NEW evidence-directory argument. The expected process exit code is1.
Only one test method is patched in this child process; source files are unchanged.
"""

import os
from pathlib import Path
import runpy
import sys
from unittest.mock import patch

root = next(p for p in Path(__file__).resolve().parents if (p / "backend/manage.py").is_file())
sys.path[:0] = [str(root), str(root / "backend")]
sys.dont_write_bytecode = True
os.environ["DJANGO_SETTINGS_MODULE"] = "tests.team.settings"
from tests.team.safety import assert_disposable_database

assert_disposable_database()
import django

django.setup()
from tests.team.foundation.test_foundation import FoundationTests


def deliberate_failure(self):
    """Deliberate non-product failure: verify both streams and process status."""
    print("A2.0 stdout propagation marker")
    print("A2.0 stderr propagation marker", file=sys.stderr)
    self.fail("A2.0 deliberate failure-propagation probe")


if len(sys.argv) != 2:
    raise SystemExit("Supply one NEW evidence-directory path.")
target = sys.argv[1]
script = root / "scripts/sqe/run_tests.py"
sys.argv = [
    str(script), "team",
    "tests.team.foundation.test_foundation.FoundationTests.test_pending_record_and_approved_only_consumption",
    "--evidence-dir", target,
]
with patch.object(FoundationTests, "test_pending_record_and_approved_only_consumption", deliberate_failure):
    runpy.run_path(str(script), run_name="__main__")
