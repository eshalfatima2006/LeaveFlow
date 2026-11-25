# Business rules and future design inventories

Baseline `bada9a03ecec53ef6945827230e3594d825da87a`; 21 November 2026. Six rules. “Invalid” below means invalid for the named rule; defects and missing guards are explicitly separated. These are design foundations, not executed EP/BVA, decision tables, MCC or MC/DC results. Full requirement oracles and pinned evidence appear in [TEST-BASIS.md](TEST-BASIS.md).

## BR-01 — Ordered dates and inclusive weekdays (W1; W2 balance dependency)

- **Description/evidence:** `LeaveRequest.clean`, `backend/leave/models.py:80–82`, rejects end<start; `business_days`, lines 70–78, loops inclusively and counts weekday()<5. Serializer invokes clean at `backend/leave/serializers.py:30–35`; frontend preview is `frontend/src/App.vue:25–31`.
- **Inputs:** Start/end calendar dates, weekday of each included day. **Valid classes:** End≥start; same day; weekdays/weekends; past/future/cross-year spans. **Invalid:** End<start (field parse/missing errors are BR-06).
- **Boundaries:** Hold start=2026-12-07: end=12-06 rejects, 12-07 yields 1, 12-08 yields 2; weekday cutoff weekday indices 4/5/6 (Fri/Sat/Sun) yields 1/0/0 on single dates. Inclusive-loop final day is counted. No max duration or date relative to today is enforced.
- **Decisions/outcomes:** end<start true → field validation error; false → overlap check. current≤end controls loop; weekday<5 true increments, false skips. Not one compound Python Boolean expression.
- **States/events:** Submission creates pending only after validation; W2 reads the same duration indirectly through approved totals.
- **Enforcement/deficiencies:** Applied through serializer.clean, not automatically on every ORM save; no holiday/year/type/positive-day rule. Max representable end date can overflow the unconditional increment; very long ranges have linear cost. Robustness risks, not reproduced defects.
- **Techniques:** Date/weekday EP, three-point BVA, unit loop zero/one/many iterations and both weekday outcomes, mutation of < and ≤; not compound-condition MCC alone.

## BR-02 — No active interval overlap for the employee (W1; W2 changes blocking status)

- **Description/evidence:** `backend/leave/models.py:83–90`: same employee, status in pending/approved, existing.start≤new.end AND existing.end≥new.start, exclude own pk; exists → ValidationError. `backend/leave/serializers.py:31–35` converts it to DRF 400.
- **Inputs:** Employee identity, candidate pk, both intervals and existing status. **Valid classes:** No matching row; rejected-only intersection; different employee; strictly before/after existing interval. **Invalid:** Any pending/approved intersection for same employee, including equal endpoints.
- **Boundaries:** Existing 2026-12-07..11: new one-day on 12-06 allowed, 12-07 blocked, 12-08 blocked; and 12-10 blocked, 12-11 blocked, 12-12 allowed. Other rules held valid, including zero-day/balance conditions.
- **Boolean conditions:** Per-row predicate E∧S∧L∧R∧X (same employee; blocking status; start comparison; end comparison; different pk). All true → block; any false → that row does not block. exists aggregates over all rows. SQL evaluation has no promised Python left-to-right short circuit.
- **States/events:** Pending/approved block; rejected does not. W2 rejection permits a subsequent otherwise identical W1 interval; approval keeps it blocked.
- **Enforcement/deficiencies:** Query-before-create, not DB exclusion/unique constraint. W1 candidate is unsaved (pk=None); update-self exclusion is reachable at model level, not an API update feature. Concurrent inserts may both pass; no reproduction claimed.
- **Techniques:** Date EP/BVA, multi-condition decision table, API persisted counts, model predicate tests, mutation of comparisons/status set/ownership and existence result.

## BR-03 — Submission allowance limit and derived consumption (W1/W2)

