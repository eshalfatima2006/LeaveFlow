# AI-use record — Phase 1 draft

- **Date:** 21 November 2026, Asia/Karachi.
- **Tool:** Codex. No human author, reviewer, member identity or student sign-off is implied.
- **Purpose:** Source-code analysis and draft Phase 1 requirements, scope, rules, test basis, workflow trace and proposed coverage boundary for SE3002.
- **Prompt:** Existing repository-root `prompt.md`, supplied by the user through “analyze the prompt.md file and do as it says.” Retain that file for disclosure; it was already untracked and was not edited or staged by this work. It authorizes documentation/analysis only and reserves all Git/GitHub mutations for the students.
- **Assistance output:** Seven local Markdown files listed below. No application fixes, student test suite, schema repair, CI change or later testing implementation.

## Generated files

| File | Purpose |
|---|---|
| `docs/sqe/requirements/SCOPE.md` | Identity, selected module/actors/shared data, boundaries, assignment mapping, setup/reset basis and unresolved decisions |
| `docs/sqe/requirements/FUNCTIONAL-REQUIREMENTS.md` | 12 independently testable baseline requirements, six per workflow; desired approval safeguard explicitly separated |
| `docs/sqe/requirements/BUSINESS-RULES.md` | Six rules; EP/BVA input, compound-decision/feasibility and state inventories |
| `docs/sqe/requirements/TEST-BASIS.md` | Pinned evidence for every FR/BR, acceptance oracles, contradictions, known risks and proposed failing test |
| `docs/sqe/requirements/WORKFLOW-TRACE.md` | Browser→HTTP→DRF→validation→ORM→response trace; errors, shared identity, notification boundary and use-case feasibility |
| `docs/sqe/requirements/COVERAGE-BOUNDARY.md` | 17 included callable bodies (including nested callback), proposed exclusions, MCC/MC/DC feasibility and mutation foundations |
| `docs/sqe/AI-USE-RECORD.md` | Assistance disclosure, source/command/verification record and required student review |

## Source material inspected

- Local `SQE_Final_Project Fall 2026.pdf`, all seven pages (text extracted with pypdf). No lecture PDF found in workspace; none claimed read.
- Root `AGENTS.md`, `prompt.md`, `README.md`, `README.it.md`, `LICENSE`, `.gitignore` diff, `requirements.txt`, `.github/workflows/ci.yml` (read-only context).
- `backend/leave/models.py`, `serializers.py`, `views.py`, `urls.py`, `events.py`, `tests.py`, `admin.py`, `migrations/0001_initial.py`, `management/commands/seed_demo.py`; `backend/config/urls.py`, `settings.py`.
- `frontend/src/App.vue`, `RequestRow.vue`, `api.ts`, `types.ts`, `main.ts`, `BalanceGauge.vue`, `i18n.ts` (relevant localization functions/labels), `notifications.ts`, `NotificationCenter.vue`; `frontend/package.json`, `vite.config.ts`.
- `notifications/src/app.ts`, `index.ts`; `notification_worker/lib/leave_flow_worker/domain.ex` for dependency boundary and request-ID propagation. No claim of a full downstream service audit.
- Historical `docs/sqe/BASELINE-VERIFICATION.md` read with `git show` at `81e677a` and `7948f74`, plus environment/upstream-test/frontend-build logs from `7948f74` and later docs tree. These files are absent from current HEAD; they were **not restored**. Their logged results and screenshot narrative remain historical evidence.
- Installed DRF AutoSchema implementation and actual model-derived serializer field metadata, without production database queries/writes.

## Commands executed and effects

The following groups describe the commands actually used; repeated reads/checks are grouped. Shell loops, small inline Python scripts and final Markdown validation are analysis helpers, not newly created application test suites.

| Commands / operations | Purpose and effect |
|---|---|
| `pwd`, `ls -la`, `rg --files`, `rg -n`, `find`, `cat`, `nl -ba`, `sed`, `tail`, `command -v` | Locate/read prompt, instructions, source, local PDF and docs; search baseline/report/schema paths; no project mutation |
| `git status --short`, `git branch --show-current`, `git rev-parse --show-toplevel`, `git rev-parse HEAD`, `git cat-file -t <baseline>`, `git merge-base --is-ancestor <baseline> HEAD` | Confirm required branch/current root/baseline existence/ancestry |
| `git remote -v`, `git log --all --oneline -6`, `git show`, `git ls-tree -r --name-only` | Read remotes/history/historical evidence; no network Git operations |
| `git diff`, `git diff --stat`, `git diff --cached --stat`, `git diff <baseline> -- <application paths>`, `git diff --check` | Inspect existing user work and verify source/diff preservation |
| `.venv/bin/python --version`; inline `importlib.util.find_spec` | Inspect interpreter and available PDF/Django modules. A bare `python` probe was unavailable in the non-login shell; existing `.venv/bin/python` used thereafter |
| `.venv/bin/python -m pip install --target /tmp/leaveflow-phase1-pdf pypdf --disable-pip-version-check` | First download attempt failed due sandbox DNS; no dependency installed into the project |
| Same install with `--no-cache-dir`, approved network escalation | Installed pypdf 7.1.1 **only into /tmp** to read the local assignment; no project/production dependency or lock changes |
| `PYTHONPATH=/tmp/leaveflow-phase1-pdf .venv/bin/python` with PdfReader | Extract/read all seven pages; no repository output artifact |
| Inline Python with `PYTHONDONTWRITEBYTECODE=1`, backend on sys.path, `DJANGO_SETTINGS_MODULE=config.settings`, django.setup | Print actual LeaveRequestSerializer field metadata and inspect AutoSchema methods/request and response schemas; no write operations |
| Isolated Django check/test script below | Zero system-check issues; nine upstream tests passed in 2.467s, using in-memory DB and disabled Redis. Not team-created tests/coverage |
| `apply_patch` | Create only the seven authorized Markdown files and correct draft inconsistencies |
| Final inline Python validator | Count/link FRs/BRs, compare local referenced source to pinned Git bytes, validate source ranges/local doc links, match coverage symbols to AST and check Git changes; no application/data mutation |

