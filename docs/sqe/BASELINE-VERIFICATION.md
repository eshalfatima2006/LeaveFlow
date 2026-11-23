# LeaveFlow — Baseline Verification Report

> **Revision note (23 November 2026).** Sections 3, 5–7 and 10–12 were corrected after the PR #1 review, and section 13 was added. The original baseline execution took place on 21 November 2026; its artifacts are kept unedited. Results produced on 23 November 2026 are labelled **newly reproduced** and are not presented as part of the original execution.
>
> **Evidence status labels used below:** **Historically verified** — supported by an artifact captured on 21 November 2026 · **Newly reproduced** — executed again on 23 November 2026 in an isolated environment, with logs · **Source-verified only** — confirmed by reading code/configuration, not by execution · **Unverified** — stated but not supported by any retained artifact · **Blocked** — cannot be verified without information or access not available locally.

## 1. Project Information

**Course:** SE3002 — Software Quality Engineering  
**Project:** Automated Testing of LeaveFlow Management Information System  
**Upstream Repository:** https://github.com/cmdr-chara/LeaveFlow  
**Team Repository:** https://github.com/eshalfatima2006/LeaveFlow  
**Baseline Commit:** `bada9a03ecec53ef6945827230e3594d825da87a`  
**Baseline Date:** 21 November 2026  
**Environment:** Windows with WSL Ubuntu

## 2. Objective

The purpose of baseline verification is to confirm that the original LeaveFlow application can be installed, initialized and executed locally before the team begins implementing its independent software quality engineering tests.

This baseline provides a reproducible reference for later testing, defect identification, code changes and regression analysis.

## 3. Development Environment

| Component | Version / Configuration | Evidence status |
|---|---|---|
| Operating system | WSL2, kernel `6.6.114.1-microsoft-standard-WSL2`; Ubuntu 26.04 LTS | Kernel: historically verified ([environment.txt](evidence/baseline/environment.txt)). Distribution: newly reproduced only ([01-environment.json](evidence/baseline/reproduction-2026-11-23/01-environment.json)) |
| Python | 3.12.7 | Historically verified and newly reproduced |
| Git | 2.53.0 | Historically verified and newly reproduced |
| Node.js | 22.23.3 | Historically verified and newly reproduced |
| npm | 10.9.9 | Historically verified and newly reproduced |
| Django | 6.0.7 | **Newly reproduced only** — the historical `environment.txt` has an empty `Django:` entry |
| Django REST Framework | 3.17.1 | **Newly reproduced only** — not recorded historically |
| Other packages | django-cors-headers 4.9.0, redis 6.4.0, psycopg 3.3.4, gunicorn 26.0.0, pip 26.3 | Newly reproduced only |
| Database | Historical run: SQLite development database (`backend/db.sqlite3`). Reproduction: disposable SQLite file in a temporary directory; Redis disabled | Historical: environment.txt. Reproduction: [02-settings-guard.log](evidence/baseline/reproduction-2026-11-23/02-settings-guard.log) |
| Python environment | `.venv` | Newly reproduced (`python_executable` in 01-environment.json) |
| Backend address | `http://127.0.0.1:8000` (historical run) | Unverified — no server log was retained. The reproduction used `127.0.0.1:8797` |

## 4. Repository and Version Control

The original LeaveFlow repository was cloned into WSL Ubuntu.

A team-owned GitHub fork was configured as `origin`, while the developer's repository was configured as `upstream`. *Historically verified:* the terminal capture [baseline.png](screenshots/baseline.png) shows the remote rename/add and `git rev-parse HEAD` returning the baseline commit.

The exact audited baseline commit was verified using `git rev-parse HEAD` (same capture).

The project uses feature branches for changes and a protected `main` branch for reviewed work. *Feature branches are visible in local history; branch protection is a GitHub setting and is* **blocked** *from local verification.*

## 5. Backend Installation and Initialization