- **Description/evidence:** `backend/leave/models.py:29–43`: A=allowance−sum(D of all approved requests for the employee). `backend/leave/serializers.py:36–39`: reject iff balance exists AND candidate D>A. `backend/leave/views.py:74–87` contains **no approval-time validation**.
- **Inputs:** Balance existence B, allowance, prior approved weekday totals U, candidate weekday count D; pending records do not contribute. **Valid classes:** With balance, D≤A; equality accepted. **Rejected class:** With balance, D>A. **Observed bypass:** No balance allows submission whatever D; not endorsed as desired policy.
- **Boundary:** A=5 with no overlap: D=4/5/6 → accepted/accepted/400. A=0: D=0 accepted, D=1 rejected; D<0 is impossible for normal ordered dates. Negative A can arise from approvals and causes even D=0 to fail W1's comparison.
- **Boolean conditions:** B∧E, E=(D>A); true → insufficient-balance error, false → accept attrs. Python skips E if B false. See MCC feasibility below.
- **States/events:** Pending/rejected contribute zero; approved contributes full weekdays for all leave types and years. Approving k changes derived totals without updating LeaveBalance. Repeating decision on final k is blocked by BR-05.
- **Enforcement/deficiencies:** Submission only, no reservation, no year filter, no type distinction, no mandatory balance, no approval guard, no balance-level lock. A numeric model field is not enforcement of nonnegative *remaining* balance.
- **Desired rule (unimplemented):** Approval must not produce A<0. Contract agreed 25 Nov 2026 (GAP-01): 400 `{"detail": "Insufficient leave balance"}`; request stays pending, `decided_by` null, balance unchanged; D=A is still approved. Missing balance is not covered (GAP-07). TEST-BASIS specifies the proposed failing cross-workflow scenario. Do not label this desired rule as baseline enforcement.
- **v0.2 clarification (24 Nov 2026, no policy change):** If instructor decision D-1 brings UC-08 into scope, the allowance A is maintained by staff in Django Admin (PROPOSED FR-ADM-01). Its validated range is 0 to an engine-dependent maximum (PostgreSQL 32767; SQLite 2^63−1). An administrator can lower A below the employee's approved days without a warning, so available can become negative through this path as well as through approval overdraw (GAP-01, GAP-05). Observed baseline behaviour only; the desired policy remains undecided.
- **Techniques:** EP/three-point numerical BVA, complete decision table and MCC/derived MC/DC, cross-workflow state assertions, mutations (`>`→`>=`, removing B guard, wrong status aggregation), later concurrency tests.

## BR-04 — Role, team and ownership permission (W1/W2)

- **Description/evidence:** Token/authenticated defaults `backend/config/settings.py:142–149`; visibility `backend/leave/views.py:46–51`; decision role/scoped lookup/self guards `backend/leave/views.py:68–80`; caller-bound creation `backend/leave/serializers.py:41–42`.
- **Inputs:** Token validity, role, team presence/membership, actor ID and target employee ID. **Valid classes:** Authenticated own submission; manager with team viewing that team's requests and deciding a non-self pending request; admin viewing all and deciding non-self. **Invalid:** Unauthenticated API access, employee decision, out-of-scope target and self-decision.
- **Boundary:** IDs and roles are identity/categories, not numeric permission thresholds; three-point BVA does not apply to role. Route ID classes are listed below.
- **Boolean decisions:** `role==MANAGER and team_id` selects team queryset (after admin guard). Role not in [MANAGER,ADMIN] denies; item.employee_id==actor.id denies. All guards' ordering determines 403/400/404/409 precedence.
- **States/events:** All states listable within visibility; decision permission applies before transition check. No team → manager sees own only, which the self guard prevents deciding.
- **Enforcement/deficiencies:** Server enforces request decisions; UI shows self-decision buttons for manager/admin. `/api/team/` is authenticated/team-based for every role, not restricted to managers. Teamless requested-event routing can target teamless managers who cannot actually access another employee's request.
- **v0.2 clarification (24 Nov 2026, no policy change):** Visibility and decision authority are evaluated on **every request** from the actor's current role and team (`views.py:46–51,75–80`). After a team change (UC-09, conditional), the former manager receives 404 for the employee's pending requests and the new team manager may decide them. Notification recipients are fixed when the event is produced (`events.py:19–27`), so earlier alerts stay with the former recipients and the new approver gets no alert for inherited requests (GAP-08, GAP-11). Source-derived; browser verification is planned with UC-09.
- **Techniques:** Access matrix, compound-condition table/MCC/MC/DC, allowed and denied API/browser cases, ownership/team mutations. Later defensive security must automate ≥4 access decisions across two roles.

## BR-05 — Pending-only decision and immutable final state (W1/W2)

