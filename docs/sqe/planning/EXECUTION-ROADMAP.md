# Dependency-aware execution roadmap

Version0.1 — 22 November 2026. This is a **proposed future roadmap**, not a schedule of completed work. No actual final deadline, availability or announcement date was supplied by the accessible assignment; milestones are relative to T0=actual planning acceptance. Do not convert person-hours to invented dates. Area/member allocations and budgets require review. [EFFORT-ESTIMATION](EFFORT-ESTIMATION.md) is the arithmetic source; [TEST-PLAN](TEST-PLAN.md) defines environment/isolation, and [criteria](ENTRY-EXIT-CRITERIA.md) defines completion.

## Sequencing and concurrent lanes

M0 review fixes boundaries/oracles, top PR-01/PR-02 controls and feasibility; M1 proves safe isolation/tools; M2 establishes white-box/API/generated functional foundation; M3 integrates browser/mutation/CI; M4 adds controlled nonfunctional/recovery/before-after evidence; M5 consolidates completion/package/viva. A gate may need approval before it can be evaluated, not before unrelated planning can proceed.

After isolation, A1 Sonar/CFG/unit and A2 spec/API/generator can proceed concurrently; A3 can specify approved browser goals/selectors and security/performance protocols while runtime tools are being repaired. Each member implements two approved UCs, coordinated by A3. Accessibility/security can start as soon as their browser dependencies stabilize, without waiting for every CI task. Mutation follows meaningful team tests, not empty green stubs; strict gates follow functioning tools but must be complete before final release. Defects/weekly metrics run throughout. No sub-agent work or repository branch changes are implied by concurrent student lanes.

**First runtime priorities:** reproduce PR-01 desired allowance violation and prove PR-02 access matrix with real token/persisted assertions; do not postpone them until late E2E/load work. Investigation can use source/spec planning while oracle/fixtures are reviewed, but an unapproved policy cannot yield a claimed passing regression. State/concurrency/recovery checks follow safe isolation and the appropriate database profile.

## Work packages, dependencies and completion evidence

All E values are proposed aggregate person-hours (including all participants), not actual logs. Dependencies identify minimum upstream package inputs; major-finding fixes, scope approvals and appropriate entry criteria remain additional gates. Package labels are unchanged from the estimate table; all execution outcomes are NOT MEASURED.

