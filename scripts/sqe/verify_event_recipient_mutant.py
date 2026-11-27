"""Verify that the privileged-requester assertion kills historical mutant E-10."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("backend/leave/events.py")
BEFORE = ".exclude(pk=item.employee_id)"
AFTER = ".exclude(pk=None)"
TEST = "tests/team/unit/test_events.py::LeaveEventTests::test_requested_event_excludes_manager_and_admin_requesters"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, "-m", "pytest", "-q", TEST]
    with tempfile.TemporaryDirectory(prefix="leaveflow-e10-") as temp:
        target = Path(temp)
        shutil.copytree(ROOT / "backend", target / "backend", ignore=shutil.ignore_patterns(
            "__pycache__", "db.sqlite3", "db.sqlite3-*", ".venv*"))
        shutil.copytree(ROOT / "tests", target / "tests", ignore=shutil.ignore_patterns(
            "__pycache__", ".pytest_cache"))
        shutil.copy2(ROOT / "pytest.ini", target / "pytest.ini")

        def run(name):
            result = subprocess.run(command, cwd=target, capture_output=True, text=True, timeout=90)
            (args.output / f"{name}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
            return result

        baseline = run("baseline")
        if baseline.returncode:
            raise RuntimeError("Baseline test failed before mutation")
        path = target / SOURCE
        original = path.read_text(encoding="utf-8")
        if original.count(BEFORE) != 1:
            raise RuntimeError("E-10 source expression was not found exactly once")
        path.write_text(original.replace(BEFORE, AFTER), encoding="utf-8")
        mutant = run("mutant-e10")
        mutant_log = (args.output / "mutant-e10.log").read_text(encoding="utf-8")
        killed = mutant.returncode == 1 and "FAILED" in mutant_log and "AssertionError" in mutant_log

    evidence = {
        "mutant": "leave.events.x_build_leave_event__mutmut_10",
        "source": SOURCE.as_posix(),
        "before": BEFORE,
        "after": AFTER,
        "test": TEST,
        "baseline_exit_code": baseline.returncode,
        "mutant_exit_code": mutant.returncode,
        "killed_by_assertion": killed,
    }
    (args.output / "result.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence))
    return 0 if killed else 1


if __name__ == "__main__":
    raise SystemExit(main())