- **Description/evidence:** Default pending and three states `backend/leave/models.py:52–65`; `backend/leave/views.py:70–89` accepts approved/rejected, atomically locks visible row, rejects self/final state then saves decision fields.
- **Inputs:** Current state, submitted decision, authorized actor. **Valid:** Pending+approved or pending+rejected. **Invalid:** Any decision from approved/rejected; value not approved/rejected (including pending).
- **Boundary:** Unordered state choices, no three-point numerical BVA.
- **Decisions/outcomes:** Invalid value true →400; nonpending true →409; otherwise save same k, actor, timestamp and publish after commit. These are ordered simple guards rather than one compound expression.
- **States/events:** Creation→pending; pending→approved/rejected; approved/rejected terminal **for selected API**. No reopen/cancel/delete operation. Direct ORM/admin edits are outside the API state machine.
- **Enforcement/deficiencies:** Atomic decision update with selected-row lock; database engine matters. No approval balance guard or idempotent successful duplicate response (repeat is 409). Decision audit fields persist but are absent from serializer response.
- **v0.2 clarification (24 Nov 2026, no policy change):** Approval and rejection remain the only two transitions out of pending and are both terminal for the API; UC-02 treats them as two valid outcomes of one decision goal. A2.1 executes every valid API transition and an invalid event from each state (`tests/team/api/test_w2_decisions.py` `FinalStateTests`, `DecisionValueTests`). Django Admin can still change `LeaveRequest.status` directly, bypassing this state machine and the self-decision guard (source-observed, GAP-12); that path is out of scope and is not an allowed flow. No new state (cancelled, withdrawn, returned) exists or is proposed.
- **Techniques:** State-event table, every allowed edge and at least one disallowed event per state, repeats, transaction failure assertions, mutations removing pending/self guard or changing saved status.

## BR-06 — API field and decision domains (W1/W2)

- **Description/evidence:** Request ModelSerializer fields `backend/leave/serializers.py:16–28`, model domains `backend/leave/models.py:47–65`; manual decision domain `backend/leave/views.py:70–72`. Serializer field metadata confirmed in installed DRF 3.17.1 without writes.
- **Inputs/classes:** Required nonnull start/end dates; optional type (vacation default), choices vacation/permit/personal, nonnull; optional note, blank allowed, nonnull and trimmed maximum 280. Decision status required in practice by `.get`, exactly approved/rejected. ID/employee/status response fields read-only for W1; unknown extra keys have no explicit rejecting validator.
- **Boundaries:** Trimmed note 279/280/281 characters accepted/accepted/400; empty note valid, “−1 characters” infeasible. No maximum decision-body length or minimum date relative to now is defined. Type/state enums use EP, not artificial string-length BVA.
- **Boolean outcomes/states:** Field validity false →400 before create; decision membership false →400 after role guard. Valid fields proceed to the date/overlap/balance/state rules; supplied W1 status cannot set a final state.
- **Enforcement/deficiencies:** Framework-derived request fields but no discoverable spec; W2/login manual bodies lack serializer definitions. Field errors do not prove cross-field rules. Arbitrary malicious/malformed shapes may exercise framework behavior; response contracts need later verification.
- **Techniques:** Generated EP/BVA, serializer API tests, decision enum table, mutation note length/choice handling. No production schema repair this phase.

## EP and three-point BVA input inventory

Expected HTTP outcomes below are source/framework-derived oracles, not newly executed requests. Hold other inputs valid; use one invalid partition per test. A generated API contract must distinguish omission, blank, null and invalid type. Error text depends on installed DRF/language; assert stable keys/status and meaning before translated exact strings.

