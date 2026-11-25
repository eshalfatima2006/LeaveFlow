#!/usr/bin/env python3
"""Run four k6 workloads against one disposable, read-only test dataset."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

from browser_harness import ROOT, fixture, init


def wait_for_backend(url, process):
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline and process.poll() is None:
        try:
            with urlopen(f"{url}/health/", timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, URLError):
            time.sleep(0.25)
    raise RuntimeError("Disposable backend did not start. See backend.log.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k6", default="k6", help="Path to the k6 OSS executable")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.evidence_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    k6 = str(Path(args.k6).resolve()) if Path(args.k6).exists() else args.k6
    os.environ.pop("SQE_ENABLE_NOTIFICATIONS", None)
    os.environ["SQE_BROWSER_RUN_DIR"] = init()["run_dir"]
    with socket.socket() as port_guard:
        port_guard.bind(("127.0.0.1", 0))
        port = port_guard.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    with (output / "backend.log").open("w", encoding="utf-8") as backend_log:
        backend = subprocess.Popen(
            [sys.executable, str(ROOT / "scripts/sqe/browser_harness.py"), "serve", "--port", str(port)],
            cwd=ROOT, stdout=backend_log, stderr=subprocess.STDOUT,
        )
        try:
            wait_for_backend(url, backend)
            dataset = fixture("scenario", {
                "teams": ["Orchid"],
                "users": [
                    {"key": "load-manager", "role": "manager", "team": "Orchid"},
                    {"key": "load-employee", "role": "employee", "team": "Orchid", "allowance": 20},
                ],
                "requests": [
                    {"key": f"row-{day}", "owner": "load-employee", "start": f"2027-04-{day:02d}",
                     "end": f"2027-04-{day:02d}", "note": f"Synthetic row {day}"}
                    for day in range(1, 21)
                ],
            })
            user = dataset["users"]["load-manager"]
            rows = fixture("requests", {})
            environment = {
                "started_at_utc": datetime.now(timezone.utc).isoformat(),
                "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "platform": platform.platform(), "cpu_count": os.cpu_count(), "python": platform.python_version(),
                "k6": subprocess.check_output([k6, "version"], text=True).strip(),
                "backend": fixture("whoami", {}), "starting_rows": len(rows),
                "operation": "GET /api/requests/ as the team manager",
                "steady_seconds": 70, "p95_limit_ms": 500, "unexpected_failure_rate_limit": 0.01,
            }
            (output / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
            runs = []
            for vus in (1, 5):
                for repeat in (1, 2):
                    label = f"{vus}vu-run-{repeat}"
                    summary = output / f"{label}.json"
                    env = {
                        **os.environ, "SQE_K6_URL": url, "SQE_K6_VUS": str(vus),
                        "SQE_K6_USER": user["username"], "SQE_K6_PASSWORD": user["password"],
                    }
                    print(f"Running {label} for 70 seconds", flush=True)
                    with (output / f"{label}.log").open("w", encoding="utf-8") as log:
                        result = subprocess.run(
                            [k6, "run", "--summary-export", str(summary),
                             str(ROOT / "tests/team/performance/list-requests.js")],
                            cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=False,
                        )
                    metrics = json.loads(summary.read_text(encoding="utf-8")).get("metrics", {}) if summary.exists() else {}
                    failure_rate = metrics.get("list_unexpected", {}).get("value")
                    runs.append({
                        "run": label, "vus": vus, "exit_code": result.returncode,
                        "p95_ms": metrics.get("list_latency", {}).get("p(95)"),
                        "requests_per_second": metrics.get("list_completed", {}).get("rate"),
                        "unexpected_failure_percent": failure_rate * 100 if failure_rate is not None else None,
                        "dataset_unchanged": rows == fixture("requests", {}),
                    })
                    (output / "results.json").write_text(json.dumps(runs, indent=2), encoding="utf-8")
            return int(any(
                run["exit_code"] or not run["dataset_unchanged"]
                or any(run[key] is None for key in ("p95_ms", "requests_per_second", "unexpected_failure_percent"))
                for run in runs
            ))
        finally:
            backend.terminate()
            try:
                backend.wait(timeout=10)
            except subprocess.TimeoutExpired:
                backend.kill()
                backend.wait()


if __name__ == "__main__":
    raise SystemExit(main())
