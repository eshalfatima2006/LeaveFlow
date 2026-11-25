# Use-case specifications (v0.2, PROPOSED)

Version 0.2 — 24 November 2026. Supersedes the Phase 1 candidate table in [WORKFLOW-TRACE.md](WORKFLOW-TRACE.md) (historical record retained there). Method: SE3002 Lecture 16 (use case = actor achieving a goal; main, alternative and exception flows; preconditions and postconditions become test checks; one test per flow; `<<include>>` for shared steps, `<<extend>>` for optional behaviour; coverage = flows tested ÷ flows specified).

## Status and approval

- **This catalog is a PROPOSED baseline.** It has not been approved by the instructor.
- **Approval dependencies:**
  - **D-1:** whether the README-documented Django Admin screens count as MIS user interface. This decides UC-08 and UC-09.
  - **D-2:** whether the notification services count as secondary actors in browser scope. This decides UC-07.
- **Core workflows (unchanged):**
  - **W1:** an employee submits a leave request.
  - **W2:** a manager or administrator decides the **same persisted request** (same primary key).
- **Requirements (unchanged):** the original FR-W1-01…06, FR-W2-01…06 and BR-01…06 keep their meaning. Supporting requirements FR-ADM-01, FR-ADM-02 and FR-NOTIF-01 are PROPOSED ([FUNCTIONAL-REQUIREMENTS.md](FUNCTIONAL-REQUIREMENTS.md#supporting-requirements-proposed)).

**Evidence labels:**
- **[O]** observed in an executed browser run;
- **[X]** asserted by an executed automated test;
- **[S]** derived from source code (not yet observed);
- **[P]** predicted, which must be observed before it becomes an expected result.

**Flow status vocabulary:**
- **Specified:** written here.
- **Automated:** a committed test exists.
- **Executed/passed:** recorded in run evidence.

## Catalog and ownership (proposed)

| UC | Actor goal | Owner | Workflow link | Flows specified | Automated | Passed (evidence) | Scope status |
|---|---|---|---|---|---|---|---|
| UC-01 | Employee submits a leave request | Member 1 | W1 | 5 | 5 | 5 ([b1/run-1](../evidence/browser/b1/run-1/flow-coverage.md), [run-2](../evidence/browser/b1/run-2/flow-coverage.md), [committed-source re-run](../evidence/browser/b1-provenance-2026-11-24/flow-coverage.md)) | In scope |
| UC-02 | Manager/admin decides a pending request (approve or reject) | Member 2 | W2 | 5 (+1 blocked objective) | 5 | 5 (same runs) | In scope |
| UC-04 | Employee reviews own leave record and remaining entitlement | Member 3 | W1/W2 outcome (read-only) | 5 | 5 | 5 | In scope |
| UC-07 | Recipient receives leave notifications | Member 3 | W1/W2 events | 5 | 5 | 5 | **Conditional on D-2** |
| UC-08 | Administrator maintains employee leave entitlement | Member 3 | Input to W1 balance rule | 5 | 5 | 5 | **Conditional on D-1** |
| UC-09 | Administrator changes an employee's approving team | Member 3 | Input to W2 authorization | 5 | 5 | 5 | **Conditional on D-1** |

**Mandatory flow coverage:** 10 of 30 executed and passed (33.3%). Counting rules:
- **The 30 mandatory flows** (6 × 5) are the only denominator.
- **OBJ-UC02-01** is a blocked regression objective. It joins the denominator (making 31) only if the approval-time error contract is approved and it is then specified as a UC-02 exception.
- **Included use cases** (INC-01, INC-02) are tested once and reported separately (Lecture 16 p16).
- **Reported separately, never counted:** supplementary checks (SUP-*), characterisations and observations (OBS-*).

The machine-readable registry is [`tests/team/browser/flows.json`](../../../tests/team/browser/flows.json).

## Included use cases (`<<include>>`)

### INC-01 — Sign in to LeaveFlow (single-page app)

- **Actors:** any user (primary); Django token authentication (secondary).
- **Main flow:**
  1. Open the app.
  2. Enter username and password.
  3. Choose "Enter the dashboard".
  4. `POST /api/auth/login/` → 200 with a token.
  5. Main navigation shown.
- **Alternatives:**
  - **A1 (at 1):** a stored token restores the session through `GET /api/me/` (`App.vue:38`).
- **Exceptions:**
  - **E1 (at 4):** wrong credentials → 400 `Credenziali non valide.` shown in the login card [X API-W1-001.02].
  - **E2 (at A1):** stored token no longer valid → 401 → token cleared → login screen [S `App.vue:38`; P].
- **Tests:**
  - **API level:** API-W1-001.01–04 ([X], A2.1).
  - **Browser:** every UC-01/UC-02 test signs in through this flow ([X] B1). A dedicated INC-01 browser test is planned (owner Member 3).

### INC-02 — Administrator signs in to Django Admin

- **Main flow:** a staff user signs in at `/admin/` and gets a session.
- **Exception:** a non-staff user is refused with Django's staff-account message [S; P].
- **Tests:** planned with UC-08/UC-09 (owners Member 1 and Member 3). Conditional on D-1.

---

## UC-01 — Submit leave request

| Field | Specification |
|---|---|
| Primary / secondary actors | Employee / — (with Redis configured, the notification system receives `leave.requested`; outside UC-01 assertions) |
| Objective | Obtain a recorded, pending leave request for chosen dates |
| Trigger | "New request" (header) |
| Preconditions | INC-01 done; employee E has a LeaveBalance with allowance A (test data A = 5) and no approved history; E has its own pending request P 2027-03-15..19 |
| Requirements / rules | FR-W1-01…06; BR-01, BR-02, BR-03, BR-04, BR-05, BR-06 |
| Owner / status | Member 1 / **5 of 5 automated and passed** ([uc01-submit-leave.spec.ts](../../../tests/team/browser/specs/uc01-submit-leave.spec.ts)) |

**Main flow (TC-UC01-M):**
1. E opens the request form.
2. E selects type Vacation.
3. E enters From 2027-03-01 and To 2027-03-05.
4. The system shows the working-day preview "5 working days" [X].
5. E optionally enters a note.
6. E submits.
7. The server validates date order, overlap and balance, then creates the request: `POST /api/requests/` → 201 with id k, `pending`, `business_days` 5 [X].
8. The form closes, and Requests shows k as Pending, "Vacation · 5 days" [X].

**Alternative flows:**
- **A1 — revise dates after the preview (TC-UC01-A1).** Branches at step 4: the preview for Fri 03-05 → Tue 03-09 shows 3 working days. E changes To to Mon 03-08, the preview shows 2, and the flow rejoins at step 5. The persisted `end_date` is 2027-03-08 with D = 2, i.e. the revised values reach the record [X].
- **A2 — abandon before submitting (TC-UC01-A2).** Branches at steps 2–5: E closes the form, and the use case ends without its goal. There is no `POST /api/requests/` and the row set is unchanged [X]. Observation OBS-UC01-01 [O]: reopening the form shows the abandoned values.

**Exception flows:**
- **E1 — active overlap (TC-UC01-E1).** Branches at step 7: dates 2027-03-19..19 (P's last day, an inclusive overlap) → 400. The form stays open showing `Esiste già una richiesta sovrapposta.` and no row is created [X]. E changes the dates to 2027-03-22 and rejoins at step 6 → 201 [X].
- **E2 — requested days exceed remaining entitlement (TC-UC01-E2).** Branches at step 7: 2027-04-05..04-12 (D = 6 = A+1) → 400 with `Saldo ferie insufficiente.` and no row [X]. E shortens to 04-09 (D = 5) and rejoins at step 6 → 201 [X].

**Postconditions:**
- **Success:** exactly one new request k, owner E, status pending, D = inclusive weekdays, `decided_by`/`decided_at` null. Allowance unchanged and available unchanged: pending reserves nothing, which is a characterisation of GAP-01 [X].
- **Failure:** the row set is unchanged.

**Data (EP/BVA):** D = A (accepted) and D = A + 1 (rejected); P's last day (blocked) and the next weekday (allowed); revised end date. Type and note variants are EP data covered at API level (API-W1-002.*), not separate flows.

**Evidence:** Playwright HTML report and `results.json`, end-state screenshot, database readback JSON per test, development-database metadata before and after.

**Limitations:**
- Server messages are Italian in the English UI.
- The insufficient-balance message doesn't say how many days remain.

---

## UC-02 — Decide pending leave request

| Field | Specification |
|---|---|
| Primary / secondary actors | Team manager (administrator as the per-actor repeat, Lecture 16 p17) / the affected employee; the notification system (UC-07) |
| Objective | Bring a pending request to a decided state: approved (main) or rejected (alternative end) |
| Trigger | "Approve" or "Reject" on a pending row |
| Preconditions | INC-01 done. Pending k was created by the employee **through the real W1 API**, is visible to the actor and is not the actor's own. Test data: employee allowance 3, k 2027-05-03..05 (D = 3); a team-B request b; the manager's own pending request s |
| Requirements / rules | FR-W2-01…06; BR-02, BR-03, BR-04, BR-05, BR-06 |
| Owner / status | Member 2 / **5 of 5 automated and passed** ([uc02-decide-leave.spec.ts](../../../tests/team/browser/specs/uc02-decide-leave.spec.ts)); OBJ-UC02-01 registered as blocked (`fixme`) |

**Main flow (TC-UC02-M):**
1. The manager opens Requests.
2. The manager selects the Pending filter.
3. The manager locates k.
4. The manager chooses Approve.
5. The server checks role → decision value → visibility → not self → pending, then sets `approved`, `decided_by` and `decided_at` on the same row: `POST /api/requests/k/decision/` → 200 [X].
6. Row k shows Approved with no actions, and the employee's People card reads 0 / 3 days [X].

**Alternative flows:**
- **A1 — reject (TC-UC02-A1).** Branches at step 4: Reject → 200, `rejected`, the employee's availability is unchanged and the "Rejected" filter appears. Postcondition: the same dates can be submitted again as a new request ≠ k (BR-02) [X].
- **A2 — administrator decides another team's request (TC-UC02-A2).** Branches at step 1: the actor is an admin and the target is team B's request → 200 with `decided_by` = admin [X].

**Exception flows:**
- **E1 — already decided by another approver (TC-UC02-E1).** Branches at step 5: the admin rejected k after the page loaded → 409 `La richiesta è già stata decisa.` The first decision is preserved exactly [X], and after a reload the row shows Rejected [X]. Observed UI [O] (OBS-UC02-01): no message is shown, the row still says Pending with its actions until reload, and the console logs the unhandled error.
- **E2 — own request (TC-UC02-E2).** Branches at step 4: the Approve button is offered on the manager's own pending request [X] (GAP-04) → 403 `Non puoi decidere una tua richiesta.` and the row is unchanged [X]. Observed UI [O]: no message is shown.

**Blocked regression objective OBJ-UC02-01.** An approval with D > available should be refused atomically. The baseline approves it (GAP-01, PR-01). It stays blocked until the approval-time error contract is approved. Outside the 30.

**Postconditions:** the same k reaches a final state, audit fields are set once, and the employee's derived availability falls by D only on approval. After 409 or 403, nothing changes.

**Data:** D = available (boundary accepted); team A versus team B; own versus other's request.

**Evidence:** as UC-01, plus attached UI-feedback observations for E1 and E2.

**Open policy:** whether "a visible error message" becomes part of the E1/E2 expected result. That is a team oracle decision; if adopted, those tests will fail before a UI fix.

---

## UC-04 — Review own leave record and remaining entitlement (read-only)

| Field | Specification |
|---|---|
| Primary / secondary actors | Employee / — |
| Objective | Find out the outcome of one's own requests and how much entitlement remains (a pull goal; Lecture 16 p6 "Track delivery", p56 "checks exam schedule") |
| Trigger | Signing in or opening Overview or Requests |
| Preconditions | INC-01 done. E has k1 approved (D = 3), k2 rejected and k3 pending, all created through the real W1/W2 APIs; allowance A = 10; a teammate has requests of their own |
| Requirements / rules | FR-W2-01 (employee sees own records only), FR-W1-05, FR-W1-06, FR-W2-05, FR-W2-06; BR-03, BR-04 |
| Owner / status | Member 3 / **5 of 5 automated and passed** ([Area 3 evidence](../testing/AREA3-RESULTS.md)) |

**Main flow (TC-UC04-M):**
1. Overview shows available 7, used 3 of 10, and counts pending 1 / approved 1 / total 3 [S].
2. E opens Requests.
3. Each own request shows its correct status badge, and no teammate rows appear [S].

**Alternative flows:**
- **A1 — filter by outcome (`<<extend>>`) (TC-UC04-A1).** Branches at step 3: the Approved, Rejected and Pending filters show exactly k1, k2 and k3. The Rejected filter exists only because k2 exists (`App.vue:107`) [S].
- **A2 — outcome changes during the journey (TC-UC04-A2).** Branches after step 3: an approver decides k3 while the page is open. The view stays stale because data is refreshed only on boot, login, submit or decide (`App.vue:37–42`) [S]. E reloads and rejoins at step 1 with the new status and availability [P].

**Exception flows:**
- **E1 — session no longer valid (TC-UC04-E1).** At entry: the token is revoked server-side and the page reloads → `GET /api/me/` 401 → login screen with the stored token removed [S `App.vue:38`; P]. This is an included-step failure, endorsed for lookup use cases by Lecture 16 p56.
- **E2 — the requests service fails while loading (TC-UC04-E2).** At steps 1–2: `/api/requests/` returns 500 (route interception). The **expected result is undecided** (TEST-BASIS GAP-15). The source predicts [P] an empty Overview and a misleading "No requests found." with no error. A runtime probe is required, then a team oracle decision.

**Postconditions (safe state):** displayed values equal the derived database state, and **zero writes**: the request row snapshot is identical before and after.

**Characterisation (not counted):** an employee without a LeaveBalance sees 0 / 0 (GAP-07).

**Limitations:** UC-04 is the weakest single-page use case because both exceptions are infrastructure or session related.

---

## UC-07 — Receive leave notifications (CONDITIONAL on D-2)

| Field | Specification |
|---|---|
| Primary / secondary actors | Recipient (employee for decisions; team manager or admin for new requests) / Redis stream `leaveflow:events`, Elixir worker (consumer group `leaveflow-notifications`), Node gateway (`/notifications`, `/events`), the triggering actor |
| Objective | Be informed in the app, without searching, when a leave event concerns the recipient (push; distinct from UC-02's decision and UC-04's pull) |
| Trigger | A W1 submission or W2 decision commits |
| Preconditions | An **isolated notification environment** exists (see [TEST-PLAN.md](../planning/TEST-PLAN.md#isolated-notification-environment-uc-07)). The recipient is signed in. A decision event for k is produced by the triggering actor through the API |
| Requirements / rules | FR-NOTIF-01 (PROPOSED), FR-W1-06, FR-W2-05, FR-W2-06; BR-04, BR-05 |
| Owner / status | Member 3 / **5 of 5 automated and passed** ([Area 3 evidence](../testing/AREA3-RESULTS.md)) |

**Main flow (TC-UC07-M):**
1. The triggering manager approves k.
2. Django appends `leave.approved` to the stream after commit (`events.py:49–63`).
3. The worker stores one feed item `<event-id>:<employee-id>` (dedup key `leaveflow:notification:seen:<id>`, 7 days) and acknowledges the entry (`worker.ex`, `store.ex`).
4. The gateway pushes the item over server-sent events.
5. The employee's bell count increases without a reload, and the panel shows "Request approved" with the actor and dates [S].

**Alternative flows:**
- **A1 — new-request alert (TC-UC07-A1).** Branches at step 1: the employee submits → the team's managers and the admins receive "New request to review"; the requester and other-team managers receive nothing (`events.py:19–27`) [S].
- **A2 — recipient offline (TC-UC07-A2).** Branches at step 4: the recipient is signed out. At the next sign-in the panel lists the stored item from `GET /notifications` [S].

**Exception flows:**
- **E1 — gateway unavailable (TC-UC07-E1).** At step 4: the panel shows "The notification service is unavailable." and leave operations still work (`NotificationCenter.vue:32–50`) [S]. An outage that starts mid-session is silent (`notifications.ts:49`) [S; P].
- **E2 — event publication fails (TC-UC07-E2).** At step 2: Redis is unreachable during the decision. The decision persists (200), the failure is logged, and no feed item is ever created (`events.py:57–61`, GAP-14) [S].

**Postconditions:**
- exactly one feed item for k per recipient;
- `XPENDING` = 0 for the group;
- nothing for non-recipients;
- leave data unaffected by notification failures.

**Supplementary SUP-UC07-01:** a duplicate delivery of the same event still leaves one feed item.

**Limitations:**
- Recipients are fixed when the event is produced (GAP-08, GAP-11).
- The worker never reclaims an event it rejected (an error-guessing finding).

---

## UC-08 — Maintain employee leave entitlement (CONDITIONAL on D-1)

| Field | Specification |
|---|---|
| Primary / secondary actors | Administrator, a staff user (INC-02) / the affected employee |
| Objective | Set the entitlement that W1's balance rule checks against (the only UI that writes LeaveBalance A) |
| Trigger | Opening Django Admin "Leave balances" |
| Preconditions | Staff admin X; employee E with allowance 10; employee E_nb without a balance |
| Requirements / rules | FR-ADM-01 (PROPOSED), FR-W1-05; BR-03 |
| Owner / status | Member 3 / **5 of 5 automated and passed** ([Area 3 evidence](../testing/AREA3-RESULTS.md)) |

**Main flow (TC-UC08-M):**
1. X opens Leave balances.
2. X selects E's balance. Observation OBS-UC08-01 [P]: rows are labelled "LeaveBalance object (n)" because the model has no `__str__` and no `list_display`, so finding E needs browser verification.
3. X sets allowance 12.
4. X saves.
5. Django shows its success message [P exact text].
6. E's Overview shows "/ 12", and W1 checks against A = 12 [S].

**Alternative flows:**
- **A1 — create a missing entitlement (TC-UC08-A1).** Branches at step 2: Add a balance for E_nb with allowance 5. E_nb's 6-day request is then refused (GAP-07 closes for that user) [S].
- **A2 — reduce below approved use (TC-UC08-A2, characterisation).** Branches at step 3: allowance 2 with 3 approved days is saved without warning, and available becomes −1 [S]. The desired policy is undecided (GAP-05, BR-03).

**Exception flows:**
- **E1 — invalid entitlement value (TC-UC08-E1).** Branches at step 4: −1 → `Assicurati che questo valore sia maggiore o uguale a 0.`; empty → `Questo campo è obbligatorio.`; 0 accepted. The upper bound depends on the engine: 32767 on PostgreSQL, 2^63−1 on SQLite (Django `integer_field_range`) [S]. On error nothing is written.
- **E2 — duplicate entitlement (TC-UC08-E2).** Branches at step 2: Add a second balance for E → a uniqueness error and an unchanged count [S; P exact text].

**Postconditions:** the allowance changed (success) or is unchanged (error); W1 and the dashboards use the stored value.

**Data:** −1 / 0 / 1 and the engine-dependent maximum boundary.

**Limitations:** the admin forms are Italian (`LANGUAGE_CODE=it-it`). Django Admin can also edit `LeaveRequest.status` directly (GAP-12); that is out of scope for this use case.

---

## UC-09 — Change an employee's approving team (CONDITIONAL on D-1)

| Field | Specification |
|---|---|
| Primary / secondary actors | Administrator (INC-02) / the former and new team managers |
| Objective | Make a different manager responsible for an employee's leave decisions after an organisational change |
| Trigger | Editing the employee in Django Admin "Users" (role and team fields, `admin.py:7–10`) |
| Preconditions | Teams T (manager M_T) and U (manager M_U); employee E in T with pending k; staff admin X |
| Requirements / rules | FR-ADM-02 (PROPOSED), FR-W2-01, FR-W2-02; BR-04 |
| Owner / status | Member 3 / **5 of 5 automated and passed** ([Area 3 evidence](../testing/AREA3-RESULTS.md)) |

**Main flow (TC-UC09-M):**
1. X opens Users.
2. X selects E.
3. X sets team U.
4. X saves.
5. Django shows its success message [P exact text].
6. M_U's Requests list includes k with decision buttons, and M_T's list no longer does. k is unchanged (same id, pending). Visibility is computed per request from the current team (`views.py:46–51`) [S].

**Alternative flows:**
- **A1 — grant decision authority by role (TC-UC09-A1).** Branches at step 3: user P in team U changes from employee to manager, and P then sees team U's requests with decision buttons [S].
- **A2 — remove the employee from every team (TC-UC09-A2, characterisation).** Branches at step 3: E's team is blank, so only admins can see and decide k, with no warning [S].

**Exception flows:**
- **E1 — target team removed while the form is open (TC-UC09-E1).** Branches at step 4: `Scegli un'opzione valida. La scelta effettuata non compare tra quelle disponibili.` and E's team is unchanged [S].
- **E2 — employee record removed while the form is open (TC-UC09-E2).** Branches at step 4: a redirect to the admin index with `user con ID "<id>" non esiste. Probabilmente è stato cancellato?`, and nothing is recreated (Django admin `_get_obj_does_not_exist_redirect`) [S].

**Supplementary SUP-UC09-01 (outside the 30):** M_T's page was open before the change. M_T's decision on k then returns 404 and k stays pending [S].

**Postconditions:** E's team or role changed; k unchanged; decision authority follows the current team.

**Limitations (weakest use case):**
- It is realised as a generic field edit with no hand-over semantics.
- There is no audit trail.
- The new approver gets no alert for inherited pending requests (GAP-11).

---

## Legacy ID mapping (never reuse retired IDs)

| Old ID (v0.1) | New ID | Disposition |
|---|---|---|
| E2E-UC01-01 | TC-UC01-M | Mapped |
| E2E-UC01-02 (permit/personal type) | — | Retired as a flow: input-data variant, covered as EP data (API-W1-002.01) |
| E2E-UC01-03 (omitted note, same weekday) | — | Retired as a flow: EP/BVA data (API-W1-002.02, 003.02) |
| E2E-UC01-04 / -05 | TC-UC01-E1 / TC-UC01-E2 | Mapped |
| E2E-UC02-01 | TC-UC02-M | Mapped |
| E2E-UC02-02 (approve via Overview) | — | Retired: navigation-only `<<extend>>` entry point |
| E2E-UC02-03 / -04 / -05 | TC-UC02-A2 / TC-UC02-E1 / TC-UC02-E2 | Mapped |
| UC-03 (reject leave) | UC-02 | Use case merged; rejection is UC-02's alternative end |
| E2E-UC03-01 | TC-UC02-A1 | Mapped |
| E2E-UC03-02 / -03 / -04 | — | Retired: navigation entry, data variant of TC-UC02-A2, same 409 guard as TC-UC02-E1 |
| E2E-UC03-05 (401 on decision) | INC-01 E2 (and API-W1-001.04) | Moved to the included use case |
| UC-04 (inspect balance) | UC-04 (review own record and entitlement) | Same ID, rescoped |
| E2E-UC04-01 / -04 / -05 | TC-UC04-M / TC-UC04-E2 / TC-UC04-E1 | Mapped |
| E2E-UC04-02 (sidebar balance) | — | Retired: navigation-only |
| E2E-UC04-03 (close modal) | TC-UC01-A2 | Moved to UC-01 |
| UC-05 and E2E-UC05-01…05 | — | Retired use case (locating work is a step of UC-02) |
| UC-06 and E2E-UC06-01…05 | — | Reserve only; inactive and not counted |
| — | TC-UC01-A1/A2, TC-UC04-A1/A2, TC-UC07-*, TC-UC08-*, TC-UC09-*, INC-01/02, OBJ-UC02-01, SUP-UC07-01, SUP-UC09-01, OBS-* | New in v0.2 |
