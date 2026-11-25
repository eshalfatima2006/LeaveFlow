"""Contract tests for the production demo-data management command."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from leave.models import LeaveBalance, LeaveRequest, Team, User


class SeedDemoCommandTests(TestCase):
    def run_seed_command(self):
        output = StringIO()
        call_command("seed_demo", stdout=output)
        return output.getvalue()

    def test_seed_demo_creates_the_documented_demo_state(self):
        output = self.run_seed_command()

        team = Team.objects.get(name="Product Studio")
        users = User.objects.in_bulk(field_name="username")
        self.assertEqual(set(users), {"employee", "teammate", "manager", "admin"})
        self.assertEqual(users["employee"].team_id, team.id)
        self.assertEqual(users["teammate"].role, User.Role.EMPLOYEE)
        self.assertEqual(users["manager"].role, User.Role.MANAGER)
        self.assertEqual(users["admin"].role, User.Role.ADMIN)
        for username in users:
            self.assertEqual(users[username].first_name, "Demo")
            self.assertEqual(users[username].last_name, username.title())
            self.assertEqual(users[username].email, f"{username}@example.invalid")
            self.assertTrue(users[username].check_password("demo1234"))
        self.assertTrue(users["admin"].is_staff)
        self.assertTrue(users["admin"].is_superuser)

        balances = LeaveBalance.objects.select_related("user").order_by("user__username")
        self.assertEqual(balances.count(), 4)
        self.assertEqual({balance.allowance for balance in balances}, {26})
        self.assertEqual({balance.year for balance in balances}, {2026})

        requests = LeaveRequest.objects.select_related("employee", "decided_by")
        self.assertEqual(requests.count(), 3)
        self.assertEqual(
            {(item.employee.username, item.leave_type, item.status) for item in requests},
            {
                ("employee", LeaveRequest.Type.VACATION, LeaveRequest.Status.PENDING),
                ("employee", LeaveRequest.Type.PERMIT, LeaveRequest.Status.APPROVED),
                ("teammate", LeaveRequest.Type.VACATION, LeaveRequest.Status.PENDING),
            },
        )
        approved = requests.get(status=LeaveRequest.Status.APPROVED)
        self.assertEqual(approved.decided_by.username, "manager")
        self.assertEqual(
            output,
            "Demo pronta: employee / manager / admin · password demo1234\n",
        )

    def test_seed_demo_is_repeatable_without_duplicate_users_or_requests(self):
        self.run_seed_command()
        self.run_seed_command()

        self.assertEqual(Team.objects.filter(name="Product Studio").count(), 1)
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(LeaveBalance.objects.count(), 4)
        self.assertEqual(LeaveRequest.objects.count(), 3)
