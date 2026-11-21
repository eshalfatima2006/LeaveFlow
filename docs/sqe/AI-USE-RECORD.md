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