| API input | Type / presence / source constraint | Valid equivalence classes | Invalid equivalence classes / expected error | Limits and below/at/above examples |
|---|---|---|---|---|
| W1 start_date | Date string; required, nonnull; model:59 and serializer | ISO calendar date, past/today/future, leap day, weekday/weekend | Omitted/null/empty/unparseable/impossible date →400, no insert | Relative end-order boundary in BR-01; no application earliest/latest rule. Parser representability is a framework boundary to verify later |
| W1 end_date | Date string; required, nonnull; model:60 | Parseable, ≥start incl same day; weekend, cross-month/year | As start plus end<start →400 | With start 2026-12-07: 12-06/07/08; no max duration. Date.max increment overflow risk is separate robustness case |
| W1 leave_type | Choice; optional, nonnull; default vacation; model:47–58 | Omitted; vacation/permit/personal | Null, blank, unknown enum, wrong structured type →400 | Unordered category: BVA N/A. max_length model 16 is not a useful accepted-value boundary when all other strings fail enum |
| W1 note | String; optional, blank allowed, nonnull; max_length=280; model:61 | Omitted/empty/whitespace-only, trimmed text length≤280 | Null, trimmed length>280, structured nonstring →400 | 279/280/281 **nonwhitespace** characters; at lower length 0 use infeasible −1/0/1. DRF may coerce scalar numbers; do not assert all scalars reject |
| W1 employee/id/status and other read-only output fields | Not writable; serializer:17–28; model defaults | Omit; supplying cannot choose employee/status | No explicit read-only-field rejection; expect ignored fields, then ordinary validation | N/A; verify ownership/status persisted, not a fabricated 400 |
| W1 unknown property | No declared serializer field | Ordinary known payload plus extra key (ignored by baseline serializer) | No strict reject-unknown constraint exists | N/A; schema must not imply strict enforcement without change |
| W2 request_id path | Django `<int:request_id>`; urls:11 | Nonnegative digit syntax resolving to visible existing k | Negative/nondigits/no matching route →404; zero/nonexistent/invisible ID →404 after earlier guards | 0 is syntactically accepted but normally absent; −1/0/1 tests routing/record existence, **not** a domain minimum of 1; no declared maximum ID input bound |
| W2 status body | Manual choice `.get`; required for success, views:70–72 | approved, rejected | Omitted/null/blank/pending/unknown enum/wrong scalar or container →400 after role guard | Unordered category: BVA N/A |
| W2 extra body keys | Unused by handler | Additional fields do not alter actor/time/target | No strict unknown-field rejection | N/A; confirm they cannot overwrite stored audit fields |
| Both workflow Authorization header | `Token <key>` for protected routes; settings:142–149 | Valid active user's token; distinct roles/teams | Missing, malformed/invalid token, inactive user →401 per token authentication | Opaque credential; numerical BVA N/A; avoid real credentials in artifacts |
| Setup login username/password | Manual `.get`; views:33–38 | Correct active synthetic credentials →200 | Missing/blank/wrong/inactive →400 invalid credentials; unusual JSON types need robustness verification | No API username/password length validators declared here. Model registration limits are not login constraints; BVA N/A absent an enforced login limit |
| GET /me, /dashboard, /team, /requests | No selected body/query inputs | Authenticated GET | Unauthenticated →401; wrong method →405 (login has AllowAny) | No implemented filter/pagination query schema; UI filtering is local |

Derived numerical inputs also require EP/BVA although they are not writable API fields: D at A−1/A/A+1, missing vs present balance, A=0 and negative A, weekday 4/5/6, inclusive endpoint −1/0/+1 day, overlap before/touch/after. Allowance/year are setup data, not writable through selected routes; do not generate fictional POST allowance constraints. Non-JSON body/malformed JSON, unsupported content type and method are protocol partitions (typically 400/415/405), to verify in the later API suite.

## Compound decision inventory and feasibility

Truth combinations count **atomic predicates**, not cyclomatic complexity or measured coverage.py branches. A skipped operand is not an observed false operand. Complete MCC tables and derived independence pairs remain future work.

