# Phase 1 scope — LeaveFlow

Analysis date: 21 November 2026 (Asia/Karachi). Course: SE3002 Software Quality Engineering; three students; 120 marks. This is a source-grounded documentation draft for student review, not a claim that later testing is complete.

## Identity and evidence

| Item | Value |
|---|---|
| Selected MIS / module | LeaveFlow / leave requests and decisions |
| Upstream | https://github.com/cmdr-chara/LeaveFlow |
| Team fork | https://github.com/eshalfatima2006/LeaveFlow |
| Licence | MIT; `LICENSE:1–21` |
| Pinned upstream baseline | `bada9a03ecec53ef6945827230e3594d825da87a` |
| Local repository | `/home/pc/projects/sqe-final/LeaveFlow` |
| Current branch and HEAD verified | `docs/requirements-and-scope`; HEAD equals the pinned baseline |
| Assignment actually read | Local `SQE_Final_Project Fall 2026.pdf`, all seven pages |
| Lecture PDFs | None found in the workspace; none claimed as consulted |

The pre-existing `.gitignore` edit and untracked `prompt.md` were preserved. The requirements directory existed and contained no files before this work. No tracked application file differed from the baseline.

The baseline report is **absent from this branch's working tree**. It was read through `git show 81e677a:docs/sqe/BASELINE-VERIFICATION.md`; the original report and environment/test/build logs were also read from commit `7948f74`. Those commits exist locally on other history. They are historical evidence, not newly generated results. The report's “frontend build outstanding” conclusion conflicts with its successful build log; its screenshot paths also differ from the later tree. Students must reconcile these on their documentation branch. No history or branch was changed here.

## Selected workflows

| Attribute | W1 — employee submits leave | W2 — manager decides leave |
|---|---|---|
| Actor / authentication | Active user authenticated by DRF token; selected actor is employee | Authenticated manager; admin variants retained because the same handler implements them |
| Starting conditions | Synthetic user exists; valid dates; no active overlap; balance preferably present with known allowance and approved history | The **same request primary key** returned by W1 exists, is visible to the manager, belongs to another user and is pending |
| Starting balance | Read actual allowance and approved requests; `available = allowance − sum(approved business_days)`; 26 is a default, not a universal starting balance | Re-read the request employee's calculated balance for assertions; the handler itself does not check it |
| Browser event | New request opens the modal; select type, dates, optional note; submit | Open Overview recent rows or Requests; choose approve or reject on a pending row |
| HTTP event | `POST /api/requests/` | `POST /api/requests/{request_id}/decision/` with `status=approved` or `rejected` |
| Domain constraints | Date order, inclusive overlap, weekday count, optional balance check, serializer field constraints | Role, scoped lookup, not self, pending-only, accepted decision value |
| Persistent changes | Insert one `LeaveRequest` owned by caller, initially pending | Update that row's status, `decided_by`, `decided_at`; retain its ID and employee |
| Success | 201 with serialized request; modal closes, clears and refreshes data | 200 with same ID and final status; refresh removes pending buttons |
| Rejections | Invalid fields/date order/overlap/insufficient existing balance: 400; missing/invalid token: 401 | 401 unauthenticated; 403 role/self; 400 decision value; 404 invisible/missing request; 409 already decided |
| Balance effect | No reservation, no `LeaveBalance` write | Approval increases derived used days and reduces available; rejection leaves derived balance unchanged; no `LeaveBalance` write |

Required W1 dates are `start_date` and `end_date`. `leave_type` is optional at API level (defaults to vacation), although the UI always supplies a selected type; allowed values are vacation, permit and personal. Note is optional, blank allowed, up to 280 characters after serializer trimming. Count Monday–Friday inclusively; no holidays, half-days, future-only rule, annual-date restriction or positive-day minimum exists. Weekend-only zero-day requests are accepted if other checks pass. A missing balance **bypasses** submission balance validation. A balance's year is not used to filter approved requests.

## Permissions and shared state

| Action | Employee | Manager | Admin |
|---|---|---|---|
| Submit own request | Yes | Yes (no employee-only server restriction) | Yes |
| List requests | Own | Own team if assigned; otherwise own only | All |
| Decide another user's request | No, 403 | Own team, pending only | Any team, pending only |
| Decide own request | No | No, 403 even though buttons may appear | No, 403 |
| Read own dashboard | Yes | Yes, counts/recent reflect team visibility | Yes, counts/recent reflect all visibility |
| Read People / team API | Own team's members | Own team's members | Own team's members, not all teams |

