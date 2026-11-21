# Functional requirements

Baseline: `bada9a03ecec53ef6945827230e3594d825da87a`; analysis 21 November 2026. **12 independently verifiable requirements, six per workflow.** These specify implemented baseline behavior unless explicitly labelled desired. References are repository-relative baseline line ranges; pinned links and acceptance oracles are in [TEST-BASIS.md](TEST-BASIS.md). BR definitions and input classes are in [BUSINESS-RULES.md](BUSINESS-RULES.md). Applicable test levels are plans, not completed tests.

## FR-W1-01 — Authenticate and bind ownership

- **Statement:** The API shall require token authentication to submit a request and shall set its employee to the authenticated user, ignoring supplied read-only employee/status fields.
- **Actor / preconditions:** Employee with an active synthetic account and valid token for success; absent/invalid token for rejection.
- **Expected outcome:** Valid caller reaches validation; missing/invalid token receives 401. A successful record belongs to the caller and starts pending; no other user's ownership can be injected.
- **Rules:** BR-04, BR-05, BR-06.
- **Evidence:** `backend/config/settings.py:142–149`; `backend/leave/serializers.py:17–28,41–42`; `backend/leave/models.py:57–65`; `backend/leave/views.py:54–61`.
- **Test levels:** Unit (create binding), API/integration (real token, DB owner), browser (login then submit).
- **Ambiguity/defect note:** “Employee” is the selected actor, not an enforced role restriction: manager/admin may submit their own requests too.

## FR-W1-02 — Validate the submission payload

- **Statement:** The API shall require parseable start/end dates; accept only vacation, permit or personal if leave_type is provided; default omitted type to vacation; accept omitted/blank note; reject an overlength trimmed note (>280 characters).
- **Actor / preconditions:** Authenticated employee; no overlap and adequate balance to isolate field behavior.
- **Expected outcome:** Valid fields proceed to business validation and 201; missing/invalid required fields, null dates/type/note, invalid type or overlength note receive 400 without insertion.
- **Rules:** BR-06.
- **Evidence:** `backend/leave/models.py:47–61`; `backend/leave/serializers.py:16–28`; `frontend/src/App.vue:18,123`.
- **Test levels:** API generated EP/BVA; serializer unit; browser valid field entry and native required controls.
- **Ambiguity/defect note:** UI maxlength prevents ordinary typing of >280; API cases must bypass that control. Supplied read-only/unknown fields do not imply a strict reject-unknown contract. Exact installed field metadata was inspected without DB writes.

## FR-W1-03 — Validate order and calculate working days

- **Statement:** The system shall reject end before start and calculate business_days inclusively, counting Monday–Friday only.
- **Actor / preconditions:** Authenticated employee with field-valid dates, no overlap and adequate existing balance.
- **Expected outcome:** Reversed dates return 400 with end_date error; a Monday–Friday range reports 5; same weekday reports 1; weekend-only reports 0. No row on rejection.
- **Rules:** BR-01.
- **Evidence:** `backend/leave/models.py:70–82`; `backend/leave/serializers.py:30–38`; `frontend/src/App.vue:25–31,123`.
- **Test levels:** Unit loop/weekday branches, API date EP/BVA, browser preview/server-result comparison.
- **Ambiguity/defect note:** Past and cross-year dates are accepted; holidays/half-days and positive-day minimum are not implemented. Extremely large date spans and date.max overflow require later robustness investigation.

## FR-W1-04 — Reject active overlaps

- **Statement:** Submission shall reject any inclusive interval overlap with another pending or approved request owned by the caller; rejected requests and other employees' requests shall not block it.
- **Actor / preconditions:** Authenticated employee with a controlled existing request and otherwise valid payload.
- **Expected outcome:** Overlap returns 400 and creates no row; adjacent nonoverlapping dates, other employees' records and rejected-history-only overlaps may succeed.
- **Rules:** BR-02.
- **Evidence:** `backend/leave/models.py:83–90`; `backend/leave/serializers.py:31–35`; `backend/leave/tests.py:40–48` (upstream context).
- **Test levels:** Unit predicate cases, API EP/BVA and decision table, integration persisted-count checks, browser error/correction.
- **Ambiguity/defect note:** Calendar intervals overlap even on weekends. Query-then-insert is not a concurrent uniqueness guarantee; there is no idempotency key.