| Package / activity | Relative milestone | Proposed owner | E h | Dependencies | Actual completion evidence required | Main risk/blocker |
|---|---|---|---|---|---|---|
| WP-01 Scope/requirements and policy review | M0 | Shared | 6.33 | None | Actual scope/oracle/critical-module/UC/API checklist decisions and retained prompts | JR-03/04: instructor and roster decisions |
| WP-02 Strategy/test-plan/criteria and ownership review | M0 | Shared | 5.17 | WP-01 | Reviewed strategy/plan/criteria/ownership acknowledgments with revision record | JR-03/04: approval/capacity unknown |
| WP-03 Risk register, matrix and prioritization | M0 | Shared | 4.17 | WP-01 | Reviewed16-risk register/matrix/rank and accepted provisional scores | PR-01/02 priorities; JR-03 scope |
| WP-04 Forward/backward RTM and case catalog | M0 | A2 | 4.17 | WP-01, WP-03 | Reviewed12FR/6BR forward/backward catalog with all planned links | GEN/UC execution evidence not yet present |
| WP-05 Isolated environments, fixed fixtures and reset proof | M1 | A2 | 7.33 | WP-02 | Tool/lock/version manifest, disposable target guard, repeat fixed-fixture reset proof | JR-01/02: unsafe seed, Node/npm failure (v0.2: resolved; versions verified in B1), PostgreSQL availability |
| WP-06 Sonar deployment, scan and metric interpretation | M2-A1 | A1 | 5.50 | WP-05 | Genuine Sonar task and full metrics/ratings/debt interpretation with source SHA | JR-02: free OSS server/runner capacity/PR-gate features |
| WP-07 Manual CFG/cyclomatic comparison | M2-A1 | A1 | 3.17 | WP-06 | Hand CFG nodes/edges/V(G), corresponding Sonar function comparison | JR-03: agreed function and metric convention |
| WP-08 Team unit/white-box tests, full coverage and assertions | M2-A1 | A1 | 14.67 | WP-05 | Team-owned meaningful assertions and raw100/100 coverage/approved exceptions; early PR-01/02 probes | PR-01/02; JR-03 denominator; tools/fixtures |
| WP-09 Complete critical-module MCC and derived MC/DC | M2-A1 | A1 | 7.33 | WP-07, WP-08 | Full selected-critical-module (DR-001, PROPOSED) MCC with infeasible-row reasons and derived MC/DC pair evidence | JR-03: missing-balance masking interpretation/critical-module approval |
| WP-10 API tests and cross-workflow integration | M2-A2 | A2 | 14.67 | WP-05, WP-11 | Real-token API results and W1→W2 original-k readbacks; prioritize balance/access before broad cases | PR-01/02/03/10; approved desired balance oracle |
| WP-11 Accurate OpenAPI and rule-manifest repair | M2-A2 | A2 | 5.33 | WP-01 | Accurate versioned selected-endpoint OpenAPI, error/status/field contracts and rule manifest | PR-06/07: empty inference and policy gaps |
| WP-12 EP/BVA generator, API consumption and two-constraint demo | M2-A2 | A2 | 10.67 | WP-10, WP-11 | Reproducible generator cases consumed by APIs; two constraint-change/regeneration diffs | PR-06/07: approved spec; no fake fixed maxDays26 |
| WP-13 Decision tables and feasible/infeasible row tests | M2-A2 | A2 | 5.33 | WP-10 | All applicable compound-rule rows mapped to executions with feasibility justifications | PR-04/07; SQL vs Python branch distinction |
| WP-14 State transitions, repeated decisions and duplicates | M2-A2 | A2 | 5.33 | WP-10 | Both allowed decision transitions and ≥1 disallowed event per state; repeat/no-duplicate assertions | PR-03/05: same-k metadata and real locking DB |
| WP-15 Six accepted UCs and all Playwright flows | M3 | A3 (all implement two UCs) | 21.00 | WP-10, WP-11 | Six accepted UCs/two per member, every main/≥2alt/≥2exception flow automated with UI/persistence evidence | JR-03/PR-08: actor-goal feasibility and missing decision error feedback (v0.2: 10/30 flows passed; UC-07/08/09 depend on D-1/D-2) |
| WP-16 Mutation tool, custom operators and survivor analysis | M3 | A1 | 11.67 | WP-08, WP-09 | Tool results, ≥2 custom rule operators, ≥15 real survivor analyses/reruns and adjusted/raw score | JR-02/03: mutation runtime/compatibility/fewer-than15 survivors |
| WP-17 Strict PR CI gates and real blocked/fix PR evidence | M3 | A1 | 8.67 | WP-06, WP-12, WP-15, WP-16 | Required PR test/Sonar/mutation gates; genuine blocked PR and corrected fail-before/pass-after fix evidence | JR-02/04: student Git/protected checks, full-job release linkage |
| WP-18 Task/keyboard, Lighthouse/axe and before/after improvement | M4 | A3 | 8.50 | WP-15 | Two task tests/error-correction/keyboard, Lighthouse3 categories+axe per UC screen, one before/after improvement | PR-08: later authorized screen change and repeatable logged-in scans |
| WP-19 Role security, ZAP passive and dependency audit | M4 | A3 | 9.50 | WP-10, WP-15 | ≥4 browser access decisions, ≥2 actual controls, ZAP passive and pinned pip/npm audit with triage | PR-02/09: local authorization and unverified dependency reports |
| WP-20 k6 fixture protocol and four steady-state runs | M4 | A3 | 7.33 | WP-05, WP-10 | Four k6 runs1/5VUs twice each, ≥60s steady state, raw p95/rps/errors vs predeclared budgets | PR-03/10/JR-01: stable fixture/DB/hardware; SQLite limitations |
| WP-21 Controlled write failure/restoration/retry and readback | M4 | A3 | 7.50 | WP-10, WP-14 | Controlled prewrite failure, state assertion, restore/retry once; W2 rollback and postcommit outage distinction | PR-10/12: safe fault seam, no valuable data or real outage |
| WP-22 Genuine defect reporting, triage, fixes/retests and regression | Continuous after first genuine finding | Shared | 6.50 | WP-08, WP-10 | Actual issues/severity/priority/triage, separately authorized fix and independent retest/regression | PR-01 candidate first; second major defect not assumed |
| WP-23 Two verified major-defect RCAs, fishbones and Pareto | M4–M5 | Shared | 7.67 | WP-22 | Two independent verified major-defect5Whys/fishbones, corrective/preventive actions and actual Pareto | No second major verified; do not inflate minor UI findings |
| WP-24 Session actual-effort logs and weekly GQM/control reports | Continuous from M0 | Shared | 5.33 | WP-02, WP-03 | Actual session hours, weekly GQM density/FR coverage/reopen/control reports and evidence | JR-04: no backfilled actuals/fake zeros |
| WP-25 Completion, residual risk and release/hold report | M5 | Shared | 5.33 | WP-17, WP-18, WP-19, WP-20, WP-21, WP-23, WP-24 | Tested/not-tested/deviations/open defects/residual risk per risk; EC actual-vs-target and release/hold | All10 gates evaluated; EC-01/02/04 headline three; mandatory gaps HOLD |
| WP-26 Final PDF/ZIP, source/evidence/link checks | M5 | Shared | 5.17 | WP-25 | PDF/ZIP with .git, public team link, evidence/scripts/config/versions/AI record; naming and integrity checks | Section/confirmed rolls/deadline not supplied; sanitize secrets not history evidence |
| WP-27 Individual viva reruns and live-rule/spec rehearsal | M5 final; practice earlier | Shared | 7.33 | WP-26 | Each member reruns own/peer test and live rule/spec change prediction→failure→fix/gate explanation | JR-04: genuine contribution/understanding across all components |

