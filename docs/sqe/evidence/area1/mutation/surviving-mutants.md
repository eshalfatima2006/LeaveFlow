# Individual analysis of historical survivors

Initial evidence: [CI run 66](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/45702440867)
recorded 267 killed and **30 survived** out of 297. Its unmodified
[mutmut stats](historical-run-66/mutmut-cicd-stats.json) and
[original survivor table](historical-run-66/original-survivor-table.md) are
preserved from the uploaded artifact at commit `25253fff` in PR #17.
The first 15 records are analyzed below. Current evidence in
`pr17-after-stronger-tests/results.json`
records 296 killed, 3 survived, 299 total, no unresolved results: **99.00% raw score**.
Equivalent mutants remain in that raw denominator. No test was weakened.

The earlier [hosted PR #17 run 74, attempt 4](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/46052602581)
passed at commit `65e229d` with **295 killed, 4 survived, 299 total (98.66%)**;
its [raw stats](hosted-run-74/mutmut-cicd-stats.json) are preserved separately.
The combined local and hosted numbers are different revisions and test suites.
The [exact-PR-tree local rerun](pr17-pre-new-test/README.md) identifies the fourth survivor as **E-10**:
`.exclude(pk=item.employee_id)` becomes `.exclude(pk=None)` in the requested
event's recipient query. It is killable. PR #17 lacked a test where the
requester is a manager or admin, so its existing employee-only assertion did
not detect self-notification. The added manager/admin requester assertion now
kills it; [focused evidence](pr17-post-test-e10-v2/README.md) records a passing
baseline and assertion failures under the exact mutant. No existing test was
removed or weakened.

The historical rerun attempted during this audit stalled in its clean-test
phase and was stopped; it is not a completed baseline run. Initial statuses
below come from the committed historical report; final statuses and changes
come from the newly executed run. All production source remains unchanged.

`E-n` = `leave.events.x_build_leave_event__mutmut_n` in `backend/leave/events.py`.
`S-n` = `leave.management.commands.seed_demo.xǁCommandǁhandle__mutmut_n`
in `backend/leave/management/commands/seed_demo.py`. JSON stores the full IDs.

| Historical survivor | Actual mutation | Classification/cause | Assertion or equivalence justification | Final |
|---|---|---|---|---|
| E-8 | Remove `'id'` from `values_list('id', flat=True)` | Equivalent | Django selects the User primary key by default; flat=True still yields scalar IDs | Survived |
| E-10 | Replace self exclusion with `.exclude(pk=None)` | Missing actor-context test | Added `test_requested_event_excludes_manager_and_admin_requesters`; it detects self-notification for both roles | Initially survived; killed after stronger test |
| S-52 | Replace balance defaults with None | Missing existing-state test | Added `test_seed_restores_existing_allowance_and_year`; it changes an existing balance to 3/2025 and requires reset to 26/2026 | Initially survived; killed after stronger test |
| S-54 | Remove balance defaults argument | Missing existing-state test | The same added reset test verifies existing values are updated; fresh model defaults previously hid the gap | Initially survived; killed after stronger test |
| S-69 | Omit first request's vacation type | Equivalent | LeaveRequest.leave_type defaults to vacation, so persisted type is unchanged | Survived |
| S-72 | Omit vacation note | Weak content assertion | Added `test_demo_schedule_and_account_permissions_match_documented_fixture`; it requires `Cinque giorni in montagna` | Initially survived; killed after stronger test |
| S-77 | Vacation start: today+18 to today-18 | Weak date assertion | The added schedule test freezes 2026-12-01 and requires start 2026-12-19 | Initially survived; killed after stronger test |
| S-79 | Vacation start offset 18 to 19 | Missing exact boundary assertion | The added schedule test rejects start 2026-12-20 | Initially survived; killed after stronger test |
| S-80 | Vacation end: today+22 to today-22 | Weak date assertion | The added schedule test requires end 2026-12-23 and detects the reversed interval | Initially survived; killed after stronger test |
| S-82 | Vacation end offset 22 to 23 | Missing exact boundary assertion | The added schedule test requires 2026-12-23, not 2026-12-24 | Initially survived; killed after stronger test |
| S-83 | Add XX markers to vacation note | Weak content assertion | The added exact-note assertion rejects extra markers | Initially survived; killed after stronger test |
| S-84 | Lowercase vacation note | Weak content assertion | The added exact-note assertion preserves documented capitalization | Initially survived; killed after stronger test |
| S-85 | Uppercase vacation note | Weak content assertion | The added exact-note assertion rejects uppercase text | Initially survived; killed after stronger test |
| S-97 | Omit permit note | Weak content assertion | The added schedule test requires `Visita medica` on the permit record | Initially survived; killed after stronger test |
| S-104 | Permit start: today-25 to today+25 | Weak date assertion | The added fixed-clock assertion requires start and end 2026-11-06 | Initially survived; killed after stronger test |

## All final survivors and scope

The combined local run's survivors are E-8, S-69 and S-123. PR #17's last
hosted run also retained E-10, but the newly added focused assertion kills it.
S-123 omits the teammate request's
vacation type and is equivalent for the same model-default reason as S-69.
Equivalence applies to the current model and stored/HTTP observations; a
future default change requires reanalysis. The [full revised-tree mutation
run](pr17-after-stronger-tests/README.md) confirms **296 killed, 3 survived,
299 total, 0 unresolved**. The current [hosted PR #17 run 76](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/46067326691)
on commit `c811cb7b` confirms the same result. The hosted 295/299 figure is
historical only.
the revised commit runs in GitHub Actions. All core models/serializers/views
mutants were killed.

Most historical examples are in demo support code. They must not be claimed
as 15 survivors confined to DR-001: this is an expanded application scope.
Within `models.py`, `serializers.py`, and `views.py`, the combined local run
killed **24/24, 36/36, and 5/5** mutants respectively: **65/65 (100%)** across
those three critical files. This is a separate denominator from the broader
299-mutant application score. The two custom inclusive-overlap boundary
mutants and the overlap-truth mutant were generated in `models.py` and killed.
The source hashes and exact changes for every mutant are in
`pr17-after-stronger-tests/results.json`.
Both custom operators run: inclusive overlap boundaries become exclusive,
and the overlap existence predicate is inverted; their mutants are killed.
mutmut 3.8.1 skips decorated functions, including properties and API views;
the old calendar operator never reached business_days. Two separate temporary
source-copy mutations now verify weekend counting and inclusive final dates
(`property-rules/results.json`, both killed). These are separate from the
standard 299-mutant score. API tests exercise the decorated views, but that
does not mean those views were mutated.
