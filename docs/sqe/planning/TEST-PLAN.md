# Operational test plan

Controlled document LF-SQE-TP, version0.1; drafted 22 November 2026 (Asia/Karachi); approval **PENDING**. Project: LeaveFlow MIS Testing, SE3002, three-member group; MIT licence. Upstream: https://github.com/cmdr-chara/LeaveFlow; team fork: https://github.com/eshalfatima2006/LeaveFlow. A1/A2/A3 allocations are proposals. Change control: shared team owns revisions; peer reviewer records version, rationale, requirement/risk impact, proposed thresholds, approval and effective commit. No human approval or final deadline is recorded. Source baseline `bada9a03ecec53ef6945827230e3594d825da87a`; current planning input `f9fafbf1ce89e63701753cafcb18a5cd1616e6ca`. *v0.2 (24 Nov 2026): reconciled with executed A2.0/A2.1/B1 work and the PROPOSED use-case catalog; approval still PENDING.*

## Scope, approach and test items

Test W1 employee submission and W2 manager decision of original request k, shared ownership and derived leave balance. Use [TEST-STRATEGY](TEST-STRATEGY.md) for all testing areas and [Phase 1 source boundary](../requirements/COVERAGE-BOUNDARY.md) for functions. All 12 FRs/six BRs feed the [RTM](REQUIREMENTS-TRACEABILITY-MATRIX.md); future tests are separate in `tests/team/` (v0.2: implemented — foundation, API and browser suites). Preserve upstream nine tests as separately reported smoke checks; they earn no student test marks.

Highest risks PR-01/PR-02 receive first fixtures, unit/API assertions, defect reproduction and blocking EC-01/EC-02. Select technique/depth from the [risk register](RISK-REGISTER.md), not from the simplest available tool. Requirements planning coverage does not establish executed coverage. Permission changes, state/balance fixes and schema repair are later separately reviewed work, not part of this documentation phase.

## Responsibilities and environment

[TEAM-OWNERSHIP](TEAM-OWNERSHIP.md) proposes A1 static/white-box/mutation/CI, A2 API/integration/generator, A3 browser/usability/security/performance/recovery. All members review requirements, triage, risk, metrics, evidence and final package, and own two approved browser use cases. Names/roll numbers/ownership have not been corroborated in existing records; do not infer them from commit author names. *v0.2 use-case allocation: Member 1 UC-01/UC-08, Member 2 UC-02/UC-07, Member 3 UC-04/UC-09 (PROPOSED; see TEAM-OWNERSHIP).*

