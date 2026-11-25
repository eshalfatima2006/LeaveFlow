<!-- Paste everything below this comment as the issue body; use the Title line as the issue title. The links work once the commit is pushed. Fill in PENDING fields from real events only. -->
**Title:** [W1] Concurrent leave submissions both succeed creating duplicate requests

**Evidence classification:** executed (DEF-A2-02)

**Tested commit and working diff:** `53c4da3` (HTTP run and cause experiments), `707a5b3` (API-INT-002). Application code is identical to baseline `bada9a0`; working diff: none in application code.

**Environment/profile, tool versions, DB/fixture/spec hashes:** Python 3.12.7, Django 6.0.7, DRF 3.17.1, gunicorn 26.0.0, psycopg 3.3.4, PostgreSQL 17.12 (`postgres:17-alpine`, throwaway container, data in memory). Profile `sqe-postgres-v1`. Fixture SHA-256 `db3f0129…`; OpenAPI spec `e5095486…`.

**FR / BR / risk IDs / test IDs:** FR-W1-04, FR-W1-06; BR-02; risk PR-03 (score 15), related to PR-10 (duplicates from a repeated request; recovery itself not tested). Exit criterion EC-03. Tests API-INT-002.01 (overlapping) and .02 (identical).

**Severity proposal / priority proposal / rationale:** S2 Major / P1. Breaks the no-overlap rule and stores duplicate active requests. For triage: it needs **at least two server processes** (see frequency). Final values: PENDING.

**Preconditions and synthetic initial state:** one employee with a token and enough allowance, no requests in the chosen week; backend on PostgreSQL with two or more worker processes or replicas.

**Reproduction steps:**
1. Start the backend on a disposable PostgreSQL: `gunicorn config.wsgi:application --workers 2`.
2. At the same moment, send two `POST /api/requests/` with the same employee's token and overlapping dates, for example 2026-12-07 to 2026-12-09 and 2026-12-08 to 2026-12-10, or two identical bodies.

Or run:
```
.venv/bin/python scripts/sqe/run_concurrency.py             # forced order; passes while the defect exists
docs/sqe/defects/rca-experiments/run_rca.sh NEW_DIR         # includes the HTTP run below
```

**Expected result and test basis:** one 201, one 400 `{"non_field_errors": ["Esiste già una richiesta sovrapposta."]}`, one row. Basis: BR-02, FR-W1-04. Sequentially the application does exactly this (API-INT-001.08).

**Observed result:** 201 and 201.

**Persisted before/after:** 0 rows before; 2 pending rows for the same employee and overlapping (or identical) dates after. Balance unchanged (10, 0, 10), as pending requests reserve nothing.

**Frequency and independent reproduction:** API-INT-002.01/.02 with the order forced between check and insert: every run. Real HTTP, no test hook, 100 identical pairs per row:

| Server | Both 201 | One 201, one 400 |
|---|---|---|
| 1 sync worker (shipped command) | 0 | 100 |
| 2 workers | 99 | 1 |
| 3 one-worker servers (stand-in for the 3 replicas the shipped autoscaler allows) | 100 | 0 |

All runs so far were by AI-assisted scripts for Member 2. Independent reproduction by another member: **PENDING** (name, date, commit).

**Logs and evidence:** [PostgreSQL run](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/docs/sqe/evidence/concurrency/postgresql17-2026-11-25/result.json), [HTTP run](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/docs/sqe/evidence/defects/rca-2026-11-25/http.txt), [cause experiments](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/docs/sqe/evidence/defects/rca-2026-11-25/results.txt). Synthetic data; no tokens in the logs.

**Assigned owner / triage decision / status:** PENDING / PENDING / New

**Root cause and RCA link:** the overlap rule is a check in Python ([`models.py` lines 83–90](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/backend/leave/models.py#L83-L90)) followed by a separate insert ([`serializers.py` lines 41–42](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/backend/leave/serializers.py#L41-L42)), with no lock and no database constraint. [Full RCA](https://github.com/eshalfatima2006/LeaveFlow/blob/19678451f98fd1f030085928697cd912bba419fb/docs/sqe/defects/RCA-MAJOR-02-CONCURRENT-SUBMISSIONS.md). Pareto category: State/Transaction.

**Corrective action (proposed):** lock the employee's row in a transaction around validation and insert (experiment: 50 of 50 pairs gave [201, 400]); add a PostgreSQL exclusion constraint as defence in depth, with its errors mapped to the BR-02 400. `transaction.atomic` alone does **not** fix it (50 of 50 still both 201). SERIALIZABLE works only with a retry.

**Preventive action (proposed):** run the PostgreSQL concurrency tests in CI; state in BR-02 that the rule holds under simultaneous requests.

**Fix commit / real PR URL / regression ID:** PENDING / PENDING / replaces API-INT-002.01 and .02

**Retest SHA, independent tester, actual result and evidence:** PENDING

**Residual risk / closure or reopen reason:** PR-03 open; EC-03 affected.