| Decision / exact source | Atomic conditions and action | Short circuit | Theoretical combinations / feasibility |
|---|---|---|---|
| D1 `balance and instance.business_days > balance.available_days`, serializers:37 | B=balance exists; E=D>A; B∧E rejects | If B false, E and property reads are skipped | 2²=4 abstract rows. B=true supports E=false/true through real fixtures. B=false makes A/E undefined, so the two abstract E rows are masked, not independently realizable domain cases. Unique-cause MC/DC for B is not demonstrable using real missing-balance objects; use explicit masking justification/instructor review, no invented values |
| D2 `user.role == User.Role.MANAGER and user.team_id`, views:49 | M=manager; T=team_id truthy; M∧T selects team filter after admin guard | If M false, T not read | 2²=4; all feasible with employee/manager × absent/present team; admin bypasses this expression. T truthiness, not a threshold comparison |
| D3 `self.get_full_name() or self.username`, models:26 | N=nonempty full name; U=username truthiness; returns first truthy value | U evaluated only if N false | 2²=4 abstract truth rows, but empty username is not a normal valid account fixture; only N true/false with valid username needed for scope. Value-selection fallback, not a multi-condition eligibility rule; no false claim of complete domain MCC |
| D4 overlap queryset, models:83–88 | E same employee ∧ S active-status membership ∧ L existing.start≤new.end ∧ R existing.end≥new.start ∧ X different pk | SQL predicates have no guaranteed order | 2⁵=32 abstract rows per existing row. For ordered intervals L=false and R=false together impossible: existing.start>new.end≥new.start>existing.end contradicts existing.start≤existing.end. X always true for W1 unsaved candidate; X=false feasible only model-level existing-instance clean. If S decomposed into pending∨approved, both simultaneously true is impossible. Multiple-row exists adds aggregation, not 32 API response types |
| D5 recipients `Q(role=ADMIN) \| Q(role=MANAGER, team_id=item.employee.team_id)`, events:21–25 | A admin ∨ (M manager ∧ T team equality); exclude employee separately | SQL, no promised Python short circuit | 2³=8; A and M simultaneously true impossible for a single role field; other role/team combinations feasible incl employee/no-team. Self-exclusion independently tested. Prefer semantic decision table; do not count Q object bitwise operators as Python short-circuit branches |
| D6 upcoming team leave filter, views:119–122 | P approved ∧ F end≥localdate; earliest start among matches | SQL predicates; no guaranteed order | 2²=4 feasible status/date combinations; no request →null is separate output condition |

`hasattr(exc,'message_dict')` in serializers:35 is a **single** Boolean choosing field-dict vs message-list exception shape. Guards at views:68,71,79,81 and models:81,89 are simple decisions; membership sets should still receive enum/role EP and decision tables in combination with surrounding guards. Dashboard status-filtered counts are independent aggregate membership checks, not a compound Python condition. All of these remain in the coverage boundary.

> **Superseded by [DR-001](../planning/DR-001-CRITICAL-MODULE.md) (24 Nov 2026):** D1's evaluable vectors (F,–), (T,F) and (T,T) were all executed; B is shown independent by masking MC/DC (pair T1/T3) and E by unique cause (T1/T2). D2 is also short-circuited: its two employee rows both evaluate as (F,–), so it gives no masking-free alternative. v0.1 text: D1 is the critical rule candidate, but its missing-balance masking means “four combinations covered” cannot honestly be claimed using real domain values. D2 supplies four feasible rows and clear unique-cause MC/DC pairs (TT/FT for M, TT/TF for T); it does not substitute for D1 silently. See COVERAGE-BOUNDARY for critical-module choice and instructor decision.

## State-transition inventory

Guard order: authentication → role → decision value → visible k → not self → pending. The following assumes those earlier actor/lookup guards succeed; otherwise they determine the error first.

| Source state | Event | Guard / action | Result | Persisted effect |
|---|---|---|---|---|
| No record | Valid W1 submission | Fields/date/overlap/balance pass; create | pending /201 | New k, employee caller; no allowance write |
| pending | Approve | Authorized visible non-self; lock; no balance guard | approved /200 | Same k; set actor/time; derived available−D |
| pending | Reject | Same guards | rejected /200 | Same k; set actor/time; derived available unchanged |
| pending | Set pending/unknown | Invalid decision | pending /400 | No change; candidate disallowed event from pending |
| approved | Approve or reject | Nonpending guard | approved /409 | No change, including actor/time; duplicate approve not successful idempotency |
| rejected | Approve or reject | Nonpending guard | rejected /409 | No change; duplicate reject blocked |
| approved/rejected | Reopen/cancel/delete | No selected endpoint | No API transition | Do not invent events or controls |

Both final states are terminal for this API. Repeating W1 over a pending/approved interval normally returns overlap 400; after rejection it can create a **new** k. That is distinct from W2 repeated decisions on the original k. No DB state-transition constraint prevents direct ORM/admin writes. Later tests must expand this inventory into a complete state-event table, cover both allowed transitions and ≥1 disallowed event from **each** real state, and assert persisted postconditions.