The following commands were executed during the original baseline (21 November 2026):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python backend/manage.py check
python backend/manage.py migrate
python backend/manage.py seed_demo
```

**Observed results (original run) and evidence status:**

- Python dependencies installed successfully. — *Unverified for the original run* (no install log retained); the installed versions are newly reproduced in section 3.
- Django system check completed with zero reported issues. — *Historically verified* ([django-check.log](evidence/baseline/django-check.log)) and *newly reproduced* ([03-django-check.log](evidence/baseline/reproduction-2026-11-23/03-django-check.log)).
- Database migrations completed successfully. — *Not supported by the historical log:* [migrations.log](evidence/baseline/migrations.log) is a hand-written summary of `migrate --check` (no unapplied migrations), not the output of `migrate`. *Newly reproduced* on a disposable database: `showmigrations` before (23 unapplied), `migrate` (23 applied, exit 0), `showmigrations` after (23 applied, 0 unapplied) and `migrate --check` (exit 0) — see [05-migrate.log](evidence/baseline/reproduction-2026-11-23/05-migrate.log) and steps 04–07.
- Demo data was initialized. / Local demonstration accounts were created. — *Historically verified indirectly:* the 21 November screenshots (section 12) show the seeded demo accounts. `seed_demo` was **not** re-run in the reproduction (it overwrites demo users and deletes all leave requests); synthetic users were created instead.

## 6. Original Test Suite

**Command:**

```bash
python backend/manage.py test leave
```

**Observed result (original run, 21 November 2026):**

- Tests discovered: 9
- Tests executed: 9
- Failures: 0
- Errors: 0
- Final status: PASS

*Historically verified* by [upstream-tests.log](evidence/baseline/upstream-tests.log) (`Found 9 test(s)`, `Ran 9 tests`, `OK`). That log does not record the command line or exit code, and only one execution is retained, so the earlier statement that the suite "was executed successfully more than once" is *unverified*.

*Newly reproduced* (23 November 2026): `manage.py test leave -v 2` with the disposable-database settings — 9 found, 9 ran, OK, exit code 0, Django test database `file:memorydb_default?mode=memory&cache=shared` (in memory). The nine tests are all in the upstream file `backend/leave/tests.py` (1 in `HealthApiTests`, 8 in `LeaveRequestApiTests`) — see [08-upstream-tests.log](evidence/baseline/reproduction-2026-11-23/08-upstream-tests.log). The result matches the historical run.

These are upstream tests and are not claimed as the team's independently developed tests. Tests written later by the team (`tests/team/` on other branches) are not part of this count.

## 7. Backend and API Verification

In the original run, the Django development server was started at `http://127.0.0.1:8000`, and the following observations were taken from its console logs:

| Operation | HTTP result | Observation |
|---|---|---|
| Login | 200 | Successful authentication response |
| Retrieve dashboard | 200 | Dashboard endpoint returned successfully |
| Retrieve leave requests | 200 | Leave request data returned |
| Retrieve team | 200 | Team data returned |
| Create leave request | 201 | Request creation accepted |
| Process leave decision | 200 | Decision endpoint accepted the request |
| Invalid leave request | 400 | Request rejected by server |
| Current-user lookup before authentication | 401 | Unauthorized request rejected |

*Unverified for the original run:* those server logs were not retained, so the table above is not supported by an artifact.

**Newly reproduced API smoke test (23 November 2026)** — real HTTP calls to a live `runserver` on a disposable database, with synthetic users (`smoke-employee`, `smoke-manager`, same team, allowance 10). Tokens and passwords are redacted/not recorded. Full results: [09-api-smoke.json](evidence/baseline/reproduction-2026-11-23/09-api-smoke.json); server log: [09b-api-server.log](evidence/baseline/reproduction-2026-11-23/09b-api-server.log).

| Step | Operation | Expected | Actual | Key fields |
|---|---|---|---|---|
| S01 | `GET /api/me/` without token | 401 | 401 | `detail` present |
| S02 | Login with wrong password | 400 | 400 | `Credenziali non valide.` |
| S03–S04 | Employee and manager login | 200 | 200 | correct `user.username`/`role`; token redacted |
| S05 | `GET /api/me/` as employee | 200 | 200 | `smoke-employee`, `employee`, `Smoke Team` |
| S06 | Employee dashboard | 200 | 200 | balance 10/0/10 |
| S07 | Employee submits 2027-03-01..05 (W1) | 201 | 201 | `id` k, `pending`, owner `smoke-employee`, 5 business days |
| S08 | Submission with end before start | 400 | 400 | error key `end_date` |
| S09 | Employee tries to decide k | 403 | 403 | `Operazione non consentita.` |
| S10 | Manager lists team requests | 200 | 200 | contains k |
| S11 | Manager approves k (W2) | 200 | 200 | same `id` k, `approved` |
| S12 | Repeated decision on k | 409 | 409 | `La richiesta è già stata decisa.` |
| S13 | Employee dashboard after approval | 200 | 200 | balance 10/5/5 |

