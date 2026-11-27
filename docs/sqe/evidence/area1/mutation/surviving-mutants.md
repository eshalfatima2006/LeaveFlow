# Individual analysis of historical survivors

Initial evidence: the 30-survivor report committed at `25253fff` in PR #17.
The first 15 records are analyzed below. Current evidence in `final/results.json`
records 296 killed, 3 survived, 299 total, no unresolved results: **99.00% raw score**.
Equivalent mutants remain in that raw denominator. No test was weakened.

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
| E-10 | Replace self exclusion with `.exclude(pk=None)` | Missing actor-context test | Area 2 DT-004 self-exclusion cases require manager/admin requesters to be absent from recipients | Killed |
| S-52 | Replace balance defaults with None | Missing existing-state test | `test_seed_restores_existing_allowance_and_year` changes an existing balance to 3/2025 and requires reset to 26/2026 | Killed |
| S-54 | Remove balance defaults argument | Missing existing-state test | Same reset test verifies update of existing values; fresh model defaults previously hid this gap | Killed |
| S-69 | Omit first request's vacation type | Equivalent | LeaveRequest.leave_type defaults to vacation, so persisted type is unchanged | Survived |
| S-72 | Omit vacation note | Weak content assertion | `test_demo_schedule_and_account_permissions_match_documented_fixture` requires Cinque giorni in montagna | Killed |
| S-77 | Vacation start: today+18 to today-18 | Weak date assertion | Freeze today at 2026-12-01 and require start 2026-12-19 | Killed |
| S-79 | Vacation start offset 18 to 19 | Missing exact boundary assertion | Same test rejects start 2026-12-20 | Killed |
| S-80 | Vacation end: today+22 to today-22 | Weak date assertion | Require end 2026-12-23; changed/reversed interval is detected | Killed |
| S-82 | Vacation end offset 22 to 23 | Missing exact boundary assertion | Require end 2026-12-23, not 2026-12-24 | Killed |
| S-83 | Add XX markers to vacation note | Weak content assertion | Exact expected note rejects extra markers | Killed |
| S-84 | Lowercase vacation note | Weak content assertion | Exact expected note preserves its documented capitalization | Killed |
| S-85 | Uppercase vacation note | Weak content assertion | Exact expected note rejects uppercase text | Killed |
| S-97 | Omit permit note | Weak content assertion | Require Visita medica on the permit record | Killed |
| S-104 | Permit start: today-25 to today+25 | Weak date assertion | Fixed clock requires start and end both 2026-11-06 | Killed |

## All final survivors and scope

Final survivors: E-8, S-69 and S-123. S-123 omits the teammate request's
vacation type and is equivalent for the same model-default reason as S-69.
Equivalence applies to the current model and stored/HTTP observations; a
future default change requires reanalysis. No final survivor is a known
killable test gap. All core models/serializers/views mutants were killed.

Most historical examples are in demo support code. They must not be claimed
as 15 survivors confined to DR-001: this is an expanded application scope.
The source hashes and exact changes for every mutant are in `final/results.json`.
Both custom operators run: inclusive overlap boundaries become exclusive,
and the overlap existence predicate is inverted; their mutants are killed.
mutmut 3.8.1 skips decorated functions, including properties and API views;
the old calendar operator never reached business_days. Two separate temporary
source-copy mutations now verify weekend counting and inclusive final dates
(`property-rules/results.json`, both killed). These are separate from the
standard 299-mutant score. API tests exercise the decorated views, but that
does not mean those views were mutated.