**v0.2 progress (24 Nov 2026, executed evidence only):**

- **WP-05 partly done:** `sqe-memory-v1` and `sqe-browser-v1` disposable profiles and the PR #1 reproduction tooling. The PostgreSQL profile and reset proof remain.
- **WP-10 partly done:** A2.1 API functional tests, 40/40 passed. API-INT-001/002 are not started.
- **WP-15 in progress:** 10/30 flows passed (B1).
- **WP-04:** RTM reconciled to v0.2.
- **Not started:** white-box, Sonar, generator, mutation, CI gates, usability, security, performance, recovery and management reporting.

Total E across packages **210.67 person-hours**, counted once. This includes completion/reporting/review, not just test coding. Use actual availability and package dependencies to set later calendar commitments. Individual phases may overlap; do not add parallel-lane durations as calendar time. Weekly reviews compare real effort and blockers with the original baseline, revise remaining forecasts with rationale and retain prior estimates.

## Student-owned stacked-branch and review workflow

These are **instructions for students only**, not actions performed by Codex. Current local work remains on `docs/test-planning`; pending PR review never authorizes bypassing protected main or changing history automatically.

1. Review this planning diff and preserve unrelated `.gitignore`/prompt changes. Verify the Phase1 branch actually contains reviewed requirements and determine whether its PR is merged. Local history alone does not prove remote PR status.
2. Students stage only the ten planning files and appended AI record, commit their genuine reviewed work, and push `docs/test-planning`. Do not attribute AI drafting as a student's unassisted work; retain AI disclosure and prompts.
3. If Phase1 is **unmerged**, manually open the Phase2 PR with base `docs/requirements-and-scope` and compare `docs/test-planning`. The review diff should show only Phase2 planning/AI additions. If Phase1 is **merged**, inspect actual ancestry and manually choose base `main`; if squash/rebase changed ancestry, the team must resolve/rebase/merge through its own agreed protected workflow before assuming a clean diff.
4. Keep the dependency/stack relationship explicit in the PR description. Peers review requirements/risk math/traceability and source oracles. Required checks and approvals must pass; no bypass or self-approved merge. After Phase1 merges, students retarget/update the Phase2 PR and re-inspect diff/checks before merging.
5. Later implementation branches/PRs can be stacked on the reviewed prerequisite branch while approvals are pending; each student controls their own checkout and records the base. Independent spec/CFG/browser design need not stop. Never mix unrelated source fixes into the planning PR; genuine later fixes get regression evidence and appropriate review.
6. Every student commits actual contributions and reviews peers. Students alone perform fetch/switch/stage/commit/push/rebase/retarget/merge operations, branch protection and Issue/PR actions. No automation account/assistant authorship, credential request or GitHub mutation is made by Phase2.

Manual stage/commit/push commands are provided to the user at completion; no mutating command has been executed. The currently untracked prompt.md has changed from Phase1 to Phase2: students must retain both original prompt records (e.g. prior chat/export and current file) before future replacement. This plan does not reconstruct or silently overwrite historical evidence.

## Completion and submission handoff

At M5, all area owners bring actual results for EC-01–10 and unresolved findings; shared review records tested/not-tested work, scope deviations, remaining risks per risk, genuine defects and release/hold rationale. Show actual vs target for EC-01/EC-02/EC-04 headline release criteria and retain all other blockers. No plan approval means a product release is ready. Missing major-defect RCA cases,15-survivor evidence or six accepted/automated UCs remain explicit mandatory gaps; escalate rather than fabricate.

Prepare one PDF and ZIP named `Project_<confirmed-roll1>_<confirmed-roll2>_<confirmed-roll3>_<section>.pdf` and `.zip` using actual roster/section, not guessed identifiers. ZIP must include .git history, source baseline/upstream reference, real runnable tests/scripts/data, versions/config/CI, genuine blocked/fix PR links and evidence; do not include credentials/development databases/node_modules/venv as unnecessary data. PDF includes scope, risks, management/traceability, area ownership, all activity findings (root cause/severity/risk/fix), evidence links, actual effort, AI-use record and final release/hold decision. Keep original raw evidence unaltered and record any redacted copies explicitly.

Viva rehearsal covers every component and the live business-rule/spec-change task: predict impacted tests/gates, rerun assertions, explain MCC/MC/DC/fixtures/recovery, and demonstrate actual effect. Each member must understand shared risk/management work as well as their area; no AI-generated claim substitutes for explanation or genuine contributions. Archive actual package/link checks and real reviewer acknowledgments only after they occur.