Exact framework smoke invocation from repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
import os, sys
sys.path.insert(0, 'backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
from django.conf import settings
settings.DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
settings.REDIS_URL = ''
import django
django.setup()
from django.core.management import call_command
call_command('check')
call_command('test', 'leave', verbosity=1, interactive=False)
PY
```

Only disposable test schema/data were created in memory. No current database reset, migration command, seeding, volume operation, production record modification or external event publishing was performed. No Git/GitHub mutation, credential request, commit attribution or messages to collaborators occurred.

## Verification and limits

- Confirmed current branch `docs/requirements-and-scope`, HEAD/pinned baseline match, baseline exists and is ancestor, origin/upstream match prompt. Initial user changes were `.gitignore` and untracked `prompt.md`; preserved.
- Read all required backend sources and actual frontend paths; no fictional router/pages, cancellation/reopen/rejection-reason fields, annual filtering, balance reservation or approval-time validation added to requirements.
- Actual Django runtime 6.0.7 / DRF 3.17.1 / Python 3.12.7 inspected; upstream suite passed as above. No new frontend build/browser test was run; prior build logs were read only.
- Direct schema introspection confirmed empty schemas for POST requests/decision/login and default201 mismatch for decision/login. This was not a complete generated OpenAPI artifact or a live endpoint test.
- Final documentation validator passed: seven Markdown files; 12 unique FRs (W1=6, W2=6), six unique BRs; every FR has the required fields; every FR/BR has a test-basis row and all ID references resolve. Verified 22 pinned line-range links and 118 qualified source ranges; the 22 referenced source files are byte-identical to pinned Git blobs; all relative Markdown links resolve. AST inventory matched all 20 callable bodies in models/serializers/views/events (17 included, three proposed excluded). Required branch/HEAD unchanged; tracked diff remains only the pre-existing `.gitignore` edit; staging empty; untracked set exactly the preserved `prompt.md` plus seven authorized documents. Git diff and Markdown whitespace/newline checks passed. These structural checks complement the manual source analysis; they do not prove every prose interpretation.
- No measured team coverage/MCC/MC/DC/mutation result or reproduced concurrency/approval defect is claimed.
- Approval-time negative balance is a static source finding with a proposed failing test; desired error code and missing-balance/year/type/zero-day policies remain unresolved.
- Six accepted use cases, full browser automation, deterministic isolated reset, accurate OpenAPI and coverage scope approval remain outstanding for later work.

## Student review required

The assignment's page 7 permits AI only with checked/disclosed output and retained prompts. **The students have not yet reviewed or signed off this draft.** Each member must inspect source references, check every requirement/oracle, correct anything unsupported and be able to explain it in the viva. Keep an amendment/review record of what the team actually checked or changed; do not claim this tool's checks as human verification.

Confirm section registration, area ownership, coverage interpretation and MCC infeasible-combination policy, use-case feasibility, approval insufficiency response contract and deterministic reset design. Reconcile historical baseline report/screenshot paths on the team's own branch. Retain original prompt, AI-use record and later genuine results; do not submit historical/upstream metrics as independent student achievement.


# Phase 2 — test planning, risk and traceability assistance

- **Date/tool:** 22 November 2026 (Asia/Karachi), Codex. This section is AI-generated draft disclosure; no named student author or human approval is implied.
- **Purpose:** Implement the revised prompt's Phase2 documentation/analysis: strategy/operational plan, proposed ownership, PERT estimates, risk matrix, entry/exit controls, RTM, defect/RCA procedure, GQM and execution roadmap.
- **Prompt:** Current untracked repository-root `prompt.md`, headed “PHASE 2 — COMPLETE TEST PLANNING, RISK MANAGEMENT, ESTIMATION & TRACEABILITY”; SHA-256 `0902b88feb2d7dc4259bc3e8538c67ecbc34815e28a7c5a95f73404eb5c33de4`. User asked “analyze the prompt.md file and do as it says.” It was read and preserved, not staged/committed. Root prompt now contains Phase2, so the earlier Phase1 prompt reference is historical; students must retain the original Phase1 prompt from their prior chat/export/copy. No archived Phase1 prompt file was found or fabricated.
- **Input/source state:** Required branch `docs/test-planning`; initial/current input HEAD `f9fafbf1ce89e63701753cafcb18a5cd1616e6ca`; upstream source baseline `bada9a03ecec53ef6945827230e3594d825da87a`. Phase1 six requirement documents and disclosure were present and read. Application/toolchain source had no differences from the upstream baseline; initial user work `.gitignore` edit and untracked prompt preserved. No staging, commits, branch changes, remote/GitHub operations or identity/author changes.

## Phase 2 output artifacts

All ten files under `docs/sqe/planning/` were created as proposals: [TEST-STRATEGY](planning/TEST-STRATEGY.md), [TEST-PLAN](planning/TEST-PLAN.md), [TEAM-OWNERSHIP](planning/TEAM-OWNERSHIP.md), [EFFORT-ESTIMATION](planning/EFFORT-ESTIMATION.md), [RISK-REGISTER](planning/RISK-REGISTER.md), [ENTRY-EXIT-CRITERIA](planning/ENTRY-EXIT-CRITERIA.md), [REQUIREMENTS-TRACEABILITY-MATRIX](planning/REQUIREMENTS-TRACEABILITY-MATRIX.md), [DEFECT-MANAGEMENT-PLAN](planning/DEFECT-MANAGEMENT-PLAN.md), [QUALITY-METRICS-PLAN](planning/QUALITY-METRICS-PLAN.md), [EXECUTION-ROADMAP](planning/EXECUTION-ROADMAP.md). This existing AI record was appended only; Phase1 text was preserved. No new test implementation, production logic, schema repair, dependencies, CI file or raw project-evidence report was created.

## Phase 2 sources and commands actually inspected/executed

- Read all seven pages of local `SQE_Final_Project Fall 2026.pdf` with the **already present** temporary pypdf reader from Phase1. No dependency install in Phase2; no lecture PDF found in workspace and none claimed read. Assignment p2–7 mandates later tests/metrics/CI/submission/AI integrity; it supplies no actual deadline, full roster, installed future-tool versions or detailed separate API checklist.
- Read current `prompt.md`, `AGENTS.md`, all six Phase1 requirements documents and this original Phase1 AI-use record. Read historical baseline report with `git show 81e677a:docs/sqe/BASELINE-VERIFICATION.md` and environment log at `7948f74`; did not restore/merge those files. Current branch/history statements inside Phase1 documents remain historical observations.
- Read `backend/leave/models.py`, `serializers.py`, `views.py`, `events.py`, `urls.py`, `tests.py`, `migrations/0001_initial.py`; relevant `backend/config/settings.py`; relevant `frontend/src/App.vue`, `api.ts`, `RequestRow.vue`, `types.ts`; `requirements.txt`, `frontend/package.json`, README/README.it sections and existing `.github/workflows/ci.yml`/`auto-release.yml`. Existing Phase1 call graphs/rule/source references were used; no new source path/field/rule was invented.
- Commands: `pwd`, `rg --files`, `rg -n`, `find`, `cat`, `sed`, `nl -ba`, `ls`; read-only `git status`, `git branch --show-current`, `git rev-parse`, `git remote -v`, `git log --all --oneline -10`, `git diff`/`--cached`/`--stat`/`--name-only`/`--check`, `git show` and read-only file listings. Source/member/PDF searches found no corroborating complete named roster or lectures. No network browsing/Git fetch, Issue/PR creation, scan or message to others.
- Read-only Python probes (`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python`) confirmed Python3.12.7, Django6.0.7 and DRF3.17.1 package metadata. The non-login-shell `node --version` probe found no node executable; `npm --version` failed with WSL1/install-directory error. Those are current command observations, **not proof that the actual OS is WSL1**. Node22.23.3/npm10.9.9/Windows-WSL-Ubuntu remain historical report values, not current confirmation. No hardware/browser/future-tool versions were invented.
- Took a SHA-256 snapshot of125 tracked files plus initial prompt/AI text/HEAD/status into `/tmp/leaveflow-phase2-before.json` before edits. Temporary Python documentation helpers in `/tmp` calculated estimates/risk ranks and generated Markdown tables. These helpers are not application tests or project deliverables. Mutations were limited to the ten planning documents and this appended record.
- Used `apply_patch` and temporary standard-library Python scripts to create/revise authorized Markdown. Final documentation validator checks existing IDs,75 unique planned objective definitions, forward/backward mappings, risk scores/ranks/matrix, PERT/SD/totals/dependency graph, criteria/top-risk consistency, links/source ranges, Markdown structure and repository preservation. Final actual results are recorded below after execution, rather than asserted in advance.

## Phase 2 interpretation and evidence limits

Planned inventory:12 preserved FRs, six BRs,12 product/four project risks,10 release-blocking exit criteria,27 proposed work packages with total expected210.67 person-hours. All actual effort, execution/coverage/mutation/Sonar/security/accessibility/performance/CI metrics are **NOT MEASURED**.75 planned objective definitions (including30 conditional browser flow slots) are not implemented tests, execution evidence or marks. All scores, allocations and nonmandatory numeric budgets are explicit proposals. No application tests were run in Phase2; Phase1's nine-test run remains historical, not rerun evidence. No migrations, seed, reset, database write, k6, ZAP/audit scan or dependency-failure experiment was executed.

PR-01 missing approval validation is statically grounded, not independently reproduced here; PR-02 authorization regression is a risk despite implemented guards, not an allegation of a breach. Concurrency/dependency vulnerabilities and recovery failures remain hypotheses/reported concerns until measured. Missing-balance/zero-day/year policy, denominator/critical-module/MCC interpretation, six actor-goal UCs and absent detailed API checklist require real decisions. The second major RCA defect is deliberately UNIDENTIFIED; no issue/PR number, survivor analysis or human test result was fabricated. Existing auto-release source was inspected as a future full-gate integration dependency, not changed or triggered.

## Phase 2 human review still required

**No human review/approval or confirmed team allocation was evidenced.** Students must check every output, resolve high-impact policy/scope/UC questions, confirm roster/section/availability/ownership, approve estimates and provisional thresholds before experiments, preserve both prompts, and record actual changes/approval only when they occur. Review source-linked oracles and every denominator/formula, implement genuine separate team tests later, retain real issue/CI/results and be able to explain all components in viva. A commit containing an AI draft does not by itself establish human validation. All Git/GitHub work remains student-owned.

## Phase 2 final validation results

- Standard-library documentation validator passed for all ten required planning files:12 original FRs/six BRs retained, exact FR→BR associations preserved, every requirement/rule planned,75 unique backward-catalog objective definitions (including30 conditional browser flows) and consistent forward references. These counts are planning metadata, not executed tests.
- Verified12 product/four project risk entries,1–5 scales, all scores/ranks/tie ordering and every5×5 matrix coordinate; PR-01/PR-02 match blocking EC-01/EC-02. Incorrect generated test constraints were explicitly classified under JR-01 project/testware assurance, distinct from PR-07 possible product input-acceptance failures. All ten exit criteria remain NOT MEASURED.
- Recomputed all27 O/M/P/E/SD entries and unrounded total210.67h (O116/M199/P352), checked8.38h illustrative independent aggregate SD, unmeasured actual/variance fields, acyclic dependency graph and roadmap estimate/dependency consistency. No calendar deadline or actual effort inferred.
- Checked ten GQM chains, required weekly metrics, proposed-case/FR/BR/risk/work-package/criterion references, explicit unidentified second major RCA case,58 relative Markdown links,30 qualified source ranges, new table column consistency and Markdown whitespace/newlines. Source analysis/peer-oracle review is still needed; structural checks do not prove every prose claim.
- Compared the125-file initial tracked SHA-256 snapshot: every initial file preserved byte-for-byte except the authorized AI-record append; original Phase1 AI text remains an exact prefix; prompt.md and existing .gitignore edit unchanged. Application/toolchain/dependency/CI paths still have no diff from original upstream baseline. Branch remains docs/test-planning at original input HEAD, staging empty; new untracked set is exactly ten planning documents plus the pre-existing prompt. Git diff --check passed.
- Validation helpers and snapshot stayed in /tmp, outside project deliverables. An initial validator regex mistakenly matched EC inside SEC identifiers; the helper was corrected with word boundaries and final checks passed. No application defect/result was inferred from that helper correction. No runtime application tests, scans, migrations/seeds/resets, Git/GitHub mutations or human approvals occurred in Phase2.


# A2.0 — implemented shared automated test foundation

- **Date/tool:** 22 November 2026 (Asia/Karachi), Codex. AI-assisted implementation and verification; no claim of human authorship, member review or instructor approval.
- **Prompt and authorization:** Corrected root `prompt.md` (SHA-256 `6d1c9f041a9c7a4eff7941386dcc9d6584f9af4c61adb2265ecad9a3f088171a`) requires existing `test/isolated-fixtures-and-baseline`; user explicitly confirmed proceeding with A2.0 while forbidding production logic changes and every Git/GitHub mutation. Earlier stopped attempt made no edits because its expected branch differed. Current prompt replaces earlier Phase1/2 root prompt content; students must retain prior prompt/chat records rather than infer old text remains at the same path.
- **Source state:** Tested HEAD `0a9a3f00e30859adca969a2673fa3e7698357d34`, pinned original baseline `bada9a03ecec53ef6945827230e3594d825da87a`; branch matched before edits. Working tree was dirty with pre-existing .gitignore change and untracked prompt, then uncommitted new test/evidence files. Raw manifests identify exact SHA, Git status/diff hash and all Python source hashes; no pretend committed test revision.
- **Sources read:** Updated prompt/AGENTS; all seven local assignment PDF pages (existing temporary pypdf reader, no new install); Phase1 scope/FRs/BRs/test basis/workflow/coverage boundary and Phase2 strategy/plan/risk/entry-exit/RTM/roadmap and other relevant planning sections. Actual backend models/serializers/views/events/urls/tests/seed/settings/config urls/migration, requirements and .gitignore; installed Django DiscoverRunner and SQLite test-creation implementation for safety/discovery compatibility. No lecture PDF located, none claimed read.

## A2.0 files and implementation

Created `scripts/sqe/run_tests.py`; `tests/__init__.py`; `tests/team/__init__.py`, `settings.py`, `safety.py`, `runner.py`; `tests/team/fixtures/__init__.py`, `leave_data.py`; `tests/team/foundation/__init__.py`, `test_foundation.py`; package markers `tests/team/api/__init__.py`, `integration/__init__.py`, `generated/__init__.py`; [SHARED-TEST-FOUNDATION.md](testing/SHARED-TEST-FOUNDATION.md); actual logs/result manifests, deliberately injected-failure wrapper and final preservation verification under `docs/sqe/evidence/foundation/a20/`. Only this disclosure is appended among pre-existing tracked files; prior Phase1/2 documentation/evidence and all application/dependency/CI files preserved. Exact created-file inventory is in [verification.json](evidence/foundation/a20/verification.json).

Selected installed Django unittest runner/DRF client, not a new framework/dependency. Core profile forces SQLite :memory: /Django memory URI and Redis disabled before setup; guard refuses files/unknown targets/extra aliases/mirrors/external engines, fixtures require active memory target. No production seed/reset helper exists. Django TestCase transactions/savepoints provide teardown; repeatability uses two independent processes and compares logical state, not random IDs/password hashes/tokens/timestamps. Fixture defaults use explicit dates and valid ownership/decision actors; invalid overlap requires explicit opt-in. Fixture-only allowance safeguards do not alter or claim to repair W2 balance validation.

## A2.0 commands actually executed and evidence

Read-only `git branch --show-current`, `git rev-parse`, `git status --short --untracked-files=all`, `git log`, `git diff`/`--check` and file/source searches/reads (`rg`, `find`, `cat`, `ls`, inline Python inspection). Snapshot135 initial tracked files and development SQLite/sidecar fingerprints in `/tmp/leaveflow-a20-before.json`. `apply_patch` and stdlib Python wrote authorized infrastructure/report/disclosure/evidence only. No dependency install, external scan, Git mutation, GitHub operation or message to others.

Actual runtime commands from repository root:

```bash
.venv/bin/python scripts/sqe/run_tests.py check --evidence-dir docs/sqe/evidence/foundation/a20/check
.venv/bin/python scripts/sqe/run_tests.py team --evidence-dir docs/sqe/evidence/foundation/a20/team
.venv/bin/python scripts/sqe/run_tests.py upstream --evidence-dir docs/sqe/evidence/foundation/a20/upstream
.venv/bin/python scripts/sqe/run_tests.py repeatability --evidence-dir docs/sqe/evidence/foundation/a20/repeatability
POSTGRES_DB=sqe_never_connect POSTGRES_HOST=127.0.0.1 POSTGRES_PORT=1 REDIS_URL=redis://127.0.0.1:1/0 DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python scripts/sqe/run_tests.py team tests.team.foundation.test_foundation.FoundationTests.test_pending_record_and_approved_only_consumption --evidence-dir docs/sqe/evidence/foundation/a20/environment-override
.venv/bin/python docs/sqe/evidence/foundation/a20/failure_probe.py docs/sqe/evidence/foundation/a20/failure-propagation
```

System check: zero reported issues, exit0. Team:12 passed,0 failures/errors/skips/expected failures, exit0. Upstream:9 passed,0 failures/errors/skips, exit0, separately reported with no student test credit. Repeatability children:12 passed each,0 failures/errors/skips, separate processes/memory DBs, parent exit0 and exact canonical reference comparison passed. Environment-override single selected case passed, exit0, active SQLite memory/Redis disabled despite sentinel external settings. Deliberate child-process method patch:1 executed/1 intentional failure,0 errors/skips, **actual process exit1**, stdout/stderr markers and traceback retained. This last run verifies failure propagation; it is not a product failure or a permanently failing discovered test. No failure was suppressed or edited into a pass.

Measured Python3.12.7, Django6.0.7, DRF3.17.1, SQLite3.46.1, django-cors-headers4.9.0, redis6.4.0 and psycopg3.3.4. Genuine start/finish UTC timestamps are retained per result.json; UTC21November21:56+ corresponds to22November in Asia/Karachi. No hardware/browser/performance/coverage/mutation/CI result invented. Stdout and stderr saved independently without raw token/credential values. Each evidence directory was new; prior output was never overwritten.

Development SQLite remained180224 bytes, SHA-256 `70155559be6dc448fa8eb05e804ff7a60532afbac881bac21bc42de47cbcd33d`, sidecars absent. No development DB opened for SQL or changed, no real PostgreSQL/Redis selected. Normal migrations/seed/flush/reset not executed; Django migrated **only its verified in-memory test schema**. Source/dependency/lockfile preservation and staged-state checks are independently recorded in final verification.json.

## A2.0 limits and required student review

12 unique smoke/infrastructure tests with FND/FR/BR docstrings are not full FR/BR/API/white-box coverage; repeated12-case runs are not additional independently authored tests. The overapproval fixture prepares two pending4-day requests at allowance5 without calling W2 or asserting negative allowance is correct. Suspected approval defect remains unchanged; genuine failing-before integration regression belongs to A2.1, accurate OpenAPI/generator/generated EP/BVA and regeneration to proposed A2.2. External DB concurrency, browser server reset, full CI/mutation/security/accessibility/performance/recovery and unresolved instructor policies remain future work. Normal development reset is deliberately unsupported.

Students must review source safety/fixtures/assertions/evidence, retain prompts, agree shared fixture changes/IDs and implement their own real contributions/reviews/commits. No student review, member allocation, issue/PR creation or human sign-off occurred during this assistance. All Git/GitHub operations remain student-owned. See the foundation report for exact independent verification commands and contributor contract.


# A2.0 — audit and independent re-verification

- **Date/tool:** 23 November 2026 (Asia/Karachi), Claude Code (Claude Sonnet 5.5). AI-assisted audit and re-execution at the student's instruction; no human review or approval is claimed.
- **Scope:** Read the existing uncommitted A2.0 files (`scripts/sqe/run_tests.py`, `tests/`, foundation doc, evidence, prior AI record) against `prompt.md` A2.0 requirements. No test, fixture, runner, settings, dependency or production file was modified. The `.gitignore` was not changed.
- **Commands run:** read-only git inspection (using a per-command `-c safe.directory=*`, no config change), then `check`, `upstream`, `team`, `repeatability`, the sentinel-environment single test and `failure_probe.py` via `.venv/bin/python` inside WSL, writing to the new directory `docs/sqe/evidence/foundation/a20-reverify-20261123/`. Results: check 0; upstream 9/9; team 12/12; repeatability 12/12 twice with equal reference hashes; environment-override 1/1; deliberate probe exit 1 as intended. Development SQLite hash unchanged.
- **Edits:** appended a re-verification section to `docs/sqe/testing/SHARED-TEST-FOUNDATION.md` and this entry. No Git/GitHub mutation occurred.


# A2.1 — core API functional testing

- **Date/tool:** 23 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted implementation and execution; no human review, approval or authorship is claimed.
- **Sources read:** FUNCTIONAL-REQUIREMENTS, BUSINESS-RULES, TEST-BASIS (GAP list, proposed regression), RTM API families, SHARED-TEST-FOUNDATION; `backend/leave/models.py`, `serializers.py`, `views.py`, `urls.py`, `events.py`, `config/settings.py` (REST_FRAMEWORK, language), existing foundation code.
- **Created:** `tests/team/api/support.py`, `test_authentication.py`, `test_w1_submission.py`, `test_w2_decisions.py`; `docs/sqe/testing/API-FUNCTIONAL-TESTING.md`, `docs/sqe/testing/A21-EXECUTION-MAPPING.md`; `docs/sqe/evidence/api/a21/` (sensitivity_probe.py, first run, `final/`).
- **Modified:** `tests/team/safety.py` (removed trailing blank line); `tests/team/runner.py` (record failed subtests with owning method); `scripts/sqe/run_tests.py` (`passed` counts distinct non-passing methods; added `non_passing_test_methods`). This entry appended. No production, dependency, `.gitignore` or `prompt.md` change.
- **Commands:** read-only git (`branch`, `log`, `status`, `show --stat`, `diff`); discovery probe on a scratch copy in `/tmp` without `tests/__init__.py`; `run_tests.py` check/upstream/team/repeatability with `--evidence-dir` into new directories; A2.0 `failure_probe.py`; four `sensitivity_probe.py` faults. All via `.venv/bin/python` inside WSL.
- **Results (final run):** check 0; upstream 9/9; foundation 12/12; API 40/40; combined team 52/52; repeatability 52/52 twice with identical per-case outcomes; deliberate failure probe exit 1; each of four injected faults caused exit 1 in the matching test group. Development SQLite hash unchanged before/after.
- **Corrections made during the work (honestly recorded):** an authored 401 case for a lowercase `token` keyword was removed before execution after reading DRF's case-insensitive keyword match; a duplicate case ID (API-W2-002.01) was renumbered to API-W2-002.06 after the first run; the runner `passed` count fix was made after the first run exposed it under the sensitivity probes. The first run is preserved and marked superseded.
- **Uncertainties / student review:** characterization tests pin unresolved policies (GAP-01, GAP-07, zero-day/past dates, manager self-submission) — do not read them as approved oracles. Review the shared runner change with teammates per the foundation contract. `tests/__init__.py` must be committed or the team suite cannot be discovered from a clean checkout. The approval-time balance defect was neither fixed nor exercised. All Git/GitHub actions remain student-owned.


# Use-case analysis and B1 — browser harness, UC-01/UC-02 automation

- **Date/tool:** 23 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted analysis, implementation and execution; no human review, approval, instructor decision or authorship is claimed.
- **Analysis (no files changed):** three use-case feasibility/strategy reviews and a Lecture 16 alignment review. The lecture PDF was found as `SQE_Lecture16_UseCase_ExperienceBased.pdf` (Downloads) and read in full via `pypdf` in a scratch virtual environment. The team then chose Strategy A; Django Admin and notification-service inclusion remain pending instructor decisions.
- **Created:** `tests/team/browser_safety.py`, `tests/team/browser_settings.py` (profile `sqe-browser-v1`), `scripts/sqe/browser_harness.py`, `tests/team/browser/` (package.json + lock pinning `@playwright/test` 1.49.1, `playwright.config.ts`, `support/`, `specs/uc01-submit-leave.spec.ts`, `specs/uc02-decide-leave.spec.ts`, `flows.json`, `tools/flow-coverage.mjs`), `docs/sqe/testing/BROWSER-USE-CASE-TESTING.md`, `docs/sqe/evidence/browser/b1/` (run-1, run-2, regression-team). This entry appended. No production, frontend, backend, `.gitignore`, `prompt.md` or A2.0/A2.1 file changed.
- **Commands:** `npm install` (tests/team/browser only) and `npx playwright install chromium` (user cache); guard negative/positive checks; exploratory Playwright runs into temporary run directories (two failed on a form-field selector, one ARIA-snapshot probe whose spec file was deleted after use); two evidence runs; `flow-coverage.mjs`; `run_tests.py team` regression; evidence scan for credential strings; removal of harness-created `/tmp/leaveflow-sqe-browser-*` directories (marker checked). Development database checked by `stat` metadata only.
- **Results:** run-1 and run-2: 10/10 mandatory UC-01/UC-02 flows passed, OBJ-UC02-01 skipped as blocked; mandatory coverage 10/30; A2 team suite 52/52; development database metadata unchanged in every run.
- **Corrections made during the work:** `getByLabel` selectors replaced by role locators after an ARIA snapshot showed the real accessible names; the UC-09 second exception refined to an in-journey failure (deleted employee record) with the former-manager 404 kept as a supplementary check; an earlier claim that allowance 32768 is rejected was corrected (true on PostgreSQL only; SQLite accepts up to 2^63−1).
- **Student review required:** decide whether missing decision feedback (OBS-UC02-01) becomes part of the expected result; review the harness safety controls and new dependency; confirm the scope questions with the instructor before UC-07/UC-08/UC-09; all Git/GitHub actions remain student-owned.


# Cross-branch audit and v0.2 reconciliation (24 November 2026)

- **Tool:** Claude Code (Claude Opus 5.5), at the student's instruction. AI-assisted audit, documentation reconciliation and test execution. No instructor decision, team approval, human review or authorship is claimed.
- **Audit (read-only, 23 Nov):** cross-branch consistency and change-impact audit; report kept outside the repository. Runtime checks ran on a `git archive` export of `433a9e6` (team 52/52, upstream 9/9).
- **Branches:** local branch `docs/uc-reconciliation` created from `433a9e6` for the documentation remediation; local branch `ci/fork-release-guard` created from `bada9a0` for the auto-release guard. No merge, rebase, reset, push, pull or fetch.
- **Created:**
  - `docs/sqe/requirements/USE-CASE-SPECIFICATIONS.md`;
  - `docs/sqe/REPOSITORY-STRUCTURE.md`;
  - `scripts/sqe/check_docs.py`;
  - evidence `docs/sqe/evidence/browser/b1-provenance-2026-11-24/` and `docs/sqe/evidence/regression/r5-2026-11-24/`.
- **Modified (v0.2 notes beside preserved v0.1 text):**
  - SCOPE, FUNCTIONAL-REQUIREMENTS (PROPOSED FR-ADM-01/02, FR-NOTIF-01), BUSINESS-RULES (clarifications only), TEST-BASIS (GAP-04/09/10 updated; GAP-11–15 added), WORKFLOW-TRACE, COVERAGE-BOUNDARY;
  - RTM, TEAM-OWNERSHIP, TEST-STRATEGY, TEST-PLAN, ENTRY-EXIT-CRITERIA (SU-06/RS-06), RISK-REGISTER (JR-05), EXECUTION-ROADMAP, EFFORT-ESTIMATION;
  - BROWSER-USE-CASE-TESTING;
  - `tests/team/browser/flows.json` (owners, legacy IDs, included use cases).
- **Not changed:** application code, test behaviour, A2.0/A2.1/B1 evidence, `setup/local-baseline` (already pushed), `prompt.md`, the assignment PDF.
- **Commands and checks:**
  - pyflakes and reference scans for the cleanup inventory: no tracked file deleted or moved;
  - `git clean -ndX` dry run (revealed that `git clean -X` would delete the development database);
  - `docker compose -p sqe-uc07-designcheck config` render only, plus read-only `docker ps -a` and `docker volume ls` (no container or volume created, started or removed);
  - `scripts/sqe/check_docs.py` with a negative test;
  - `run_tests.py check/upstream/team`;
  - the Playwright suite re-run;
  - evidence token scans.

  Development database checked by metadata only: unchanged.
- **Process errors, honestly recorded:**
  - A gated commit run stopped on `git diff --cached --check` (raw Playwright `console.log` ends with a blank line) **after** the evidence had been staged.
  - The next run first committed `docs/sqe/evidence/.gitattributes` (`*.log -whitespace`, so raw logs stay byte-exact). That commit, `065fca0` "chore: exempt raw evidence logs from whitespace checks", therefore **also contains all 29 files of `browser/b1-provenance-2026-11-24/` and `regression/r5-2026-11-24/`**, although its message mentions only the attributes file.
  - The content is correct and intended; the grouping and message are not. History was not rewritten (no amend or reset). Every later commit asserted an empty index first.
  - Separately, two scripted edits briefly produced a missing or an extra final newline, which the whitespace gate caught before any commit.
- **PR #1 AI record:** `docs/sqe/AI-USE-RECORD-PR1-REMEDIATION.md` exists only on `setup/local-baseline`. It is consolidated into this file after integration ([REPOSITORY-STRUCTURE.md](REPOSITORY-STRUCTURE.md)); it is not duplicated here.
- **Student review required:**
  - confirm the proposed catalog and ownership;
  - ask the instructor D-1/D-2;
  - decide the decision-feedback oracle, the over-allowance error contract and the TCL target;
  - review the auto-release guard;
  - each owner reviews and explains the B1 tests assigned to them.


# PR #2 review remediation — critical-module decision (24 November 2026)

- **Tool:** Claude Code (Claude Opus 5.5), at the student's instruction. No reviewer approval, instructor decision or team agreement is claimed.
- **Concern addressed:** the PR #2 reviewer asked for a documented decision process for selecting one critical module (serializer `validate` vs `visible_requests`). PR #2's merge commit is not present locally (no fetch); the concern text was supplied by the student.
- **Analysis and evidence:** written to `docs/sqe/evidence/whitebox/critical-module-2026-11-24/`.
  - radon 6.0.1 cyclomatic complexity;
  - coverage.py 7.6.10 branch coverage of the existing A2.1 API suite (40/40 passed) on the candidate files;
  - `feasibility_probe.py`, which executes every evaluable truth row of D1, H and D2 on the in-memory test database.
  - The tools were installed with `pip --target` into `/tmp`; the project `.venv` was not modified.
- **Created:** `docs/sqe/planning/DR-001-CRITICAL-MODULE.md` (PROPOSED: W1 validation chain; `visible_requests` rejected as an alternative).
- **Modified:** COVERAGE-BOUNDARY, TEST-STRATEGY, BUSINESS-RULES (v0.1 text kept, marked superseded), RTM (MCC-001), RISK-REGISTER (JR-03), ENTRY-EXIT-CRITERIA (EC-04), EXECUTION-ROADMAP (WP-09), SCOPE (open decision 2), TEST-PLAN (M0).
- **Not changed:** application code, tests, existing evidence; no business rule.
- **Development database:** unchanged (metadata only).
- **Student review required:** confirm DR-001; obtain instructor confirmation of the critical module; reply to the PR #2 reviewer.

# A2.2 — cross-workflow integration testing

- **Date/tool:** 24 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted implementation and execution; no human review, approval or authorship is claimed.
- **Sources read:** FUNCTIONAL-REQUIREMENTS (FR-W1-05, FR-W1-06, FR-W2-04, FR-W2-05, FR-W2-06), BUSINESS-RULES (BR-02, BR-03, BR-05), TEST-BASIS (GAP-01), RTM (API-INT-001), API-FUNCTIONAL-TESTING.md; `backend/leave/models.py`, `serializers.py`, `views.py`.
- **Created:** `tests/team/integration/test_w1_w2_integration.py` (7 tests); `docs/sqe/evidence/integration/a22-2026-11-24/`.
- **Tests:** 7 passed — approve path, reject path, overdraw characterization, self-decision forbidden, cross-team visibility, re-decide after approval (409), re-decide after rejection (409).
- **Limitations:** the overdraw test (API-INT-001) is a characterization test pinning GAP-01 baseline behavior, not an approved oracle. Concurrency integration (API-INT-002) requires PostgreSQL and is not implemented.
- **Student review required:** confirm characterization tests do not misrepresent baseline as correct behavior; all Git/GitHub actions remain student-owned.

# A2.3 — EP/BVA, decision table and state transition testing

- **Date/tool:** 24 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted implementation and execution; no human review, approval or authorship is claimed.
- **Sources read:** FUNCTIONAL-REQUIREMENTS, BUSINESS-RULES, TEST-BASIS, COVERAGE-BOUNDARY, RTM structural families; `backend/leave/models.py`, `serializers.py`, `views.py`.
- **Created:** `tests/team/structural/test_ep_bva.py` (48 tests: 22 W1 EP, 12 W2 EP, 14 BVA 3-point), `tests/team/structural/test_decision_table.py` (10 tests: DT1 W1 validation — 5 rules covering date order, overlap, balance record and balance amount; DT2 W2 authorisation — 5 rules covering role, visibility, self-decision and pending guard; each with ASCII truth table in docstring), `tests/team/structural/test_state_transition.py` (7 tests: full pending→approved/rejected transition table with invalid transitions).
- **Total:** 65 tests, all passed.
- **Techniques:** equivalence partitioning per FR, 3-point BVA on numeric/date/string boundaries, decision tables for compound business rules, state transition testing for leave request lifecycle.
- **ID mapping note:** the code's DT1 (W1 validation) maps to RTM objectives DT-001 (balance boundary) and DT-002 (overlap predicate) combined. The code's DT2 (W2 authorisation) maps to parts of RTM DT-003 (visibility/role check). DT-004 (notification recipients) and DT-005 (upcoming-leave filter) are not covered by either table.
- **Limitations:** BVA uses 3-point (boundary, boundary−1, boundary+1). Decision tables DT-004 (notification recipients) and DT-005 (upcoming-leave filter) are not covered. EP classes derived from requirements, not from code paths.
- **Student review required:** verify EP classes are complete for each FR; confirm 3-point BVA is acceptable per course guidelines; all Git/GitHub actions remain student-owned.

# A2.4 — OpenAPI spec, automated test data generation, constraint change analysis

- **Date/tool:** 24 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted implementation and execution; no human review, approval or authorship is claimed.
- **Sources read:** FUNCTIONAL-REQUIREMENTS, BUSINESS-RULES, `backend/leave/models.py`, `serializers.py`, `views.py`, `urls.py`; OpenAPI 3.0 specification standard.
- **Created:** `docs/sqe/openapi/leaveflow-api.yaml` (OpenAPI 3.0 spec covering all 7 endpoints with x-business-rules extensions), `scripts/sqe/generate_api_tests.py` (standalone script that reads the YAML spec and writes Django TestCase source files with one method per generated case, producing EP + 3-point BVA test cases), `tests/team/generated/test_generated_api.py` (33 generated tests: 7 login, 20 W1, 6 W2), `tests/team/generated/test_generated_api_v2.py` and `test_generated_api_v3.py` (constraint change demonstrations), `docs/sqe/openapi/CHANGE-1-NOTE-LENGTH.md`, `docs/sqe/openapi/CHANGE-2-SICK-TYPE.md`.
- **Process:** spec written manually from source code and requirements, not auto-generated from DRF. Generator is a standalone Python script that writes Django TestCase source, not parameterized pytest cases. Two constraint changes demonstrated: (1) note maxLength 280→200 produces 1 expected failure, (2) adding "sick" leave type produces 1 expected failure. Demo files load only when `SQE_SPEC_CHANGE_DEMO=v2` (for v2) or `=v3` (for v3), not `=1`.
- **Limitations:** generator produces EP and BVA cases only; it does not generate decision table, state transition or integration tests. The spec is a testing artifact, not a contract with the application. Admin endpoints are out of scope.
- **Student review required:** verify spec matches actual API behavior; confirm constraint change demonstrations are sufficient for the rubric; all Git/GitHub actions remain student-owned.

# PR #10 review — decision-table coverage (25 November 2026)

- **Date/tool:** 25 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted audit, implementation and execution; no human review, approval or authorship is claimed.
- **Purpose:** check the PR #10 review claim that decision-table coverage falls short. Verdict: valid. DT-004 and DT-005 describe logic that exists in the baseline (`events.py`, `team_view`) and had no team test; DT-003 lacked the employee-without-team row; DT-002 had no combination table.
- **Correction of an earlier AI statement:** the 24 November RTM edit marked DT-002 as executed at rule level and pk exclusion as unreachable. Both were overstated and are corrected in the RTM.
- **Created:** `tests/team/structural/test_decision_table_rules.py` (42 tests: DT-002 14, DT-003 6, DT-004 13, DT-005 9); `docs/sqe/evidence/structural/decision-tables-2026-11-25/` (run on commit `bbb3174`). RTM status updated.
- **Checked:** 42/42 passed; full team suite 199/199; development database unchanged. Twelve faults injected one at a time in a throwaway copy of the application: 11 caught by this file. The twelfth (`start_date__lte` to `__lt` in the overlap query) is an exact-boundary fault that the table's mid-interval dates cannot see; `test_bva_overlap_start_at` catches it. The repository source was not changed.
- **Limits:** DT-004 verifies who is in the event, not delivery through Redis, the worker or the gateway. The GAP-08 row is a characterisation. DT-001's W2 half stays blocked by GAP-01. Some rows repeat A2.1 case classes; the file header lists them so that each is counted once.
- **Student review required:** check each table's infeasibility argument and be able to explain the recorder used for DT-004; all Git/GitHub actions remain student-owned.

# PR #10 review — OpenAPI contract verification (25 November 2026)

- **Date/tool:** 25 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted audit, implementation and execution; no human review, approval or authorship is claimed.
- **Purpose:** check the PR #10 review claim that the API contract is not verified. Verdict: valid. No test compared a response with the spec, and the generated tests checked the status class and stored rows only.
- **Correction of an earlier AI output:** the 24 November spec omitted responses the application really returns. Added: login 401 (invalid Authorization header), 415 on the three POST operations, W1 400 with `detail` (malformed JSON), W2 404 as HTML (id that does not match the route), and `x-known-deviations`.
- **Created:** `tests/team/api/contract.py` (strict validator, standard library only), `tests/team/api/test_openapi_contract.py` (41 tests), `tests/team/generated/api_contract.json` (exported from the spec by the generator, because the test environment has no YAML parser); `docs/sqe/evidence/api/contract-2026-11-25/` (run on commit `2d02e9c`). RTM status updated.
- **Found in the application (not changed):** 500 for a non-object JSON body on login and on W2 (`request.data.get`), and 500 for W1 `end_date` 9999-12-31 (date overflow in `business_days`). Pinned as characterisations.
- **Checked:** 41/41 passed; full team suite 240/240 at that commit; spec validated with openapi-spec-validator; development database unchanged. Eight response faults injected one at a time in a throwaway copy of the application: all caught.
- **Limits:** verifies response structure, not every business value. 405 responses are outside the spec, since OpenAPI lists only implemented methods. The spec types `note` as string, while the application also accepts a number.
- **Student review required:** file the three defects, decide severity, and confirm the spec changes; all Git/GitHub actions remain student-owned.

# PR #10 review — generated inputs (25 November 2026)

- **Date/tool:** 25 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted audit, implementation and execution; no human review, approval or authorship is claimed.
- **Purpose:** check the PR #10 review claim that generated inputs fall short. Verdict: partly valid. The generator did read the spec and produce EP and BVA, but it skipped the W2 path `id`, the token, null/omitted optional fields and the note's lower limit, generated nothing for the balance and overlap rules named by GEN-001, and wrote no case manifest.
- **Correction of an earlier AI output:** the 24 November generated tests accepted any documented 4xx for an invalid body, so a wrong 401, 403 or 409 would have passed. They now require the exact status and error key.
- **Created/changed:** `scripts/sqe/generate_api_tests.py`; spec extensions `x-invalid-examples`, `x-rule-boundaries` and `x-sqe-fixture`, and `minLength: 0` for note; `tests/team/generated/` regenerated (33 → 68 tests; v2 68, v3 69), with `generated_cases.json` and `test_generated_manifest.py` (2 tests); `docs/sqe/evidence/generated/inputs-2026-11-25/`, `change-1-note-length-2026-11-25/`, `change-2-sick-type-2026-11-25/` (run on commit `3ebeb40`); CHANGE documents (section 5); RTM status.
- **Checked:** 70/70 passed; full team suite 277/277; v2 and v3 fail on exactly one intended test each; spec restored byte for byte and validated; development database unchanged. Six faults injected one at a time in a throwaway copy of the application: all caught.
- **Limits:** invalid examples and rule boundaries are written by hand in the spec, then generated. Only POST operations are generated; the GET operations have no input except the token, and their 401 is covered by the contract tests. The W2 `id` has EP only, because existence is not a numeric limit.
- **Student review required:** be able to change a constraint in the spec, regenerate and predict the failing tests in the viva; all Git/GitHub actions remain student-owned.

# PR #10 completion report — remaining Area 2 gaps (25 November 2026)

- **Date/tool:** 25 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction ("analyze this review and check that if its identified gaps are genuine if yes then fill the gaps"). AI-assisted audit, implementation and execution; no human review, approval or authorship is claimed.
- **Input:** the reviewer's completion report for head `0bf291a`. Each finding was checked against `ce0b53f` and reproduced where it is a runtime claim (padded 282-character note → 201; nullable change; EC-01 → −3).
- **Corrections of earlier AI outputs:** the spec's raw `maxLength` contradicted the application's trimming; form and multipart bodies were undocumented; a nullable field gained no valid null case; the generated readback checked a row count or status only.
- **Created/changed:** generator rewritten (127 tests; contexts, media, methods, reads; full row, balance, token and schema readback; manifest with constraints and inapplicable techniques; `--patch`), spec, three change patches and v2–v4; API-INT-001.08/.09; `test_event_publication.py` (6); API-INT-002 with its PostgreSQL profile and runner (5); `api_coverage.py` and API-COVERAGE.md; fast hasher in the core profile; DEFECT-RECORDS.md; `docs/sqe/openapi/README.md`; RTM, EC-03, EC-05 and GAP-02 status.
- **Checked:** team 344/344 and upstream 9/9 in the working tree and from a fresh local clone with a new virtual environment, where regeneration reproduced the committed files; concurrency 5/5 in five consecutive runs on PostgreSQL 17.12 after one probe bug was fixed (`pg_stat_activity` is cached inside a transaction); 12 faults injected one at a time in a throwaway copy, all caught (one was first injected wrongly, as an equivalent change, and repeated); removing the row lock fails both lock tests; the coverage tool reports level 0 without calls and rejects a flow on a different request id. Development database unchanged; no other container touched.
- **External access:** the public image `postgres:17-alpine` (the one in docker-compose.yml) was pulled, and the fresh virtual environment installed the pinned packages from PyPI. No project or personal data was sent.
- **Limits:** the operation flows and the TCL mapping were written by the AI and need checking against the Lecture 20 slides. Worker, gateway and browser delivery of events are not tested (UC-07, D-2). Characterisations pin open defects.
- **Not done, student/team:** filing issues, agreeing the EC-01 rejection contract, the TCL target and notification scope, the CI job (Member 1), actual effort, UC-07, and the 5 Whys/fishbone analyses. All Git/GitHub actions remain student-owned.

# PR #10 — defect issues and root cause analysis (25 November 2026)

- **Date/tool:** 25 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction (issue texts and RCAs for two major defects, EC-05/GAP-02 status, review reply). AI-assisted analysis, execution and drafting; no human review, reproduction, triage or approval is claimed.
- **Created:** `ISSUE-MAJOR-01/02`, `RCA-MAJOR-01/02` and `PR-10-REVIEW-RESPONSE.md` in `docs/sqe/defects/`; `rca-experiments/` (scripts) and `docs/sqe/evidence/defects/rca-2026-11-25/` (run on commit `53c4da3`). **Updated:** DEFECT-RECORDS, EC-05, TEST-BASIS GAP-02 and risk B. Application code and CI unchanged; experimental changes exist only in throwaway clones and as `.diff` evidence.
- **Executed:** eight application variants on throwaway PostgreSQL 17.12 containers; upstream and team suites against two candidate fixes; 300 pairs of simultaneous HTTP submissions against real gunicorn with 1, 2 and 3 processes.
- **Statements of the task prompt corrected by evidence:** `views.py:81–86` does not read the allowance at all; default autocommit contributes to the second defect, but a transaction alone does not fix it, and `select_for_update` helps only on a row that always exists; SERIALIZABLE needs a retry; EC-05 and GAP-02 no longer said the spec was missing (wording completed instead); the defects are executed but not independently verified, so every human field says PENDING.
- **Corrections of earlier AI outputs:** DEFECT-RECORDS said the W1 race "can occur in production" without evidence. It cannot be shown with the shipped single worker and is near certain with two processes. An earlier entry said the TCL mapping needs checking against Lecture 20; it was now compared with the Lecture 20 text and the original paper and matches.
- **Errors during the work:** the first experiment run reported a 500 for both requests while one row was stored. Django's test client collects exceptions through a process-wide signal, so one thread re-raised the other's error; fixed, and all variants rerun. The first HTTP run did not start, because an invalid debug value made the application redirect to HTTPS.
- **External access:** the public A-TEST 2019 paper and a related preprint were downloaded and a web search was made. No project or personal data was sent.
- **Limits:** three local servers stand in for Kubernetes replicas. Why the original authors omitted the rules is not known. Severity, priority and root-cause categories are proposals.
- **Student review required:** reproduce both defects, be able to explain each Why and each refuted cause, have another member verify independently, file the issues, and fill the PENDING fields from real events. All Git/GitHub actions beyond local commits remain student-owned.

# DEF-A2-01 — agreed rejection contract recorded (25 November 2026)

- **Date/tool:** 25 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted documentation update; the decision is the team's, as stated by the student in the task prompt. The AI did not take part in it and saw no separate approval record.
- **Contract recorded:** an over-balance approval returns 400 `{"detail": "Insufficient leave balance"}`; the request stays pending, `decided_by` null, balance unchanged.
- **Changed (documents only):** ISSUE-MAJOR-01, RCA-MAJOR-01, DEFECT-RECORDS, PR-10-REVIEW-RESPONSE; ENTRY-EXIT-CRITERIA (EC-01, EC-05), RISK-REGISTER, TEST-STRATEGY, DEFECT-MANAGEMENT-PLAN, RTM; TEST-BASIS, BUSINESS-RULES, FUNCTIONAL-REQUIREMENTS, SCOPE, USE-CASE-SPECIFICATIONS; BROWSER-USE-CASE-TESTING, A21-EXECUTION-MAPPING, SHARED-TEST-FOUNDATION. Earlier entries of this record and all evidence files are kept as history.
- **Statement of the task prompt corrected by the source:** submission does return 400, but with `{"non_field_errors": ["Saldo ferie insufficiente."]}`, not a `detail` body. The `detail` key matches the decision endpoint; the English text differs from the Italian messages of the application. The contract was recorded as given and the difference is noted in RCA 1.
- **Interpretation:** GAP-01 is marked resolved as a specification gap only. The safeguard is still missing, DEF-A2-01 is open and EC-01 stays NOT MEASURED. Employees without a balance row are not covered (GAP-07).
- **Not changed:** application code, tests (the characterizations, the `fixme` OBJ-UC02-01 and `flows.json`, whose comments still say the contract is not approved), the OpenAPI spec (describes the implemented behaviour) and the W2 half of DT-001.
- **Not executed:** no test asserts the new contract, and the earlier experiments returned a placeholder 409.
- **Student review required:** record who agreed and when, decide the message language and the missing-balance case, and confirm the wording. All Git/GitHub actions beyond local commits remain student-owned.

# PR #10 review — flow matching, DT-001 W2, generator fixes (27 November 2026)

- **Date/tool:** 27 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction (four review items and an updated PR description). AI-assisted implementation, execution and drafting; no human review, approval or authorship is claimed.
- **Flow matching (TCL7):** confirmed the review finding by running the previous matcher on an approve-then-submit sequence: it reported "reject then resubmit the dates". Each `x-operation-flows` step now states its status and conditions (decision, same record or dates, actor), enforced by `scripts/sqe/api_coverage.py`; `tests/team/foundation/test_flow_matcher.py` (7 tests, negative cases with the same endpoint sequence). Spec, generated modules and change patches regenerated (spec SHA-256 now `939d1303…`). Coverage rerun: TCL7 kept, 8/8 flows each matched by a test that meets every condition (`submit then own list` 3 → 2 tests). The report's old note that the TCL mapping still had to be checked against the slides was replaced, since it was checked on 25 November.
- **DT-001 W2 half:** R1 reject over limit, R2 no balance record (GAP-07 characterisation), R4 approval to exactly 0, all passing; R3, the overdraw regression with the agreed 400 contract, loads only with `SQE_DESIRED_RULES=1` and fails on the baseline (200). It passed 14/14 with the module against a candidate fix in a throwaway clone (deleted). Gated rather than marked as an expected failure, because the runner exits 1 for expected failures and skips. Issue links #25/#26 (given by the student) added to DEFECT-RECORDS, the RTM and both RCAs.
- **Statement of the task prompt not followed as worded:** no concurrent-submission row was added to DT-001. DT-001 is the balance table; the concurrency regression belongs to API-INT-002 on PostgreSQL (#26) and is not written.
- **Generator:** both reported bugs confirmed. The one-day allowance crashed the generator with `OverflowError` (a 0-day interval looped past `date.max`); fixed with a minimum of one business day, a recorded skip, and an invalid class that stays a real duration (allowance 0 also crashed through that class). The null-note `.strip()` was latent: the v4 null case fails at its status check before the readback, so it never ran; it is guarded now. Generation checked with allowances 0, 1, 2 and 10; the committed spec still yields 127 tests.
- **Checked:** team 354/354, upstream 9/9, PostgreSQL 17.12 concurrency 5/5 (container removed), v2/v3/v4 fail on the predicted 2/1/1 tests, docs check 0 problems, development database unchanged. `openapi-spec-validator` was not available in this environment, so the edited spec was not revalidated with it; the generator parsed it.
- **Created:** `PR-10-DESCRIPTION-UPDATE.md`; evidence `api/coverage-2026-11-27/`, `structural/dt001-w2-2026-11-27/`, `concurrency/postgresql17-2026-11-27/`.
- **Not changed:** application code and CI. The CHANGE documents keep the spec hashes of their original runs.
- **Student review required:** check the flow conditions against the intended meaning of each flow, the R2 characterisation, and that #25/#26 are the right issues; agree the CI job with Member 1. All Git/GitHub actions beyond local commits remain student-owned.

# Independent reproduction of DEF-A2-01 and DEF-A2-02 recorded (27 November 2026)

- **Date/tool:** 27 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted documentation only; the reproduction itself was done by a team member, not by the AI.
- **Source of the facts:** the comments by Muhammad Bilal (@Bilalmughal-07) on [#25](https://github.com/eshalfatima2006/LeaveFlow/issues/25#issuecomment-7220515359) and [#26](https://github.com/eshalfatima2006/LeaveFlow/issues/26#issuecomment-7220564456), read through the GitHub CLI (read-only). The attached zips were downloaded to a scratch directory and their runner records checked: all at commit `8ee5176`. #25: characterization `ExitCriterionScenarioTests` 1/1 passed, regression `W2ApprovalOverdrawRegression` 1 failed (`AssertionError: 200 != 400`), in-memory SQLite. #26: 5/5 passed on PostgreSQL 17.12 (`postgres:17-alpine`). The development-database check is unchanged in all three runs. The zips were not added to the repository.
- **Updated:** both RCAs (independent reproduction CONFIRMED; triage, severity, fix and closure still PENDING), both issue texts, DEFECT-RECORDS, EC-10, the PR #10 description, the PR-01/PR-03 risk evidence, and WP-23 in the effort estimate and roadmap.
- **Statement of the task prompt not followed as worded:** EC-10 was set to **PARTLY MET**, not MET. Its target also needs weekly defect/coverage/reopen reporting, actual effort against estimates, the completion review, the PDF/ZIP package and each member's rerun, none of which is measured; and the corrective and preventive actions are proposed, not complete (owners and fixes PENDING, the #26 regression not written). Only the major-defect part is recorded as met.
- **Not changed:** application code, tests, historical records (earlier AI-use entries and `PR-10-REVIEW-RESPONSE.md`, which record what was true when written).
- **Student review required:** confirm the EC-10 verdict with the team, and run shared triage for #25 and #26. All Git/GitHub actions beyond local commits remain student-owned.

## Area 1 integration and evidence audit - 27 November 2026

- Tool: Codex, at Bilal's instruction to implement CI integration and complete
  Area 1 evidence. AI-assisted implementation, execution and drafting; human
  approval is not claimed. No remote push, issue comment, review or merge was made.
- Created local `ci/integrate-team-tests-and-area1-evidence` from PR #17 and
  merged Area 2 head `8ee5176` locally. Added team/generator/TCL7/PostgreSQL CI
  checks, aggregate quality enforcement and release-event safeguards.
- Corrected MC/DC outcome pairs and CFG edge/node counts. Added explicit
  balance-presence, demo schedule/reset and failing-report gate tests.
- Verified 384 Django team tests, 9 upstream tests, all critical statement/branch
  coverage, generator consistency, TCL7 and disposable PostgreSQL concurrency.
- Actual final Linux mutmut run: 296 killed, 3 equivalent survivors, 299 total.
  Reviewed 15 historical survivors from the committed PR #17 report individually.
  A historical rerun stalled and was stopped; it is not reported as completed.
- Found mutmut's decorated-function exclusion: replaced the inactive calendar
  custom operator with reachable overlap boundaries. Separate temporary-copy
  mutations kill weekday and inclusive-date property changes without changing
  production files or weakening tests. Source/test/runtime provenance is retained.
- Captured historical and fresh live Sonar API evidence. Corrected the upstream
  test file's source classification; fresh scan passed at 100% overall coverage,
  zero findings and all A ratings. An unchanged extracted validate function
  measured 4 in Sonar versus hand/radon 5; documented exception convention.
  Temporary analysis tokens were revoked and no credentials were committed.
- Verified remote historical fail/fix/pass step evidence (runs 16, 18 and 68)
  through read-only GitHub API calls. New hosted execution, the new required
  branch check and instructor decisions remain explicitly external.

## PR #17 mutation and required-check audit - 28 November 2026

- Tool: Codex, at Bilal's request to satisfy the mutation evidence requirement
  and explain the added CI check. AI-assisted inspection, test drafting,
  execution and evidence writing; no human review or full-marks guarantee is
  claimed. The student must inspect the output and be able to explain it.
- Checked the assignment wording against PR #17's source, the GitHub CI jobs,
  active repository ruleset, and downloaded run 66/run 74 artifacts. Run 66
  recorded 30 survivors; run 74 recorded 4 at 295/299. Preserved both raw
  stats and the original historical survivor table with revision links.
- Repeated mutmut on the exact PR #17 tree: 295 killed,
  4 survived, no unresolved, including 65/65 killed in models, serializers
  and views. Identified E-10 as a killable event-recipient survivor.
- Added a manager/admin requester assertion after the student requested that
  E-10 be killed. The correct source passed; the exact E-10 mutation failed by
  assertion for both role subcases. Existing tests were not weakened.
- Full verification after the assertion: 82 tests and 144 subtests passed;
  mutmut recorded 296 killed, 3 equivalent survivors, 299 total and no
  unresolved mutants. Raw output, environment, source hashes and diffs are
  preserved. This is local evidence until the revised commit runs on GitHub.
- The earlier 295/299 hosted result is not changed or presented as the new
  score. No push or new hosted run occurred in this audit. Most of the 15
  historical survivors are in demo support code, which is disclosed instead
  of claiming they all belong to DR-001.

# PR #10 updated with `dev` after PR #17 (28 November 2026)

- **Date/tool:** 28 November 2026 (Asia/Karachi), Claude Code (Claude Opus 5.5) at the student's instruction. AI-assisted merge resolution, CI-compatibility fixes and execution; no human review is claimed.
- **Merge:** completed the student's merge of `origin/dev` (`65d8f06`, PR #17) into `test/a2.4-openapi-gen`. The only conflict, in this record, was resolved by keeping both sides' entries unchanged.
- **Problems found by running the Area 1 gate commands locally:** (1) `pytest` ignores the `load_tests` hooks, so it collected 387 tests excluded from the default suite (spec-change demonstrations v2/v3/v4, PostgreSQL-only concurrency). Added `tests/conftest.py` with the same four exclusions. (2) mutmut's clean-test run failed because its `mutants/` copy lacked `docs/sqe/openapi/leaveflow-api.yaml`, read by the contract tests. Added `docs/sqe/openapi` to `also_copy` in `setup.cfg` (a single-file entry crashes mutmut 3.8.1, which does not create parent directories for files).
- **Checked (Python 3.12.7 in a disposable virtualenv; CI uses 3.13):** `coverage run --branch -m pytest` 384 passed, 184 subtests; critical-module coverage 100% statement and branch for models, serializers, views and events; mutmut 296 killed, 3 survived, 299 total, no unresolved, threshold passed; Django runner team 384/384 and upstream 9/9; development database unchanged. SonarQube was not run locally. Hosted CI has not run on this revision yet.
- **Not changed:** application code, existing tests, `ci.yml`.
- **Student review required:** confirm the exclusions match the `load_tests` hooks, and check the hosted run after pushing.
