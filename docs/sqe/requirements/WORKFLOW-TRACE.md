# Workflow and shared-record trace

Baseline `bada9a03ecec53ef6945827230e3594d825da87a`; 21 November 2026. All paths/ranges below refer to that baseline. These are static traces, not execution transcripts. Pinned source links are in [TEST-BASIS.md](TEST-BASIS.md); actors and scope decisions are in [SCOPE.md](SCOPE.md).

## Browser and endpoint map

`frontend/src/main.ts:1–4` mounts `App.vue`. There are no separate route files or Vue Router dependency. The `active` ref (`App.vue:15`) switches Overview, Requests and People. `formOpen` displays a single modal; switching screens does not change an application route.

| Browser screen/action | Client source | HTTP route / DRF view | Persistence / response |
|---|---|---|---|
| Login submit | App:39,56–64; api.ts:12 | POST /api/auth/login/ →login_view, views:31–38; AllowAny | Django authenticate reads user; Token.get_or_create; 200 token/user or 400 credentials |
| Boot with stored token | App:38,43; api.ts:4,14 | GET /api/me/ →me_view, views:41–43 | Read authenticated user/team; 200 identity; authentication failure 401; boot catch clears token |
| Overview and any refresh | App:37,89–99; api.ts:14 | GET /api/dashboard/ →dashboard_view, views:92–108 | Own balance plus visible requests counts/recent; 200 |
| Requests screen / recent rows | App:99–108; api.ts:14 | GET /api/requests/ →requests_view GET, views:62–63 | visible_requests →request rows plus nested employee/team and derived weekdays; 200 |
| People and any refresh | App:37,110–118; api.ts:15 | GET /api/team/ →team_view, views:111–132 | Own-team users/balances/upcoming approved leave; 200 array (empty if no team) |
| New request modal submit | App:41,82,87,91,123; api.ts:16 | POST /api/requests/ →requests_view POST, views:54–61 | Validate/create pending row; 201 serialized record |
| Approve/reject row | RequestRow:21–23; App:42; api.ts:17 | POST /api/requests/{request_id}/decision/ →decide_request, views:66–89 | Atomic existing-row decision; 200 serialized same record |

All protected API routes inherit TokenAuthentication/IsAuthenticated (`backend/config/settings.py:142–149`). Prefix resolution is `backend/config/urls.py:25` →`backend/leave/urls.py:5–12`. HTTP methods outside decorators return 405 after applicable framework checks. No selected detail GET, PUT/PATCH, cancel, delete, status-query filter or pagination operation exists.

## W1 — success call chain

| Step | Function/screen and exact source | Validation / reads / writes | Result passed onward |
|---|---|---|---|
| 1 | App.vue:18,25–31,123, `submit`:41 | Required date controls, enum select, maxlength note; preview skips weekends; no client overlap/balance check | `{leave_type,start_date,end_date,note}` |
| 2 | api.ts `createRequest`:16 →`call`:5–9 | fetch JSON, Authorization Token header if stored; non-OK throws flattened detail/field error | POST /api/requests/ |
| 3 | config urls:25 →leave urls:10; settings:142–149; views `requests_view`:54–58 | DRF auth/permission and parsing; POST path instantiates LeaveRequestSerializer with caller context | serializer.is_valid(raise_exception=True) |
| 4 | serializers.py:16–28, `validate`:30–35 | Model-derived required dates, enum, note length/null/blank/read-only constraints; build **unsaved** candidate with employee=caller | `LeaveRequest.clean()` |
| 5 | models.py `clean`:80–90 | Date order; SELECT same employee AND pending/approved AND interval intersection, exclude candidate pk; exists() | Field/nonfield ValidationError or valid candidate |
| 6 | serializers.py:36–39 →models.py `business_days`:70–78 / `available_days`:42–43 / `approved_days`:35–39 | Optional employee.leave_balance read; candidate inclusive weekdays; SELECT all employee approved requests and sum each weekday count; compare D>A only if balance exists | Validated attrs or insufficient-balance error |
| 7 | views.py:59 →serializer `create`:41–42 | INSERT leave_leaverequest with employee_id=caller; model defaults pending/type; timestamps created_at; decided_by/at null | Persisted item k; no LeaveBalance UPDATE |
| 8 | views.py:60 →events.py `publish_leave_event`:49–63 →`build_leave_event`:18–46 | No Redis URL: return. Else SELECT admins or matching-team managers excluding employee; build UUID/type/time/actor/request payload; on_commit registers callback; xadd uses stream leaveflow:events | In normal W1 autocommit, callback runs immediately after already committed insert. Redis exception caught/logged |
| 9 | views.py:61 →LeaveRequestSerializer.data; UserSerializer /User.display_name | Read back object fields, nested employee/team, translated model labels and computed business_days | 201 JSON: id,employee,leave_type,leave_type_label,start_date,end_date,note,status,status_label,business_days,created_at |
| 10 | App.vue `submit`:41 →`refresh`:37 | Close modal/reset inputs then Promise.all dashboard/requests/team | New pending k in list; counts updated; no approved-day charge; a failed refresh can occur after successful insert |