Database readback ([09c-api-db-readback.log](evidence/baseline/reproduction-2026-11-23/09c-api-db-readback.log)): one request only; the same ID k; owner `smoke-employee`; status `approved`; `decided_by` `smoke-manager`; `decided_at` set; derived balance allowance 10, used 5, available 5. This confirms that W1 and W2 operate on the same persisted `LeaveRequest`.

Detailed database assertions and full browser-flow verification are captured separately in the team-owned API and Playwright test work.

## 8. Selected Workflows

**Workflow 1 — Employee Leave Request**

An authenticated employee submits a leave application, subject to the application's validation and eligibility rules.

**Workflow 2 — Manager Leave Decision**

An authorized manager approves or rejects a pending leave application. Both workflows operate on the same persisted `LeaveRequest` record.

## 9. Known Baseline Risks

The repository feasibility audit previously identified:

1. A potential approval-time leave-balance integrity defect.
2. Incomplete OpenAPI request/response schemas.
3. A need to verify full deterministic database reset.
4. A need to verify the complete frontend browser workflow.

These findings remain subject to independent reproduction and verification by the project team.

## 10. Baseline Conclusion

The initial local backend setup was successful. The Django system check and all nine upstream backend tests passed in the original run (historically verified) and again in the isolated reproduction (newly reproduced). Database migrations, which the original artifacts did not evidence, were newly reproduced on a disposable database.

API authentication, leave-request creation and the leave decision on the same persisted request were newly reproduced over HTTP with database readback (section 7). The original run's API observations are unverified because its server logs were not retained.

**Correction:** the original conclusion stated that the frontend production build still required verification. That contradicted the committed [frontend-build.log](evidence/baseline/frontend-build.log), which records a successful `npm run build` (`vue-tsc -b && vite build`, 1575 modules, built in 391 ms) from the original session. The build is therefore **historically verified**, and it was **newly reproduced** in a temporary copy of `frontend/` ([10-frontend-build.log](evidence/baseline/reproduction-2026-11-23/10-frontend-build.log), exit 0, identical asset file names).

Still outstanding: complete browser-flow assertions with persisted-state checks, and a deterministic database reset procedure.

**Baseline status: BACKEND, MIGRATIONS, UPSTREAM TESTS, API SMOKE AND FRONTEND BUILD VERIFIED — BROWSER-FLOW ASSERTIONS AND DETERMINISTIC RESET OUTSTANDING.**

## 11. Evidence References

Historical artifacts (21 November 2026, unedited):

- [evidence/baseline/environment.txt](evidence/baseline/environment.txt) — OS kernel, Python, Git, Node, npm, commit, branch (Django entry empty)
- [evidence/baseline/django-check.log](evidence/baseline/django-check.log)
- [evidence/baseline/migrations.log](evidence/baseline/migrations.log) — summary of `migrate --check` only
- [evidence/baseline/upstream-tests.log](evidence/baseline/upstream-tests.log)
- [evidence/baseline/frontend-build.log](evidence/baseline/frontend-build.log)
- Screenshots in [screenshots/](screenshots/) (section 12)

Newly reproduced artifacts (23 November 2026): [evidence/baseline/reproduction-2026-11-23/](evidence/baseline/reproduction-2026-11-23/) — `summary.json`, `01-environment.json`, and logs 02–10 (one file per command, each with the command, timestamps, exit code and unedited output).

## 12. Browser Screenshots

The following screenshots were captured on 21 November 2026 (the dashboards show "Saturday 21 November") from the locally running LeaveFlow application, using the seeded demonstration accounts. They are historical and were not regenerated.

