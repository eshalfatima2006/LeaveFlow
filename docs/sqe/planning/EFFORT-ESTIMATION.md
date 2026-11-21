# Proposed effort estimates and actual-effort procedure

Version0.1 — 22 November 2026. All estimates are **team-review proposals**, in **person-hours**, not professor-supplied figures or historical measured effort. Existing planning drafts are partial inputs; package estimates include their review/rework and later full deliverable. No elapsed AI turn or previously completed baseline work is retrospectively recorded as student actual effort. Proposed owner areas are defined in [TEAM-OWNERSHIP](TEAM-OWNERSHIP.md).

For each package: E=(O+4M+P)/6; standard deviation SD=(P−O)/6. O assumes compatible tools/clear oracles; M allows normal fixture/debug/review work; P allows major tool/CI/spec/mutation investigation. These are judgments, not calibrated distributions. Display two decimals; compute totals from unrounded values. No package hours are multiplied by three merely because all members participate. Cross-package shared fixes/UC effort are logged once against their primary package, with other links informational.

| Work package | Description | Proposed owner | O h | M h | P h | E h | SD h | Actual h | Variance h | Status | Dependencies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| WP-01 | Scope/requirements and policy review | Shared | 4 | 6 | 10 | 6.33 | 1.00 | NOT MEASURED | NOT MEASURED | Draft review pending | None |
| WP-02 | Strategy/test-plan/criteria and ownership review | Shared | 3 | 5 | 8 | 5.17 | 0.83 | NOT MEASURED | NOT MEASURED | Draft review pending | WP-01 |
| WP-03 | Risk register, matrix and prioritization | Shared | 2 | 4 | 7 | 4.17 | 0.83 | NOT MEASURED | NOT MEASURED | Draft review pending | WP-01 |
| WP-04 | Forward/backward RTM and case catalog | A2 | 2 | 4 | 7 | 4.17 | 0.83 | NOT MEASURED | NOT MEASURED | Draft review pending | WP-01, WP-03 |
| WP-05 | Isolated environments, fixed fixtures and reset proof | A2 | 4 | 7 | 12 | 7.33 | 1.33 | NOT MEASURED | NOT MEASURED | Not started | WP-02 |
| WP-06 | Sonar deployment, scan and metric interpretation | A1 | 3 | 5 | 10 | 5.50 | 1.17 | NOT MEASURED | NOT MEASURED | Not started | WP-05 |
| WP-07 | Manual CFG/cyclomatic comparison | A1 | 2 | 3 | 5 | 3.17 | 0.50 | NOT MEASURED | NOT MEASURED | Not started | WP-06 |
| WP-08 | Team unit/white-box tests, full coverage and assertions | A1 | 8 | 14 | 24 | 14.67 | 2.67 | NOT MEASURED | NOT MEASURED | Not started | WP-05 |
| WP-09 | Complete critical-module MCC and derived MC/DC | A1 | 4 | 7 | 12 | 7.33 | 1.33 | NOT MEASURED | NOT MEASURED | Not started | WP-07, WP-08 |
| WP-10 | API tests and cross-workflow integration | A2 | 8 | 14 | 24 | 14.67 | 2.67 | NOT MEASURED | NOT MEASURED | Not started | WP-05, WP-11 |
| WP-11 | Accurate OpenAPI and rule-manifest repair | A2 | 3 | 5 | 9 | 5.33 | 1.00 | NOT MEASURED | NOT MEASURED | Not started | WP-01 |
| WP-12 | EP/BVA generator, API consumption and two-constraint demo | A2 | 6 | 10 | 18 | 10.67 | 2.00 | NOT MEASURED | NOT MEASURED | Not started | WP-10, WP-11 |
| WP-13 | Decision tables and feasible/infeasible row tests | A2 | 3 | 5 | 9 | 5.33 | 1.00 | NOT MEASURED | NOT MEASURED | Not started | WP-10 |
| WP-14 | State transitions, repeated decisions and duplicates | A2 | 3 | 5 | 9 | 5.33 | 1.00 | NOT MEASURED | NOT MEASURED | Not started | WP-10 |
| WP-15 | Six accepted UCs and all Playwright flows | A3 (all implement two UCs) | 12 | 20 | 34 | 21.00 | 3.67 | NOT MEASURED | NOT MEASURED | Blocked on UC acceptance | WP-10, WP-11 |
| WP-16 | Mutation tool, custom operators and survivor analysis | A1 | 6 | 11 | 20 | 11.67 | 2.33 | NOT MEASURED | NOT MEASURED | Not started | WP-08, WP-09 |
| WP-17 | Strict PR CI gates and real blocked/fix PR evidence | A1 | 5 | 8 | 15 | 8.67 | 1.67 | NOT MEASURED | NOT MEASURED | Not started | WP-06, WP-12, WP-15, WP-16 |
| WP-18 | Task/keyboard, Lighthouse/axe and before/after improvement | A3 | 5 | 8 | 14 | 8.50 | 1.50 | NOT MEASURED | NOT MEASURED | Not started | WP-15 |
| WP-19 | Role security, ZAP passive and dependency audit | A3 | 5 | 9 | 16 | 9.50 | 1.83 | NOT MEASURED | NOT MEASURED | Not started | WP-10, WP-15 |
| WP-20 | k6 fixture protocol and four steady-state runs | A3 | 4 | 7 | 12 | 7.33 | 1.33 | NOT MEASURED | NOT MEASURED | Not started | WP-05, WP-10 |
| WP-21 | Controlled write failure/restoration/retry and readback | A3 | 4 | 7 | 13 | 7.50 | 1.50 | NOT MEASURED | NOT MEASURED | Not started | WP-10, WP-14 |
| WP-22 | Genuine defect reporting, triage, fixes/retests and regression | Shared | 3 | 6 | 12 | 6.50 | 1.50 | NOT MEASURED | NOT MEASURED | Not started | WP-08, WP-10 |
| WP-23 | Two verified major-defect RCAs, fishbones and Pareto | Shared | 4 | 7 | 14 | 7.67 | 1.67 | NOT MEASURED | NOT MEASURED | Blocked until major defects verified | WP-22 |
| WP-24 | Session actual-effort logs and weekly GQM/control reports | Shared | 3 | 5 | 9 | 5.33 | 1.00 | NOT MEASURED | NOT MEASURED | Not measured | WP-02, WP-03 |
| WP-25 | Completion, residual risk and release/hold report | Shared | 3 | 5 | 9 | 5.33 | 1.00 | NOT MEASURED | NOT MEASURED | Not started | WP-17, WP-18, WP-19, WP-20, WP-21, WP-23, WP-24 |
| WP-26 | Final PDF/ZIP, source/evidence/link checks | Shared | 3 | 5 | 8 | 5.17 | 0.83 | NOT MEASURED | NOT MEASURED | Not started | WP-25 |
| WP-27 | Individual viva reruns and live-rule/spec rehearsal | Shared | 4 | 7 | 12 | 7.33 | 1.33 | NOT MEASURED | NOT MEASURED | Not started | WP-26 |

