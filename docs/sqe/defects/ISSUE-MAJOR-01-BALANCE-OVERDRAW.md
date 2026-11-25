<!-- Paste everything below this comment as the issue body; use the Title line as the issue title. The links work once the commit is pushed. Fill in PENDING fields from real events only. -->
**Title:** [W2] Approval succeeds when remaining leave balance would go negative

**Evidence classification:** executed (DEF-A2-01)

**Tested commit and working diff:** `53c4da3` (cause experiments), `707a5b3` (integration run). Application code is identical to baseline `bada9a0`; working diff: none in application code.

**Environment/profile, tool versions, DB/fixture/spec hashes:** Python 3.12.7, Django 6.0.7, DRF 3.17.1. Profile `sqe-memory-v1` (in-memory SQLite); also PostgreSQL 17.12 in a throwaway container. Fixture `tests/team/fixtures/leave_data.py` SHA-256 `db3f0129…`; OpenAPI spec `e5095486…`.

**FR / BR / risk IDs / test IDs:** FR-W2-05, FR-W1-05; BR-03; risk PR-01 (score 25); gap GAP-01 (rejection contract agreed); exit criterion EC-01. Tests API-INT-001.09 and .03 (implemented), API-INT-002.05 (concurrent form), OBJ-UC02-01 (not implemented).

**Severity proposal / priority proposal / rationale:** S2 Major / P1. Wrong entitlement in a selected workflow, reproducible every time, and the decision cannot be reopened through the API. It blocks release under EC-01. Final values: triage PENDING.

**Preconditions and synthetic initial state:** employee E and manager M in the same team; E has allowance 5 and no requests.

**Reproduction steps:**
1. As E, `POST /api/requests/` for 2026-12-07 to 2026-12-10 (4 working days) → 201, id A.
2. As E, `POST /api/requests/` for 2026-12-14 to 2026-12-17 (4 working days, no overlap) → 201, id B.
3. As M, `POST /api/requests/{A}/decision/` with `{"status": "approved"}` → 200.
4. As M, `POST /api/requests/{B}/decision/` with `{"status": "approved"}`.

Or run (the test passes while the defect exists):
```
.venv/bin/python scripts/sqe/run_tests.py team tests.team.integration.test_w1_w2_integration.ExitCriterionScenarioTests
```

**Expected result and test basis:** 400 `{"detail": "Insufficient leave balance"}`, B stays pending without a decider (`decided_by` and `decided_at` null), and 1 day remains. Basis: EC-01 and the BR-03 rule "approval must not produce A<0"; contract agreed by the team on 25 Nov 2026 (GAP-01).

**Observed result:** 200. Remaining balance **−3**.

**Persisted before/after (step 4):**

| | Before | After |
|---|---|---|
| Request B | pending, `decided_by` null, `decided_at` null | approved, `decided_by` = M, `decided_at` set |
| Balance (allowance, used, available) | 5, 4, 1 | 5, 8, **−3** |
| Request count | 2 | 2 |

**Frequency and independent reproduction:** every run, no timing involved; also with two approvers at once on PostgreSQL. All runs so far were by AI-assisted scripts for Member 2. Independent reproduction by another member: **PENDING** (name, date, commit).

**Logs and evidence:** [integration run](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/docs/sqe/evidence/integration/completion-2026-11-25/result.json), [PostgreSQL run](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/docs/sqe/evidence/concurrency/postgresql17-2026-11-25/result.json), [cause experiments](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/docs/sqe/evidence/defects/rca-2026-11-25/results.txt). Synthetic data; no tokens in the logs.

**Assigned owner / triage decision / status:** PENDING / PENDING / New

**Root cause and RCA link:** the rule "approved days ≤ allowance" was never specified for approval and is not checked there: [`backend/leave/views.py` lines 81–86](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/backend/leave/views.py#L81-L86) save the decision without reading the balance. The only check is at submission ([`serializers.py` lines 36–38](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/backend/leave/serializers.py#L36-L38)), where pending requests reserve nothing. [Full RCA](https://github.com/eshalfatima2006/LeaveFlow/blob/518684b4e3f7d104f97e169e717dcfde6920df76/docs/sqe/defects/RCA-MAJOR-01-BALANCE-OVERDRAW.md). Pareto category: Validation/Boundary.

**Corrective action (proposed):** in the decision transaction, lock the owner's `LeaveBalance` row, then refuse an approval whose days exceed the available days with 400 `{"detail": "Insufficient leave balance"}`, writing nothing. A check without that lock still overdraws with two simultaneous approvers (shown by experiment).

**Preventive action (proposed):** keep the rule and its agreed error contract in BR-03 and FR-W2-05 (recorded 25 Nov 2026); boundary regressions at available −1, equal and +1; the team suite in CI.

**Fix commit / real PR URL / regression ID:** PENDING / PENDING / replaces API-INT-001.03, .09 and API-INT-002.05

**Retest SHA, independent tester, actual result and evidence:** PENDING

**Residual risk / closure or reopen reason:** PR-01 open; release blocked under EC-01.