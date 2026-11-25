<!-- Paste everything below this comment as the PR #10 reply, after pushing. Check each statement first; change "will" lines if they are already done. -->
Thank you for the review. It covered head `0bf291a`. I checked each point against the code; the findings were valid, and the ones below are fixed. No application code, CI workflow or assertion was changed to make a test pass.

**Result:** team suite **344/344**, upstream 9/9, plus 5/5 concurrency tests on PostgreSQL 17.12 (run separately). The team and upstream suites also passed from a fresh clone with a new virtual environment, where regeneration reproduced the committed files.

| You asked for | What was done | Commits |
|---|---|---|
| Decision tables | DT-001 to DT-005: 52 tests, 42 of them new. The W2 half of DT-001 is still blocked by GAP-01 | `bbb3174` `48610b0` |
| API contract verification | 41 contract tests compare real responses with the spec; missing responses added to the spec | `2d02e9c` `91d4dfa` |
| Complete generated inputs | 127 generated EP/BVA tests with a case manifest: paths, tokens, optional and null fields, whitespace, actor and record contexts, media types, methods. Exact status and error key; full row, balance and token readback | `3ebeb40` `a3d2e61` `ce0b53f` |
| Constraint changes that change the cases | Three reproducible patches (length, enum, nullable) that each change the cases and fail on the predicted tests | `a3d2e61` `9bb76cb` |
| Cross-workflow and events | Immediate repeat, EC-01 scenario, six after-commit publication tests (fake Redis client) | `45d4f7b` |
| API-INT-002 concurrency | Five tests on a throwaway PostgreSQL container. Removing the row lock makes the lock tests fail | `80f6773` |
| Measured API coverage | **TCL7**: all ten criteria 100%, computed from executed calls. The level mapping matches Lecture 20 and Martin-Lopez, Segura and Ruiz-Cortés (A-TEST 2019). Exclusions are listed in API-COVERAGE.md. The team still has to agree the target | `707a5b3` `9bb76cb` |
| Defect records | Six records, with issue text ready for the two major ones | `0bcfe9c` `460f9ff` |
| Root cause analysis | 5 Whys, fishbone, corrective and preventive actions for both major defects, with experiments that confirm or refute each cause | `53c4da3` `5e73356` `1967845` |
| EC-05 and GAP-02 status | Updated | `0bcfe9c` `ad45d23` |

**Two proposed S2 Major defects.** Their tests are characterizations: they pass while the defect exists, so 344/344 does not mean these rules hold.

1. **Approval overdraws the balance** (PR-01): allowance 5, two approved 4-day requests, remaining −3. Cause: the rule is not specified or checked at approval. Experiments also show that a check alone is not enough; the balance row must be locked.
2. **Concurrent submissions both succeed** (PR-03): two overlapping requests are stored. Over real HTTP it needs two server processes: 0 of 100 pairs with the shipped single worker, 99 of 100 with two workers, 100 of 100 with three servers, the number of replicas the shipped autoscaler allows. A transaction alone does not fix it.

I will file both as separate issues, each with its full RCA:
`docs/sqe/defects/RCA-MAJOR-01-BALANCE-OVERDRAW.md` and `docs/sqe/defects/RCA-MAJOR-02-CONCURRENT-SUBMISSIONS.md`.

**Still open:**
- **Independent reproduction and triage** of both defects. Until another member reproduces them, EC-10 is not met. The commands are in each issue text; a reproduction from you would help.
- The rejection contract for an over-allowance approval (EC-01, GAP-01), the TCL target, and the notification scope.
- The fixes themselves, with independent retest.
- CI still runs only the upstream backend tests; a proposed job is in `docs/sqe/openapi/README.md` (Member 1's area).
- Delivery of notifications through the worker and browser (UC-07).

AI assistance is recorded in `docs/sqe/AI-USE-RECORD.md`.