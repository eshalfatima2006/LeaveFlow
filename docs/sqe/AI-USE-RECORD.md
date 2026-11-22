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
