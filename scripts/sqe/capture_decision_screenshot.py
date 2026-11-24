#!/usr/bin/env python3
"""Capture PR #1 baseline evidence BL-UI-04 (manager decision result) in a real browser.

Usage (repository root, inside WSL; once: `npm ci` in scripts/sqe/baseline-browser):

    .venv/bin/python scripts/sqe/capture_decision_screenshot.py \
        --evidence-dir docs/sqe/evidence/baseline/browser-decision-<date>

Reuses the isolation helpers of scripts/sqe/reproduce_baseline.py: Django runs only
with a generated settings module whose single database is a SQLite file in a new
temporary directory (verified before use), Redis is disabled and the development
database is compared by file metadata only. Steps:

  01 environment   02 settings guard   03 migrate   04 synthetic fixture
  05 backend runserver (log)   06 frontend vite build (temporary copy)
  07 frontend vite preview (log)   08 Playwright test (Chromium)
  09 browser result (written by the spec)   10 database readback
  execution-record.json   manager-decision-approved.png

Ports must be free (the run refuses to talk to an unknown server). Passwords are
random per run and passed to the browser test through the environment only.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

sys.dont_write_bytecode = True
import reproduce_baseline as rb  # noqa: E402 - shared isolation helpers (same directory)

BROWSER_DIR = rb.ROOT / "scripts" / "sqe" / "baseline-browser"
SCREENSHOT = "manager-decision-approved.png"

FIXTURE_CODE = """
import json, os
from leave.models import LeaveBalance, Team, User
team = Team.objects.create(name='Evidence Team')
employee = User.objects.create_user(username='bl-employee', password=os.environ['BL_EMPLOYEE_PASSWORD'], first_name='Sam', last_name='Example', role='employee', team=team)
manager = User.objects.create_user(username='bl-manager', password=os.environ['BL_MANAGER_PASSWORD'], first_name='Max', last_name='Example', role='manager', team=team)
LeaveBalance.objects.create(user=employee, allowance=10)
LeaveBalance.objects.create(user=manager, allowance=10)
print(json.dumps({'team': team.name, 'employee': employee.username, 'manager': manager.username, 'employee_allowance': 10}))
"""

READBACK_CODE = """
import json, os
from leave.models import LeaveBalance, LeaveRequest
k = int(os.environ['BL_REQUEST_ID'])
rows = list(LeaveRequest.objects.select_related('employee', 'decided_by').order_by('id'))
item = next((r for r in rows if r.id == k), None)
balance = LeaveBalance.objects.get(user__username='bl-employee')
print(json.dumps({'request_count': len(rows), 'request_ids': [r.id for r in rows],
  'id': item.id if item else None, 'employee': item.employee.username if item else None,
  'status': item.status if item else None,
  'decided_by': item.decided_by.username if item and item.decided_by_id else None,
  'decided_at': item.decided_at.isoformat() if item and item.decided_at else None,
  'start_date': str(item.start_date) if item else None, 'end_date': str(item.end_date) if item else None,
  'note': item.note if item else None, 'business_days': item.business_days if item else None,
  'balance': {'allowance': balance.allowance, 'used': balance.approved_days, 'available': balance.available_days}}))
