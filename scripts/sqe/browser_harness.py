#!/usr/bin/env python3
"""Disposable-database harness for the SQE Playwright suite (profile sqe-browser-v1).

Commands
  init                      create a marked run directory under the system temp dir
  serve --port N            migrate the run directory's database, then run Django there
  fixture ACTION [--payload JSON]
                            reset / sentinel / scenario / request / requests / balance /
                            revoke-token / whoami against the same disposable database

Every Django command validates SQE_BROWSER_RUN_DIR before settings load and checks the
active connection again after setup. There are no options to choose another database,
seed demo data, flush a non-harness database or reach Redis/PostgreSQL. Output is JSON.
Generated fixture passwords are printed only to the calling process, never to files.
"""

import argparse
from datetime import date
import json
import os
from pathlib import Path
import secrets
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
sys.dont_write_bytecode = True


def init():
    from tests.team.browser_safety import MARKER, RUN_DIR_PREFIX, validate_run_dir

    run_dir = Path(tempfile.mkdtemp(prefix=RUN_DIR_PREFIX)).resolve()
    (run_dir / MARKER).write_text("Created by scripts/sqe/browser_harness.py init\n")
    validate_run_dir(run_dir)
    return {"run_dir": str(run_dir)}


def setup_django():
    from tests.team.browser_safety import assert_browser_database, run_dir_from_environment

    run_dir_from_environment()
    for name in ("POSTGRES_DB", "REDIS_URL"):
        os.environ.pop(name, None)
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.team.browser_settings"
    import django

    django.setup()
    assert_browser_database()


def serve(port):
    setup_django()
    import logging
    from django.conf import settings
    from django.core.management import call_command

    from tests.team.browser_safety import assert_browser_database, run_dir_from_environment

    call_command("migrate", interactive=False, verbosity=0)
    assert_browser_database()
    if settings.REDIS_URL:
        handler = logging.FileHandler(run_dir_from_environment() / "notification-publish.log", encoding="utf-8")
        handler.setLevel(logging.ERROR)
        logging.getLogger("leave.events").addHandler(handler)
    call_command("runserver", f"127.0.0.1:{port}", use_reloader=False, use_threading=True)


def row_state(item):
    return {
        "id": item.id,
        "employee": item.employee.username,
        "leave_type": item.leave_type,
        "start_date": item.start_date.isoformat(),
        "end_date": item.end_date.isoformat(),
        "note": item.note,
        "status": item.status,
        "decided_by": item.decided_by.username if item.decided_by_id else None,
        "decided_at": item.decided_at.isoformat() if item.decided_at else None,
        "business_days": item.business_days,
        "created_at": item.created_at.isoformat(),
    }