Success does not require a balance row to exist under the baseline, and manager/admin can use the same form. The selected scenario deliberately supplies a known employee balance so later assertions are meaningful. No model.full_clean or overridden save is invoked; only explicit clean in serializer handles overlap/order.

## W1 — rejection and error paths

| Stage/source | Trigger | HTTP / persistent effect | Actual UI behavior |
|---|---|---|---|
| Token framework, settings:142–149 | Missing/invalid token | 401; no domain insert | api.call throws; submit catches and puts error in modal; boot failure logs out |
| Native required fields, App:123 | Date omitted in ordinary browser entry | Browser may block submit before HTTP | Native validity UI, not a server rejection result |
| Serializer fields, serializers:16–28 / models:47–61 | Missing/null/invalid dates/type; trimmed note >280 | 400 field errors, no insert | api.call flattens; submit keeps modal/input and displays error |
| model.clean:81–82 / serializer:34–35 | end<start | 400, end_date keyed error; no insert | Modal error; correction and resubmit available |
| model.clean:83–90 / serializer:34–35 | Pending/approved overlap | 400, nonfield error after message-list normalization; no insert | Modal error; choose nonoverlapping dates and resubmit |
| serializer:36–38 | Existing balance and D>A | 400 nonfield insufficient balance; no insert | Modal error; shorten interval and resubmit |
| event callback, events:57–61 | Redis publish exception | Caught/logged; inserted row remains; normal HTTP 201 | Core refresh can succeed; notification may be absent |
| App submit:41 / refresh:37 | Supporting GET/network failure after 201 | Request already committed; client throws during refresh | Error stored after modal was closed; no guaranteed visible modal banner; do not assert rollback |

Raw exception messages originate in Italian; changing frontend locale does not translate backend detail strings. Parsed field-error shape is normalized by DRF; no live malformed request evidence was created here.

## W2 — success call chain

| Step | Function/screen and exact source | Validation / reads / writes | Result passed onward |
|---|---|---|---|
| 1 | App.vue `refresh`:37 / `isManager`:19 / rows:99,108; RequestRow.vue:21–23 | GET list/dashboard visibility; manager/admin +pending shows actions, including self-owned rows | Emit `decide(k,'approved'|'rejected')` |
| 2 | App.vue `decide`:42 →api.ts:17 →`call`:5–9 | Token-bearing POST JSON `{status}` with row's original k in URL | config urls:25 /leave urls:11 resolve decide_request |
| 3 | views.py `decide_request`:68–72 | Manager/admin role check then decision-domain check | 403 or 400 early; otherwise transaction |
| 4 | views.py:74–78 →`visible_requests`:46–51 | `transaction.atomic`; SELECT FOR UPDATE request WHERE pk=k from admin/all or manager/team or fallback/own queryset | Locked persisted original row or404; no replacement row |
| 5 | views.py:79–82 | Compare employee_id to actor; then status==pending | Self403; final409; otherwise proceed. No serializer.validate/clean/balance check here |
| 6 | views.py:83–86 | Set status=decision, decided_by=actor, decided_at=timezone.now(); UPDATE only these three columns | Same k, employee, dates/type/note retained |
| 7 | views.py:87 →events.py:49–63 →`build_leave_event`:18–46 | Optional event building inside transaction; decision recipient employee only; register on_commit callback | On normal exit commit, then publish leave.approved/rejected; rollback would discard callback |
| 8 | views.py:89 →LeaveRequestSerializer /UserSerializer | Serialize existing row; `validate()` is **not** invoked on output | 200 same request JSON; stored decision actor/time not exposed |
| 9 | App.vue:42 →`refresh`:37 →views.py dashboard:93–108/team:112–132 →models balance properties:35–43 | Re-read lists/counts; team member approved totals and upcoming approved dates; dashboard balance is actor's own | Final status replaces pending; actions hidden; team employee available decreases only for approval |

