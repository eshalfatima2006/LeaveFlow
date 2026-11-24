# DR-001 — Critical-module selection for MCC and MC/DC

| Field | Value |
|---|---|
| Status | **PROPOSED** — the team's recommendation; instructor confirmation of the critical module is still required (SCOPE open decision 2) |
| Date | 24 November 2026 |
| Origin | PR #2 review (reviewer Bilalmughal-07, changes requested before the 22 Nov merge of `docs/test-planning` into `docs/requirements-and-scope`): *"The plan proposes LeaveRequestSerializer.validate as the critical module but also says that the MCC/MC-DC feasibility is uncertain because of the missing-balance path. It then proposes visible_requests as an alternative. Please document the decision process for selecting one critical module."* |
| Supersedes | The "alternative focal function" wording in [COVERAGE-BOUNDARY.md](../requirements/COVERAGE-BOUNDARY.md#critical-module-for-mcc-and-derived-mcdc), [TEST-STRATEGY.md](TEST-STRATEGY.md#white-box-and-critical-module-proposal) and the D1/D2 note in [BUSINESS-RULES.md](../requirements/BUSINESS-RULES.md#compound-decision-inventory-and-feasibility) (kept as history, marked superseded) |
| Evidence | [`docs/sqe/evidence/whitebox/critical-module-2026-11-24/`](../evidence/whitebox/critical-module-2026-11-24/README.md) |

## 1. Problem

The assignment (p2, unit level) requires 100% statement and branch coverage of all server-side business logic and, for **one critical module**, complete MCC followed by MC/DC pairs derived from the MCC tables. The v0.1 plan named `LeaveRequestSerializer.validate` but kept `visible_requests` open as an alternative because of the missing-balance path, without a rule for choosing. This record makes one choice and states the criteria behind it.

## 2. Candidates

| | A. W1 validation chain | B. `visible_requests` |
|---|---|---|
| Source | `backend/leave/serializers.py:30–39` `LeaveRequestSerializer.validate`, with the rule methods it reaches: `models.py:80–90` `LeaveRequest.clean`, `:70–78` `business_days`, `:34–43` `LeaveBalance.approved_days`/`available_days` | `backend/leave/views.py:46–51` |
| Workflow | W1 submission (and the balance that W2 approvals change) | W1/W2 listing and the decision lookup scope |
| Requirements / rules | FR-W1-02…05; BR-01, BR-02, BR-03, BR-06 | FR-W2-01, FR-W2-02; BR-04 |
| Highest linked risk | PR-01 (score 25, approval overdraw) and PR-04/07/11 | PR-02 (score 20, access exposure) |

## 3. Evaluation criteria

1. **Risk and business importance** — the module that carries the highest-risk business rules.
2. **Rule breadth** — the assignment also says "cover all four business rules"; the critical module should exercise as many rules as possible.
3. **Decision richness** — compound conditions and decisions that make MCC/MC/DC meaningful rather than trivial.
4. **MCC/MC/DC feasibility** — every evaluable combination executable with real domain data; infeasible combinations justified.
5. **Observability and controllable data** — each outcome visible as a result, with fixtures the disposable database can build.
6. **Mutation suitability** — rule-specific custom operators with killable mutants.

## 4. Evidence (measured 24 Nov 2026)

**Complexity** (radon 6.0.1, each boolean operator +1; Sonar not run):

| Function | Cyclomatic complexity |
|---|---|
| `validate` | 5 |
| `LeaveRequest.clean` | 3 |
| `business_days` | 3 |
| `approved_days` | 2 |
| `available_days` | 1 |
| **Chain A aggregate** (5 functions) | **14** |
| `visible_requests` (candidate B) | 4 |

Note: Chain A aggregate is the sum of five cooperating functions that form a single validation path. Candidate B is a single function. The comparison illustrates decision density across the full validation chain, not equivalent units.

**Existing coverage by the A2.1 API suite** (coverage.py 7.6.10 `--branch`): both candidates are already at 100% statements and 100% coverage.py branches.

| Function | Statements | Branches |
|---|---|---|
| `validate` | 10/10 | 2/2 |
| `clean` | 6/6 | 4/4 |
| `business_days` | 9/9 | 4/4 |
| `visible_requests` | 6/6 | 4/4 |

**Important distinction:** These figures show coverage achieved incidentally by the Area 2 API integration tests, not the assignment's required 100% statement and branch coverage for white-box testing. The white-box unit tests achieving that requirement are Member 1's deliverable under Area 1 (WP-07/08). The numbers above demonstrate that the validation chain is exercisable and observable through the API, supporting its selection as the critical module.

This proves that **branch coverage does not settle condition coverage**. coverage.py measures the `if` arcs at serializers:37, not the two conditions inside `balance and …`.

**Condition inventory and executed truth rows** (`feasibility_probe.py`, in-memory test database):

| Decision | Conditions | Evaluated vectors (MCC under short-circuit) | Observed outcome | Infeasible abstract rows |
|---|---|---|---|---|
| D1 `serializers.py:37` `balance and D > balance.available_days` | B = balance exists; E = D > A | (B=F, E –) / (B=T, E=F) / (B=T, E=T) | accept, `available_days` evaluated 0× / accept, 1× / reject `Saldo ferie insufficiente.`, 1× | (F,T), (F,F): with no balance, A has no value (`AttributeError` on `None.available_days`) and Python skips E |
| H `serializers.py:35` `hasattr(exc, 'message_dict')` | single condition | T / F | `end_date` error (end before start) / `non_field_errors` (overlap) | none |
| C1 `models.py:81` `end_date < start_date` | single | T / F | 400 on `end_date` / continue | none |
| C2 `models.py:89` `overlap.exists()` | single at Python level; SQL predicate D4 handled by decision table DT-002 | T / F | overlap error / continue | D4 rows per [BUSINESS-RULES](../requirements/BUSINESS-RULES.md#compound-decision-inventory-and-feasibility) |
| L1/L2 `business_days` loop and `weekday() < 5` | loop 0/1/many; weekday T/F | all | counts 0 (weekend-only) / 1 / many | none |
| D2 `views.py:49` `role == MANAGER and team_id` (candidate B) | M, T | (M=F, T –) / (M=T, T=F) / (M=T, T=T), plus the admin bypass before it | own / own / team | none at input level. Both employee data rows (team and no team) evaluate as (F, –) |

## 5. Decision (PROPOSED)

**The primary critical module is Candidate A, the W1 validation chain:** `LeaveRequestSerializer.validate` (`backend/leave/serializers.py`) together with the rule methods it reaches in `backend/leave/models.py` (`LeaveRequest.clean`, `business_days`, `LeaveBalance.approved_days`, `available_days`).

`visible_requests` is **not** the critical module and is not kept as an open alternative. It remains fully inside the 100% statement/branch scope and is tested through decision table DT-003 and the access-control objectives (API-W2-001/002, SEC-001).

**Why A:**
- **Risk (criterion 1):** A carries BR-03, the rule behind the highest product risk PR-01 (25).
- **Breadth (criterion 2):** A exercises four of the six business rules (BR-01, BR-02, BR-03, BR-06); B exercises one (BR-04).
- **Decisions (criterion 3):** A has 14 complexity points and 6 decisions/conditions; B has 4 and one compound decision.
- **Mutation (criterion 6):** A offers natural custom operators: `>`→`>=` at the balance boundary, removal of the `balance and` guard, the weekday bound `< 5`→`<= 5`, the active-status set in the overlap check, and the inclusive date comparisons. Each is killable with existing boundary data (D = A, A + 1; Friday/Saturday; touching intervals).
- **Feasibility (criterion 4):** the missing-balance concern is resolved by applying the accepted short-circuit interpretation, not by changing modules (section 6).

## 6. MCC and MC/DC under short-circuit evaluation

Python's `and` evaluates its right operand only when the left one is true. For a two-condition `and`, the evaluable condition vectors are therefore (F, –), (T, F) and (T, T). **Complete MCC** for such a decision means executing every evaluable vector and documenting the abstract rows that cannot occur. **MC/DC** pairs are then derived from those MCC rows. When a pair's partner has the other condition unevaluated, it is **masking MC/DC**, the form accepted for short-circuit languages (FAA position paper CAST-6, *Rationale for Accepting Masking MC/DC in Certification Projects*).

**D1 (critical) — 3 tests give complete MCC and MC/DC:**

| Test | B | E | Data | Expected |
|---|---|---|---|---|
| T1 | T | T | A = 5, D = 6 (2027-03-01..08) | 400 `Saldo ferie insufficiente.`, no row |
| T2 | T | F | A = 5, D = 5 (2027-03-01..05) | accepted, pending row |
| T3 | F | – | no LeaveBalance, D = 5 | accepted (baseline GAP-07 characterisation) |

- **E independence (unique cause):** pair T1/T2. Only E changes and the outcome flips.
- **B independence (masking):** pair T1/T3. B changes, E is masked in T3, and the outcome flips.

The two abstract rows (B=F, E=T/F) are **infeasible** with real domain objects, and the evidence above shows why. No test double is used to fake them.

**Rejected rationale for B:** v0.1 suggested that `visible_requests` avoids masking. The probe shows it does not. D2 is also a short-circuit `and`, and its rows employee + team and employee without team both evaluate as (F, –). Its M pair (TT/FT) is masking MC/DC in exactly the same way. B's only advantage is that T still has a defined *input* value. That is not a reason to give up the higher-risk, broader module.

## 7. Known limitations

- The missing-balance path (T3) passes under the baseline because of GAP-07. It is a characterisation, not an approved oracle. The MC/DC demonstration does not depend on the policy decision, only on observable outcomes.
- The approval-time balance check (PR-01, GAP-01) is in `decide_request`, not in this module. It is covered by the planned regression API-INT-001 / OBJ-UC02-01, and by 100% statement/branch coverage of `views.py`.
- D4, the SQL overlap predicate, is analysed with decision table DT-002, not reported as Python condition coverage.
- The complexity figures come from radon. A hand-drawn CFG and the Sonar comparison (WP-07) are still required by the assignment.

## 8. Obligations (Member 1, A1 — not started)

- Unit tests in `tests/team/unit/` for:
  - T1–T3;
  - H true/false;
  - C1 true/false;
  - C2 true/false with DT-002 rows;
  - `business_days` loop 0/1/many and weekday true/false;
  - `approved_days` with 0, 1 and many approved requests.
- The MCC table and derived MC/DC pairs recorded as MCC-001 evidence.
- 100% statement and branch coverage of the approved server-side denominator.
- Mutation testing (MUT-001) on this module, with at least the custom operators listed in section 5.
- Hand CFG for `validate` versus radon/Sonar (WP-07).

## 9. Approval and traceability

- **Status:** PROPOSED. This document records the team's selection process and recommendation. It does not constitute final assignment evidence until: (a) the instructor confirms the critical-module choice, and (b) the instructor confirms that masking MC/DC under short-circuit evaluation is acceptable for this course. The hand-drawn CFG and SonarQube complexity comparison (WP-07) are Member 1's Area 1 deliverables and are not included in this PR.
- **Traceability:**
  - RTM objective MCC-001;
  - FR-W1-02…05, BR-01/02/03/06;
  - risks PR-01, PR-04, PR-07, PR-11, JR-03;
  - roadmap WP-07/08/09/16.