def fixture(action, payload):
    setup_django()
    from django.conf import settings
    from django.contrib.sessions.models import Session
    from django.db import transaction
    from django.utils import timezone
    from rest_framework.authtoken.models import Token

    from leave.models import LeaveBalance, LeaveRequest, Team, User
    from tests.team.browser_safety import PROFILE, run_dir_from_environment

    if action == "whoami":
        import django
        from django.db import connection

        return {
            "profile": PROFILE,
            "database": str(connection.settings_dict["NAME"]),
            "python": sys.version.split()[0],
            "django": django.get_version(),
        }
    if action == "reset":
        with transaction.atomic():
            LeaveRequest.objects.all().delete()
            LeaveBalance.objects.all().delete()
            Token.objects.all().delete()
            Session.objects.all().delete()
            User.objects.all().delete()
            Team.objects.all().delete()
        return {"reset": True}
    if action == "sentinel":
        username = f"sqe-sentinel-{secrets.token_hex(4)}"
        password = secrets.token_urlsafe(16)
        User.objects.create_user(username=username, password=password)
        return {"username": username, "password": password}
    if action == "scenario":
        return build_scenario(payload, Team, User, LeaveBalance, LeaveRequest, timezone)
    if action == "request":
        item = LeaveRequest.objects.filter(pk=payload["id"]).select_related("employee", "decided_by").first()
        return row_state(item) if item else None
    if action == "requests":
        return [row_state(item) for item in LeaveRequest.objects.select_related("employee", "decided_by").order_by("id")]
    if action == "balance":
        balance = LeaveBalance.objects.filter(user__username=payload["username"]).first()
        if balance is None:
            return None
        return {"allowance": balance.allowance, "used": balance.approved_days, "available": balance.available_days}
    if action == "balance-id":
        return LeaveBalance.objects.filter(user_id=payload["id"]).values_list("id", flat=True).first()
    if action == "user":
        return User.objects.filter(pk=payload["id"]).values("role", "team_id").first()
    if action == "delete-team":
        return Team.objects.filter(pk=payload["id"]).delete()[0]
    if action == "delete-user":
        return User.objects.filter(pk=payload["id"]).delete()[0]
    if action in {"notification-fault", "notification-state"}:
        if not settings.REDIS_URL:
            raise SystemExit("The isolated notification profile is required.")
        run_dir = run_dir_from_environment()
        if action == "notification-fault":
            (run_dir / "notification-publish-fault").touch(exist_ok=False)
            return True
        from redis import Redis

        log_path = run_dir / "notification-publish.log"
        stream = "leaveflow:events"
        group_name = "leaveflow-notifications"
        with Redis.from_url(settings.REDIS_URL, decode_responses=True) as client:
            events = [
                (entry_id, json.loads(fields["payload"]))
                for entry_id, fields in client.xrange(stream)
            ]
            events = [(entry_id, event) for entry_id, event in events if event["request"]["id"] == payload["id"]]
            groups = client.xinfo_groups(stream) if client.exists(stream) else []
            group = next((group for group in groups if group["name"] == group_name), None)
            unacknowledged = None
            if group:
                def stream_position(entry_id):
                    return tuple(map(int, entry_id.split("-")))

                last_delivered = stream_position(group["last-delivered-id"])
                unacknowledged = sum(
                    stream_position(entry_id) > last_delivered
                    or bool(client.xpending_range(stream, group_name, entry_id, entry_id, 1))
                    for entry_id, _ in events
                )
        return {
            "events": [
                {"id": event["id"], "type": event["type"], "recipients": event["recipients"]}
                for _, event in events
            ],
            "unacknowledged": unacknowledged,
            "publish_errors": log_path.read_text(encoding="utf-8").count("SQE controlled Redis outage")
            if log_path.exists() else 0,
        }
    if action == "revoke-token":
        deleted, _ = Token.objects.filter(user__username=payload["username"]).delete()
        return {"revoked": deleted}
    raise SystemExit(f"Unknown fixture action: {action}")


def build_scenario(spec, Team, User, LeaveBalance, LeaveRequest, timezone):
    """Create synthetic teams/users/balances and ORM-level precondition requests.

    Requests under test are created by the specs through the real API instead.
    """
    from django.db import transaction

    with transaction.atomic():
        teams = {name: Team.objects.create(name=name) for name in spec.get("teams", [])}
        users = {}
        for entry in spec.get("users", []):
            role = entry["role"]
            password = secrets.token_urlsafe(16)
            user = User.objects.create_user(
                username=entry["key"],
                password=password,
                first_name=entry.get("first", ""),
                last_name=entry.get("last", ""),
                role=role,
                team=teams[entry["team"]] if entry.get("team") else None,
                is_staff=role == User.Role.ADMIN,
                is_superuser=role == User.Role.ADMIN,
            )
            if entry.get("allowance") is not None:
                LeaveBalance.objects.create(user=user, allowance=entry["allowance"])
            users[entry["key"]] = {
                "id": user.id,
                "username": user.username,
                "password": password,
                "display_name": user.display_name,
            }
        requests = {}
        for entry in spec.get("requests", []):
            decided_by = entry.get("decided_by")
            item = LeaveRequest.objects.create(
                employee=User.objects.get(username=entry["owner"]),
                leave_type=entry.get("type", "vacation"),
                start_date=date.fromisoformat(entry["start"]),
                end_date=date.fromisoformat(entry["end"]),
                note=entry.get("note", ""),
                status=entry.get("status", "pending"),
                decided_by=User.objects.get(username=decided_by) if decided_by else None,
                decided_at=timezone.now() if decided_by else None,
            )
            requests[entry["key"]] = item.id
    return {"users": users, "requests": requests, "teams": {name: team.pk for name, team in teams.items()}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    serve_parser = sub.add_parser("serve")
    serve_parser.add_argument("--port", type=int, required=True)
    fixture_parser = sub.add_parser("fixture")
    fixture_parser.add_argument("action")
    fixture_parser.add_argument("--payload", default="{}")
    args = parser.parse_args(argv)
    if args.command == "init":
        print(json.dumps(init()))
    elif args.command == "serve":
        serve(args.port)
    else:
        print(json.dumps(fixture(args.action, json.loads(args.payload))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