An approval writes no balance row: it changes which request rows match the next `approved_days` SELECT. Rejection neither reserves nor consumes days and removes k from overlap-blocking states. Both types are terminal for this endpoint. Model choices alone do not implement those transitions; the pending guard does.

## W2 — rejection/precedence matrix

| Ordered check / exact source | Trigger | Expected status | Persisted effect / client consequence |
|---|---|---|---|
| DRF token, settings:142–149 | Missing/invalid token | 401 | No writes |
| Role, views:68–69 | Employee or other non-manager/admin | 403 | No writes; employee UI hides buttons |
| Decision value, views:70–72 | Missing/null/invalid status incl pending | 400 | No transaction/write; precedes target lookup |
| Scoped lookup, views:75–78 and46–51 | Nonexistent k or outsider-team k | 404 | No write; teamless manager only sees own records |
| Self, views:79–80 | Own k for manager/admin | 403 | No audit/status write, even if k is already final |
| Pending, views:81–82 | Approved/rejected k and valid decision | 409 | Same state/actor/time; no duplicate record, event or consumption |
| Missing approval balance check, views:83–86 | Approved decision with D>employee A | **200 in baseline** | Defective possible negative available; desired rejection not implemented |
| Callback, events:57–63 | Redis publication fails after commit | Normal 200 | Decision persists; notification can be missing |

`api.call` throws on a non-OK response (`api.ts:8`); `App.decide` has no catch (`App.vue:42`). Do not claim any manager rejection error is displayed in a banner. A later E2E test can inspect server/network and unchanged UI state, but a usable explanatory UI error is a missing behavior. Error precedence matters: an employee with bad status/nonexistent k still gets role403; authorized actor with invalid status gets400 before lookup; valid decision to another user's final k gets409; self-owned final k gets403 first.

## Shared record and balance assertions for later integration

1. Establish synthetic E/M in same team, outsider O in another, allowance A and fixed approved history. Record counts and derived balance, not merely model allowance.
2. W1 POST as E →capture actual returned k. ORM verifies k.employee_id=E, pending, null audit fields; GET E list contains k. Balance row/approved total unchanged.
3. W2 POST as M **to k**, never to a separately constructed row. ORM verifies unchanged identity/content plus final status/actor/time. Approval yields available−D; rejection yields unchanged available. Re-query E dashboard or E's entry in manager team, not manager's own dashboard balance.
4. Try denied actor/invalid value/repeated decision using k; re-read row/count/balance and audit metadata, proving no unintended write. Check owner-visible list after each step.
5. For any subsequent W1, interpret rejected vs approved/pending k correctly in overlap and derived balance. Duplicate/recovery tests must distinguish a failed operation from a committed operation whose response was lost.

## Direct notification dependency and boundary

`NotificationCenter.vue:32–38` calls `loadNotifications` (`frontend/src/notifications.ts:19–24`) then `streamNotifications` (:27–50). They request **GET http://localhost:3000/notifications** and **GET http://localhost:3000/events** with the same token; configurable `VITE_NOTIFICATIONS_URL`. Gateway source `notifications/src/app.ts:18–23,55–59,67–106` authenticates by GET Django `/api/me/`, lists that user's feed (200 JSON), or opens authenticated SSE (200 event-stream); unauthorized401/errors500. The gateway also has independent GET `/health` (:61–65), outside selected leave operations. No gateway input limit is added to the selected Django API inventory: the Vue call supplies none.

