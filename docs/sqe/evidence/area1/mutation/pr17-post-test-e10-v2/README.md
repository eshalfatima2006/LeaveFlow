# E-10 kill verification after stronger test

E-10 changes `.exclude(pk=item.employee_id)` to `.exclude(pk=None)` in the
requested-event recipient query. The added
`test_requested_event_excludes_manager_and_admin_requesters` asserts that a
manager or administrator who submits a request does not receive their own
event.

[`result.json`](result.json) records a passing baseline and mutant exit code 1.
[`mutant-e10.log`](mutant-e10.log) shows assertion failures for both role
subcases. The verification runs in a disposable source copy and does not edit
application code. This proves E-10 changed from an initial survivor to a killed
mutant after the stronger test was added.
