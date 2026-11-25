#!/usr/bin/env python3
"""Run ordinary W1/W2 browser tasks through a loopback-only ZAP passive proxy."""

import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import time
from urllib.parse import urlencode
from urllib.request import urlopen

from browser_harness import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zap", type=Path, required=True)
    parser.add_argument("--zap-home", type=Path, help="Optional dedicated ZAP home with cached add-ons")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.evidence_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    app = ROOT / "tests/team/browser"
    with socket.socket() as port_guard:
        port_guard.bind(("127.0.0.1", 0))
        port = port_guard.getsockname()[1]
    proxy = f"http://127.0.0.1:{port}"
    key = secrets.token_hex(24)
    executable = args.zap.resolve(strict=True)
    launcher = ["java", "-jar", str(executable)] if executable.suffix == ".jar" else [str(executable)]

    def api(path, **parameters):
        query = urlencode({"apikey": key, **parameters})
        with urlopen(f"{proxy}/JSON/{path}/?{query}", timeout=5) as response:
            return json.load(response)

    with (output / "zap.log").open("w", encoding="utf-8") as log:
        zap = subprocess.Popen([
            *launcher, "-daemon", "-host", "127.0.0.1", "-port", str(port),
            "-dir", str(args.zap_home.resolve() if args.zap_home else output / "zap-home"),
            "-config", f"api.key={key}",
            "-config", "autoupdate.checkOnStart=false",
            "-config", "autoupdate.downloadNewRelease=false",
        ], cwd=executable.parent, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 240
            while True:
                try:
                    version = api("core/view/version")
                    break
                except OSError:
                    if zap.poll() is not None or time.monotonic() >= deadline:
                        raise RuntimeError("ZAP did not start. See zap.log.") from None
                    time.sleep(0.5)
            api("pscan/action/setEnabled", enabled="true")
            env = {
                **os.environ, "SQE_ZAP_PROXY": proxy, "SQE_EVIDENCE_DIR": str(output / "playwright"),
                "SQE_BACKEND_PORT": "8781", "SQE_FRONTEND_PORT": "4781", "SQE_NOTIFICATIONS_PORT": "4782",
                "SQE_ENABLE_NOTIFICATIONS": "0",
            }
            with (output / "playwright.log").open("w", encoding="utf-8") as browser_log:
                result = subprocess.run([
                    "node", "node_modules/@playwright/test/cli.js", "test", "tasks-and-access",
                ], cwd=app, env=env, stdout=browser_log, stderr=subprocess.STDOUT, check=False)
            deadline = time.monotonic() + 60
            while int(api("pscan/view/recordsToScan")["recordsToScan"]):
                if time.monotonic() >= deadline:
                    raise RuntimeError("The passive scan queue did not drain within 60 seconds.")
                time.sleep(0.5)
            sites = api("core/view/sites")["sites"]
            expected_sites = {"http://127.0.0.1:8781", "http://127.0.0.1:4781"}
            captured = expected_sites.issubset(sites)
            report = {
                "scanner": version, "mode": "passive", "sites": sites, "both_origins_captured": captured,
                "playwright_exit_code": result.returncode,
                "alerts": [
                    alert for alert in api("alert/view/alerts")["alerts"]
                    if any(alert["url"].startswith(f"{site}/") for site in expected_sites)
                ],
            }
            (output / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            return result.returncode or int(not captured)
        finally:
            try:
                api("core/action/shutdown")
            except OSError:
                if zap.poll() is None:
                    zap.terminate()
            try:
                zap.wait(timeout=15)
            except subprocess.TimeoutExpired:
                zap.kill()
                zap.wait()


if __name__ == "__main__":
    raise SystemExit(main())
