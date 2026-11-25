"""Apply one experimental variant to a throwaway clone. Never run against the working tree."""
import sys
from pathlib import Path
root, variant = Path(sys.argv[1]), sys.argv[2]
assert str(root).startswith("/tmp/rca-"), root
V = root / "backend/leave/views.py"
t = V.read_text()


def sub(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old)
    t = t.replace(old, new)


W1 = """        serializer.is_valid(raise_exception=True)
        item = serializer.save()
"""
def w1(*lines):
    sub(W1, "        with transaction.atomic():\n" + "".join(f"            {l}\n" for l in lines)
        + "            serializer.is_valid(raise_exception=True)\n            item = serializer.save()\n")

CHECK = """        item.status = decision
        item.decided_by"""
GUARD = """        if decision == LeaveRequest.Status.APPROVED:
            balance = {balance}
            if balance and item.business_days > balance.available_days:
                return Response({{'detail': 'EXPERIMENT: insufficient balance'}}, status=status.HTTP_409_CONFLICT)
"""
if variant == "baseline":
    pass
elif variant == "w1-atomic-only":
    w1()
elif variant == "w1-lock-overlapping-rows":
    w1("list(LeaveRequest.objects.select_for_update().filter(employee=request.user, status__in=['pending', 'approved']))")
elif variant == "w1-lock-employee-row":
    w1("User.objects.select_for_update().get(pk=request.user.pk)")
elif variant == "w1-serializable":
    w1("connection.cursor().execute('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE')")
elif variant == "w1-exclusion-constraint":
    (root / "backend/leave/migrations/0002_rca_experiment.py").write_text('''from django.db import migrations
class Migration(migrations.Migration):
    dependencies = [("leave", "0001_initial")]
    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS btree_gist"),
        migrations.RunSQL("ALTER TABLE leave_leaverequest ADD CONSTRAINT rca_no_overlap EXCLUDE USING gist "
            "(employee_id WITH =, daterange(start_date, end_date, '[]') WITH &&) WHERE (status IN ('pending','approved'))"),
    ]
''')
elif variant == "w2-check-only":
    sub(CHECK, GUARD.format(balance="getattr(item.employee, 'leave_balance', None)") + CHECK)
elif variant == "w2-check-and-lock-balance":
    sub(CHECK, GUARD.format(balance="LeaveBalance.objects.select_for_update().filter(user_id=item.employee_id).first()") + CHECK)
    sub("from .models import LeaveRequest, User", "from .models import LeaveBalance, LeaveRequest, User")
else:
    raise SystemExit(variant)
V.write_text(t)