## FR-W1-05 — Enforce the implemented submission balance check

- **Statement:** When the caller has a LeaveBalance, submission shall reject business_days greater than its calculated available_days, and shall allow equality subject to other checks.
- **Actor / preconditions:** Authenticated employee, known allowance and approved history, ordered dates and no overlap.
- **Expected outcome:** D>A returns 400 without request/balance change; D≤A proceeds. Pending requests reserve no days. When no balance exists the baseline skips this check.
- **Rules:** BR-03, BR-01.
- **Evidence:** `backend/leave/serializers.py:36–39`; `backend/leave/models.py:29–43,70–78`.
- **Test levels:** Unit compound decision and MCC/MC/DC candidates; API numerical BVA; integration calculated totals.
- **Ambiguity/defect note:** Missing-balance acceptance and ignoring balance year/leave type need policy review. Approval-time checking is absent; this requirement does not pretend otherwise.

## FR-W1-06 — Persist and present a pending request

- **Statement:** After valid submission, the API shall insert one pending request and return its ID, caller, fields and business_days with 201; the UI shall close/reset the modal and refresh dashboard, request list and team.
- **Actor / preconditions:** Authenticated employee; field/date/overlap/balance checks pass; supporting reads available.
- **Expected outcome:** GET list contains returned ID k, unchanged allowance, derived used/available unchanged; client displays pending row. With Redis configured the server schedules leave.requested for after commit; without it no event publication occurs.
- **Rules:** BR-04, BR-05, BR-06.
- **Evidence:** `backend/leave/serializers.py:41–42`; `backend/leave/views.py:54–63`; `backend/leave/events.py:18–63`; `frontend/src/App.vue:37–41,99–108`; `frontend/src/api.ts:14–16`.
- **Test levels:** API/integration shared-record and event-hook checks; browser successful display; unit event failure paths.
- **Ambiguity/defect note:** UI success depends on three refresh calls; a refresh failure after insertion does not roll back the request. “One” means one successful invocation, not unconditional retry idempotency.

## FR-W2-01 — Discover visible requests

- **Statement:** Request listing shall return own records to employees, team records to managers with a team, own records to managers without a team, and all records to admins.
- **Actor / preconditions:** Authenticated role with seeded own, teammate and outsider requests.
- **Expected outcome:** GET /api/requests/ returns 200 and exactly the applicable set, including request k for its authorized team manager; dashboard recent/counts use the same visibility.
- **Rules:** BR-04.
- **Evidence:** `backend/leave/views.py:46–51,62–63,93–108`; `frontend/src/App.vue:19–20,37,99–108`.
- **Test levels:** Unit manager/team compound condition; API access matrix; browser pending filtering.
- **Ambiguity/defect note:** Filters are client-side over the returned list; no server status-filter query parameter is implemented. Dashboard balance remains the caller's own balance.

## FR-W2-02 — Authorize the decision actor and target

- **Statement:** Decision processing shall require manager/admin role, resolve the request within the actor's visible set, and forbid decisions on the actor's own request.
- **Actor / preconditions:** Authorized team manager or admin, valid decision value and existing pending k for success.
- **Expected outcome:** Employee receives 403; invisible/nonexistent k receives 404 after role/value guards; self-decision receives 403; authorized non-self target reaches the pending-state guard. No rejected action changes persisted state.
- **Rules:** BR-04.
- **Evidence:** `backend/leave/views.py:46–51,66–80`; `backend/config/settings.py:142–149`; `frontend/src/RequestRow.vue:21–23`.
- **Test levels:** Unit ordered guards; API access decisions and unchanged-state assertions; browser employee hidden controls/manager allowed action.
- **Ambiguity/defect note:** Manager/admin self-owned pending rows expose buttons despite server refusal. App.decide lacks catch/display handling, so a visible error banner is not promised.