| Evidence | Description (checked against the image) | File |
|---|---|---|
| BL-UI-01 | Employee overview ("Demo Employee"): 25 of 26 days available; counters 1 pending, 1 approved, 3 total | [screenshots/employee-dashboard.png](screenshots/employee-dashboard.png) |
| BL-UI-02 | New-request form: Vacation, 11/03/2026–11/24/2026, preview "16 working days" | [screenshots/new-request-form.png](screenshots/new-request-form.png) |
| BL-UI-03 | Manager overview ("Demo Manager"): team requests, including a pending row with approve/reject buttons | [screenshots/manager-dashboard.png](screenshots/manager-dashboard.png) |
| BL-UI-04 | Manager's decision result for a leave request | **Not captured.** No screenshot of a decision result exists. The decision is evidenced instead by the newly reproduced API smoke test (section 7, S11–S13) |
| BL-UI-05 | Administrator overview ("Demo Admin") | [screenshots/admin-dashboard.png](screenshots/admin-dashboard.png) |
| BL-ENV-01 | Terminal: remote configuration and `git rev-parse HEAD` = baseline commit | [screenshots/baseline.png](screenshots/baseline.png) |

These screenshots provide preliminary browser evidence only. Automated browser assertions and persisted-database verification are performed separately in the team's Playwright and integration testing phases.

## 13. PR #1 Review Remediation (23 November 2026)

The text of the GitHub issue that tracks the PR #1 findings was not available locally and was not retrieved over the network. The findings below come from the review list supplied by the team and the locally recorded gap GAP-09 ("report conclusion and screenshot paths disagree with later logs/tree").

| Finding | Problem found | Change | Status |
|---|---|---|---|
| A — Screenshot/evidence paths | Section 12 pointed to `evidence/baseline/screenshots/0N-*.png`, which never existed; the real files are in `screenshots/` under other names; BL-UI-04 was never captured; two committed screenshots were unreferenced | Paths corrected to working relative links; descriptions checked against each image; BL-UI-04 marked not captured; BL-UI-05 and BL-ENV-01 added | Partially resolved — links fixed and verified; no browser screenshot of a decision result exists (API evidence substitutes) |
| B — Migration evidence | `migrations.log` is a hand-written `migrate --check` summary, not migration output | `showmigrations` / `migrate` / `showmigrations` / `migrate --check` executed on a disposable SQLite database with logs | Fixed (newly reproduced) |
| C — Environment versions | Historical `environment.txt` has no Django version; DRF never recorded | Full environment captured in `01-environment.json`; section 3 now states the source of each value | Fixed (newly reproduced; historical gap kept visible) |
| D — API smoke evidence | API table based on server logs that were not retained | Real HTTP smoke test with synthetic users, redacted tokens and DB readback of the same request | Fixed (newly reproduced) |
| E — Upstream tests | Historical log lacked command and exit code; "more than once" unsupported | Re-run with command, exit code, test names and database isolation recorded: 9/9 OK | Fixed (newly reproduced; matches historical result) |
| F — Report contradiction | Conclusion called the frontend build outstanding despite a successful build log | Conclusion corrected; build re-run in a temporary copy | Fixed |
| G — Markdown quality | Section 12 heading glued to the previous paragraph; evidence references were not links; `frontend-build.log` unlisted; status wording outdated | Headings, links, evidence list and status corrected | Fixed |

**Reproduce (repository root, inside WSL):**

```bash
.venv/bin/python scripts/sqe/reproduce_baseline.py --evidence-dir docs/sqe/evidence/baseline/reproduction-<date>
```

The script ([scripts/sqe/reproduce_baseline.py](../../scripts/sqe/reproduce_baseline.py)) runs Django only with a generated settings module whose single database is a SQLite file in a new temporary directory, and it aborts if Django resolves to any other database. Redis is disabled and PostgreSQL variables are removed. The development database is never opened: only its file metadata (size, modification time, inode) is compared before and after — unchanged in the 23 November run (`summary.json`). The script never runs `seed_demo`, `flush` or a reset, and it builds the frontend in a temporary copy so that the repository tree is not written. The evidence directory must not already exist.