Employees also read colleagues' balances and upcoming approved dates through `/api/team/`; do not describe this endpoint as manager-only. A manager without a team can see only their own requests and cannot decide those. UI visibility never establishes authorization.

The cross-workflow identity is `LeaveRequest.id=k`. W1 writes `employee_id=e`, pending status and dates; W2 loads and updates `k`, never creates a replacement request. `User.team_id` controls manager lookup; `LeaveRequest.decided_by_id` references the decision maker. `LeaveBalance.user_id=e` is one-to-one with the employee, not directly foreign-keyed by the request. `approved_days` queries approved requests for `e` across all dates/types; `available_days` derives from that total. W2 approval therefore changes the value W1 subsequently reads without modifying the allowance row. Database tables are `leave_leaverequest`, `leave_leavebalance`, `leave_user`, `leave_team`; token authentication also uses `authtoken_token`.

## Source boundaries and dependencies

| Included boundary | Exact responsibility |
|---|---|
| `backend/leave/models.py:15–90` | Roles, display names, ownership, balances, weekday/date/overlap rules |
| `backend/leave/serializers.py:7–42` | Nested response identity, field constraints, W1 validation and creation |
| `backend/leave/views.py:31–132` | Login/me, request visibility, submission, decision, dashboard, team; all support calls retained |
| `backend/leave/events.py:18–63` | Directly called event builder, optional publication and nested after-commit callback including failure handling |
| `backend/leave/urls.py:5–12`; `backend/config/urls.py:22–26` | All six API paths; requests supports two methods |
| `backend/config/settings.py:81–98,123–151` | SQLite/PostgreSQL, application timezone, token/authenticated defaults, CORS and Redis switch |
| `frontend/src/App.vue:13–43,70–123` | State-driven Overview, Requests, People, request modal, refresh and decision actions |
| `frontend/src/RequestRow.vue:13–24`; `frontend/src/api.ts:3–18` | Row actions and token-bearing HTTP calls |
| `frontend/src/types.ts:1–5`; `frontend/src/BalanceGauge.vue:4–18`; `frontend/src/i18n.ts:225–272` | Response/display contracts, balance clamping, localization |
| `backend/leave/migrations/0001_initial.py:19–81`; `backend/leave/management/commands/seed_demo.py:7–29` | Persistence and setup analysis; not production-path coverage |
| `backend/leave/tests.py:11–108` | Nine upstream tests inspected as context; no student credit |

No Vue Router exists in the inspected frontend: `frontend/src/main.ts:1–4` mounts App, and `active` selects screens. The modal has no separate browser route. Read [WORKFLOW-TRACE.md](WORKFLOW-TRACE.md) for full calls and [COVERAGE-BOUNDARY.md](COVERAGE-BOUNDARY.md) for every included server function.

Exclude Django Admin CRUD, user/team provisioning, health probes, Kubernetes/deployment administration, notification worker/gateway internal algorithms and future features (holidays, cancellation, delegation, exports, SSO). These are not either actor goal. **Include** event production/failure paths, auth, dashboard and team helpers because the selected UI actually calls them. Notification feed/SSE presentation is an external service dependency, not an extra selected workflow; its independent endpoints are mapped in WORKFLOW-TRACE. Any broader instructor interpretation of “all server-side business logic” needs approval of this proposed boundary, not silent exclusion of those services.

Dependencies include Django/DRF authentication and serializer behavior, SQLite or PostgreSQL transaction semantics, browser localStorage and fetch, Vue's refresh of three APIs, optional Redis, and downstream notification services. Server business dates use Europe/Rome; seed uses machine `date.today()`; reports use Asia/Karachi. Test fixtures must fix dates explicitly rather than rely on these clocks. Requirements pins are in `requirements.txt`; preserve npm locks. Python 3.12.7 was confirmed in the supplied environment; compatibility/support review belongs to the later toolchain plan (upstream CI requests Python 3.13). Do not claim local success proves vendor support.

## Setup, seed and reset basis (instructions only)

