"""Baseline application under real gunicorn + disposable PostgreSQL: simultaneous W1 double submits over HTTP."""
import json, os, secrets, subprocess, sys, time, urllib.error, urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
from threading import Barrier
import psycopg

ROOT = Path(sys.argv[1]); VENV = Path(sys.argv[2])
assert str(ROOT).startswith("/tmp/rca-"), ROOT
PAIRS = 100
tok = secrets.token_hex(6); name = f"leaveflow-sqe-{tok}"; pw = secrets.token_urlsafe(24)
docker = lambda *a: subprocess.run(["docker", *a], check=True, capture_output=True, text=True, env={**os.environ, "POSTGRES_PASSWORD": pw}).stdout.strip()
docker("run", "-d", "--rm", "--name", name, "--label", "leaveflow-sqe=concurrency", "--tmpfs", "/var/lib/postgresql/data",
       "-p", "127.0.0.1::5432", "-e", "POSTGRES_PASSWORD", "-e", "POSTGRES_USER=sqe", "-e", "POSTGRES_DB=sqe_rca", "postgres:17-alpine")
try:
    port = docker("port", name, "5432/tcp").splitlines()[0].rsplit(":", 1)[1]
    for _ in range(120):
        try:
            psycopg.connect(host="127.0.0.1", port=port, dbname="sqe_rca", user="sqe", password=pw, connect_timeout=3).close(); break
        except psycopg.OperationalError: time.sleep(.5)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("POSTGRES", "REDIS", "DJANGO", "PG"))}
    env.update(POSTGRES_DB="sqe_rca", POSTGRES_USER="sqe", POSTGRES_PASSWORD=pw, POSTGRES_HOST="127.0.0.1", POSTGRES_PORT=port,
               DJANGO_ALLOWED_HOSTS="127.0.0.1", DJANGO_DEBUG="true")
    py = str(VENV / "bin/python"); cwd = ROOT / "backend"
    manage = lambda *a: subprocess.run([py, "manage.py", *a], cwd=cwd, env=env, check=True, capture_output=True, text=True).stdout
    manage("migrate", "--noinput")
    key = manage("shell", "-v0", "-c", "from django.db import connection as c; assert c.vendor=='postgresql'\n"
        "from leave.models import *; from rest_framework.authtoken.models import Token\n"
        "t=Team.objects.create(name='Synthetic'); u=User.objects.create(username='rca_synthetic', team=t)\n"
        "LeaveBalance.objects.create(user=u, allowance=30000); print(Token.objects.create(user=u).key)").strip().splitlines()[-1]
    def post(http, day, gate):
        body = json.dumps({"leave_type": "vacation", "start_date": str(day), "end_date": str(day + timedelta(1))}).encode()
        req = urllib.request.Request(f"http://127.0.0.1:{http}/api/requests/", body, {"Authorization": f"Token {key}", "Content-Type": "application/json"})
        gate.wait(10)
        try:
            with urllib.request.urlopen(req, timeout=30) as r: return str(r.status)
        except urllib.error.HTTPError as e: return str(e.code)
    for i, (label, extra, servers) in enumerate([("1 sync worker (shipped command)", [], 1), ("2 worker processes", ["--workers", "2"], 1),
                                                 ("3 separate 1-worker servers, requests split (as 3 HPA replicas)", [], 3)]):
        ports = [18110 + 10 * i + s for s in range(servers)]
        procs = [subprocess.Popen([py, "-m", "gunicorn", "config.wsgi:application", "--bind", f"127.0.0.1:{p}", *extra], cwd=cwd, env=env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for p in ports]
        try:
            for p in ports:
                for _ in range(80):
                    try: urllib.request.urlopen(f"http://127.0.0.1:{p}/health/", timeout=2).read(); break
                    except Exception as e: last = e; time.sleep(.25)
                else: raise SystemExit(f"server not ready: {last!r}")
            tally = Counter()
            for n in range(PAIRS):
                day, gate = date(2027 + 3 * i, 1, 4) + timedelta(7 * n), Barrier(2)
                with ThreadPoolExecutor(2) as pool:
                    fs = [pool.submit(post, ports[k % servers], day, gate) for k in range(2)]
                    tally["+".join(sorted(f.result() for f in fs))] += 1
        finally:
            for p in procs: p.terminate(); p.wait(10)
        print("RCA-HTTP", json.dumps({"server": label, "pairs": PAIRS, "outcomes": dict(tally)}), flush=True)
    with psycopg.connect(host="127.0.0.1", port=port, dbname="sqe_rca", user="sqe", password=pw) as c:
        print("RCA-HTTP", json.dumps({"rows": c.execute("select count(*) from leave_leaverequest").fetchone()[0],
            "date_ranges_stored_twice": c.execute("select count(*) from (select 1 from leave_leaverequest group by employee_id,start_date,end_date having count(*)>1) x").fetchone()[0],
            "postgres": c.execute("show server_version").fetchone()[0]}))
finally:
    subprocess.run(["docker", "stop", "-t", "5", name], capture_output=True)