## FR-W2-03 — Validate decision values

- **Statement:** The decision endpoint shall accept only status equal to approved or rejected and return 400 for other, absent or null values after role validation.
- **Actor / preconditions:** Manager/admin token; control other guards to isolate status.
- **Expected outcome:** Accepted values proceed; invalid status produces a detail response and no request/balance change.
- **Rules:** BR-06, BR-05.
- **Evidence:** `backend/leave/views.py:68–72`; `frontend/src/api.ts:17`; `frontend/src/RequestRow.vue:8,21–23`.
- **Test levels:** API categorical EP; unit guard outcomes; browser approve/reject actions.
- **Ambiguity/defect note:** This is a manual request.data.get guard, not a decision serializer. Extra keys are unused. Login/decision default schema inference is inaccurate.

## FR-W2-04 — Permit a decision only from pending

- **Statement:** Under an atomic transaction and selected-row lock, decision processing shall change only a pending request; subsequent decisions on approved/rejected k shall return 409.
- **Actor / preconditions:** Authorized non-self actor, visible k and valid status value.
- **Expected outcome:** Pending moves to approved or rejected; both final states reject either decision, preserving original status, actor, timestamp, request count and derived balance.
- **Rules:** BR-05.
- **Evidence:** `backend/leave/views.py:74–87`; `backend/leave/models.py:52–65`; `frontend/src/RequestRow.vue:21–24`.
- **Test levels:** Unit guards; API/integration full allowed/disallowed transition table and repeats; browser disappearance of controls.
- **Ambiguity/defect note:** No cancel/reopen/delete API exists. select_for_update protection differs between SQLite and PostgreSQL. No concurrency reproduction is claimed.

## FR-W2-05 — Persist approval and derive its balance effect

- **Statement:** Authorized approval of pending k shall update the same row to approved with the actor and timestamp and return 200; subsequent calculated used days shall include its business_days.
- **Actor / preconditions:** Manager/admin, visible non-self pending k, valid approved value.
- **Expected outcome:** ID, employee, dates/type/note and request count unchanged; decision fields populated; allowance row unchanged; employee available drops by D; manager response refreshes rows and team availability. Configured event is leave.approved for the employee after commit.
- **Rules:** BR-03, BR-04, BR-05.
- **Evidence:** `backend/leave/views.py:74–89,112–132`; `backend/leave/models.py:35–43`; `backend/leave/events.py:18–63`; `frontend/src/App.vue:37,42,108,115–116`.
- **Test levels:** API/integration cross-workflow readback and transaction/event checks; browser team balance; model unit total.
- **Ambiguity/defect note:** **Actual baseline:** approval can make available negative. **Desired, unimplemented:** reject approval when D exceeds remaining allowance, atomically preserving all state. Desired error code needs student/instructor confirmation; proposed failing test is in TEST-BASIS.

## FR-W2-06 — Persist rejection without charging allowance

- **Statement:** Authorized rejection of pending k shall update the same row to rejected with the actor and timestamp, return 200, and leave derived approved totals unchanged; UI shall refresh and show rejected status.
- **Actor / preconditions:** Manager/admin, visible non-self pending k, valid rejected value.
- **Expected outcome:** Same k and other original fields; no new request or allowance write; rejected row no longer blocks W1 overlap checks; configured leave.rejected targets employee after commit.
- **Rules:** BR-02, BR-03, BR-04, BR-05.
- **Evidence:** `backend/leave/views.py:74–89`; `backend/leave/models.py:35–43,83–90`; `backend/leave/events.py:18–63`; `frontend/src/App.vue:37,42,107–108`.
- **Test levels:** Unit and API/integration state/balance/overlap readback; browser rejected filter and row state.
- **Ambiguity/defect note:** No reason-for-rejection field or UI exists; do not invent one. Decision actor/time are stored but omitted from the response serializer, so verify them through ORM assertions later.
