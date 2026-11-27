# Blocked pull-request evidence

PR [#27](https://github.com/eshalfatima2006/LeaveFlow/pull/27) targets `dev`
from `evidence/blocked-quality-gate`. Keep it open and unmerged as the
deliberately failing CI example.

The previous hosted [run #40](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/45657735906)
failed the Area1 quality gate because of an evidence-only `assert False` test.
That failure was collected by pytest but not by the project's Django team
runner. It also did not prove a status-check merge block while the `CI_Checks`
ruleset was disabled. Do not describe that run as proof of enforced protection.

The **local, not yet pushed** revision replaces the dummy failure with a
deliberate inclusive-overlap regression: `start_date__lte` becomes
`start_date__lt` in `LeaveRequest.clean`. A request that touches an existing
request's first day is wrongly accepted. The existing API test
`OverlapTests.test_inclusive_boundaries_against_pending_request` fails because
the API returns 201 instead of the expected 400. No test is weakened.
The guarded team runner also failed on two boundary subcases while leaving the
development database unchanged; see [the local result](blocked-local-run/result.json)
and its raw logs in the same directory. This is local evidence, not a hosted
branch-protection result.
The corresponding corrected business rule remains in the passing Area 1 work;
this regression must never enter `dev` or `main`.

After the revised branch is pushed, capture its failing GitHub Actions run
and the merge box. A repository administrator must enable a required check
for `Area1 quality gate` or the later aggregate `Project quality gate` on
`dev`; a review requirement or draft status alone does not prove the failed
check prevents merging. Add that screenshot and run link here only after the
enforced state has been observed.
