# Endpoint weaknesses — defect records for triage (Area 2)

25 November 2026. **Drafts for GitHub Issues.** DEF-A2-01 is filed as [#25](https://github.com/eshalfatima2006/LeaveFlow/issues/25) and DEF-A2-02 as [#26](https://github.com/eshalfatima2006/LeaveFlow/issues/26); DEF-A2-03 to 06 are not filed (PENDING). Severity and priority are proposals until shared triage ([DEFECT-MANAGEMENT-PLAN](../planning/DEFECT-MANAGEMENT-PLAN.md)). All were observed by executed tests against the unchanged application (baseline `bada9a0`, tests at `707a5b3`). The tests that pin them are characterizations: they pass while the defect exists and must be replaced when it is fixed. No application code was changed. The root causes of 03–06 come from reading the source. 01 and 02 have issue texts and root cause analyses with experiments (drafts for student review): [issue 1](ISSUE-MAJOR-01-BALANCE-OVERDRAW.md), [RCA 1](RCA-MAJOR-01-BALANCE-OVERDRAW.md), [issue 2](ISSUE-MAJOR-02-CONCURRENT-SUBMISSIONS.md), [RCA 2](RCA-MAJOR-02-CONCURRENT-SUBMISSIONS.md). Independent reproduction: DEF-A2-01 and DEF-A2-02 independently confirmed by Muhammad Bilal, 27 November 2026 (below); DEF-A2-03 to 06 PENDING. Triage: PENDING.

| ID | Weakness | Severity / priority (proposed) | Risk | Test | Status |
|---|---|---|---|---|---|
| DEF-A2-01 | Approval overdraws the allowance | S2 / P1 | PR-01 | API-INT-001.03, .09; API-INT-002.05 | New, [#25](https://github.com/eshalfatima2006/LeaveFlow/issues/25) — rejection contract agreed (400) |
| DEF-A2-02 | Concurrent W1 submissions create overlapping or duplicate requests | S2 / P1 | PR-03 | API-INT-002.01, .02 | New, [#26](https://github.com/eshalfatima2006/LeaveFlow/issues/26) |
| DEF-A2-03 | Login returns 500 for a non-object JSON body | S3 / P2 | PR-06 | `test_login_non_object_json_characterization` | New |
| DEF-A2-04 | W2 returns 500 for a non-object JSON body | S3 / P2 | PR-06 | `test_decide_non_object_json_characterization` | New |
| DEF-A2-05 | W1 returns 500 for `end_date` 9999-12-31 | S3 / P3 | PR-06 | `test_submit_maximum_date_characterization` | New |
| DEF-A2-06 | A teamless manager is notified of a teamless employee's request but cannot see it | S3 / P3 | PR-12 | `test_dt004_teamless_requester_characterization` | New — policy question (GAP-08) |

Evidence: `docs/sqe/evidence/integration/completion-2026-11-25/` (01), `docs/sqe/evidence/concurrency/postgresql17-2026-11-25/` (01, 02), `docs/sqe/evidence/api/contract-2026-11-25/` (03–05), `docs/sqe/evidence/structural/decision-tables-2026-11-25/` (06).

## DEF-A2-01 — Approval overdraws the allowance (GAP-01, EC-01)

- **Reproduce:** allowance 5; the employee submits 2026-12-07..10 and 2026-12-14..17 (four days each, both 201); a manager approves both.
- **Expected (EC-01; contract agreed 25 Nov 2026):** the second approval returns 400 `{"detail": "Insufficient leave balance"}`, the second request stays pending with `decided_by` null, its owner and audit fields are unchanged, the first approval is the only charge, 1 day remains.
- **Observed:** both 200; available −3. The three-day variant gives −1. Two approvers acting together give the same result on PostgreSQL.
- **Reproduction status:** Independently confirmed by Muhammad Bilal, 2026-11-27 (commit `8ee5176`, in-memory SQLite; regression `200 != 400`). Evidence: [issue-25-independent-evidence.zip](https://github.com/user-attachments/files/35516410/issue-25-independent-evidence.zip) on [#25](https://github.com/eshalfatima2006/LeaveFlow/issues/25).
- **Root cause:** `decide_request` (`backend/leave/views.py`) has no balance check; W1 checks `available_days`, but pending requests reserve nothing.
- **Proposed fix:** check the balance inside the decision transaction, with the owner's `LeaveBalance` row locked. Locking the request row alone would not serialize two different requests.
- **Retest:** the regression DT-001 W2 R3 (`SQE_DESIRED_RULES=1`, fails on the baseline) must pass; then replace API-INT-001.03/.09 and API-INT-002.05 with the agreed 400. **Residual risk:** open, score 25, release-blocking under EC-01.

## DEF-A2-02 — Concurrent submissions bypass the overlap rule

- **Reproduce:** two simultaneous `POST /api/requests/` by one employee with overlapping (or identical) dates, both past validation before either inserts. Run `scripts/sqe/run_concurrency.py`.
- **Expected (BR-02):** one 201 and one 400 `Esiste già una richiesta sovrapposta.`, one row.
- **Observed (PostgreSQL 17.12):** both 201, two active rows. A sequential repeat is refused correctly (API-INT-001.08).
- **Reproduction status:** Independently confirmed by Muhammad Bilal, 2026-11-27 (commit `8ee5176`, PostgreSQL 17.12; 5/5). Evidence: [issue-26-independent-evidence.zip](https://github.com/user-attachments/files/35516520/issue-26-independent-evidence.zip) on [#26](https://github.com/eshalfatima2006/LeaveFlow/issues/26).
- **Root cause:** `LeaveRequest.clean` queries and `create` inserts later, without a lock, a transaction around both, or a database constraint. The test holds both requests between the two steps with a barrier. Over real HTTP without the barrier it depends on the server: 0 of 100 pairs with the shipped single worker, 99 of 100 with two workers, 100 of 100 with three servers (RCA 2).
- **Proposed fix:** a lock on the employee row around check and insert, plus a PostgreSQL exclusion constraint as defence in depth (RCA 2; a transaction alone does not fix it).
- **Retest:** API-INT-002.01/.02 expecting [201, 400]. **Residual risk:** open.

## DEF-A2-03 and DEF-A2-04 — 500 for a non-object JSON body

- **Reproduce:** `POST /api/auth/login/`, or `POST /api/requests/{id}/decision/` as a manager, with body `[]`, `"x"`, `5` or `null` (application/json).
- **Expected:** 400 with `detail`, as for other malformed input. **Observed:** 500; nothing is written.
- **Root cause:** `request.data.get(...)` assumes an object (`login_view`, `decide_request`). W1 is not affected, because its serializer checks the type.
- **Proposed fix:** validate with a serializer, or reject a non-mapping body. Login needs no credentials, so anyone can trigger its 500.
- **Retest:** contract tests expecting 400. **Residual risk:** open (availability and log noise; no data exposure observed).

## DEF-A2-05 — 500 for the maximum date

- **Reproduce:** W1 with `start_date` 9999-12-30 and `end_date` 9999-12-31. **Expected:** 400, or 201 if policy allows it. **Observed:** 500, no row.
- **Root cause:** `business_days` adds one day after the last day and exceeds `date.max` (OverflowError). The loop is also linear in the interval length and runs before the balance check.
- **Proposed fix:** bound the interval length, or stop the loop before incrementing past `end_date`. **Residual risk:** open.

## DEF-A2-06 — Teamless recipient mismatch

- **Reproduce:** an employee without a team submits; a manager without a team exists. **Expected:** recipients can act on the request, or policy says otherwise (undecided). **Observed:** that manager is among the recipients, but `GET /api/requests/` does not list the request for them.
- **Root cause:** `Q(role=MANAGER, team_id=None)` matches as IS NULL in `build_leave_event`, while `visible_requests` requires a team.
- **Proposed fix:** require a team for manager recipients. **Residual risk:** low; decide the policy first.

## Correct behaviour confirmed by the same runs

- Concurrent decisions on one request: one 200 and one 409, the winner's audit kept, charged once (API-INT-002.03/.04). Both deciders were observed waiting for the row lock, and both tests fail when `select_for_update` is removed in a throwaway copy.
- Events are published only after commit, dropped on rollback, and a Redis failure does not undo a decision (`test_event_publication.py`, with a fake Redis client).