"""


def wait_for(url, timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"{url} did not become ready")


def start(name, command, cwd, env, evidence):
    log = open(evidence / f"{name}.log", "w")
    log.write(f"Command: {' '.join(command)}\nWorking directory: {cwd}\n----- output -----\n")
    log.flush()
    return subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT), log


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--backend-port", type=int, default=8798)
    parser.add_argument("--frontend-port", type=int, default=4798)
    parser.add_argument("--notifications-port", type=int, default=4799, help="must be unused; the notification centre stays unavailable")
    args = parser.parse_args(argv)
    if not (BROWSER_DIR / "node_modules" / "@playwright" / "test").is_dir():
        raise SystemExit("Run `npm ci` in scripts/sqe/baseline-browser first.")
    evidence = args.evidence_dir.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    before = rb.dev_db_metadata()
    backend_url = f"http://127.0.0.1:{args.backend_port}"
    frontend_url = f"http://127.0.0.1:{args.frontend_port}"
    sources = [Path(__file__).resolve(), rb.ROOT / "scripts" / "sqe" / "reproduce_baseline.py",
               BROWSER_DIR / "manager-decision.spec.ts", BROWSER_DIR / "playwright.config.ts", BROWSER_DIR / "package-lock.json"]
    record = {"scenario": "PR1-BL-UI-04", "started_at_utc": rb.utc(), "development_database_before": before,
              "source_sha256": {str(p.relative_to(rb.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              "backend_url": backend_url, "frontend_url": frontend_url,
              "screenshot": str((evidence / SCREENSHOT).relative_to(rb.ROOT)) if evidence.is_relative_to(rb.ROOT) else str(evidence / SCREENSHOT)}
    run_dir = Path(tempfile.mkdtemp(prefix="leaveflow-baseline-browser-")).resolve()
    recorder = rb.Recorder(evidence, run_dir)
    processes = []
    try:
        for port in (args.backend_port, args.frontend_port, args.notifications_port):
            if not rb.port_free(port):
                raise RuntimeError(f"Port {port} is in use; refusing to run.")
        rb.environment(evidence)
        database = rb.write_settings(run_dir)
        with open(run_dir / f"{rb.SETTINGS_MODULE}.py", "a") as settings:
            settings.write(f"CORS_ALLOWED_ORIGINS = [{frontend_url!r}]\n")
        guard = ("import django; django.setup(); from django.db import connection; from django.conf import settings; "
                 "print(connection.settings_dict['NAME']); print('REDIS_URL=' + repr(settings.REDIS_URL)); "
                 "print('CORS_ALLOWED_ORIGINS=' + repr(settings.CORS_ALLOWED_ORIGINS))")
        code, output = recorder.run("02-settings-guard", [sys.executable, "-c", guard])
        resolved = Path(output.splitlines()[0].strip()).resolve() if output else None
        if code != 0 or resolved != database or resolved == rb.DEV_DB.resolve():
            raise RuntimeError("Settings guard failed: Django did not resolve to the disposable database.")
        record["disposable_database"] = str(database)
        if recorder.run("03-migrate", [sys.executable, "manage.py", "migrate", "--no-input"])[0] != 0:
            raise RuntimeError("migrate failed")
        passwords = {"BL_EMPLOYEE_PASSWORD": secrets.token_urlsafe(16), "BL_MANAGER_PASSWORD": secrets.token_urlsafe(16)}
        record["fixture"] = rb.shell_json(recorder, "04-fixture", FIXTURE_CODE, passwords)

        backend, backend_log = start("05-backend-server", [sys.executable, "manage.py", "runserver", f"127.0.0.1:{args.backend_port}", "--noreload"],
                                     rb.BACKEND, recorder.env(), evidence)
        processes.append((backend, backend_log))
        wait_for(f"{backend_url}/health/")

        frontend = run_dir / "frontend"
        shutil.copytree(rb.ROOT / "frontend", frontend, ignore=shutil.ignore_patterns("node_modules", "dist", "*.tsbuildinfo"))
        os.symlink(rb.ROOT / "frontend" / "node_modules", frontend / "node_modules")
        vite_env = {"VITE_API_URL": f"{backend_url}/api", "VITE_NOTIFICATIONS_URL": f"http://127.0.0.1:{args.notifications_port}"}
        if recorder.run("06-frontend-build", ["npx", "vite", "build", "--outDir", "dist", "--emptyOutDir"], cwd=frontend,
                        extra_env=vite_env, note="Temporary copy of frontend/; API base points at the disposable backend.")[0] != 0:
            raise RuntimeError("frontend build failed")
        preview, preview_log = start("07-frontend-preview", ["npx", "vite", "preview", "--outDir", "dist", "--host", "127.0.0.1",
                                                             "--port", str(args.frontend_port), "--strictPort"], frontend, os.environ.copy(), evidence)
        processes.append((preview, preview_log))
        wait_for(frontend_url)

        result_path = evidence / "09-browser-result.json"
        browser_env = {**passwords, "BL_EMPLOYEE_USERNAME": "bl-employee", "BL_MANAGER_USERNAME": "bl-manager",
                       "BL_FRONTEND_URL": frontend_url, "BL_EVIDENCE_DIR": str(evidence), "BL_ARTIFACTS_DIR": str(run_dir / "playwright-artifacts"),
                       "BL_SCREENSHOT_PATH": str(evidence / SCREENSHOT), "BL_RESULT_PATH": str(result_path)}
        code, _ = recorder.run("08-playwright", ["npx", "playwright", "test", "--config", "playwright.config.ts"], cwd=BROWSER_DIR,
                               extra_env=browser_env, note="Credentials are passed through the environment and are not recorded.")
        record["playwright_exit_code"] = code
        if code != 0 or not result_path.exists():
            raise RuntimeError("Browser test failed")
        browser_result = json.loads(result_path.read_text())
        k = browser_result["request_id"]
        record["request_id"] = k
        record["browser"] = browser_result["browser"]
        record["playwright"] = json.loads((BROWSER_DIR / "node_modules" / "@playwright" / "test" / "package.json").read_text())["version"]

        readback = rb.shell_json(recorder, "10-db-readback", READBACK_CODE, {"BL_REQUEST_ID": str(k)})
        backend.terminate()
        backend.wait(timeout=10)
        server_log = (evidence / "05-backend-server.log").read_text()
        db_assertions = {
            "single_request_created": readback["request_count"] == 1 and readback["request_ids"] == [k],
            "same_primary_key_w1_w2": readback["id"] == k and browser_result["w2_decision"]["body_id"] == k,
            "owner_is_employee": readback["employee"] == "bl-employee",
            "status_approved": readback["status"] == "approved",
            "decided_by_manager": readback["decided_by"] == "bl-manager",
            "decided_at_not_null": readback["decided_at"] is not None,
            "dates_and_days_unchanged": (readback["start_date"], readback["end_date"], readback["business_days"]) == ("2027-03-01", "2027-03-05", 5),
            "balance_allowance_10_used_5_available_5": readback["balance"] == {"allowance": 10, "used": 5, "available": 5},
            "exactly_one_submission_post": server_log.count('"POST /api/requests/ HTTP') == 1,
            "exactly_one_decision_post": server_log.count(f'"POST /api/requests/{k}/decision/ HTTP') == 1,
        }
        record.update(browser_result=browser_result, db_readback=readback, db_assertions=db_assertions)
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        for process, log in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
            log.close()
        shutil.rmtree(run_dir, ignore_errors=True)
        after = rb.dev_db_metadata()
        record.update(steps=recorder.steps, development_database_after=after,
                      development_database_unchanged=before == after, finished_at_utc=rb.utc(),
                      screenshot_exists=(evidence / SCREENSHOT).is_file(),
                      credentials="random per run, passed via environment only, never written")
        record["overall_pass"] = bool(
            not record.get("error") and record.get("playwright_exit_code") == 0 and record["screenshot_exists"]
            and all(record.get("db_assertions", {"missing": False}).values()) and record["development_database_unchanged"]
            and all(step["exit_code"] == 0 for step in recorder.steps))
        (evidence / "execution-record.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: record.get(k) for k in ("request_id", "playwright_exit_code", "db_assertions", "development_database_unchanged", "screenshot_exists", "overall_pass", "error")}, indent=2))
    return 0 if record["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
