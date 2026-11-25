# Requirements traceability matrix and planned objective catalog

Version0.1 — 22 November 2026. Preserve exactly the12 existing FR IDs and six BR IDs from [Phase1 requirements](../requirements/FUNCTIONAL-REQUIREMENTS.md) and [rules](../requirements/BUSINESS-RULES.md). **All IDs here are proposed test objectives/case families, not implemented scripts or executed results.** Parameterized objectives will be expanded into actual executable case IDs/manifests without overwriting these planning references. A planned row or empty test file never establishes tested coverage.

> **v0.2 — 24 November 2026 (reconciliation).** Execution evidence now exists for A2.0 (foundation), A2.1 (API) and B1 (browser UC-01/UC-02); see [Execution status (v0.2)](#execution-status-v02). The use-case model follows the PROPOSED catalog in [USE-CASE-SPECIFICATIONS.md](../requirements/USE-CASE-SPECIFICATIONS.md). The canonical browser IDs are `TC-UCxx-{M,A1,A2,E1,E2}`. The v0.1 `E2E-UCxx-NN` rows are kept below as history with their disposition, and are not counted. The 12 FRs and six BRs are unchanged; FR-ADM-01, FR-ADM-02 and FR-NOTIF-01 are PROPOSED and excluded from coverage until instructor decisions D-1/D-2.

## Conventions, evidence and status

UT=unit, API=HTTP, API-INT=integration, DT=decision table, ST=state, GEN=generator, E2E=browser flow, SEC=security, ACC=accessibility/task, PERF=load, REC=recovery, MUT=mutation, MCC=critical Boolean analysis, REG=regression. A catalog ID is defined once below, may be referenced by many requirements and can use several techniques. E2E-UCxx-01=main, -02/-03=alternatives, -04/-05=exceptions. These are30 planned flow slots, not a claim of30 passing tests; six accepted actor goals still require approval. *v0.2: E2E-UCxx-NN are superseded v0.1 IDs; canonical browser flow IDs are TC-UCxx-M/A1/A2/E1/E2, plus INC-01/02 (included use cases), OBJ-* (blocked objectives) and SUP-* (supplementary checks), defined in [Browser use-case flow catalog (v0.2)](#browser-use-case-flow-catalog-v02).*

Evidence for each eventual implemented ID: future `docs/sqe/evidence/<area>/<run-id>/` manifest keyed by ID with actual test path/node ID, tested SHA, profile/spec/fixture/seed hashes, expected/observed, status, output/DB/browser artifacts and genuine issue URLs. No such evidence files or issue numbers are invented here. *(v0.1 statement, 22 Nov 2026 — superseded in v0.2: see [Execution status (v0.2)](#execution-status-v02) for executed rows; all other rows remain PLANNED / NOT MEASURED.)* future defect field for **every FR** is **PENDING — real issue URL when created**. This shared default applies to forward/reverse/rule/browser tables, not an omitted status.

## Forward trace: FR → planned checks → future evidence

| Exact FR | Business rules | Product risks | Test objective | Unit ID | API ID | Use cases (v0.2; † conditional on D-1/D-2) | Decision/state and other objective IDs |
|---|---|---|---|---|---|---|---|
| FR-W1-01 | BR-04, BR-05, BR-06 | PR-02 | Authenticate, reject invalid tokens and bind caller ownership | UT-W1-001 | API-W1-001 | UC-01, UC-02, INC-01 | DT-003, SEC-001, SEC-002, SEC-003, MUT-001, REG-001 |
| FR-W1-02 | BR-06 | PR-06, PR-07 | Validate declared payload fields and defaults | UT-W1-002 | API-W1-002 | UC-01 | GEN-001, SEC-003, ACC-001, MUT-001, REG-001 |
| FR-W1-03 | BR-01 | PR-04, PR-11 | Validate ordered dates and inclusive weekday total | UT-W1-003 | API-W1-003 | UC-01 | GEN-001, SEC-003, ACC-001, MUT-001, REG-001 |
| FR-W1-04 | BR-02 | PR-03, PR-04 | Reject active inclusive overlap for same owner | UT-W1-004 | API-W1-004 | UC-01 | API-INT-002, GEN-001, DT-002, SEC-003, ACC-001, MUT-001, REG-001 |
| FR-W1-05 | BR-03, BR-01 | PR-01, PR-07, PR-11 | Apply existing submission allowance boundary | UT-W1-005 | API-W1-005 | UC-01, UC-04, UC-08† | API-INT-001, GEN-001, DT-001, SEC-003, ACC-001, MUT-001, MCC-001, REG-001 |
| FR-W1-06 | BR-04, BR-05, BR-06 | PR-03, PR-08, PR-10, PR-12 | Persist one pending original k and refresh UI | UT-W1-006 | API-W1-006 | UC-01, UC-04, UC-07† | API-INT-001, API-INT-002, DT-004, ST-001, SEC-003, ACC-001, PERF-001, REC-001, UT-EVT-001, MUT-001, REG-001 |
| FR-W2-01 | BR-04 | PR-02 | List exactly visible own/team/all requests | UT-W2-001 | API-W2-001 | UC-02, UC-04, UC-09† | DT-003, DT-005, SEC-001, SEC-003, MUT-001, MCC-001, REG-001 |
| FR-W2-02 | BR-04 | PR-02, PR-08 | Authorize role, scoped target and nonself actor | UT-W2-002 | API-W2-002 | UC-02, UC-09† | DT-003, SEC-001, SEC-002, SEC-003, ACC-002, MUT-001, MCC-001, REG-001 |
| FR-W2-03 | BR-06, BR-05 | PR-05, PR-06, PR-07 | Accept only approved/rejected decision values | UT-W2-003 | API-W2-003 | UC-02 | GEN-001, ST-001, SEC-003, MUT-001, REG-001 |
| FR-W2-04 | BR-05 | PR-03, PR-05, PR-10 | Allow pending decisions only; preserve final metadata | UT-W2-004 | API-W2-004 | UC-02 | API-INT-001, API-INT-002, ST-001, SEC-001, SEC-003, ACC-002, REC-002, MUT-001, REG-001 |
| FR-W2-05 | BR-03, BR-04, BR-05 | PR-01, PR-03, PR-11, PR-12 | Approve same k and derive employee allowance effect | UT-W2-005 | API-W2-005 | UC-02, UC-04, UC-07† | API-INT-001, API-INT-002, DT-001, DT-004, DT-005, ST-001, SEC-003, ACC-002, REC-002, UT-EVT-001, MUT-001, REG-001 |
| FR-W2-06 | BR-02, BR-03, BR-04, BR-05 | PR-05, PR-10, PR-12 | Reject same k without allowance consumption | UT-W2-006 | API-W2-006 | UC-02, UC-04, UC-07† | API-INT-001, DT-002, DT-004, DT-005, ST-001, SEC-003, ACC-002, REC-002, UT-EVT-001, MUT-001, REG-001 |

All FRs also inherit the evidence/status/defect fields stated above. Browser mapping is intentionally incomplete/conditional while UC distinctness and exception feedback remain unresolved (JR-03/PR-08). Read-only UC goals have state-observation postconditions, not fictional writes. No hypothetical requirement ID was added for desired approval safeguarding; the separate proposed oracle remains attached to FR-W2-05/BR-03 until reviewed.

## Backward trace: unique objective → FR / BR / risk

Each row is a **definition**; all later mentions are references. Use meaningful independent expected values, persisted readback and a real token/API boundary where applicable. Execution will split parameterized classes/rows into explicit node IDs; do not report a single aggregate objective as all combinations tested without that expansion.

| Planned ID (unique definition) | Area | Objective / expected assertion basis | Exact FR IDs | BR IDs | Product risks |
|---|---|---|---|---|---|
| UT-W1-001 | Unit | Isolate Real token/no token/invalid token; read-only employee/status injection cannot choose another owner or final state; assert independent expected values and all callable paths, not only mocked calls | FR-W1-01 | BR-04, BR-05, BR-06 | PR-02 |
| API-W1-001 | API | Real token/no token/invalid token; read-only employee/status injection cannot choose another owner or final state; verify actual response/schema and persisted state with real identity | FR-W1-01 | BR-04, BR-05, BR-06 | PR-02 |
| UT-W1-002 | Unit | Isolate Required/null/blank/type/enum/date classes; omitted vacation default; trimmed note279/280/281 and unchanged DB on invalid input; assert independent expected values and all callable paths, not only mocked calls | FR-W1-02 | BR-06 | PR-06, PR-07 |
| API-W1-002 | API | Required/null/blank/type/enum/date classes; omitted vacation default; trimmed note279/280/281 and unchanged DB on invalid input; verify actual response/schema and persisted state with real identity | FR-W1-02 | BR-06 | PR-06, PR-07 |
| UT-W1-003 | Unit | Isolate Reversed/same-day/weekday/weekend/cross-year intervals with independent known counts; preview/server agreement; assert independent expected values and all callable paths, not only mocked calls | FR-W1-03 | BR-01 | PR-04, PR-11 |
| API-W1-003 | API | Reversed/same-day/weekday/weekend/cross-year intervals with independent known counts; preview/server agreement; verify actual response/schema and persisted state with real identity | FR-W1-03 | BR-01 | PR-04, PR-11 |
| UT-W1-004 | Unit | Isolate Touch/before/after intervals across pending/approved/rejected and other-owner rows; no insert on rejection; assert independent expected values and all callable paths, not only mocked calls | FR-W1-04 | BR-02 | PR-03, PR-04 |
| API-W1-004 | API | Touch/before/after intervals across pending/approved/rejected and other-owner rows; no insert on rejection; verify actual response/schema and persisted state with real identity | FR-W1-04 | BR-02 | PR-03, PR-04 |
| UT-W1-005 | Unit | Isolate D=A−1/A/A+1, zero/negative available and absent balance characterization; approved-only aggregate checked; assert independent expected values and all callable paths, not only mocked calls | FR-W1-05 | BR-03, BR-01 | PR-01, PR-07, PR-11 |
| API-W1-005 | API | D=A−1/A/A+1, zero/negative available and absent balance characterization; approved-only aggregate checked; verify actual response/schema and persisted state with real identity | FR-W1-05 | BR-03, BR-01 | PR-01, PR-07, PR-11 |
| UT-W1-006 | Unit | Isolate Returned k read back with caller/pending/null audit, unchanged allowance; refresh failure and event/commit paths; assert independent expected values and all callable paths, not only mocked calls | FR-W1-06 | BR-04, BR-05, BR-06 | PR-03, PR-08, PR-10, PR-12 |
| API-W1-006 | API | Returned k read back with caller/pending/null audit, unchanged allowance; refresh failure and event/commit paths; verify actual response/schema and persisted state with real identity | FR-W1-06 | BR-04, BR-05, BR-06 | PR-03, PR-08, PR-10, PR-12 |
| UT-W2-001 | Unit | Isolate Employee, manager with/without team and admin visible ID sets; dashboard recent/count and People boundaries; assert independent expected values and all callable paths, not only mocked calls | FR-W2-01 | BR-04 | PR-02 |
| API-W2-001 | API | Employee, manager with/without team and admin visible ID sets; dashboard recent/count and People boundaries; verify actual response/schema and persisted state with real identity | FR-W2-01 | BR-04 | PR-02 |
| UT-W2-002 | Unit | Isolate Role403, invisible404, self403, allowed manager/admin, real tokens and no denied writes; UI mismatch recorded; assert independent expected values and all callable paths, not only mocked calls | FR-W2-02 | BR-04 | PR-02, PR-08 |
| API-W2-002 | API | Role403, invisible404, self403, allowed manager/admin, real tokens and no denied writes; UI mismatch recorded; verify actual response/schema and persisted state with real identity | FR-W2-02 | BR-04 | PR-02, PR-08 |
| UT-W2-003 | Unit | Isolate Missing/null/blank/pending/unknown/wrong-type decision400 after role guard; valid values reach next checks; assert independent expected values and all callable paths, not only mocked calls | FR-W2-03 | BR-06, BR-05 | PR-05, PR-06, PR-07 |
| API-W2-003 | API | Missing/null/blank/pending/unknown/wrong-type decision400 after role guard; valid values reach next checks; verify actual response/schema and persisted state with real identity | FR-W2-03 | BR-06, BR-05 | PR-05, PR-06, PR-07 |
| UT-W2-004 | Unit | Isolate Both allowed transitions; ≥1 disallowed per state; valid repeats409 preserve actor/time/count/balance; actual DB locking; assert independent expected values and all callable paths, not only mocked calls | FR-W2-04 | BR-05 | PR-03, PR-05, PR-10 |
| API-W2-004 | API | Both allowed transitions; ≥1 disallowed per state; valid repeats409 preserve actor/time/count/balance; actual DB locking; verify actual response/schema and persisted state with real identity | FR-W2-04 | BR-05 | PR-03, PR-05, PR-10 |
| UT-W2-005 | Unit | Isolate Same ID/content/owner, approved actor/time; employee available drops D; desired overbalance rejection separately approved and tested; assert independent expected values and all callable paths, not only mocked calls | FR-W2-05 | BR-03, BR-04, BR-05 | PR-01, PR-03, PR-11, PR-12 |
| API-W2-005 | API | Same ID/content/owner, approved actor/time; employee available drops D; desired overbalance rejection separately approved and tested; verify actual response/schema and persisted state with real identity | FR-W2-05 | BR-03, BR-04, BR-05 | PR-01, PR-03, PR-11, PR-12 |
| UT-W2-006 | Unit | Isolate Same original row rejected with actor/time, unchanged approved total, later W1 overlap eligibility and final-state duplicate rejection; assert independent expected values and all callable paths, not only mocked calls | FR-W2-06 | BR-02, BR-03, BR-04, BR-05 | PR-05, PR-10, PR-12 |
| API-W2-006 | API | Same original row rejected with actor/time, unchanged approved total, later W1 overlap eligibility and final-state duplicate rejection; verify actual response/schema and persisted state with real identity | FR-W2-06 | BR-02, BR-03, BR-04, BR-05 | PR-05, PR-10, PR-12 |
| API-INT-001 | Integration | W1 creates original keys; W2 approves/rejects/readbacks; desired allowance5/two4-day overapproval regression fails on baseline until authorized fix | FR-W1-05, FR-W1-06, FR-W2-04, FR-W2-05, FR-W2-06 | BR-02, BR-03, BR-05 | PR-01, PR-10 |
| API-INT-002 | Integration | Barrier-synchronized overlap/same-k/distinct-k concurrency, independent connections and bounded waits on disposable PostgreSQL; full final DB state | FR-W1-04, FR-W1-06, FR-W2-04, FR-W2-05 | BR-02, BR-03, BR-05 | PR-03 |
| GEN-001 | Generator | Reviewed OpenAPI/rule fixture constraints →all EP/applicable3-point BVA classes →API consumes manifest; two changed spec constraints regenerate; compare actual contract drift | FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W2-03 | BR-01, BR-02, BR-03, BR-06 | PR-06, PR-07 |
| DT-001 | Decision | Balance-exists and over-limit combination table, masked/undefined E explicitly marked; baseline W1 vs desired W2 oracle distinct | FR-W1-05, FR-W2-05 | BR-03 | PR-01, PR-07, PR-11 |
| DT-002 | Decision | Same employee, blocking state, inclusive interval intersection and pk exclusion; feasible SQL rows and infeasibility justification | FR-W1-04, FR-W2-06 | BR-02 | PR-03, PR-04 |
| DT-003 | Decision | Role/team presence/self/scoped target visibility and ordered authorization conditions; all four manager/team truth rows plus admin bypass | FR-W1-01, FR-W2-01, FR-W2-02 | BR-04 | PR-02 |
| DT-004 | Decision | Requested admin OR(manager AND team) recipients, self exclusion and owner-only decision recipients; infeasible dual-role assignments noted | FR-W1-06, FR-W2-05, FR-W2-06 | BR-04, BR-05 | PR-12 |
| DT-005 | Decision | Upcoming leave approved AND end≥localdate, all four feasible rows, no-result/null and earliest-start selection through team refresh | FR-W2-01, FR-W2-05, FR-W2-06 | BR-03, BR-04 | PR-11 |
| ST-001 | State | Creation→pending; pending→approved/rejected; every final-state repeat/invalid event; ≥1 disallowed from each state, same k/audit/count assertions | FR-W1-06, FR-W2-03, FR-W2-04, FR-W2-05, FR-W2-06 | BR-05, BR-06 | PR-03, PR-05 |
| SEC-001 | Security | Playwright ≥4 access decisions: employee submit allow/decision deny, manager team nonself allow/self or outsider deny; HTTP and persisted assertions | FR-W1-01, FR-W2-01, FR-W2-02, FR-W2-04 | BR-04, BR-05 | PR-02, PR-08 |
| SEC-002 | Security | Corroborate ≥2 controls (TokenAuthentication/IsAuthenticated and role/team/self server guards) with normal local actions/source, ZAP passive both workflows | FR-W1-01, FR-W2-02 | BR-04 | PR-02 |
| SEC-003 | Security | Pinned Python and npm inventory/advisories with genuine audits, applicability/severity/impact/likelihood/remediation/residual review; no invented vulnerabilities | FR-W1-01, FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W1-06, FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-05, FR-W2-06 | BR-04, BR-06 | PR-09 |
| ACC-001 | Accessibility | W1 task: invalid rule input→explanatory error→correction→pending confirmation; keyboard focus/order/submit; authenticated Lighthouse/axe and before/after improvement | FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W1-06 | BR-01, BR-02, BR-03, BR-06 | PR-08 |
| ACC-002 | Accessibility | W2 complete decision task/final confirmation; approved UC key-screen Lighthouse3 categories+axe, duplicate finding review and missing decision-feedback characterization | FR-W2-02, FR-W2-04, FR-W2-05, FR-W2-06 | BR-04, BR-05 | PR-08 |
| PERF-001 | Performance | Valid POST requests with deterministic nonoverlap windows, same initial dataset per run;1/5VUs twice each ≥60s steady-state; p95/rps/unexpected failures | FR-W1-06 | BR-04, BR-05, BR-06 | PR-03, PR-10 |
| REC-001 | Recovery | Inject preinsert DB failure, assert no request/event, restore/retry same payload once, exactly one pending original record and unchanged derived balance | FR-W1-06 | BR-04, BR-05 | PR-10 |
| REC-002 | Recovery | Decision atomic rollback/failure/restoration/retry and after-commit Redis outage/lost response distinguished; same k/no double charge/audit corruption | FR-W2-04, FR-W2-05, FR-W2-06 | BR-03, BR-05 | PR-10, PR-12 |
| UT-EVT-001 | Unit | Exercise event builder/publisher/nested callback: names/fallback, all recipient classes, Redis disabled/success/error, commit/rollback and original ID/payload | FR-W1-06, FR-W2-05, FR-W2-06 | BR-04, BR-05 | PR-12 |
| MUT-001 | Mutation | Run approved business-rule mutations, ≥2 custom rule operators, ≥15 genuine survivor classifications and killable survivors killed; raw/adjusted score and timeouts | FR-W1-01, FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W1-06, FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-05, FR-W2-06 | BR-01, BR-02, BR-03, BR-04, BR-05, BR-06 | PR-01, PR-02, PR-04, PR-05, PR-12 |
| MCC-001 | White-box | Complete approved critical-module MCC table with short-circuit/infeasible rationale, derive actual MC/DC pairs; critical module per [DR-001](DR-001-CRITICAL-MODULE.md) (PROPOSED): W1 validation chain; D1 complete MCC = 3 evaluable vectors, MC/DC pairs T1/T2 (E) and T1/T3 (B, masking); `visible_requests` covered by DT-003, not critical | FR-W1-05, FR-W2-01, FR-W2-02 | BR-03, BR-04 | PR-01, PR-02 |
| REG-001 | Regression | Retain each genuine defect regression and impacted team suites on fix candidate; real fail-before/pass-after; upstream smoke separately reported | FR-W1-01, FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W1-06, FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-05, FR-W2-06 | BR-01, BR-02, BR-03, BR-04, BR-05, BR-06 | PR-01, PR-02, PR-03, PR-04, PR-05, PR-06, PR-07, PR-08, PR-09, PR-10, PR-11, PR-12 |
| E2E-UC01-01 | Browser | **v0.1 — mapped → TC-UC01-M.** UC-01 Employee submit leave: Submit valid modal→pending original k. Conditional on accepted UC/flow specification. | FR-W1-01, FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W1-06 | BR-01, BR-02, BR-03, BR-04, BR-05, BR-06 | PR-01, PR-04, PR-07, PR-08 |
| E2E-UC01-02 | Browser | **v0.1 — retired (input-data variant; EP data, API-W1-002.01).** UC-01 Employee submit leave: Alternative: permit/personal type, same create rule. Conditional on accepted UC/flow specification. | FR-W1-01, FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W1-06 | BR-01, BR-02, BR-03, BR-04, BR-05, BR-06 | PR-01, PR-04, PR-07, PR-08 |
| E2E-UC01-03 | Browser | **v0.1 — retired (EP/BVA data; API-W1-002.02, 003.02).** UC-01 Employee submit leave: Alternative: omit optional note, valid same-day weekday. Conditional on accepted UC/flow specification. | FR-W1-01, FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W1-06 | BR-01, BR-02, BR-03, BR-04, BR-05, BR-06 | PR-01, PR-04, PR-07, PR-08 |
| E2E-UC01-04 | Browser | **v0.1 — mapped → TC-UC01-E1.** UC-01 Employee submit leave: Exception: overlap400, rendered error and date correction. Conditional on accepted UC/flow specification. | FR-W1-01, FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W1-06 | BR-01, BR-02, BR-03, BR-04, BR-05, BR-06 | PR-01, PR-04, PR-07, PR-08 |
| E2E-UC01-05 | Browser | **v0.1 — mapped → TC-UC01-E2.** UC-01 Employee submit leave: Exception: insufficient allowance400, shorten/correct and succeed. Conditional on accepted UC/flow specification. | FR-W1-01, FR-W1-02, FR-W1-03, FR-W1-04, FR-W1-05, FR-W1-06 | BR-01, BR-02, BR-03, BR-04, BR-05, BR-06 | PR-01, PR-04, PR-07, PR-08 |
| E2E-UC02-01 | Browser | **v0.1 — mapped → TC-UC02-M.** UC-02 Manager approve leave: Requests pending row→approve→same k approved/balance effect. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-05 | BR-03, BR-04, BR-05, BR-06 | PR-01, PR-02, PR-05, PR-08 |
| E2E-UC02-02 | Browser | **v0.1 — retired (navigation-only <<extend>> entry point).** UC-02 Manager approve leave: Alternative: approve via Overview recent row. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-05 | BR-03, BR-04, BR-05, BR-06 | PR-01, PR-02, PR-05, PR-08 |
| E2E-UC02-03 | Browser | **v0.1 — mapped → TC-UC02-A2.** UC-02 Manager approve leave: Alternative: admin approves nonself different-team visible request. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-05 | BR-03, BR-04, BR-05, BR-06 | PR-01, PR-02, PR-05, PR-08 |
| E2E-UC02-04 | Browser | **v0.1 — mapped → TC-UC02-E1.** UC-02 Manager approve leave: Exception: stale already-decided row409, original audit unchanged; missing feedback recorded. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-05 | BR-03, BR-04, BR-05, BR-06 | PR-01, PR-02, PR-05, PR-08 |
| E2E-UC02-05 | Browser | **v0.1 — mapped → TC-UC02-E2.** UC-02 Manager approve leave: Exception: self-owned pending row403, no write; current shown button/error gap recorded. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-05 | BR-03, BR-04, BR-05, BR-06 | PR-01, PR-02, PR-05, PR-08 |
| E2E-UC03-01 | Browser | **v0.1 — mapped → TC-UC02-A1 (UC-03 merged into UC-02).** UC-03 Manager reject leave: Requests pending row→reject→same k rejected/no charge. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-06 | BR-02, BR-03, BR-04, BR-05, BR-06 | PR-02, PR-05, PR-08 |
| E2E-UC03-02 | Browser | **v0.1 — retired (navigation-only).** UC-03 Manager reject leave: Alternative: reject through Overview recent row. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-06 | BR-02, BR-03, BR-04, BR-05, BR-06 | PR-02, PR-05, PR-08 |
| E2E-UC03-03 | Browser | **v0.1 — retired (data variant of TC-UC02-A2).** UC-03 Manager reject leave: Alternative: admin rejects nonself visible request. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-06 | BR-02, BR-03, BR-04, BR-05, BR-06 | PR-02, PR-05, PR-08 |
| E2E-UC03-04 | Browser | **v0.1 — retired (same 409 guard as TC-UC02-E1).** UC-03 Manager reject leave: Exception: stale decision409, unchanged final row; feedback gap recorded. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-06 | BR-02, BR-03, BR-04, BR-05, BR-06 | PR-02, PR-05, PR-08 |
| E2E-UC03-05 | Browser | **v0.1 — moved → INC-01 E2 (and API-W1-001.04).** UC-03 Manager reject leave: Exception: invalid stored token401 on decision, no write; no invented token expiry. Conditional on accepted UC/flow specification. | FR-W2-01, FR-W2-02, FR-W2-03, FR-W2-04, FR-W2-06 | BR-02, BR-03, BR-04, BR-05, BR-06 | PR-02, PR-05, PR-08 |
| E2E-UC04-01 | Browser | **v0.1 — mapped → TC-UC04-M (UC-04 rescoped).** UC-04 Employee inspect remaining balance: Overview displays known available/used, open date preview. Conditional on accepted UC/flow specification. | FR-W1-03, FR-W1-05, FR-W2-05 | BR-01, BR-03 | PR-01, PR-11 |
| E2E-UC04-02 | Browser | **v0.1 — retired (navigation-only).** UC-04 Employee inspect remaining balance: Alternative: inspect sidebar balance for same known fixture. Conditional on accepted UC/flow specification. | FR-W1-03, FR-W1-05, FR-W2-05 | BR-01, BR-03 | PR-01, PR-11 |
| E2E-UC04-03 | Browser | **v0.1 — moved → TC-UC01-A2.** UC-04 Employee inspect remaining balance: Alternative: close modal without creating a record. Conditional on accepted UC/flow specification. | FR-W1-03, FR-W1-05, FR-W2-05 | BR-01, BR-03 | PR-01, PR-11 |
| E2E-UC04-04 | Browser | **v0.1 — mapped → TC-UC04-E2.** UC-04 Employee inspect remaining balance: Exception: dashboard GET fails during refresh/boot; actual logout/error behavior recorded. Conditional on accepted UC/flow specification. | FR-W1-03, FR-W1-05, FR-W2-05 | BR-01, BR-03 | PR-01, PR-11 |
| E2E-UC04-05 | Browser | **v0.1 — mapped → TC-UC04-E1.** UC-04 Employee inspect remaining balance: Exception: invalid token at boot clears token, login shown. Conditional on accepted UC/flow specification. | FR-W1-03, FR-W1-05, FR-W2-05 | BR-01, BR-03 | PR-01, PR-11 |
| E2E-UC05-01 | Browser | **v0.1 — retired (UC-05 withdrawn; locating work is a step of UC-02).** UC-05 Manager locate decision work: Requests→pending filter→identify original k. Conditional on accepted UC/flow specification. | FR-W1-06, FR-W2-01, FR-W2-02 | BR-04, BR-05 | PR-02, PR-08 |
| E2E-UC05-02 | Browser | **v0.1 — retired (UC-05 withdrawn; locating work is a step of UC-02).** UC-05 Manager locate decision work: Alternative: locate through Overview recent rows. Conditional on accepted UC/flow specification. | FR-W1-06, FR-W2-01, FR-W2-02 | BR-04, BR-05 | PR-02, PR-08 |
| E2E-UC05-03 | Browser | **v0.1 — retired (UC-05 withdrawn; locating work is a step of UC-02).** UC-05 Manager locate decision work: Alternative: inspect All/approved/rejected history filters. Conditional on accepted UC/flow specification. | FR-W1-06, FR-W2-01, FR-W2-02 | BR-04, BR-05 | PR-02, PR-08 |
| E2E-UC05-04 | Browser | **v0.1 — retired (UC-05 withdrawn; locating work is a step of UC-02).** UC-05 Manager locate decision work: Exception: requests GET failure; record real refresh error/no dedicated retry control. Conditional on accepted UC/flow specification. | FR-W1-06, FR-W2-01, FR-W2-02 | BR-04, BR-05 | PR-02, PR-08 |
| E2E-UC05-05 | Browser | **v0.1 — retired (UC-05 withdrawn; locating work is a step of UC-02).** UC-05 Manager locate decision work: Exception: invalid token during refresh; assert no write, record actual displayed state. Conditional on accepted UC/flow specification. | FR-W1-06, FR-W2-01, FR-W2-02 | BR-04, BR-05 | PR-02, PR-08 |
| E2E-UC06-01 | Browser | **v0.1 — reserve only (UC-06 inactive; not counted).** UC-06 Manager inspect team availability: People→employee balance/next leave→return to Requests. Conditional on accepted UC/flow specification. | FR-W2-05, FR-W2-06 | BR-03, BR-04, BR-05 | PR-01, PR-08, PR-11 |
| E2E-UC06-02 | Browser | **v0.1 — reserve only (UC-06 inactive; not counted).** UC-06 Manager inspect team availability: Alternative: no approved upcoming leave shows none. Conditional on accepted UC/flow specification. | FR-W2-05, FR-W2-06 | BR-03, BR-04, BR-05 | PR-01, PR-08, PR-11 |
| E2E-UC06-03 | Browser | **v0.1 — reserve only (UC-06 inactive; not counted).** UC-06 Manager inspect team availability: Alternative: no-team fixture shows empty People. Conditional on accepted UC/flow specification. | FR-W2-05, FR-W2-06 | BR-03, BR-04, BR-05 | PR-01, PR-08, PR-11 |
| E2E-UC06-04 | Browser | **v0.1 — reserve only (UC-06 inactive; not counted).** UC-06 Manager inspect team availability: Exception: team GET fails; record actual refresh/error limitation. Conditional on accepted UC/flow specification. | FR-W2-05, FR-W2-06 | BR-03, BR-04, BR-05 | PR-01, PR-08, PR-11 |
| E2E-UC06-05 | Browser | **v0.1 — reserve only (UC-06 inactive; not counted).** UC-06 Manager inspect team availability: Exception: invalid token on team GET, no writes and actual UI state recorded. Conditional on accepted UC/flow specification. | FR-W2-05, FR-W2-06 | BR-03, BR-04, BR-05 | PR-01, PR-08, PR-11 |

## Execution status (v0.2)

Status as of 24 Nov 2026. Only executed evidence is reported here; everything else is PLANNED. Evidence sources:

- **A2.0:** `docs/sqe/evidence/foundation/a20/` and `a20-reverify-20261123/` (12/12).
- **A2.1:** [A21-EXECUTION-MAPPING.md](../testing/A21-EXECUTION-MAPPING.md), evidence `docs/sqe/evidence/api/a21/final/` (API 40/40; team 52/52).
- **B1:** [BROWSER-USE-CASE-TESTING.md](../testing/BROWSER-USE-CASE-TESTING.md), evidence `docs/sqe/evidence/browser/b1/` (10/10 UC-01/UC-02 flows; OBJ-UC02-01 skipped as blocked); re-run from committed sources at `73cfc93`: `docs/sqe/evidence/browser/b1-provenance-2026-11-24/` (10/10, 1 skipped).
- **Regression at `73cfc93`:** `docs/sqe/evidence/regression/r5-2026-11-24/` — check exit 0, upstream 9/9, team 52/52.
- **A2.2:** evidence `docs/sqe/evidence/integration/a22-2026-11-24/` (7/7 API-INT-001 integration tests).
- **A2.3:** evidence `docs/sqe/evidence/structural/a23-2026-11-24/` (65 tests: 48 EP/BVA, 10 decision-table, 7 state-transition).
- **A2.3 decision tables, part 2:** evidence `docs/sqe/evidence/structural/decision-tables-2026-11-25/` (42 tests: DT-002 14, DT-003 6, DT-004 13, DT-005 9).
- **A2.4:** evidence `docs/sqe/evidence/generated/a24-2026-11-24/` (33 generated tests; the v2/v3 change demonstrations are recorded in the CHANGE documents).
- **A2.4 generated inputs, extended:** evidence `docs/sqe/evidence/generated/inputs-2026-11-25/` (70 passed: 68 generated tests and 2 manifest checks); `change-1-note-length-2026-11-25/` and `change-2-sick-type-2026-11-25/` (demonstrations, one intended failure each).
- **A2.4 contract:** evidence `docs/sqe/evidence/api/contract-2026-11-25/` (41 tests).
- **PR #10 completion:** `docs/sqe/evidence/generated/completion-2026-11-25/` (129), `generated/change-{1,2,3}-*-final-2026-11-25/` (demonstrations), `integration/completion-2026-11-25/` (15), `concurrency/postgresql17-2026-11-25/` (5, PostgreSQL 17.12), `api/coverage-2026-11-25/` (coverage and observed cases), `regression/clean-checkout-2026-11-25/` (team 344/344, upstream 9/9 from a fresh clone and virtual environment).
- **Upstream:** the nine `backend/leave/tests.py` tests are reported separately and earn no team credit.

| FR | Executed API tests (A2.1) | Executed browser flows (B1) | Executed structural/integration/generated (A2.2–A2.4) | Still planned |
|---|---|---|---|---|
| FR-W1-01 | API-W1-001.01–.05, .07 passed; .06 characterisation (manager/admin self-submission) | TC-UC01-* (sign-in steps), INC-01 via every B1 test | EP authentication: valid, no and wrong token (3); GEN-001 login (19, incl. media and methods) and missing/unknown token on the six secured operations (12) | UT-W1-001 |
| FR-W1-02 | API-W1-002.01–.05 passed | TC-UC01-M (valid fields) | EP `leave_type` (6), `start_date` missing/non-date/null (3), `end_date` missing (1), `note` (4); BVA `note` 279/280/281 (3); GEN-001 W1 field cases (32) and media (4) | UT-W1-002 |
| FR-W1-03 | API-W1-003.01–.02 passed; .03/.04 characterisation (zero-day, past dates) | TC-UC01-A1 (preview/persisted agreement) | EP `start_date` future/today and `end_date` same/after/before (5); BVA end = start−1/start/start+1 (3); DT1 R1 (DT-001/002 table); GEN-001 `end_date >= start_date` BVA (2) | UT-W1-003 |
| FR-W1-04 | API-W1-004.01–.04 passed | TC-UC01-E1 | BVA overlap start/end boundaries (5); DT1 R2 and DT-002 table (14); GEN-001 overlap limits (5); API-INT-001.02 (rejection releases the dates), .08 (sequential repeat); API-INT-002.01/.02 characterisation (concurrent overlap, DEF-A2-02) | UT-W1-004 |
| FR-W1-05 | API-W1-005.01–.02 passed; .03 partly characterisation; .04/.05 characterisation (GAP-07, GAP-01) | TC-UC01-M (D = A), TC-UC01-E2 (D = A+1) | BVA balance D = A−1/A/A+1 (3); GEN-001 balance limit (4); DT1 R3–R5 (DT-001; R3 characterisation GAP-07); API-INT-001.03 and .09 (EC-01 scenario) overdraw characterisation (GAP-01, DEF-A2-01) | UT-W1-005, MCC-001, API-INT-001 desired overdraw regression (blocked, GAP-01) |
| FR-W1-06 | API-W1-006.01 passed | TC-UC01-M | ST-001 none→pending; API-INT-001.01/.02 (same k read back through W2); DT-004 submission recipients (10) and refused calls (1); event after commit (`test_event_publication.py`) | UT-W1-006, UT-EVT-001 (Redis disabled in profile) |
| FR-W2-01 | API-W2-001.01, API-W2-002.04 passed | TC-UC02-A2 (admin sees all teams) | EP role manager of other team (404); DT2 R2; DT-003 visibility table (6); DT-005 upcoming leave (9); API-INT-001.01, .05 (list and scoped lookup) | UT-W2-001 |
| FR-W2-02 | API-W2-002.01–.07 passed | TC-UC02-E2 (self 403), TC-UC02-A2 | EP role (4) and nonexistent request id; DT2 R1–R3, R5 (DT-003 authorization guards); GEN-001 W2 path `id` (5) and contexts (8 refusals, admin); API-INT-001.04 (self/role), .05 (cross-team) | UT-W2-002, SEC-001 |
| FR-W2-03 | API-W2-003.01–.03 passed (invalid values API-only) | TC-UC02-M/A1 (valid values) | EP `status` (5); GEN-001 W2 `status` cases (8) | UT-W2-003 |
| FR-W2-04 | API-W2-004.01–.02 passed | TC-UC02-E1 (409, first decision preserved) | EP already-decided request id; DT2 R4; ST-001 final-state rows (4 × 409); API-INT-001.06/.07 (re-decide after approval/rejection); API-INT-002.03/.04 (row lock: one 200, one 409) | UT-W2-004 |
| FR-W2-05 | API-W2-002.02 + 005.01, 002.03 passed | TC-UC02-M | EP `status` approved; DT2 R5; ST-001 pending→approved; DT-004 approval recipient; DT-005 approval becomes upcoming leave; API-INT-001.01 (approve path), .03 (overdraw characterisation) | UT-W2-005, API-INT-001 desired overdraw regression, OBJ-UC02-01 blocked |
| FR-W2-06 | API-W2-006.01 passed | TC-UC02-A1 (no charge, dates released) | EP `status` rejected; ST-001 pending→rejected; DT-004 rejection recipient; API-INT-001.02 (reject path), .07 | UT-W2-006 |

**Requirements coverage (Lecture 18: requirements with at least one executed test).**

- **API level:** 12 of 12 original FRs have at least one passing A2.1 test (some rows are characterisations of unresolved policy, labelled as such).
- **Browser level:** 12 of 12 are touched by a passing UC-01/UC-02 flow. Invalid decision values are exercised at API level only.
- **Unit level:** 0 of 12 (white-box work not started).
- **PROPOSED FRs:** FR-ADM-01, FR-ADM-02 and FR-NOTIF-01 have 0 executed tests and are excluded until approved.

**Objective families with executed evidence:**

- API-W1-001…006 and API-W2-001…006 (A2.1 child IDs).
- **ST-001 — executed at API level:** creation→pending, pending→approved/rejected, approved/rejected × {approve, reject} → 409, and pending × invalid value → 400 (`FinalStateTests`, `DecisionValueTests`, `AuthorizedDecisionTests`). This meets Lecture 15 "all transitions" for the API state table; browser-level ST is partial. A2.3 adds the dedicated 7-row state table (`tests/team/structural/test_state_transition.py`).
- **API-INT-002 — executed (A2.2) on disposable PostgreSQL 17:** 5 tests, API-INT-002.01–.05 (`tests/team/concurrency/`, run by `scripts/sqe/run_concurrency.py`; not part of the in-memory suite). .01/.02/.05 are characterisations of DEF-A2-02 and DEF-A2-01.
- **API coverage — measured:** [API-COVERAGE.md](../testing/API-COVERAGE.md): TCL7 under the mapping stated there, 100% of the ten REST criteria. The target level is a pending team decision.
- **Endpoint weaknesses:** [DEFECT-RECORDS.md](../defects/DEFECT-RECORDS.md), DEF-A2-01…06; issue links PENDING.
- **API-INT-001 — executed (A2.2):** 9 integration tests, API-INT-001.01–.09 (`tests/team/integration/test_w1_w2_integration.py`). .03 is a characterisation of GAP-01 that passes on the baseline; the desired failing overapproval regression remains blocked until the approval-time error contract is approved.
- **GEN-001 — executed (A2.4, completed 25 Nov 2026):** 127 tests generated from the spec (19 login, 49 W1, 32 W2, 27 reads; 33 on 24 November, 68 earlier on 25 November). Inputs: body fields, trimmed note, path `id`, actor and record context, Authorization, request media, methods, and the balance and overlap limits. Exact status, error key, response schema and stored state are asserted. Manifest `tests/team/generated/generated_cases.json`, observed results in `api/coverage-2026-11-25/observed_cases.json`. Three constraint changes are demonstrated (`docs/sqe/openapi/README.md`). Some generated cases repeat classes of A2.1, A2.3 and the contract suite: count each class once at the API level.
- **OpenAPI contract — executed (A2.4, part of GEN-001 "compare actual contract drift"):** 41 tests in `tests/team/api/test_openapi_contract.py`. Every documented (operation, status) pair of the seven operations is produced by a real call and its status, media type and body validated against the spec; a completeness test enforces this. Three baseline deviations are pinned as characterisations, not approved behaviour: 500 for a non-object JSON body on login and on W2, and 500 for W1 `end_date` 9999-12-31. **Defect issues: PENDING — student to file.**
- **DT-001 — executed (A2.3):** code table DT1 rules R3–R5 (balance record × over-limit; the masked row R3 is a GAP-07 characterisation).
- **DT-002 — executed:** `tests/team/structural/test_decision_table_rules.py`, all 24 feasible combinations of the five overlap conditions: 12 through the API (one test each, plus the approved value of the all-true row) and 12 with pk exclusion at model level (one test). The other 8 are infeasible for ordered intervals. *(Corrects the 24 November entry, which called DT-002 executed on the strength of one rule and the BVA cases, and called pk exclusion unreachable; it is reachable through `clean()` on a saved row.)*
- **DT-003 — executed:** visibility table in the same file (all four manager/team rows and the admin bypass; the teamless-employee row had no earlier team test), with code table DT2 for the ordered decision guards.
- **DT-004 — executed:** the nine feasible recipient rules, the decision branch (owner only) and refused calls (no event). The teamless row is a GAP-08 characterisation. Recipients are computed by the real `build_leave_event` from a real API call; Redis delivery is not exercised.
- **DT-005 — executed:** all four rows with today−1/today/today+1, the no-request and earliest-start cases, and approval through W2, read from `GET /api/team/`.
- **SEC-001:** partly executed (browser allow decisions TC-UC02-M/A2 and deny TC-UC02-E2; the dedicated ≥4-decision access suite is still planned).

**Not started:** UT-*, SEC-002/003, ACC-*, PERF-001, REC-*, UT-EVT-001, MUT-001, MCC-001 and REG-001. DT-001's W2 half (approval-time balance oracle) is blocked by GAP-01. *(MCC-001: feasibility evidence only — `docs/sqe/evidence/whitebox/critical-module-2026-11-24/`; no team white-box test exists yet.)*

## Browser use-case flow catalog (v0.2)

Canonical definitions; flows are specified in [USE-CASE-SPECIFICATIONS.md](../requirements/USE-CASE-SPECIFICATIONS.md) and registered in `tests/team/browser/flows.json`. **Mandatory denominator: 30 flows.** INC, OBJ and SUP rows are reported separately.

| ID | UC (owner) | Kind | FR | BR | Status (24 Nov 2026) | Legacy v0.1 ID |
|---|---|---|---|---|---|---|
| TC-UC01-M | UC-01 (M1) | main | FR-W1-01…06 | BR-01, BR-03, BR-04, BR-05, BR-06 | Passed (b1/run-1, run-2) | E2E-UC01-01 |
| TC-UC01-A1 | UC-01 (M1) | alternative | FR-W1-03, FR-W1-06 | BR-01 | Passed | — |
| TC-UC01-A2 | UC-01 (M1) | alternative | FR-W1-06 | BR-04 | Passed | E2E-UC04-03 |
| TC-UC01-E1 | UC-01 (M1) | exception | FR-W1-04 | BR-02 | Passed | E2E-UC01-04 |
| TC-UC01-E2 | UC-01 (M1) | exception | FR-W1-05 | BR-03, BR-01 | Passed | E2E-UC01-05 |
| TC-UC02-M | UC-02 (M2) | main | FR-W2-01, FR-W2-02, FR-W2-04, FR-W2-05 | BR-03, BR-04, BR-05 | Passed | E2E-UC02-01 |
| TC-UC02-A1 | UC-02 (M2) | alternative | FR-W2-06, FR-W1-04 | BR-02, BR-03, BR-05 | Passed | E2E-UC03-01 |
| TC-UC02-A2 | UC-02 (M2) | alternative | FR-W2-01, FR-W2-02, FR-W2-05 | BR-04, BR-05 | Passed | E2E-UC02-03 |
| TC-UC02-E1 | UC-02 (M2) | exception | FR-W2-04 | BR-05 | Passed (UI feedback recorded, OBS-UC02-01) | E2E-UC02-04 |
| TC-UC02-E2 | UC-02 (M2) | exception | FR-W2-02 | BR-04 | Passed (UI feedback recorded) | E2E-UC02-05 |
| TC-UC04-M | UC-04 (M3) | main | FR-W2-01, FR-W1-05 | BR-03, BR-04 | Specified, not automated | E2E-UC04-01 |
| TC-UC04-A1 | UC-04 (M3) | alternative | FR-W2-01 | BR-04 | Specified, not automated | — |
| TC-UC04-A2 | UC-04 (M3) | alternative | FR-W2-05, FR-W2-06 | BR-03, BR-05 | Specified, not automated | — |
| TC-UC04-E1 | UC-04 (M3) | exception | FR-W1-01 | BR-04 | Specified, not automated | E2E-UC04-05 |
| TC-UC04-E2 | UC-04 (M3) | exception | FR-W2-01 | BR-04 | Specified; expected result pending probe (GAP-15) | E2E-UC04-04 |
| TC-UC07-M | UC-07 (M2) | main | FR-NOTIF-01 (PROPOSED), FR-W1-06, FR-W2-05, FR-W2-06 | BR-04, BR-05 | Blocked: D-2 + isolated environment | — |
| TC-UC07-A1 | UC-07 (M2) | alternative | FR-NOTIF-01 (PROPOSED), FR-W1-06, FR-W2-05, FR-W2-06 | BR-04, BR-05 | Blocked: D-2 + isolated environment | — |
| TC-UC07-A2 | UC-07 (M2) | alternative | FR-NOTIF-01 (PROPOSED), FR-W1-06, FR-W2-05, FR-W2-06 | BR-04, BR-05 | Blocked: D-2 + isolated environment | — |
| TC-UC07-E1 | UC-07 (M2) | exception | FR-NOTIF-01 (PROPOSED), FR-W1-06, FR-W2-05, FR-W2-06 | BR-04, BR-05 | Blocked: D-2 + isolated environment | — |
| TC-UC07-E2 | UC-07 (M2) | exception | FR-NOTIF-01 (PROPOSED), FR-W1-06, FR-W2-05, FR-W2-06 | BR-04, BR-05 | Blocked: D-2 + isolated environment | — |
| TC-UC08-M | UC-08 (M1) | main | FR-ADM-01 (PROPOSED), FR-W1-05 | BR-03 | Blocked: D-1 | — |
| TC-UC08-A1 | UC-08 (M1) | alternative | FR-ADM-01 (PROPOSED), FR-W1-05 | BR-03 | Blocked: D-1 | — |
| TC-UC08-A2 | UC-08 (M1) | alternative | FR-ADM-01 (PROPOSED), FR-W1-05 | BR-03 | Blocked: D-1 | — |
| TC-UC08-E1 | UC-08 (M1) | exception | FR-ADM-01 (PROPOSED), FR-W1-05 | BR-03 | Blocked: D-1 | — |
| TC-UC08-E2 | UC-08 (M1) | exception | FR-ADM-01 (PROPOSED), FR-W1-05 | BR-03 | Blocked: D-1 | — |
| TC-UC09-M | UC-09 (M3) | main | FR-ADM-02 (PROPOSED), FR-W2-01, FR-W2-02 | BR-04 | Blocked: D-1 | — |
| TC-UC09-A1 | UC-09 (M3) | alternative | FR-ADM-02 (PROPOSED), FR-W2-01, FR-W2-02 | BR-04 | Blocked: D-1 | — |
| TC-UC09-A2 | UC-09 (M3) | alternative | FR-ADM-02 (PROPOSED), FR-W2-01, FR-W2-02 | BR-04 | Blocked: D-1 | — |
| TC-UC09-E1 | UC-09 (M3) | exception | FR-ADM-02 (PROPOSED), FR-W2-01, FR-W2-02 | BR-04 | Blocked: D-1 | — |
| TC-UC09-E2 | UC-09 (M3) | exception | FR-ADM-02 (PROPOSED), FR-W2-01, FR-W2-02 | BR-04 | Blocked: D-1 | — |
| INC-01 | Included (M3) | included | FR-W1-01 | BR-04 | Exercised inside every B1 test; dedicated test planned | E2E-UC03-05 |
| INC-02 | Included (M1/M3) | included | FR-ADM-01/02 (PROPOSED) | BR-04 | Blocked: D-1 | — |
| OBJ-UC02-01 | UC-02 (M2) | blocked objective | FR-W2-05 | BR-03 | Blocked: approval-time error contract (GAP-01); registered as fixme | — |
| SUP-UC07-01 | UC-07 (M2) | supplementary | FR-NOTIF-01 (PROPOSED) | BR-05 | Blocked: D-2 | — |
| SUP-UC09-01 | UC-09 (M3) | supplementary | FR-ADM-02 (PROPOSED), FR-W2-02 | BR-04 | Blocked: D-1 | — |

Mandatory flow coverage: **10 of 30 executed and passed (33.3%)**. If OBJ-UC02-01 is approved as a UC-02 exception, the denominator becomes 31.

## Rule coverage cross-check (planned only)

| BR | Primary rule purpose | Representative planned objectives |
|---|---|---|
| BR-01 | Date order/inclusive weekdays | UT-W1-003, API-W1-003, UT-W1-005, API-W1-005, GEN-001, ACC-001 |
| BR-02 | Active same-owner overlap | UT-W1-004, API-W1-004, UT-W2-006, API-W2-006, API-INT-001, API-INT-002, GEN-001, DT-002, ACC-001 |
| BR-03 | Submission balance/derived allowance; missing approval guard | UT-W1-005, API-W1-005, UT-W2-005, API-W2-005, UT-W2-006, API-W2-006, API-INT-001, API-INT-002, GEN-001, DT-001, DT-005, ACC-001, REC-002, MCC-001 |
| BR-04 | Token/role/team/self authorization | UT-W1-001, API-W1-001, UT-W1-006, API-W1-006, UT-W2-001, API-W2-001, UT-W2-002, API-W2-002, UT-W2-005, API-W2-005, UT-W2-006, API-W2-006, DT-003, DT-004, DT-005, SEC-001, SEC-002, SEC-003, ACC-002, PERF-001, REC-001, UT-EVT-001, MCC-001 |
| BR-05 | Pending-only transitions, same persisted k | UT-W1-001, API-W1-001, UT-W1-006, API-W1-006, UT-W2-003, API-W2-003, UT-W2-004, API-W2-004, UT-W2-005, API-W2-005, UT-W2-006, API-W2-006, API-INT-001, API-INT-002, DT-004, ST-001, SEC-001, ACC-002, PERF-001, REC-001, REC-002, UT-EVT-001 |
| BR-06 | Field/default/note/decision domains | UT-W1-001, API-W1-001, UT-W1-002, API-W1-002, UT-W1-006, API-W1-006, UT-W2-003, API-W2-003, GEN-001, ST-001, SEC-003, ACC-001, PERF-001 |

*v0.2 executed rule coverage:* all six BRs have passing A2.1 API tests: BR-01 API-W1-003; BR-02 API-W1-004 and TC-UC02-A1; BR-03 API-W1-005 and API-W2-005.01; BR-04 API-W1-001 and API-W2-001/002; BR-05 API-W2-004/003 (ST-001); BR-06 API-W1-002 and API-W2-003. Characterisation rows are not approved oracles.

## Conditional UC ownership and flow mapping (v0.1, historical)

> **Superseded on 24 Nov 2026.** Current catalog and ownership (PROPOSED): UC-01 Member 1, UC-02 Member 2, UC-04 Member 3, UC-07 Member 2, UC-08 Member 1, UC-09 Member 3; see [Browser use-case flow catalog (v0.2)](#browser-use-case-flow-catalog-v02) and [TEAM-OWNERSHIP.md](TEAM-OWNERSHIP.md). The table below is the v0.1 record.

Use-case goals/alternatives/exceptions are taken from [Phase1 WORKFLOW-TRACE](../requirements/WORKFLOW-TRACE.md), not invented actions. All six are **candidates**; UC-04–06 supporting goals have particular distinctness risk; approve/reject separation also requires review. Proposed member assignments do not imply agreement.

| UC candidate | Goal / proposed owner | Planned flow IDs (main, two alternatives, two exceptions) | Acceptance / gaps |
|---|---|---|---|
| UC-01 | Employee submit leave / Member1 | E2E-UC01-01, E2E-UC01-02, E2E-UC01-03, E2E-UC01-04, E2E-UC01-05 | PENDING instructor/team goal acceptance; strong candidate; exception oracles need approved spec |
| UC-02 | Manager approve leave / Member2 | E2E-UC02-01, E2E-UC02-02, E2E-UC02-03, E2E-UC02-04, E2E-UC02-05 | PENDING instructor/team goal acceptance; strong candidate; exception oracles need approved spec |
| UC-03 | Manager reject leave / Member3 | E2E-UC03-01, E2E-UC03-02, E2E-UC03-03, E2E-UC03-04, E2E-UC03-05 | PENDING instructor/team goal acceptance; strong candidate; exception oracles need approved spec |
| UC-04 | Employee inspect remaining balance / Member1 | E2E-UC04-01, E2E-UC04-02, E2E-UC04-03, E2E-UC04-04, E2E-UC04-05 | PENDING instructor/team goal acceptance; supporting/read-only goal distinction unresolved |
| UC-05 | Manager locate decision work / Member2 | E2E-UC05-01, E2E-UC05-02, E2E-UC05-03, E2E-UC05-04, E2E-UC05-05 | PENDING instructor/team goal acceptance; supporting/read-only goal distinction unresolved |
| UC-06 | Manager inspect team availability / Member3 | E2E-UC06-01, E2E-UC06-02, E2E-UC06-03, E2E-UC06-04, E2E-UC06-05 | PENDING instructor/team goal acceptance; supporting/read-only goal distinction unresolved |

## Updating traceability and guarding counts

Initial structural planning inventory:12 FRs, six BRs, **75 unique objective definitions**, including30 conditional browser flow slots. This count is document metadata, not implemented tests, coverage or marks. Security/accessibility/UC task cases may overlap; count the executable case once within its level and attach multiple trace links. Separate upstream tests from team-owned metrics.

**v0.2 recount (24 Nov 2026):**

- The 75 v0.1 definitions comprise 45 non-browser objectives (unchanged) and 30 E2E slots.
- The 30 E2E slots break down as: 12 mapped to TC flows; 1 moved to INC-01; 12 retired; 5 held as UC-06 reserve. None of them is counted any more.
- The active catalog is 45 non-browser objectives + 35 browser-level IDs (30 mandatory TC flows, 2 INC, 1 OBJ, 2 SUP) = **80 active definitions**.
- Requirements: 12 original FRs (counted) + 3 PROPOSED supporting FRs (not counted until approved); 6 BRs.

On each implementation/review: (1) retain planned ID, add real file/node ID or expand child IDs with reviewed catalog update; (2) record expected source/rule/feasibility, data/spec hash and risk; (3) append actual run evidence/outcome, never overwrite a failure with a later pass; (4) attach genuine Issue/PR URLs and regression linkage only after student creation; (5) review forward **and** backward mappings for orphan tests/requirements. New/changed requirements need controlled review, not silent renumbering. Record tested/blocked/not-tested/N/A with reason; unapproved UC/scope/API checklist items stay blocked, not green.

A2 owns RTM updates with A1 checking branch/MCC/mutation links and A3 checking browser/nonfunctional evidence. Weekly coverage uses distinct FRs with implemented or passing assertions, not number of IDs in this draft. Current all future result metrics are NOT MEASURED. See [QUALITY-METRICS](QUALITY-METRICS-PLAN.md), [criteria](ENTRY-EXIT-CRITERIA.md) and [defect lifecycle](DEFECT-MANAGEMENT-PLAN.md).