No commands in this section were run in Phase 1. Existing environment is already installed. For a **new disposable** WSL demo only, the source-backed setup sequence from the repository root is:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py seed_demo
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
# A separate terminal, from the repository root:
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Use a Python interpreter compatible with the pinned dependencies; record its exact version. Open `http://127.0.0.1:5173`; API base defaults to `http://localhost:8000/api` (override `VITE_API_URL` if needed). Demo-only profiles and credentials are documented in README; do not use real personnel data. Omit `REDIS_URL` for core workflow checks, or run the README's full Compose topology when notification integration is required. Existing tests: `.venv/bin/python backend/manage.py test leave`; frontend build: `cd frontend` then `npm run build`.

**Reset limitation:** README's `seed_demo` claim is weaker than a full reset. Lines 17–23 overwrite four users' profile/password/balance data; line 25 deletes **all** leave requests, retains other users/teams/tokens, does not reset sequences, and lines 25–28 choose relative dates. No full deterministic reset command exists at the baseline. Do not run it against the current database. Later reset design: disposable database per run; migrate it, load a reviewed fixed-date synthetic fixture with stable relationships, create fresh tokens, assert initial counts/status/balances, run both workflows on the returned request ID, then discard only that disposable database. Repeat twice and compare states. Implementation and proof are future work; the precise isolated configuration/fixture remains to be supplied. Do not advertise reset acceptance as complete.

Future student tests belong in a separate `tests/team/` hierarchy, with distinct unit/API/browser areas and discovery configuration documented when implemented. Do not edit or relabel `backend/leave/tests.py` as team work. No test suite is created by Phase 1.

## Assignment Section 1 mapping

| Requirement (assignment page 1) | Phase 1 evidence / outstanding action |
|---|---|
| Existing open-source web MIS, source/API/browser/persistence | Identity above; source trace and migrations; historical baseline report; no new browser execution |
| Two workflows, initial condition/action/outcome | W1/W2 table above |
| Shared record/value | Request `k` and employee's derived allowance above |
| URL, licence, exact commit | Identity above, locally verified |
| At least eight FRs, at least three per workflow | 12 FRs: six per workflow in FUNCTIONAL-REQUIREMENTS |
| Four rules including boundary, Boolean, state; two roles | Six BRs in BUSINESS-RULES; employee/manager matrix above (admin variants preserved) |
| Justified expected outcomes | TEST-BASIS with source evidence and explicitly proposed defect oracle |
| Baseline saved in Git | Existing pinned commit verified; team owns history operations |
| Setup/start/seed/reset instructions | Commands and reset gap above; deterministic reset acceptance outstanding |
| Register in section Google Sheet within five days | Student-owned action; announcement date and registration unverified |
| Own tests separate; upstream tests earn no marks | Planned `tests/team/`; no credit claimed |

## Open decisions for the students/instructor

1. Confirm registration, three member identities and area ownership; none inferred.
2. Confirm the scope interpretation of assignment page 2's **all server-side business logic**, including notification-service exclusion and whether the critical module may be serializer validation as proposed.
3. Approve a desired policy for approval-time insufficiency (error code, atomicity and unchanged persisted state). The code currently allows it. Also decide missing balance, year/type accounting and zero-day policy before changing requirements.
4. Confirm whether six actor goals in this narrow module meet the use-case rubric; three distinct goals are strong, the other three are supporting/overlapping goals (see WORKFLOW-TRACE). Do not expand the MIS or invent screens without review.
5. Reconcile absent baseline documents, stale conclusions and screenshot filenames using the team's own history workflow. Verify automated browser smoke and deterministic reset later.
6. Supply a reviewed OpenAPI contract, including manual decision/login schemas and cross-field rules. No schema endpoint/spec exists here; default inference is incomplete.

Later work must still deliver test management (including ≥8 product/≥2 project risks), SonarQube/CFG, full scoped statement/branch coverage, MCC/MC/DC, API generation, Playwright flows, mutations, CI gates, accessibility, passive security, k6/recovery and final reports. Pages 2–7 of the assignment were read to keep these foundations compatible, not implemented now. All student review, staging, commits, pushes, PRs and issues remain student-owned. AI assistance is disclosed in [AI-USE-RECORD.md](../AI-USE-RECORD.md).
