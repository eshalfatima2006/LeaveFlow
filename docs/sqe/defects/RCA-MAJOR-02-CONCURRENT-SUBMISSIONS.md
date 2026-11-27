# RCA 2 — Concurrent submissions create overlapping requests (DEF-A2-02)

Version 0.1 — 25 November 2026. AI-assisted draft for student review. Issue: [#26](https://github.com/eshalfatima2006/LeaveFlow/issues/26) (text in [ISSUE-MAJOR-02](ISSUE-MAJOR-02-CONCURRENT-SUBMISSIONS.md)). Independent reproduction, triage, severity and fix: **PENDING**. No application code was changed.

## 1. Problem statement

Two simultaneous `POST /api/requests/` from one employee with overlapping or identical dates both return 201, and two active requests are stored for the same days. Sent one after the other, the second is refused correctly.

- **Rule:** BR-02 (no overlap with a pending or approved request); FR-W1-04, FR-W1-06. **Risk:** PR-03 (score 15); related to PR-10, because a client that repeats a request without waiting for the answer gets duplicates. Failure and recovery themselves were not tested here.
- **Proposed severity / priority:** S2 Major / P1. Triage should weigh the exposure below.
- **Impact:** duplicate active requests. A manager can approve both; the same working days are then charged twice (`approved_days` adds both rows, `backend/leave/models.py:35–39`; this last step is from source, not executed here).

### Exposure: how the server runs decides whether it can happen

Real HTTP, real `gunicorn` 26.0.0, unmodified application, PostgreSQL 17.12, 100 simultaneous pairs each, no test hook in the server:

| Server | Both 201 | One 201, one 400 |
|---|---|---|
| 1 sync worker, the shipped command (`backend/Dockerfile`, `deploy/k8s/base/core/backend.yaml`) | **0** | 100 |
| 2 worker processes | **99** | 1 |
| 3 one-worker servers, the two requests sent to different ones | **100** | 0 |

So the defect **cannot be shown with the default single worker**, which handles one request at a time. It appears as soon as two processes serve requests. The repository ships that configuration: `deploy/k8s/base/core/autoscaling.yaml` scales the backend to 3 replicas. The three-server row stands in for those replicas; a Kubernetes cluster was not run.

### Reproduction

Automated, with the order forced between check and insert:

```
.venv/bin/python scripts/sqe/run_concurrency.py        # API-INT-002.01 and .02 (characterizations: pass while the defect exists)
docs/sqe/defects/rca-experiments/run_rca.sh NEW_DIR    # cause experiments and the HTTP table above
```

By hand: start the backend on a disposable PostgreSQL with `gunicorn config.wsgi:application --workers 2`, then send two identical `POST /api/requests/` at the same moment with one employee's token.

| | Responses | Rows |
|---|---|---|
| Expected (BR-02) | one 201, one 400 `Esiste già una richiesta sovrapposta.` | 1 |
| Observed | 201, 201 | 2 |

Evidence: [concurrency run](../evidence/concurrency/postgresql17-2026-11-25/result.json), [cause experiments](../evidence/defects/rca-2026-11-25/results.txt), [HTTP run](../evidence/defects/rca-2026-11-25/http.txt).

### Timeline

| Date | Commit | Event |
|---|---|---|
| 17 Jul 2026 | `631bf2a` | First release: overlap query, then insert, no constraint |
| 7 Aug 2026 | `efd8f41` | Kubernetes deployment added |
| 18 Aug 2026 | `fef0a37` | "serialize leave request decisions": W2 gets a transaction and a row lock. W1 is not changed |
| 22 Nov 2026 | — | Predicted from source (PR-03) |
| 25 Nov 2026 | `80f6773` | Executed on PostgreSQL (API-INT-002.01, .02), then over HTTP (`53c4da3`) |

## 2. Five Whys

| # | Why? | Answer | Evidence | Alternative considered | Confidence |
|---|---|---|---|---|---|
| 1 | Why are two overlapping rows stored? | Both requests ran the overlap query before either had inserted | API-INT-002.01/.02; HTTP run: 199 date ranges stored twice | The query is wrong. Refuted: sequential overlap → 400, adjacent dates → 201 | High |
| 2 | Why did the check not see the other request? | The query (`backend/leave/models.py:83–90`) and the insert (`serializers.py:42`) are separate statements in autocommit; `requests_view` (`views.py:54–61`) has no transaction and `ATOMIC_REQUESTS` is not set | Source. A transaction alone changes nothing: `w1-atomic-only` → both 201, 50 of 50 | "It only needs `transaction.atomic`." **Refuted** by that run: at READ COMMITTED neither request sees the other's uncommitted row | High |
| 3 | Why did nothing make the second request wait? | W1 takes no lock, and the conflicting row does not exist yet, so there is no row of that kind to lock | Locking the employee's existing requests (`w1-lock-overlapping-rows`) still stores both when there are none (forced order 201, 201; 1 of 50 natural pairs, the first, after which older rows acted as a lock by accident). Locking the **employee row** → 201, 400 in 50 of 50 | "It only needs `select_for_update`." Only on a row that always exists | High |
| 4 | Why did the database accept both? | `LeaveRequest` has no constraint: `Meta` only has `ordering`, and `0001_initial` defines none for the table. The rule exists only in Python | Source; with an exclusion constraint in the experiment, one row is stored (23P01) | A unique constraint would do. It stops identical dates only, not overlapping ones | High |
| 5 | Why was this not designed for or found? | Simultaneous submission was never specified or tested. The concurrency work of `fef0a37` covered decisions only; the upstream overlap test inserts the first row before posting (`backend/leave/tests.py:40–48`); CI uses SQLite (no database service in the backend job); the default single worker hides it | Those files; upstream 9/9 and all 344 team tests on SQLite pass **both with and without** the fix (`impact.txt`) | The risk was accepted. No record of that | Medium (the authors were not asked) |

**Root cause (actionable):** BR-02 is an invariant across rows, but it is enforced only by a check-then-insert in application code, with no lock and no database constraint. **Control failure:** no requirement and no test covered simultaneous submissions, and the default database and worker setup hide the problem.

## 3. Fishbone

```
 Code/Logic              Data/State            Concurrency/Transactions
 check then insert,      no constraint on      autocommit, no shared lock
 no lock (CONFIRMED)     the table (CONFIRMED) (CONFIRMED)
       \                      \                      \
        \                      \                      \
=========+======================+======================+=======>  EFFECT: two active
        /                      /                      /           requests for the same days
       /                      /                      /
 Specification/Policy    Process/Review/Test   Tools/Environment    People/Knowledge
 concurrent W1 never     no concurrency test;  SQLite + 1 worker    [not established]
 specified (CONTRIB.)    CI on SQLite          hide it (CONFIRMED)
                         (CONFIRMED control failure)
```

| Category | Hypothesis | Supporting / refuting evidence | Status |
|---|---|---|---|
| Code/Logic | Check and insert are separate and unlocked | `models.py:83–90`, `serializers.py:30–42`; locking the employee row fixes it | **Confirmed** direct cause |
| Code/Logic | The overlap condition is wrong | Sequential cases correct; boundary and DT-002 tests pass | Ruled out |
| Code/Logic | `select_for_update` on the matching requests is enough | Still 201, 201 when none exist | Refuted |
| Data/State | No database constraint on date ranges | `0001_initial`, `Meta`; with the constraint one row is stored | **Confirmed** |
| Concurrency/Transactions | Default autocommit, READ COMMITTED | True, but a transaction alone changes nothing (50 of 50 both 201) | **Confirmed** contributing; not sufficient as a fix |
| Concurrency/Transactions | W2 has the same problem | Approve/approve and approve/reject of one request → [200, 409] (API-INT-002.03/.04) | Ruled out (see RCA 1 for two requests on one balance) |
| Specification/Policy | BR-02 does not mention simultaneous requests | BR-02 text; TEST-BASIS risk C | **Confirmed** contributing |
| Process/Review/Test design | No concurrency test existed | `backend/leave/tests.py` has none; first one is `80f6773` | **Confirmed** control failure |
| Process/Review/Test design | The August locking change was not extended to W1 | `fef0a37` changes `decide_request` only | **Confirmed** contributing |
| Tools/Environment | The default setup hides it | 1 worker 0 of 100, 2 workers 99 of 100; CI on SQLite | **Confirmed** detection gap |
| People/Knowledge | The authors did not know the pattern | They used it correctly in W2; why not W1 is unknown | Not established |

**Investigate first (circled):** Data/State and Concurrency/Transactions. Both were, with the results above.

## 4. Corrective action (proposed; not implemented)

| Option | Experiment (forced order / 50 natural pairs) | Assessment |
|---|---|---|
| **A. Lock the employee's `User` row** (`select_for_update`) in a transaction around validation and insert | [201, 400] / 50 of 50 [201, 400] | Smallest change; the second request gets the existing BR-02 error. Protects this endpoint only |
| **B. Exclusion constraint** on employee and `daterange(start, end, '[]')` where status is pending or approved | one row; the second request fails with 23P01, or with a deadlock error 40P01 in some runs | Protects every writer, including Django Admin. Needs `btree_gist` (extension rights), PostgreSQL only, existing duplicates cleaned first, and both errors mapped to the BR-02 400; unmapped they are 500 |
| **C. SERIALIZABLE transaction** | one row; the second request fails with 40001 | Works only with a retry; unmapped it is a 500 |
| `transaction.atomic` only; or locking the matching requests | both 201 / see Why 2–3 | **Do not use:** does not fix it |

**Recommendation:** A now, for correct API behaviour, and B as defence in depth. Diffs of every variant are in the [evidence](../evidence/defects/rca-2026-11-25/); they are experiments, not the fix.

**Impact of A:** upstream 9/9 and team 344/344 still pass, which also shows those SQLite suites cannot see this defect. API-INT-002.01/.02 must be replaced by regressions expecting [201, 400] and one row.

| Owner | Fix commit / PR | Independent retest |
|---|---|---|
| PENDING | PENDING | PENDING |

## 5. Preventive action (proposed)

| Action | What it prevents | Owner | Completion evidence |
|---|---|---|---|
| Run `scripts/sqe/run_concurrency.py` in CI (it starts its own throwaway PostgreSQL) | Races invisible to SQLite | Member 1 — PENDING | Required check on a PR |
| Extend it: W1 submit against W2 decision, and the HTTP run with 2 workers as a scheduled job | Hook-only evidence | Member 2 — PENDING | Run logs |
| State in BR-02 that the rule holds under simultaneous requests; review checklist question: "is a rule across rows protected by a lock or a constraint?" | Check-then-act rules | Shared — PENDING | Reviewed change |

**Effectiveness check:** after the fix, remove the lock (or constraint) in a throwaway copy; API-INT-002.01/.02 must fail. Repeat the HTTP table; "both 201" must be 0 in every row.

## 6. Classification and closure

- **Primary root-cause category (Pareto): State/Transaction.** API-INT-002.01 and .02 are one defect. It is independent of RCA 1: that one happens without concurrency, has another cause, and neither experimental fix changes the other defect.
- **Residual risk:** PR-03 stays open; EC-03 affected.
- **Closure:** PENDING (triage, fix, independent retest, regression in CI).