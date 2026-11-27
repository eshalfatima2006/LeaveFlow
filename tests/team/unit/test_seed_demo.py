"""Contract tests for the production demo-data management command."""

from io import StringIO
from datetime import date
from unittest.mock import patch

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

    def test_demo_schedule_and_account_permissions_match_documented_fixture(self):
        """Verify full demo record content and deny staff powers to non-admins."""
        with patch("leave.management.commands.seed_demo.date") as clock:
            clock.today.return_value = date(2026, 12, 1)
            self.run_seed_command()
        expected = {
            ("employee", "vacation"): (date(2026, 12, 19), date(2026, 12, 23), "Cinque giorni in montagna"),
            ("employee", "permit"): (date(2026, 11, 6), date(2026, 11, 6), "Visita medica"),
            ("teammate", "vacation"): (date(2026, 12, 9), date(2026, 12, 11), "Ponte lungo"),
        }
        for row in LeaveRequest.objects.select_related("employee"):
            self.assertEqual((row.start_date, row.end_date, row.note), expected[row.employee.username, row.leave_type])
        team = Team.objects.get(name="Product Studio")
        for user in User.objects.all():
            self.assertEqual(user.team_id, team.pk)
            self.assertEqual(user.is_staff, user.username == "admin")
            self.assertEqual(user.is_superuser, user.username == "admin")

    def test_seed_restores_existing_allowance_and_year(self):
        """Reset a previously edited demo balance, not only a fresh model default."""
        self.run_seed_command()
        LeaveBalance.objects.update(allowance=3, year=2025)
        self.run_seed_command()
        self.assertEqual(set(LeaveBalance.objects.values_list("allowance", "year")), {(26, 2026)})
