# E-10 focused kill verification

The new manager/admin requester assertion passes on unchanged source and
fails on the exact recorded E-10 change (`.exclude(pk=item.employee_id)` to
`.exclude(pk=None)`). [`result.json`](result.json) records exit codes and
[`baseline.log`](baseline.log) / [`mutant-e10.log`](mutant-e10.log) preserve
the raw assertions. The test runs in a disposable source copy using
`scripts/sqe/verify_event_recipient_mutant.py`; application source in the PR
branch is unchanged. Both role subcases detect the erroneous self-recipient.

This focused verification establishes that the mutant is **killable and killed
by the added test**. It does not replace a full mutmut run or change the
historical hosted 295/299 figure. The next hosted PR run must report the
revised aggregate score.
