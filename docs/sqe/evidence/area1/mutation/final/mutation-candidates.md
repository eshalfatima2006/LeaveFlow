# Mutation review candidates (not completed analysis)

Generated from the actual mutmut metadata. Review each diff against the curated survivor analysis; tool output alone does not establish equivalence or killability.

| # | Mutant | Source | Result | Affected rule | Killable? | Test or equivalence justification |
|---:|---|---|---|---|---|---|
| 1 | `leave.events.x_build_leave_event__mutmut_8` | `backend/leave/events.py` | survived | Leave-event publication behavior | REVIEW REQUIRED | Inspect the recorded diff and run a discriminating test. |
| 2 | `leave.management.commands.seed_demo.xǁCommandǁhandle__mutmut_69` | `backend/leave/management/commands/seed_demo.py` | survived | Supporting leave-workflow behavior | REVIEW REQUIRED | Inspect the recorded diff and run a discriminating test. |
| 3 | `leave.management.commands.seed_demo.xǁCommandǁhandle__mutmut_123` | `backend/leave/management/commands/seed_demo.py` | survived | Supporting leave-workflow behavior | REVIEW REQUIRED | Inspect the recorded diff and run a discriminating test. |

## leave.events.x_build_leave_event__mutmut_8

```diff
--- original
+++ mutant
@@ -1,6 +1,6 @@
 def reviewed_function(item: LeaveRequest, event_type: str, actor: User) -> dict:
     if event_type == 'leave.requested':
-        recipients = list(User.objects.filter(Q(role=User.Role.ADMIN) | Q(role=User.Role.MANAGER, team_id=item.employee.team_id)).exclude(pk=item.employee_id).values_list('id', flat=True))
+        recipients = list(User.objects.filter(Q(role=User.Role.ADMIN) | Q(role=User.Role.MANAGER, team_id=item.employee.team_id)).exclude(pk=item.employee_id).values_list(flat=True))
     else:
         recipients = [item.employee_id]
     return {'id': str(uuid4()), 'type': event_type, 'occurred_at': timezone.now().isoformat(), 'recipients': recipients, 'actor': {'id': actor.id, 'display_name': actor.display_name}, 'request': {'id': item.id, 'employee_id': item.employee_id, 'employee_name': item.employee.display_name, 'leave_type': item.leave_type, 'start_date': item.start_date.isoformat(), 'end_date': item.end_date.isoformat(), 'status': item.status}}
```

## leave.management.commands.seed_demo.xǁCommandǁhandle__mutmut_69

```diff
--- original
+++ mutant
@@ -14,7 +14,7 @@
         users[username] = user
     LeaveRequest.objects.all().delete()
     today = date.today()
-    LeaveRequest.objects.create(employee=users['employee'], leave_type='vacation', start_date=today + timedelta(days=18), end_date=today + timedelta(days=22), note='Cinque giorni in montagna')
+    LeaveRequest.objects.create(employee=users['employee'], start_date=today + timedelta(days=18), end_date=today + timedelta(days=22), note='Cinque giorni in montagna')
     LeaveRequest.objects.create(employee=users['employee'], leave_type='permit', start_date=today - timedelta(days=25), end_date=today - timedelta(days=25), note='Visita medica', status='approved', decided_by=users['manager'])
     LeaveRequest.objects.create(employee=users['teammate'], leave_type='vacation', start_date=today + timedelta(days=8), end_date=today + timedelta(days=10), note='Ponte lungo')
     self.stdout.write(self.style.SUCCESS('Demo pronta: employee / manager / admin · password demo1234'))
```

## leave.management.commands.seed_demo.xǁCommandǁhandle__mutmut_123

```diff
--- original
+++ mutant
@@ -16,5 +16,5 @@
     today = date.today()
     LeaveRequest.objects.create(employee=users['employee'], leave_type='vacation', start_date=today + timedelta(days=18), end_date=today + timedelta(days=22), note='Cinque giorni in montagna')
     LeaveRequest.objects.create(employee=users['employee'], leave_type='permit', start_date=today - timedelta(days=25), end_date=today - timedelta(days=25), note='Visita medica', status='approved', decided_by=users['manager'])
-    LeaveRequest.objects.create(employee=users['teammate'], leave_type='vacation', start_date=today + timedelta(days=8), end_date=today + timedelta(days=10), note='Ponte lungo')
+    LeaveRequest.objects.create(employee=users['teammate'], start_date=today + timedelta(days=8), end_date=today + timedelta(days=10), note='Ponte lungo')
     self.stdout.write(self.style.SUCCESS('Demo pronta: employee / manager / admin · password demo1234'))
```