Django's producer payload includes UUID, event type, time, recipient IDs, actor and request (including original k). Worker domain mapping `notification_worker/lib/leave_flow_worker/domain.ex:70–87` preserves request_id=k in notifications; validation :32–39 rejects empty recipients, while Django can build an empty requested-recipient list if no matching manager/admin exists. This is an additional static dependency risk, not a reproduced failure. Downstream persistence/dedup/SSE internals are proposed exclusions from this narrow module's white-box target; the producer and callback remain included. No notification dependency is necessary for core leave success with REDIS_URL absent.

## Six use-case candidates and feasibility

These are **candidates**, not final use-case specifications or automation. Each lists two possible alternatives (A1/A2) and two exception paths (E1/E2). An alternative variation of a goal does not become another distinct use case merely to meet a count. Flows depending on faults need controlled browser/API doubles later; no UI action was invented.

| Candidate / actor / goal / workflow | Main success path | Two potential alternatives | Two potential exceptions | Actual UI support / feasibility |
|---|---|---|---|---|
| UC-01 Employee: submit time off (W1) | Login→New request→type/dates/note→submit→pending row | A1 choose permit/personal; A2 omit note or use same weekday | E1 overlap400 then correct dates; E2 insufficient balance400 then shorten span | Strong distinct goal. Modal supports main/alternatives and caught submission errors; invalid enum/overlength are mainly API cases, not invented browser controls |
| UC-02 Manager: approve pending leave (W2) | Login→Requests pending→approve k→approved status/team availability | A1 approve through Overview recent row; A2 admin approves different-team non-self k | E1 stale already-decided k409; E2 self-owned pending k403 | Strong goal; main/alternatives exist; exception API errors lack UI error rendering. Exception flow specs must record limitation and persisted state |
| UC-03 Manager: reject pending leave (W2) | Login→Requests→reject k→rejected status/no charge | A1 reject from Overview; A2 admin non-self rejection | E1 stale decision409; E2 invalid stored token401 on decision | Strong goal but shares handler with approval. No rejection-reason input or token-expiry policy. Exception feedback gap applies; confirm rubric accepts approve/reject as separate actor outcomes |
| UC-04 Employee: check remaining balance before requesting (W1 support) | Login→Overview→read available/used→open modal preview | A1 sidebar balance; A2 close modal without submission | E1 `/dashboard/` failure; E2 invalid token at boot | Real UI, but supporting read-only goal rather than independent workflow; boot catch logs out and refresh errors lack dedicated retry control. Needs instructor acceptance |
| UC-05 Manager: locate pending work (W2 support) | Login→Requests→pending filter→identify k for decision | A1 find through Overview recent; A2 All/approved/rejected filters to review history | E1 requests GET failure; E2 invalid token during refresh | Real filters/empty state, but locating work overlaps UC-02/03 preconditions. Failure has no dedicated list-error/retry UI; requires approved goal distinction |
| UC-06 Manager: inspect team availability for a decision (W2 support) | Login→People→read employee balance/next absence→Requests | A1 no upcoming leave displays none; A2 no-team user sees empty People | E1 team GET failure; E2 invalid token on team GET | Real People cards accessible to employees too. Read-only supporting goal, not an independent state-changing workflow; dedicated error feedback absent |

Only submit/approve/reject are strong distinct actor goals in the selected UI; supporting goals UC-04–06 risk rejection under the two-use-cases-per-member rubric. **Six genuinely distinct accepted use cases are not yet established.** Students should obtain instructor agreement or propose a reviewed scope adjustment within LeaveFlow. Do not invent cancellation, editing, half-day entry, rejection reasons, exports, reset buttons or notification deep-link navigation. Do not claim six ready-to-automate accepted specifications. Later each approved use case needs full pre/postconditions, ≥2 alternative and ≥2 exception flows, every flow automated in Playwright with rendered and persisted assertions.
