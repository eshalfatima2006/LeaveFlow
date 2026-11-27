#!/usr/bin/env python3
"""Run API-INT-002 (tests.team.concurrency) on a throwaway PostgreSQL container.

    .venv/bin/python scripts/sqe/run_concurrency.py [--evidence-dir NEW_DIR] [--image postgres:17-alpine]

Starts one container with a random name, password and loopback port, data in
memory (tmpfs) and no volume; runs the tests against it; always stops exactly that
container. It never connects to any other database: tests/team/postgres_safety.py
refuses every server that does not report this run's random cluster_name.
Needs Docker. The image is the one docker-compose.yml uses and is pulled if absent.
"""

import argparse
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_tests  # noqa: E402 - reuses the team runner's fingerprint, environment and log helpers

LABEL = "tests.team.concurrency"


def docker(*args, **kwargs):
    return subprocess.run(["docker", *args], check=True, capture_output=True, text=True, **kwargs).stdout.strip()


def wait_until_ready(port, name, password):
    import psycopg

    deadline = time.monotonic() + 60
    while True:
        try:
            with psycopg.connect(host="127.0.0.1", port=port, dbname=name, user="sqe", password=password, connect_timeout=3) as c:
                return c.execute("SHOW server_version").fetchone()[0]
        except psycopg.OperationalError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)


def run_suite(report):
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.team.postgres_settings"
    import django

    django.setup()
    from tests.team.runner import SafeDiscoverRunner

    runner = SafeDiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    failed = runner.run_tests([LABEL])
    result = runner.last_result
    if result is None or result.testsRun == 0:
        raise RuntimeError("No tests executed.")
    report["counts"] = {"executed": result.testsRun, "failed": len(result.failures),
                        "errors": len(result.errors), "skipped": len(result.skipped)}
    report["cases"] = result.cases
    return int(bool(failed or result.skipped))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--evidence-dir", type=Path, help="Create a NEW directory for logs/JSON; never overwrite.")
    parser.add_argument("--image", default="postgres:17-alpine")
    args = parser.parse_args()
    directory = args.evidence_dir.resolve() if args.evidence_dir else None
    if directory is not None:
        directory.mkdir(parents=True, exist_ok=False)
    token = secrets.token_hex(6)
    name, cluster, password = f"sqe_disposable_{token}", f"leaveflow-sqe-{token}", secrets.token_urlsafe(24)
    report = {"started_at_utc": run_tests.utc_now(), "suite": LABEL, "image": args.image,
              "development_database_before": run_tests.development_fingerprint()}
    container, exit_code = None, 2
    with ExitStack() as stack:
        if directory is not None:
            out = stack.enter_context((directory / "stdout.log").open("x"))
            err = stack.enter_context((directory / "stderr.log").open("x"))
            stack.enter_context(redirect_stdout(run_tests.Tee(sys.stdout, out)))
            stack.enter_context(redirect_stderr(run_tests.Tee(sys.stderr, err)))
        try:
            report["environment"] = run_tests.environment()
            if subprocess.run(["docker", "image", "inspect", args.image], capture_output=True).returncode:
                docker("pull", args.image)
            report["image_digests"] = json.loads(docker("image", "inspect", args.image, "--format", "{{json .RepoDigests}}"))
            container = docker(
                "run", "--detach", "--rm", "--name", cluster, "--label", "leaveflow-sqe=concurrency",
                "--tmpfs", "/var/lib/postgresql/data", "--publish", "127.0.0.1::5432",
                "--env", "POSTGRES_PASSWORD", "--env", "POSTGRES_USER=sqe", "--env", f"POSTGRES_DB={name}",
                args.image, "-c", f"cluster_name={cluster}",
                env={**os.environ, "POSTGRES_PASSWORD": password},
            )
            port = docker("port", container, "5432/tcp").splitlines()[0].rsplit(":", 1)[1]
            report["server_version"] = wait_until_ready(port, name, password)
            print("PostgreSQL", report["server_version"], "in container", cluster)
            os.environ.update(SQE_PG_NAME=name, SQE_PG_PORT=port, SQE_PG_PASSWORD=password, SQE_PG_CLUSTER=cluster)
            exit_code = run_suite(report)
        except Exception as exc:
            report["harness_error_type"] = type(exc).__name__
            traceback.print_exc()
        finally:
            if container:
                docker("stop", "--time", "5", container)
                for _ in range(40):  # --rm removes the stopped container asynchronously
                    report["container_removed"] = not docker("ps", "--all", "--quiet", "--filter", f"name=^{cluster}$")
                    if report["container_removed"]:
                        break
                    time.sleep(0.25)
            report["development_database_after"] = run_tests.development_fingerprint()
            report["development_database_unchanged"] = (
                report["development_database_before"] == report["development_database_after"])
            if not report["development_database_unchanged"]:
                exit_code = 2
            report.update(finished_at_utc=run_tests.utc_now(), process_exit_code=exit_code)
            if directory is not None:
                (directory / "result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
            print(f"concurrency: exit code {exit_code}; container removed={report.get('container_removed')}; "
                  f"development database unchanged={report['development_database_unchanged']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
