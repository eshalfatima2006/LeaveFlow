<!-- Paste everything below this comment as the PR #10 description, after pushing. Check each statement first. -->
## Area 2: API testing, OpenAPI test generation, integration and concurrency (Member 2)

Tests for W1 (submit a leave request) and W2 (approve or reject it) through the real API, generated from an OpenAPI spec, with cross-workflow, concurrency and coverage evidence. **No application code or CI workflow is changed.**

### Test results (27 Nov 2026)

| Suite | Command | Result |
|---|---|---|
| Team suite (in-memory SQLite) | `.venv/bin/python scripts/sqe/run_tests.py team` | **354/354 passed** |
| Upstream tests | `.venv/bin/python scripts/sqe/run_tests.py upstream` | 9/9 passed |
| Concurrency, API-INT-002 (throwaway PostgreSQL 17.12 container) | `.venv/bin/python scripts/sqe/run_concurrency.py` | **5/5 passed** |
| Desired-rule regression DT-001 W2 R3 (#25) | `SQE_DESIRED_RULES=1 .venv/bin/python scripts/sqe/run_tests.py team tests.team.structural.test_decision_table.W2ApprovalOverdrawRegression` | **1/1 fails, as expected** until #25 is fixed |
| Spec-change demonstrations v2, v3, v4 | see `docs/sqe/openapi/README.md` | fail on exactly the 2, 1 and 1 predicted tests |

**A passing suite does not mean the rules hold.** Five tests are characterizations of the two major defects: they pass *because* the defects exist. API-INT-001.03 and .09 and API-INT-002.05 pin the overdraw (#25), and API-INT-002.01 and .02 pin the concurrent submissions (#26). The desired-rule regression for #25 is kept out of the default suite so it does not stay red; it is run on its own, as shown above.

Evidence: `docs/sqe/evidence/concurrency/postgresql17-2026-11-27/`, `docs/sqe/evidence/structural/dt001-w2-2026-11-27/`, `docs/sqe/evidence/api/coverage-2026-11-27/`.

### What the PR contains

- **Functional API tests** for W1 and W2: inputs, authorization, state transitions, and persisted data read back.
- **OpenAPI spec** `docs/sqe/openapi/leaveflow-api.yaml`, checked against real responses by 41 contract tests.
- **Generated EP/BVA tests**: 127 tests from the spec, with a case manifest. Three documented constraint changes each regenerate and fail where predicted.
- **Decision tables DT-001 to DT-005**, now including the W2 half of DT-001: rejecting an over-limit request, no balance record, and approval to exactly 0 days (allowance 4, 4 days → 200).
- **Cross-workflow, event and concurrency tests**: API-INT-001, event publication after commit, and API-INT-002 on PostgreSQL.
- **Measured API coverage**: TCL7, with all ten criteria at 100% (`docs/sqe/testing/API-COVERAGE.md`).
- **Defect records and root cause analyses** for the two major defects.

### Changes since the last review

- **Operation-flow matching fixed.** A flow now counts only when each step returns its documented status and its conditions hold: decision value, same request or dates, and acting user. Previously "approve then submit" was counted as "reject then resubmit". Negative tests are in `tests/team/foundation/test_flow_matcher.py`. All 8 flows are still covered by tests that really follow them.
- **DT-001 W2 regression rows.** The overdraw row asserts the agreed contract: 400 `{"detail": "Insufficient leave balance"}`, the request stays pending, `decided_by` stays null, and 1 day remains. It fails against the current application (200, −3) and passed against a candidate fix in a throwaway copy.
- **Generator fixes.**
  - A null note in the readback no longer crashes it.
  - A fixture allowance of 0 or 1 no longer produces a 0-day interval, which had crashed the generator with `OverflowError`.

### Defects found (proposed S2 Major)

- **#25: an approval can overdraw the leave balance** (allowance 5, two approved 4-day requests → −3). The rejection contract is agreed.
- **#26: two simultaneous submissions can both be stored**, overlapping. This needs more than one server process; the shipped single worker did not show it in 100 attempts.

Root cause analyses: `docs/sqe/defects/RCA-MAJOR-01-BALANCE-OVERDRAW.md` and `RCA-MAJOR-02-CONCURRENT-SUBMISSIONS.md`.

### Pending

- **CI integration is pending coordination with the CI owner (Member 1, Area 1).** `.github/workflows/ci.yml` still runs only the upstream tests. A proposed job for the team suite is in `docs/sqe/openapi/README.md`. The PostgreSQL suite needs Docker on the runner.
- Fixes for #25 and #26 and their independent retest. Independent reproduction by another member is also pending.
- Team decisions: the target TCL level, and what approval should do when an employee has no balance record (GAP-07).

AI assistance is recorded in `docs/sqe/AI-USE-RECORD.md`.
