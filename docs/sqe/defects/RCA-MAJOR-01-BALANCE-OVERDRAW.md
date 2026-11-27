# RCA 1 — Approval overdraws the leave balance (DEF-A2-01)

Version 0.3 — 27 November 2026 (v0.3: independent reproduction confirmed; v0.2: agreed rejection contract recorded). AI-assisted draft for student review. Issue: [#25](https://github.com/eshalfatima2006/LeaveFlow/issues/25) (text in [ISSUE-MAJOR-01](ISSUE-MAJOR-01-BALANCE-OVERDRAW.md)). Independent reproduction: **CONFIRMED** by Muhammad Bilal (@Bilalmughal-07) on 27 November 2026 at commit `8ee5176`, from a clean checkout on in-memory SQLite (`sqe-memory-v1`): the characterization `ExitCriterionScenarioTests` passed (allowance 5, two approved 4-day requests, balance −3) and the desired-rule regression `W2ApprovalOverdrawRegression` failed with `AssertionError: 200 != 400`. Evidence: [issue-25-independent-evidence.zip](https://github.com/user-attachments/files/35516410/issue-25-independent-evidence.zip) ([comment](https://github.com/eshalfatima2006/LeaveFlow/issues/25#issuecomment-7220515359)). Triage, severity and fix: **PENDING**. No application code was changed.

## 1. Problem statement

When a manager approves a request whose days exceed the employee's remaining allowance, the approval succeeds and the remaining balance becomes negative. With allowance 5 and two 4-day requests, it becomes **−3**.

- **Rule:** BR-03 rule "approval must not produce A<0"; FR-W2-05; exit criterion EC-01. **Risk:** PR-01 (score 25). **Gap:** GAP-01.
- **Agreed contract (team, 25 Nov 2026):** an approval that would make the balance negative returns 400 `{"detail": "Insufficient leave balance"}`. The request stays pending, `decided_by` stays null and the balance is unchanged.
- **Proposed severity / priority:** S2 Major / P1.
- **Impact:** the employee holds more approved leave than the allowance, and the decision is final (no endpoint reopens it, BR-05). The employee's later submissions are refused while the balance is negative. Source only, not executed here: the dashboard gauge clamps a negative balance to zero (GAP-05).

### Reproduction

Environment: Django 6.0.7, DRF 3.17.1, Python 3.12.7. Profile `sqe-memory-v1` (in-memory SQLite), and PostgreSQL 17.12 in a throwaway container. Synthetic data only.

1. Employee E, same team as manager M. Allowance 5, no requests.
2. As E: `POST /api/requests/` for 2026-12-07..2026-12-10 (4 working days) → 201, id A.
3. As E: `POST /api/requests/` for 2026-12-14..2026-12-17 (4 working days) → 201, id B.
4. As M: `POST /api/requests/{A}/decision/` `{"status":"approved"}` → 200. Balance: allowance 5, used 4, available 1.
5. As M: `POST /api/requests/{B}/decision/` `{"status":"approved"}`.

| | Response to step 5 | Row B | Balance (allowance, used, available) |
|---|---|---|---|
| Expected (EC-01; agreed contract) | 400 `{"detail": "Insufficient leave balance"}` | unchanged, pending, no decider | 5, 4, 1 |
| Observed | 200 | approved, decider M, time set | 5, 8, **−3** |

Executable form: `API-INT-001.09` in `tests/team/integration/test_w1_w2_integration.py`:

```
.venv/bin/python scripts/sqe/run_tests.py team tests.team.integration.test_w1_w2_integration.ExitCriterionScenarioTests
```

It is a characterization: it **passes while the defect exists**. Evidence: [integration run](../evidence/integration/completion-2026-11-25/result.json), [cause experiments](../evidence/defects/rca-2026-11-25/results.txt). **Frequency:** every time; no timing is involved.

### Timeline

| Date | Commit | Event |
|---|---|---|
| 17 Jul 2026 | `631bf2a` | First release. The balance check exists in the submission serializer only |
| 18 Aug 2026 | `fef0a37` | The decision view is rewritten inside a transaction with a row lock. No balance check is added |
| 22 Nov 2026 | — | Predicted from source (PR-01, GAP-01) |
| 24 Nov 2026 | — | First executed: 3+3 days, allowance 5 → −1 (API-INT-001.03) |
| 25 Nov 2026 | `45d4f7b` | EC-01 scenario executed → −3 (API-INT-001.09); on PostgreSQL in `80f6773` (API-INT-002.05) |

## 2. Five Whys

| # | Why? | Answer | Evidence | Alternative considered | Confidence |
|---|---|---|---|---|---|
| 1 | Why did the balance become −3? | The second approval was stored: 4 + 4 approved days against an allowance of 5 | API-INT-001.09; balance is `allowance − sum(approved days)`, `backend/leave/models.py:35–43` | A wrong sum. Refuted: 8 used days is the correct total | High |
| 2 | Why was it accepted? | `decide_request` checks role, decision value, scope, self-decision and pending state (`backend/leave/views.py:68–82`), then saves (`83–86`). It never reads the allowance or the approved days | Source; with a check added in a throwaway clone (`w2-check-only`) the second approval is refused, row B is unchanged and 1 day remains | Two approvals racing. Refuted: it happens with one manager, one after the other | High |
| 3 | Why did the check at submission not prevent it? | `backend/leave/serializers.py:36–38` compares one request with the balance at that moment, and pending requests reserve nothing. Each 4-day request fits in 5. The balance is consumed later, at approval, where nothing compares | Both submissions return 201; A2.1 `test_pending_requests_reserve_no_allowance` | The submission check itself is wrong. Refuted: available −1, equal and +1 are tested and correct | High |
| 4 | Why is there no check where the balance is consumed? | The rule was stated and coded for submission only. README lines 10, 24 and 44 mention balance validation of requests; none says what an approval must do. When the decision view was last reworked (`fef0a37`), only the state race was addressed | README; `git blame` (`serializers.py:36–38` from `631bf2a`, `views.py:81–86` from `fef0a37`) | Overdraw is allowed on purpose. Not supported by any source, but not excluded: the authors were not asked. For this project the team has agreed that it must be refused (25 Nov 2026) | Medium |
| 5 | Why did no control catch it? | No upstream test checks a balance. `backend/leave/tests.py:26` sets allowance 26 and the largest request is 5 days, so the limit is never approached; the approval test (`:51–63`) checks status only. CI runs only those tests | The upstream suite passes **9/9 both with and without** the check (`impact.txt`) | A test existed and was removed. Refuted: none in the file's history | High |

**Root cause (actionable):** the invariant *approved days ≤ allowance* was never specified for the approval event and is not enforced at the point where the balance is consumed. **Control failure:** no boundary or cross-workflow test of the balance existed, so the omission stayed invisible.

The chain stops here because the team can act on both. Why the original authors did not write the rule is not known and is not guessed.

## 3. Fishbone

```
 Code/Logic              Data/State            Concurrency/Transactions
 no check in decide      pending reserves      [not the cause; limits
 (CONFIRMED)             nothing (CONTRIB.)     the fix]
       \                      \                      \
        \                      \                      \
=========+======================+======================+=======>  EFFECT: approval
        /                      /                      /           leaves balance -3
       /                      /                      /
 Specification/Policy    Process/Review/Test   Tools/Environment    People/Knowledge
 approval rule not       no balance test;      [ruled out]          [not established]
 written (CONFIRMED)     CI upstream only
                         (CONFIRMED control failure)
```

| Category | Hypothesis | Supporting / refuting evidence | Status |
|---|---|---|---|
| Code/Logic | `decide_request` does not compare days with the balance | `views.py:68–86`; adding the check refuses the second approval and keeps 1 day | **Confirmed** direct cause |
| Code/Logic | Working days or the balance sum are wrong | Boundary tests for weekdays and balance pass; 8 is the correct total | Ruled out |
| Data/State | Pending requests do not reserve days, so several can exceed the balance together | `models.py:35–39` counts approved only; both submissions 201 | **Confirmed** contributing. Not sufficient alone: with a check at approval the overdraw is impossible |
| Data/State | The database could reject it | `allowance` is a positive integer, but the remaining balance is derived and not stored, so no column constraint can express the rule | Confirmed contributing |
| Concurrency/Transactions | A race causes the overdraw | Sequential approvals give −3 | Ruled out as the cause |
| Concurrency/Transactions | A check alone would be enough | `w2-check-only`: two approvers at the same time, held between check and save → both 200, −3. With the owner's balance row locked: [200, 409] and 1 day | **Refuted — constrains the fix** |
| Specification/Policy | The approval rule was never written | README lines 10, 24, 44; GAP-01. The baseline has no such rule; the team agreed one on 25 Nov 2026 | **Confirmed** root cause |
| Process/Review/Test design | Tests never approach the limit or check a balance | `tests.py:26`; upstream 9/9 with and without the check | **Confirmed** control failure |
| Process/Review/Test design | CI would have caught it | `.github/workflows/ci.yml` runs `manage.py test leave` only; the team suite is not in CI | **Confirmed** control failure |
| Tools/Environment | Only SQLite, or only PostgreSQL, behaves this way | Same −3 on both | Ruled out |
| People/Knowledge | The authors did not know the rule | No evidence either way | Not established |

**Investigate first (circled):** Specification/Policy and Code/Logic. Both were, with the results above.

## 4. Corrective action (proposed; not implemented)

1. **Contract agreed: 400 with insufficient balance message** (team, 25 Nov 2026): 400 `{"detail": "Insufficient leave balance"}`; request pending, `decided_by` null, balance unchanged. Rejecting an over-allowance request stays allowed (TEST-BASIS risk A, EC-01 controls).
2. In `decide_request`, inside the existing transaction, when the decision is `approved`: lock the **owner's** `LeaveBalance` row with `select_for_update()`, then return the agreed 400 if the request's days exceed `available_days`. Nothing is written and no event is published on refusal.
3. **Lock order:** request row, then balance row, everywhere.

Experiment result for this shape ([diff](../evidence/defects/rca-2026-11-25/w2-check-and-lock-balance.diff)): sequential [200, 409], row B unchanged, 1 day left; concurrent [200, 409]; a 5-day request with 5 days available is still approved; rejecting the refused request still works. The experiment ran before the contract was agreed and returned 409 as a placeholder; the fix must return the agreed 400. It was not rerun: the status code does not change the check or the lock.

**Contract notes for the implementer:**
- 400 is the status the app already uses when a submission exceeds the balance, but the body differs: submission returns `{"non_field_errors": ["Saldo ferie insufficiente."]}` (`serializers.py:38`). The `detail` key follows the other errors of the decision endpoint, whose texts are Italian; the agreed text is English.
- The endpoint also returns 400 for an invalid decision value (`Decisione non valida.`), so a regression must assert the `detail` text and the stored state, not only the status.
- The interface shows no message after a failed decision (GAP-04, OBS-UC02-01), so the manager will not see this text until that is fixed.

**Impact:** upstream 9/9 still pass. In the 344 team tests exactly two fail, API-INT-001.03 and .09, the characterizations the fix must replace; API-INT-002.05 (PostgreSQL) must be replaced too. Employees without a `LeaveBalance` row are not restricted (as at submission, GAP-07); the agreed contract does not cover this case, so it stays open.

| Owner | Fix commit / PR | Independent retest |
|---|---|---|
| PENDING | PENDING | PENDING |

## 5. Preventive action (proposed)

| Action | What it prevents | Owner | Completion evidence |
|---|---|---|---|
| Rule and error contract written into BR-03 and FR-W2-05 (25 Nov 2026; review PENDING). Still to do: add "what does each event do to the invariant?" to the review checklist | Rules enforced at one event only | Shared — PENDING | Reviewed requirement change |
| Replace .03/.09/002.05 with regressions: days = available −1, equal, +1, plus rejection of an over-allowance request; complete the W2 half of DT-001 | Untested balance limit | Member 2 — partly done 27 Nov 2026: DT-001 W2 R1/R2/R4 pass, R3 regression written and fails on the baseline (`SQE_DESIRED_RULES=1`); available −1 and the replacements PENDING | Fails before the fix, passes after |
| Add the team suite to CI (proposal in [openapi/README](../openapi/README.md)) | Tests that exist but do not gate | Member 1 — PENDING | Required check on a PR |

**Effectiveness check:** after the fix, remove the check in a throwaway copy; the new regressions must fail. At each later review, count new validation/boundary defects in W1 and W2 against this one.

## 6. Classification and closure

- **Primary root-cause category (Pareto): Validation/Boundary.** Related: specification. Counted once (API-INT-001.03, .09 and API-INT-002.05 are the same defect).
- **Residual risk:** PR-01 stays open; EC-01 blocks release.
- **Out of scope:** staff can also make the balance negative by lowering the allowance in Django Admin (BR-03 note, D-1). That is a different path and needs its own decision.
- **Closure:** PENDING (fix, independent retest, regression in CI). Independent reproduction: CONFIRMED 27 November 2026 (see the header).