Total proposed expected effort: **210.67 person-hours**. Sum O=116h, M=199h, P=352h. No actual-total or variance number exists. This is effort, not calendar duration; capacity, deadline, confirmed ownership and dependency bottlenecks must be supplied before forecasting dates. A notional independent-package aggregate SD is 8.38h (sqrt(sum(SD²))); shared tool/approval risks correlate packages, so do **not** treat that as a confidence interval or promised finish date.

## Estimate assumptions and change control

Highest-risk PR-01/PR-02 investigation and persisted-state assertions are included in WP-08/10/22, with allocation recorded once per work session. WP-15 is aggregate work for six accepted goals/all flows across all three members, not six screenshots or only main paths. WP-16 includes ≥2 custom operators and ≥15 survivor analyses; unclear feasibility increases uncertainty rather than reducing the requirement. WP-22 includes bounded expected fixes/retests, not unlimited defect scope; major discoveries require a revised forecast. WP-18 includes one separately authorized before/after screen improvement. Student Git/PR review time is included in respective packages and WP-17, without assuming Codex performs it.

Node/npm availability, Sonar runners, Python/tool compatibility, PostgreSQL/Redis isolation, scope/MCC approval and six-use-case acceptance are external dependencies from the risk register. WP-24 runs weekly alongside other packages; WP-22/23 start only with genuine findings and can overlap later execution. Rehearsal starts informally as tests become available; WP-27 estimates final consolidated rerun/live-task practice after packaging. See [EXECUTION-ROADMAP](EXECUTION-ROADMAP.md) for milestones/concurrent lanes.

Preserve original O/M/P and estimate version. After learning changes, add revised remaining forecast with reason/date/approver, never overwrite historical actuals or retune original estimates to look accurate. Variance for completed package=actual−original E; positive means overrun. In-progress forecasts use actual-to-date+remaining estimate and are labelled forecasts. Unlogged hours stay NOT MEASURED, not0.

## Repeatable actual-effort procedure

After **every** actual student session, append to an agreed time log (future artifact, not created here): member, work-package ID, actual start/end timezone, breaks, net person-hours, activity, artifact/test/issue links, result and blocker. For collaboration record each person's own hours once; two people ×1h=2 person-hours. Do not log waiting for CI as active work unless the student is actively investigating. Reviewer verifies totals against session evidence at weekly review; no inferred hours from commits or AI runtime.

At each weekly review aggregate unique log rows by package/member, report actual-to-date and remaining forecast, compare completed-package actual vs E, explain deviations and choose control action/owner. Retain logs and calculation source for final actual-vs-planned comparison required by assignment p2. A sample empty record is: `member=PENDING; WP=PENDING; start/end=PENDING; net hours=NOT MEASURED; evidence=PENDING` — not an observed session.

## Compact weekly progress template

Periods are relative to approved planning start T0; no announcement/deadline was available. Copy one row per real week and replace fields from logs only.

| Reporting week / actual period | Planned milestone/packages | Baseline E for those packages | Actual-to-date | Remaining forecast | Variance for completed work | Evidence / control action |
|---|---|---|---|---|---|---|
| W1 / actual dates PENDING | M0 review; M1 isolation; early PR-01/02 | Calculate from selected WP rows, no double counting | NOT MEASURED | NOT MEASURED | NOT MEASURED | Reviewer and blockers PENDING |
| W2+ / actual dates PENDING | Dependency-ready M2–M4 work | Recalculate selected-package total | NOT MEASURED | NOT MEASURED | NOT MEASURED | Link [weekly GQM report](QUALITY-METRICS-PLAN.md) |

No row is a promised one-week capacity or completed work statement. Students must map their real available hours/deadline before committing to weekly delivery.