| Environment item | Recorded state and provenance | Later verification / gap |
|---|---|---|
| Windows/WSL Ubuntu | Historical baseline report at commit81e677a; not a claimed current OS/hardware measurement | Record `uname -a`, `/etc/os-release`, WSL version, CPU/RAM, dedicated DB disk and runner limits before experiments; no invented builds |
| Python | 3.12.7 historical and current interpreter probe | `.venv/bin/python --version`; validate pinned-package support; upstream CI requests3.13 |
| Django / DRF | 6.0.7 /3.17.1 in current package metadata and pins | `.venv/bin/python -m pip show Django djangorestframework`; record exact environment and compatibility |
| Node.js /npm | 22.23.3 /10.9.9 historical environment.txt at7948f74 | v0.2: **verified** 22.23.3 / 10.9.9 in the B1 browser runs (`docs/sqe/evidence/browser/b1/run-1/environment.json`) and the PR #1 reproduction (`setup/local-baseline`); the earlier non-login PATH failure no longer blocks work |
| Database | SQLite local development recorded; settings.py:81–98 has optional PostgreSQL env switch | v0.2: disposable profiles in use — `sqe-memory-v1` (in-memory SQLite, A2.0/A2.1) and `sqe-browser-v1` (temporary-file SQLite, B1); the development database is never a target. PostgreSQL profile still required for row-lock and engine-dependent limits |
| Browser | v0.2: **verified** Playwright 1.49.1 with Chromium 131.0.6778.33 (headless shell), en-GB, Europe/Rome, 1280×720 default viewport (B1; PR #1 BL-UI-04 used 1440×900) | Upgrade only with lock-file review; record versions per run |
| Sonar/coverage/mutation/API/browser/a11y/security/k6 | Availability and versions NOT VERIFIED (v0.2: browser verified, see the Browser row; Django test runner verified in A2.0/A2.1; the others remain NOT VERIFIED) | Record version output or installed package metadata, configuration hash and commands; do not equate a tool named in prompt with configured infrastructure |
| Notifications | Optional Redis + Elixir worker +TS gateway | See [Isolated notification environment (UC-07)](#isolated-notification-environment-uc-07); nothing run yet |
| CI | Existing source inspected; remote protection/configuration not verified | Record runner/tool versions, actual required checks and tested SHA when students configure gates |
| Django Admin session (UC-08/UC-09, conditional on D-1) | Not built | Staff synthetic users in the disposable browser database; session login through `/admin/`; Italian admin messages (`LANGUAGE_CODE=it-it`) |

Future tool-version inventory should include `coverage --version`, `pytest --version`, mutation package metadata, Sonar server/scanner version, Playwright/Lighthouse/axe package versions, ZAP version, `pip-audit --version`, `k6 version`, Redis/PostgreSQL versions and relevant lock hashes. Commands are examples to run **after** tool setup, not results; installations are not performed here.

## Isolated notification environment (UC-07)

Status: **design only; not executed** (UC-07 is conditional on D-2). Hazards found on 24 Nov 2026:

- **Seeding:** the backend image always runs `migrate && seed_demo` (`backend/Dockerfile:9`). `seed_demo` overwrites demo users and balances and deletes all leave requests.
- **Persistent volumes:** `docker-compose.yml` declares named volumes `leaveflow_data` (PostgreSQL) and `leaveflow_redis`.
- **Ports:** fixed host ports 8000, 3000 and 5173.
- **Shared machine:** other, unrelated Compose projects run on the development machine and must never be touched.

Verified fact (render only, `docker compose -p sqe-uc07-designcheck config`): a unique project name prefixes the named volumes (`sqe-uc07-designcheck_leaveflow_data`, `sqe-uc07-designcheck_leaveflow_redis`), so the project name alone separates the data from any default `leaveflow` project.

Mandatory procedure before any UC-07 run (fail closed on any check):

1. Use a unique project name per run, e.g. `sqe-uc07-<UTC timestamp>`. Never use the default project name.
2. Before `up`, `docker compose -p <name> config` must show every volume prefixed with `<name>_`. `docker volume ls` and `docker ps -a --filter label=com.docker.compose.project=<name>` must return nothing for that project.
3. Use a test-only override file (to be written with UC-07) that:
   - replaces the backend command with `migrate` plus the server, so synthetic fixtures are loaded instead of `seed_demo`;
   - remaps every host port to unused ports and verifies they are free;
   - publishes no service on the default ports.
4. Synthetic users only. Credentials are passed through the environment and never logged.
5. Tear down with `docker compose -p <name> down -v` for **that project only**, and record the before/after resource listing as evidence. Never run `docker volume prune`, `docker system prune` or commands without `-p <name>`.

Owner: Member 2, with Member 3 support. If any check cannot be proved, UC-07 is not run (SU-06).

## Isolated deterministic data contract

Use synthetic E1/E2 employees, M1 same-team manager, M2 outsider manager, administrator and no-team role variants; these labels are fixture roles, not real identities. Explicit dates (e.g. 2026-12-07..10 and12-14..17) isolate weekday/balance scenarios; freeze relevant application clocks/timezone in tests and record it. Use fixed allowances/approved history, pending/approved/rejected states, with/without balance and team. Assert initial counts and derived totals before each case; capture actual generated primary keys rather than assume IDs.

Every test worker/run gets its own disposable DB name/path and namespace; no default `backend/db.sqlite3`, development PostgreSQL, real Redis feed or reused demo account is an acceptable test target. Planned reset tooling must fail closed unless target is explicitly identified as disposable. Setup/teardown operate only on their owned data/connection, with test failures not skipping cleanup and logs retaining enough sanitized state to debug. For repeated performance experiments start from identical fixture snapshot/version; verify reset twice before trusting results. Do not run normal `seed_demo`: source `backend/leave/management/commands/seed_demo.py:17–28` overwrites accounts/balances, deletes all requests and uses relative dates. A full safe deterministic reset is future work, not a completed command.

No external service credentials or real personnel data in fixtures/evidence. Redact token/Authorization/cookie/password values while retaining test identity labels and correlation IDs. Browser worker contexts and localStorage are isolated. Separate SQLite unit/core profile, PostgreSQL transaction profile and notification-enabled profile; label each result. Do not generalize measurements across them.

## Execution order and milestones

Detailed work packages, person-hours and dependencies are in [EFFORT-ESTIMATION](EFFORT-ESTIMATION.md) and [EXECUTION-ROADMAP](EXECUTION-ROADMAP.md). Milestones are relative, not invented dates:

1. **M0 planning review:** confirm scope/critical module/oracles/ownership/UC feasibility, budgets and risk ranking. Archive this Phase2 prompt and retain Phase1 prompt from original chat/copy.
2. **M1 reproducible foundation:** compatible tools, isolated fixture/reset proof, exact source/lock/environment capture; reproduce PR-01 candidate and verify PR-02 access decisions early. Source reviews/spec drafting can proceed while tools/PR reviews are pending.
3. **M2 functional foundation:** Sonar/CFG and team unit/API tests, generated data, MCC/MC/DC, decision/state/integration tests; persist real defects and baseline/fix evidence.
4. **M3 integrated automation:** approved UC Playwright flows, mutation, strict CI gates, actual blocked/fixed PR evidence; accessibility/security alongside stable browser work.
5. **M4 nonfunctional/recovery:** controlled load, fault/retry, before/after accessibility and confirmed defect RCA. Do not load-test an uncontrolled dataset.
6. **M5 completion:** consolidated metrics, Pareto, actual vs planned effort, every exit criterion evaluated, tested/not-tested/deviations/open defects/residual-risk review; PDF/ZIP and viva rehearsal.

Parallel work is permitted where dependencies allow: A1 Sonar/CFG and A2 spec/API while A3 designs accepted browser flows; weekly management spans all milestones. Pending PR approval does not stop independent local analysis. Students alone manage feature/stacked branches; no branch operation is performed by Codex.

## Entry, exit, suspension and resumption

Authoritative IDs/tools/evidence thresholds are in [ENTRY-EXIT-CRITERIA](ENTRY-EXIT-CRITERIA.md). Before a test area starts, satisfy EN-01–05 plus its strategy-row prerequisites. Targets are proposals; assignment-required coverage/counts cannot be lowered by team preference.

- Suspend the affected experiment when fixture/reset proof fails, a test target may be valuable/live, unsafe secret exposure occurs, oracle/scope conflict invalidates assertions, dependency failure prevents meaningful execution or highest-risk corruption makes load/browser results unreliable (SU-01–05). Preserve logs/failed state and mark blocked rather than pass; unaffected source analysis can continue.
- Resume only after the exact cause is resolved with a recorded verification, reset/health/oracle checks pass and affected cases rerun on the known SHA (RS-01–05). Time passing or rerunning blindly is not recovery evidence.
- Completion requires all EC-01–10 measured and satisfied or an explicit assignment-permitted, documented instructor-approved exception. Current future-test status is **NOT MEASURED**; release readiness is **HOLD — unevaluated**, not a finding that all tests failed.

## Deliverables, evidence and trace updates

Future planned evidence root: `docs/sqe/evidence/<area>/<run-id>/` (directories/artifacts not created by this phase). Run ID convention `YYYYMMDDThhmmssZ-<short-sha>-<profile>` uses actual execution time, not planned dates. Each run manifest: tested SHA/dirty diff, tool versions/config/spec/fixture hashes, DB/profile, command, duration, stdout/stderr, exit code, test case IDs, expected vs observed results and redaction record. Avoid absolute confidential paths in shared reports.

| Area | Required future evidence |
|---|---|
| Static/white-box | Full Sonar metrics and interpretation; manual CFG/complexity comparison; raw statement/branch reports, exclusions and MCC tables/MC/DC pairs |
| API/generator | Accurate OpenAPI/rule manifest; generated cases/spec changes; case manifest and genuine request/response/DB assertions; full decision/state coverage |
| Browser/accessibility | Six accepted UC specs with all flows (v0.2: PROPOSED catalog, 30 mandatory flows, 10 passed in B1); Playwright HTML/traces/screenshots; two task tests/error-correction/keyboard; Lighthouse+axe before/after with deduplicated findings |
| Mutation/CI | Tool/config, ≥2 custom operators, raw and adjusted scores, ≥15 survivor classifications/reruns; candidate-SHA job/gate logs; real blocked/fix PR links |
| Security/performance/recovery | Role matrix/≥4 decisions/≥2 controls, ZAP passive and package audit reports; four k6 steady-state runs and raw series; injected failure/restoration/retry persisted-state evidence |
| Management/completion | Risk changes, RTM execution links, genuine issues/triage, ≥2 independently verified major-defect RCAs (5Whys/fishbone), Pareto, weekly GQM, actual effort, release/hold report |

Never edit raw evidence to improve a result; preserve original restricted artifacts if redaction is required and publish explicitly labelled redacted copies. No future evidence path is a claim that a file exists. Real test IDs, paths and issue URLs replace planned status in RTM through reviewed updates; preserve old result history rather than overwrite a fail with a pass. Duplicate cases run in multiple tools do not increase requirements coverage.

## Defect escalation, reporting and residual risk

Follow [DEFECT-MANAGEMENT-PLAN](DEFECT-MANAGEMENT-PLAN.md). Any unauthorized access, corruption or destructive-target concern is escalated to all three members immediately within their active work session; suspend dependent tests, propose severity/priority and retain evidence. Students manually create/triage Issues; no Issue is created here. Triage routine findings at the next shared session; high-risk unresolved items block their ECs. Assign one owner and independent retester; no self-attested closure.

After each real work session record actual person-hours and artifact/test changes. At least weekly, issue [QUALITY-METRICS](QUALITY-METRICS-PLAN.md)'s report including requirements coverage, defect density and reopen rate, plus control actions for delay/risk. “NOT MEASURED” and N/A with reason are different from zero. Update risk likelihood only with justified evidence, not because time was spent. At completion each risk retains actual residual likelihood/impact and rationale; unknown/unverified remains explicit.

Release/hold review is shared: A1 brings CI/white-box/mutation, A2 API/generator/integration, A3 browser/nonfunctional/security, peers inspect raw evidence. Evaluate all ECs on the release candidate SHA; present **EC-01, EC-02 and EC-04** as the three headline release criteria (assignment p5 requires actual vs target for three), while retaining every other gate. Open major defects, missing evidence or unmet required counts yield hold and a specific action/owner; do not silently waive mandatory scope or fabricate a second major defect. Final package includes tested/not-tested work, deviations, open defects/residual risks and signed student decision.

## Contingencies and external decisions

- JR-02: current Node/npm probe failed; repair student WSL environment before browser/build work; source/spec/CFG tasks can continue. Use compatible pinned/locked versions and capture any reviewed toolchain changes. *v0.2: resolved for Node/npm/Playwright (versions verified in B1); Sonar, mutation tooling and team CI gates remain unverified.*
- JR-03: instructor must resolve six distinct UC goals, server denominator/MCC infeasible rows and unspecified “all API coverage criteria.” Do not silently lower counts; retain blocked trace rows. *v0.2: the API coverage criteria are defined by Lecture 20 (TCL0–TCL7 plus technique coverage); the team must choose the TCL target level (EC-05). The use-case catalog is PROPOSED; instructor decisions D-1/D-2 and the denominator/MCC questions remain open.*
- If PostgreSQL/Redis/Sonar/runners unavailable, continue isolated SQLite/source planning but mark engine/service-specific results blocked; arrange free/open-source local resources before final gates. No local result substitutes for a required PR check.
- If mutation runtime exceeds budget, optimize fixtures/test selection and runner scheduling, preserve full approved rule scope, and rerun; no skipped survivors relabelled killed. If fewer than15 real survivors, follow strategy's instructor escalation.
- If no second major defect is verified, broaden legitimate investigation of highest risks and seek instructor guidance; do not inflate UI severity. If deadline/availability becomes known, revise estimates/milestones transparently, not invent calendar commitments now.
- Phase1 historical baseline evidence remains on other local history; reconcile references manually. Existing Phase1 “current branch/HEAD” statements are **historical 21November observations**, not current state. Root `prompt.md` now contains Phase2; original Phase1 prompt retention needs student action. No Phase1 file is rewritten to conceal these changes. *v0.2: the corrected baseline report and newly reproduced evidence are on `setup/local-baseline` (PR #1, pushed); after integration they are `docs/sqe/BASELINE-VERIFICATION.md` and `docs/sqe/evidence/baseline/`.*
