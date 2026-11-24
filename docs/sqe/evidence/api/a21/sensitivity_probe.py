"""A2.1 assertion-sensitivity self-check: NOT a product defect, NOT a discovered test.

Usage: python sensitivity_probe.py <fault> <NEW evidence dir>
Patches exactly one application behaviour in THIS child process's memory, then
runs tests.team.api through the normal runner. Source files are never edited.
A meaningful suite must exit 1 with failures in the matching test group.
"""

from datetime import timedelta
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
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from leave import views
from leave.models import LeaveRequest
from leave.serializers import LeaveRequestSerializer


def validate_without_balance(self, attrs):
    instance = LeaveRequest(employee=self.context["request"].user, **attrs)
    try:
        instance.clean()
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
    return attrs


def clean_without_overlap(self):
    if self.end_date < self.start_date:
        raise DjangoValidationError({"end_date": "La data finale non può precedere quella iniziale."})


def calendar_days(self):
    return (self.end_date - self.start_date + timedelta(days=1)).days


FAULTS = {
    "no-balance-check": (LeaveRequestSerializer, "validate", validate_without_balance),
    "no-overlap-check": (LeaveRequest, "clean", clean_without_overlap),
    "count-weekends": (LeaveRequest, "business_days", property(calendar_days)),
    "visibility-all": (views, "visible_requests", lambda user: LeaveRequest.objects.all()),
}

if len(sys.argv) != 3 or sys.argv[1] not in FAULTS:
    raise SystemExit(f"Usage: sensitivity_probe.py {{{','.join(FAULTS)}}} <new-evidence-dir>")
target, attribute, replacement = FAULTS[sys.argv[1]]
print(f"A2.1 sensitivity probe: injected fault {sys.argv[1]!r} in process memory only")
script = root / "scripts/sqe/run_tests.py"
sys.argv = [str(script), "team", "tests.team.api", "--verbosity", "1", "--evidence-dir", sys.argv[2]]
with patch.object(target, attribute, replacement):
    runpy.run_path(str(script), run_name="__main__")
