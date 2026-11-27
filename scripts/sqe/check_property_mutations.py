"""Test property business rules that mutmut 3.8 excludes from trampolines.

Each mutation is made only inside a disposable source copy. The baseline must
pass first; a mutant counts as killed only by a failed test assertion, not an
import error, harness crash or timeout. Results are separate from mutmut's score.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    "weekend-counted-as-business-day": ("current.weekday() < 5", "current.weekday() <= 5"),
    "exclusive-final-date": ("while current <= self.end_date:", "while current < self.end_date:"),
}


def main():
    output = ROOT / "property-mutation-results"
    output.mkdir(exist_ok=False)
    results = []
    with tempfile.TemporaryDirectory(prefix="leaveflow-property-") as temp:
        target = Path(temp) / "source"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(
            ".git", ".venv*", "mutants", ".pytest_cache", "__pycache__", "node_modules",
            "docs", "api-results", "property-mutation-results", "coverage.*", "mutmut-run.log"))
        command = [sys.executable, "-m", "pytest", "-q", "tests/team/unit/test_critical_module.py::BusinessDaysAndCleaningTests::test_business_days_covers_weekend_weekday_and_mixed_interval"]
        env = {**os.environ, "PYTHONUTF8": "1"}
        baseline = subprocess.run(command, cwd=target, env=env, capture_output=True, text=True, timeout=60)
        (output / "baseline.log").write_text(baseline.stdout + baseline.stderr, encoding="utf-8")
        if baseline.returncode:
            raise RuntimeError("Property mutation baseline failed")
        models = target / "backend/leave/models.py"
        original = models.read_text(encoding="utf-8")
        for name, (before, after) in CASES.items():
            if original.count(before) != 1:
                raise RuntimeError(f"Ambiguous rule location: {name}")
            models.write_text(original.replace(before, after), encoding="utf-8")
            run = subprocess.run(command, cwd=target, env=env, capture_output=True, text=True, timeout=60)
            log = run.stdout + run.stderr
            (output / (name + ".log")).write_text(log, encoding="utf-8")
            killed = run.returncode == 1 and "FAILED" in log and "AssertionError" in log and "ERROR collecting" not in log
            results.append({"operator": name, "before": before, "after": after, "exit_code": run.returncode, "killed": killed})
            models.write_text(original, encoding="utf-8")
    (output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results))
    return 0 if all(row["killed"] for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
