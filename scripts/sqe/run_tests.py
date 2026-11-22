#!/usr/bin/env python3
"""One root entry point for isolated team/upstream checks and repeatability.

No database target overrides, keepdb, reset, seed or external-service options.
Evidence directories must be new, so earlier results cannot be overwritten.
"""

import argparse
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import shlex
import sqlite3
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
sys.dont_write_bytecode = True


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def development_fingerprint():
    """Read bytes only; do not open SQLite or connect to any configured database."""
    result = {}
    for suffix in ("", "-wal", "-shm", "-journal"):
        path = ROOT / "backend" / ("db.sqlite3" + suffix)
        result[path.name] = {
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else None,
            "sha256": digest(path) if path.exists() else None,
        }
    return result


def git_read(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def environment():
    source_paths = []
    for directory in ("backend", "tests", "scripts/sqe"):
        source_paths.extend((ROOT / directory).rglob("*.py"))
    source_paths.append(ROOT / "requirements.txt")
    return {
        "git_sha": git_read("rev-parse", "HEAD"),
        "git_branch": git_read("branch", "--show-current"),
        "git_status": git_read("status", "--short", "--untracked-files=all").splitlines(),
        "tracked_diff_sha256": hashlib.sha256(
            subprocess.check_output(["git", "diff", "HEAD"], cwd=ROOT)
        ).hexdigest(),
        "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sorted(source_paths)},
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "packages": {name: metadata.version(name) for name in (
            "Django", "djangorestframework", "django-cors-headers", "redis", "psycopg",
        )},
        "runner": "Django DiscoverRunner + unittest; version is the Django/Python version above",
        "sqlite_version": sqlite3.sqlite_version,
        "database_profile": "sqe-memory-v1",
        "external_database_environment_ignored": bool(os.environ.get("POSTGRES_DB")),
        "redis_environment_ignored": bool(os.environ.get("REDIS_URL")),
    }


class Tee:
    def __init__(self, original, saved):
        self.original, self.saved = original, saved

    def write(self, text):
        self.original.write(text)
        self.saved.write(text)
        return len(text)

    def flush(self):
        self.original.flush()
        self.saved.flush()

    def isatty(self):
        return False


def run_django(action, labels, verbosity, report):
    # Override the module *before* Django initializes. config.settings is imported
    # by our profile, but its database/Redis environment choices are replaced.
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.team.settings"
    import django
    from tests.team.safety import assert_disposable_database

    assert_disposable_database()
    django.setup()
    if action == "check":
        from django.core.management import call_command
        call_command("check")
        report["system_check"] = "passed"
        return 0
    from tests.team.runner import SafeDiscoverRunner

    runner = SafeDiscoverRunner(verbosity=verbosity, interactive=False, keepdb=False)
    failed = runner.run_tests(labels)
    result = runner.last_result
    if result is None or result.testsRun == 0:
        raise RuntimeError("No tests executed; an empty area is not a passing suite.")
    report["counts"] = {
        "executed": result.testsRun,
        "failed": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "expected_failures": len(result.expectedFailures),
        "unexpected_successes": len(result.unexpectedSuccesses),
        "passed": result.testsRun - len(result.failures) - len(result.errors)
        - len(result.skipped) - len(result.expectedFailures) - len(result.unexpectedSuccesses),
    }
    report["cases"] = result.cases
    report["database"] = runner.database_observations
    report["snapshots"] = runner.snapshots
    # Expected failures do not silently green a desired-rule regression.
    return int(bool(failed or result.expectedFailures or result.skipped))


def repeatability(directory, report):
    if directory is None:
        raise ValueError("repeatability requires --evidence-dir for independent run evidence.")
    children = []
    for number in (1, 2):
        target = directory / f"run-{number}"
        command = [sys.executable, str(Path(__file__).resolve()), "team", "--evidence-dir", str(target)]
        result = subprocess.run(command, cwd=ROOT, check=False)
        children.append({"command": shlex.join(command), "process_exit_code": result.returncode})
        report["independent_runs"] = children
        if result.returncode != 0:
            return 1
    runs = [json.loads((directory / f"run-{n}" / "result.json").read_text()) for n in (1, 2)]
    snapshots = [run["snapshots"] for run in runs]
    reference_equal = snapshots[0]["reference"] == snapshots[1]["reference"]
    rollback_verified = [
        s["isolation_before"] == s["isolation_next_test"]
        and s["isolation_mutated"] != s["isolation_before"]
        for s in snapshots
    ]
    unchanged = all(run["development_database_unchanged"] for run in runs)
    report["comparison"] = {
        "reference_equal": reference_equal,
        "reference_sha256": [hashlib.sha256(json.dumps(s["reference"], sort_keys=True).encode()).hexdigest() for s in snapshots],
        "mutation_then_independent_test_rollback": rollback_verified,
        "both_development_database_checks_unchanged": unchanged,
        "normalization": "user/team logical keys, explicit dates/content/status/totals; no PKs, timestamps, passwords or token values",
    }
    passed = reference_equal and all(rollback_verified) and unchanged
    print("Independent fixture comparison:", "PASS" if passed else "FAIL")
    return int(not passed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", default="team", choices=("check", "team", "upstream", "repeatability"))
    parser.add_argument("labels", nargs="*", help="Dotted labels inside tests.team (or leave.tests for upstream).")
    parser.add_argument("--evidence-dir", type=Path, help="Create a NEW directory for logs/JSON; never overwrite.")
    parser.add_argument("--verbosity", type=int, choices=(1, 2), default=2)
    args = parser.parse_args(argv)
    prefix = "leave.tests" if args.action == "upstream" else "tests.team"
    if args.labels and args.action in {"check", "repeatability"}:
        parser.error("This action does not accept test labels.")
    if any(label != prefix and not label.startswith(prefix + ".") for label in args.labels):
        parser.error(f"Only dotted labels within {prefix} are accepted.")
    directory = args.evidence_dir.resolve() if args.evidence_dir else None
    if directory is not None:
        directory.mkdir(parents=True, exist_ok=False)
    before = development_fingerprint()
    report = {
        "started_at_utc": utc_now(), "action": args.action,
        "command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
        "development_database_before": before,
    }
    started = time.monotonic()
    exit_code = 2
    with ExitStack() as stack:
        if directory is not None:
            out = stack.enter_context((directory / "stdout.log").open("x"))
            err = stack.enter_context((directory / "stderr.log").open("x"))
            stack.enter_context(redirect_stdout(Tee(sys.stdout, out)))
            stack.enter_context(redirect_stderr(Tee(sys.stderr, err)))
        try:
            report["environment"] = environment()
            if args.action == "repeatability":
                exit_code = repeatability(directory, report)
            else:
                exit_code = run_django(args.action, args.labels or [prefix], args.verbosity, report)
        except Exception as exc:
            report["harness_error_type"] = type(exc).__name__
            traceback.print_exc()
        finally:
            after = development_fingerprint()
            report["development_database_after"] = after
            report["development_database_unchanged"] = before == after
            if before != after:
                print("Development database fingerprint changed; refusing a passing result.", file=sys.stderr)
                exit_code = 2
            report.update(finished_at_utc=utc_now(), elapsed_seconds=round(time.monotonic() - started, 6), process_exit_code=exit_code)
            if directory is not None:
                (directory / "result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
            print(f"{args.action}: process exit code {exit_code}; development database unchanged={before == after}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
