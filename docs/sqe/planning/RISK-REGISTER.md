# Proposed risk register and 5×5 matrix

Version0.1 — 22 November 2026. **12 product risks and four project risks** (v0.2, 24 Nov 2026: five project risks — JR-05 added). Scores/ranks/owners are transparent proposed planning judgments, not measured occurrence rates or confirmed defects. Risk is a possible adverse outcome; existing control code does not prove bypass occurred. S=static source observation; H=hypothesis; Q=unresolved policy/scope; V=verified command observation; Reported=unverified assertion from prompt/history. Evidence types are retained below, and genuine future execution replaces uncertainty only with artifacts.

## Scales, score and priority

Likelihood L:1 rare under unusual conditions;2 unlikely;3 plausible with normal variations;4 likely exposure/repeated opportunity or major readiness gap;5 trigger is readily achievable given a statically missing safeguard (still requires reproduction). These are ordinal estimates, not calibrated percentages. Impact I:1 cosmetic/local inconvenience;2 recoverable minor workflow friction;3 incorrect response/task disruption with limited records;4 significant integrity/availability or test-program invalidation;5 unauthorized personnel exposure, entitlement corruption or inability to satisfy a core mandatory deliverable. Product and project impacts are assessed against their respective outcomes, not conflated.

Score=L×I. Priority bands: critical20–25, high15–19, medium8–14, low1–7. Within each risk type sort descending score, then impact, then likelihood, then ascending ID (deterministic tie-break). Product release priorities are ranked independently of project delivery priorities; a project risk may still suspend execution. Residual scores are NOT MEASURED until controls are verified; planned mitigation alone never reduces a number.

## Scored inventory

| ID | Category | Possible outcome | Affected workflow / requirement | L | I | Score | Rank within type | Proposed owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| PR-01 | Product / entitlement integrity | Approval can overdraw employee allowance | W1/W2; FR-W1-05, FR-W2-05; BR-03 | 5 | 5 | 25 | 1 | A2 | OPEN — proposed assessment |
| PR-02 | Product / confidentiality and permission | Role/team/self bypass or excess request exposure | W1/W2; FR-W1-01, FR-W2-01/02; BR-04 | 4 | 5 | 20 | 2 | A2 | OPEN — proposed assessment |
| PR-03 | Product / concurrent integrity | Simultaneous submissions or distinct approvals break invariants | W1/W2; FR-W1-04/06, FR-W2-04/05; BR-02/03/05 | 3 | 5 | 15 | 3 | A2 | OPEN — proposed assessment |
| PR-04 | Product / interval correctness | Overlap/date/weekday regression admits conflict or wrong duration | W1; FR-W1-03/04; BR-01/02 | 3 | 4 | 12 | 5 | A1 | OPEN — proposed assessment |
| PR-05 | Product / state and repetition | Final requests change again or duplicate decisions corrupt metadata | W2; FR-W2-03/04/06; BR-05/06 | 3 | 4 | 12 | 6 | A2 | OPEN — proposed assessment |
| PR-06 | Product / API contract completeness | Missing/wrong schemas conceal request and response constraints | W1/W2; FR-W1-02/06, FR-W2-03/05; BR-06 | 4 | 3 | 12 | 9 | A2 | OPEN — proposed assessment |
| PR-07 | Product / input acceptance correctness | API accepts invalid inputs or rejects valid boundary/default classes | W1/W2; FR-W1-02–05, FR-W2-03; BR-01/02/03/06 | 3 | 4 | 12 | 7 | A2 | OPEN — proposed assessment |
| PR-08 | Product / usability and UI consistency | Self-decision buttons and missing error display mislead users | W2 and W1 refresh; FR-W2-02/04, FR-W1-06; BR-04/05 | 4 | 3 | 12 | 10 | A3 | OPEN — proposed assessment |
| PR-09 | Product / vulnerable dependencies | Reported npm and possible Python vulnerabilities affect workflow stack | W1/W2; all FRs indirectly; BR-04/06 | 3 | 4 | 12 | 8 | A3 | OPEN — proposed assessment |
| PR-10 | Product / recovery and write consistency | Failure/retry leaves partial or duplicate request/decision state | W1/W2; FR-W1-06, FR-W2-04–06; BR-03/05 | 3 | 5 | 15 | 4 | A3 | OPEN — proposed assessment |
| PR-11 | Product / policy and accounting ambiguity | Missing balance, zero days or cross-year/type totals produce unintended allowance behavior | W1/W2; FR-W1-03/05, FR-W2-05; BR-01/03 | 3 | 3 | 9 | 11 | A2 | OPEN — proposed assessment |
| PR-12 | Product / notification side effects | Wrong recipient or failed after-commit delivery undermines workflow feedback | W1/W2; FR-W1-06, FR-W2-05/06; BR-04/05 | 3 | 3 | 9 | 12 | A1 | OPEN — proposed assessment |
| JR-01 | Project / data isolation and testware validity | Unsafe seed/reset, contaminated fixtures or incorrect generated constraints invalidate experiments | Both workflows; all FRs | 4 | 4 | 16 | 2 | A2 | OPEN — proposed assessment |
| JR-02 | Project / tooling and CI readiness | Tool/runner incompatibility, unavailable Node/Sonar or incomplete gates delay or falsely green work | All testing areas and EC-04/07 | 4 | 4 | 16 | 3 | A1 | OPEN — proposed assessment |
| JR-03 | Project / assignment scope feasibility | Coverage denominator/MCC infeasibility and six actor-goal UCs remain unapproved | All FRs, BR-03/04; EC-04/06 | 4 | 5 | 20 | 1 | Shared | OPEN — proposed assessment |
| JR-04 | Project / ownership, review and evidence retention | Unconfirmed allocation, review bottlenecks or lost prompts/evidence impair delivery/viva | All areas; shared management | 3 | 4 | 12 | 4 | Shared | OPEN — proposed assessment |
| JR-05 | Project / release and CI side effects | Upstream `auto-release.yml` publishes a patch release after successful CI on `main`, so merging SQE work into the fork's `main` could create unintended tags/releases | All areas; EC-07 | 3 | 3 | 9 | 5 | A1 | OPEN — proposed assessment (v0.2) |

## 5×5 score matrix

Each cell gives score and risk IDs initially placed there; rows likelihood, columns impact. Empty ID list means no currently proposed risk at that coordinate, not no possible risk.

| L / I | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 5 | 5 | 10 | 15 | 20 | 25 (PR-01) |
| 4 | 4 | 8 | 12 (PR-06,PR-08) | 16 (JR-01,JR-02) | 20 (PR-02,JR-03) |
| 3 | 3 | 6 | 9 (PR-11,PR-12,JR-05) | 12 (PR-04,PR-05,PR-07,PR-09,JR-04) | 15 (PR-03,PR-10) |
| 2 | 2 | 4 | 6 | 8 | 10 |
| 1 | 1 | 2 | 3 | 4 | 5 |

**Highest-priority product risks: PR-01 (25), then PR-02 (20).** The balance guard is absent where approvals change the derived total, while authorization failure could expose/change another user's records. Authorization guards are present, so PR-02 remains a failure hypothesis, not a breach allegation. EC-01/EC-02 explicitly block release on their agreed integrity/access assertions; WP-08/10/19/22 and M1 early investigations prioritize them. PR-03/PR-10 (both15) follow; their tie resolves by ID after equal score/impact/likelihood. JR-03 (20) is a separate scope/readiness blocker and cannot be buried by product ranking.

## Risk evidence, treatment and residual review

All verification IDs below are **planned** objectives defined in [REQUIREMENTS-TRACEABILITY-MATRIX](REQUIREMENTS-TRACEABILITY-MATRIX.md), not implemented tests. All test/mitigation results remain NOT MEASURED. [ENTRY-EXIT-CRITERIA](ENTRY-EXIT-CRITERIA.md) defines release blockers. Default contingency is to preserve genuine evidence, keep unresolved outcomes explicit and avoid valuable-data mutations.

### PR-01 — Approval can overdraw employee allowance

- **Evidence / classification:** S: `backend/leave/serializers.py:36–38` checks only submission; `backend/leave/views.py:81–86` saves approval with no balance check; `backend/leave/models.py:35–43` derives remaining from approved totals. Missing safeguard is statically confirmed, not a reproduced transaction. *V (25–27 Nov 2026): reproduced as DEF-A2-01 ([#25](https://github.com/eshalfatima2006/LeaveFlow/issues/25)), independently confirmed by Muhammad Bilal on 27 Nov 2026; see [RCA 1](../defects/RCA-MAJOR-01-BALANCE-OVERDRAW.md).*
- **Mitigation:** Approve desired nonnegative rule/error contract (agreed 25 Nov 2026: 400 `{"detail": "Insufficient leave balance"}`; GAP-01), reproduce two nonoverlapping pending4-day requests against allowance5; retain original k values. Prioritize before broad automation (WP-08/10/22).
- **Planned verification:** API-INT-001, API-W2-005 and UT-W1-005: check second approval rejected under agreed desired policy, original row/audit unchanged and available1; characterize defective baseline separately; EC-01.
- **Contingency:** Hold affected release; if reproduced, students triage genuine issue/fix with regression and fail-before/pass-after proof. Do not count characterization as desired-rule success.
- **Residual risk:** NOT MEASURED; original L=5, I=5 remains the planning assessment until verified controls justify a recorded revision. Owner A2 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-02 — Role/team/self bypass or excess request exposure

- **Evidence / classification:** H: guards exist at `backend/leave/views.py:46–51,68–82` and token defaults at `backend/config/settings.py:142–149`; failure is a regression/exposure hypothesis, not an observed breach. Own-team employee People visibility is baseline policy, not automatically a defect.
- **Mitigation:** Model employee/manager/admin × team/no-team × self/nonself; require real-token HTTP and browser allowed/denied paths, not UI hiding alone; execute early in WP-10/19.
- **Planned verification:** API-W1-001, API-W2-001/002, DT-003 and SEC-001/002: exact visible ID sets, 401/403/404 precedence and zero writes on denial; ≥4 automated access decisions; EC-02.
- **Contingency:** Hold and restrict testing to isolated synthetic profiles; investigate route/queryset/source before widening UI suites; escalate genuine data exposure as major.
- **Residual risk:** NOT MEASURED; original L=4, I=5 remains the planning assessment until verified controls justify a recorded revision. Owner A2 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-03 — Simultaneous submissions or distinct approvals break invariants

- **Evidence / classification:** H/S: W1 query then create `backend/leave/serializers.py:31–42`; W2 selected-row lock `backend/leave/views.py:74–87` does not lock the shared employee balance across distinct requests. No race reproduced; SQLite results cannot establish PostgreSQL locks. *V (25–27 Nov 2026): the W1 race is reproduced on PostgreSQL 17.12 as DEF-A2-02 ([#26](https://github.com/eshalfatima2006/LeaveFlow/issues/26)), independently confirmed by Muhammad Bilal on 27 Nov 2026; see [RCA 2](../defects/RCA-MAJOR-02-CONCURRENT-SUBMISSIONS.md).*
- **Mitigation:** Design synchronized independent-connection tests for overlap and same-k/distinct-k decisions, bounded barriers/timeouts, real disposable PostgreSQL and reviewed invariant oracle.
- **Planned verification:** API-INT-002 and ST-001: record every response and final request/balance/audit counts; prove no unauthorized double transition or overdraw under desired rule; EC-03.
- **Contingency:** Mark concurrency guarantee unverified/HOLD if DB unavailable; retain SQLite functional results separately. No assumed fix from wrapping one query in atomic.
- **Residual risk:** NOT MEASURED; original L=3, I=5 remains the planning assessment until verified controls justify a recorded revision. Owner A2 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-04 — Overlap/date/weekday regression admits conflict or wrong duration

- **Evidence / classification:** H: inclusive checks/count implemented at `backend/leave/models.py:70–90`; hypothesis concerns incorrect boundaries/status/ownership combinations or future regression, not a confirmed overlap failure.
- **Mitigation:** Exercise touch/before/after endpoints, pending/approved/rejected and other-owner intervals, weekend-only/same-day; use date-class fixtures and custom mutation.
- **Planned verification:** UT-W1-003/004, API-W1-003/004 and DT-002; full feasible predicate rows and unchanged count on rejection; EC-04/05.
- **Contingency:** Quarantine only invalid experiment data, revise documented oracle if policy uncertain; do not suppress boundary failures or remove difficult cases.
- **Residual risk:** NOT MEASURED; original L=3, I=4 remains the planning assessment until verified controls justify a recorded revision. Owner A1 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-05 — Final requests change again or duplicate decisions corrupt metadata

- **Evidence / classification:** H: guard implemented `backend/leave/views.py:70–86`; statuses `backend/leave/models.py:52–65`. API final states terminal; no cancel/reopen feature.
- **Mitigation:** Complete state-event table and guard-precedence tests; independent final-state fixtures; same-k repeat approval/rejection readback and concurrent repeat review.
- **Planned verification:** ST-001, API-W2-003/004 and UT-W2-004; both allowed transitions and ≥1 disallowed event from each state; audit/count/balance unchanged; EC-03/05.
- **Contingency:** Hold any genuine state-integrity defect; retain failing evidence and add regression before fix closure.
- **Residual risk:** NOT MEASURED; original L=3, I=4 remains the planning assessment until verified controls justify a recorded revision. Owner A2 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-06 — Missing/wrong schemas conceal request and response constraints

- **Evidence / classification:** S plus historical introspection: Phase1 TEST-BASIS GAP-02; function views at `backend/leave/views.py:54–89`, fields at `backend/leave/serializers.py:16–28`, route list `backend/leave/urls.py:5–12`; no spec/route found. Default inference gave empty schemas/wrong POST201 in Phase1, not rerun here.
- **Mitigation:** Author accurate versioned OpenAPI for selected endpoints, defaults/nullability/read-only and errors; peer-check decision/login200 and create201; keep rule manifest for cross-field constraints.
- **Planned verification:** GEN-001 and API field/decision objectives; validate spec against actual request/response behavior and update links; EC-05.
- **Contingency:** Do not generate cases from unreviewed inferred schema; use Phase1 source oracle to draft spec while marking generated coverage blocked.
- **Residual risk:** NOT MEASURED; original L=4, I=3 remains the planning assessment until verified controls justify a recorded revision. Owner A2 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-07 — API accepts invalid inputs or rejects valid boundary/default classes

- **Evidence / classification:** H: source `backend/leave/serializers.py:16–42` plus Phase1 EP/BVA inventory distinguishes omitted type, trimmed note, missing balance and no fixed max duration. Incorrect API acceptance/rejection is a possible product failure, not a verified finding. Incorrect generated constraints are a separate project-assurance cause under JR-01, not themselves a product defect.
- **Mitigation:** Independently review expected product input classes against source and approved policy, then verify API outcomes using valid/invalid/default/null and boundary cases. Use one invalid class per case, schema hash/seed and exact generator-case consumption; regenerate note-length and enum constraints in labelled variant.
- **Planned verification:** GEN-001, DT-001/002, API-W1-002–005 and API-W2-003; independently verify expected boundaries and meaningful spec-change diffs; EC-05.
- **Contingency:** Triage a reproduced product acceptance failure with independent oracle review; if testware was wrong, handle under JR-01, retain prior output and rerun affected APIs. No invented maxDays26/min1-day rule.
- **Residual risk:** NOT MEASURED; original L=3, I=4 remains the planning assessment until verified controls justify a recorded revision. Owner A2 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-08 — Self-decision buttons and missing error display mislead users

- **Evidence / classification:** S: `frontend/src/RequestRow.vue:21–23` shows manager pending controls, `backend/leave/views.py:79–80` denies self; `frontend/src/App.vue:41–42` catches submit but not decision. No complete browser reproduction claimed.
- **Mitigation:** Automate self/stale/invalid-token exceptions and network refresh faults; record actual feedback separately from server-correct denials. Later authorized UI improvement requires before/after evidence.
- **Planned verification:** E2E-UC02-04/05, E2E-UC03-04/05, ACC-002 and SEC-001; assert rendered state and persistence, record missing actionable error; EC-06/08 as applicable. *v0.2: executed as TC-UC02-E1 (409) and TC-UC02-E2 (403) in B1 run-1/run-2 — server denial correct, missing UI feedback **observed** (OBS-UC02-01); legacy IDs mapped in the RTM.*
- **Contingency:** Do not invent a banner or call denied request a UI pass for usability; report severity by impact, keep mandatory task/exception paths blocked until addressed or explicitly resolved.
- **Residual risk:** NOT MEASURED; original L=4, I=3 remains the planning assessment until verified controls justify a recorded revision. Owner A3 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-09 — Reported npm and possible Python vulnerabilities affect workflow stack

- **Evidence / classification:** Reported/H: prompt.md mentions npm vulnerabilities but no current audit JSON/advisory details were available. `frontend/package-lock.json`, `notifications/package-lock.json` and `requirements.txt:1–6` define audit inventory; no verified CVE/count/severity claimed.
- **Mitigation:** Run later pip-audit and appropriate npm audit locally using exact dependency/lock inventory; separate direct/transitive and production/dev reachability; review advisory evidence and proposed compatible updates.
- **Planned verification:** SEC-003; package/version/advisory/date/affected component, impact and fix/residual review, verify actual correction with repeat audit; EC-08.
- **Contingency:** Retain evidence and lock integrity; do not auto-upgrade or fabricate findings. Release blocker depends on verified applicable severity/exploitability, not an unsupported reported count.
- **Residual risk:** NOT MEASURED; original L=3, I=4 remains the planning assessment until verified controls justify a recorded revision. Owner A3 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-10 — Failure/retry leaves partial or duplicate request/decision state

- **Evidence / classification:** S/H: W1 create then event `backend/leave/views.py:59–61`; W2 atomic save `backend/leave/views.py:74–87`; event callback failure swallowed `backend/leave/events.py:56–63`. Different commit boundaries require different expectations; no injected failure executed.
- **Mitigation:** Inject controlled prewrite failure at create/save seam, re-read untouched state, restore/retry; separately test committed write with lost response or Redis publish failure.
- **Planned verification:** REC-001/002 plus API-INT-001: exactly one original/final record after valid retry, audit/balance consistency, no failed-attempt event or doubled charge; EC-03.
- **Contingency:** Suspend repeated retries if commit state unknown; read back by captured identity/scenario before retry, preserve failure logs; do not reset development DB.
- **Residual risk:** NOT MEASURED; original L=3, I=5 remains the planning assessment until verified controls justify a recorded revision. Owner A3 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-11 — Missing balance, zero days or cross-year/type totals produce unintended allowance behavior

- **Evidence / classification:** Q/S: `backend/leave/serializers.py:36–38` skips absent balance; `backend/leave/models.py:35–43,70–78` sums all approved years/types and permits0 weekday days; intended policies unconfirmed.
- **Mitigation:** Record current behavior in characterization; obtain desired policy before changing oracle; keep year/leave-type and weekend classes explicit.
- **Planned verification:** UT-W1-003/005, API-W1-003/005 and API-W2-005; distinguish observed baseline from unimplemented desired policy; EC-01/05 when policy becomes binding.
- **Contingency:** Escalate policy-dependent tests as blocked; no fabricated annual restriction or automatic defect label merely because business policy is unknown.
- **Residual risk:** NOT MEASURED; original L=3, I=3 remains the planning assessment until verified controls justify a recorded revision. Owner A2 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### PR-12 — Wrong recipient or failed after-commit delivery undermines workflow feedback

- **Evidence / classification:** S/H: `backend/leave/events.py:18–63` chooses recipients and logs/swallow Redis callback exceptions; teamless recipient mismatch documented in Phase1 WORKFLOW-TRACE. Delivery failure/recipient breach not reproduced.
- **Mitigation:** Keep producer and nested callback in coverage, test admin/team/self recipient combinations and disabled/enabled/failing Redis, commit/rollback boundaries; label downstream-service exclusion for review.
- **Planned verification:** UT-EVT-001, DT-004, REC-002; validate original request ID/recipients/payload, no publish before commit or on rollback, correct committed state during outage; EC-04/03.
- **Contingency:** Core HTTP success need not imply feed delivery. Report notification residual risk and extend downstream tests if instructor includes services; never count mocked producer as full SSE coverage.
- **Residual risk:** NOT MEASURED; original L=3, I=3 remains the planning assessment until verified controls justify a recorded revision. Owner A1 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed. *v0.2: ownership split — event producer and unit paths A1; end-to-end delivery (UC-07) Member 2.*

### JR-01 — Unsafe seed/reset, contaminated fixtures or incorrect generated constraints invalidate experiments

- **Evidence / classification:** S: `backend/leave/management/commands/seed_demo.py:17–28` overwrites users/balances, deletes all requests and uses current-relative dates. Safe deterministic reset not verified. H: a future generator could encode false constraints/oracles and falsely certify coverage; no generator currently exists. This is a project/testware assurance risk, distinct from PR-07 product acceptance failure. *v0.2: the same hazard applies to Docker Compose (the backend image runs `seed_demo` at startup on named volumes); mitigated by the isolated UC-07 procedure (TEST-PLAN, SU-06). Controls now executed: fail-closed disposable profiles `sqe-memory-v1` and `sqe-browser-v1` with metadata-only development-database checks (A2.0, A2.1, B1).*
- **Mitigation:** Isolate DB/Redis/browser workers, fixed dates/fixture hashes, fail-closed target guard, independent setup/teardown and repeat reset proof. Peer-review generated constraints against actual source/approved OpenAPI/rule manifest; do not infer maxDays26 or required leave_type from UI defaults.
- **Planned verification:** EN-03 plus WP-05, WP-12 and GEN-001; demonstrate identical initial state twice without touching development DB, independently check generated EP/BVA and two constraint changes, and mark experiments invalid if fixtures or oracles differ from their reviewed manifests.
- **Contingency:** Suspend affected tests SU-01/SU-04, preserve evidence, discard only owned disposable targets and repair reset/spec/generator; invalidate false conclusions and rerun. No valuable-data cleanup.
- **Residual risk:** NOT MEASURED; original L=4, I=4 remains the planning assessment until verified controls justify a recorded revision. Owner A2 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### JR-02 — Tool/runner incompatibility, unavailable Node/Sonar or incomplete gates delay or falsely green work

- **Evidence / classification:** V/S: current non-login node missing; npm version probe failed with WSL/install-directory error. `requirements.txt:1–6`, `.github/workflows/ci.yml:6–22` use differing local/CI toolchains; current CI lacks team/Sonar/mutation gates; auto-release follows successful main CI. *v0.2: Node 22.23.3, npm 10.9.9 and Playwright 1.49.1 verified in B1; Sonar, mutation and team CI gates still absent; the auto-release side effect is tracked separately as JR-05.*
- **Mitigation:** Record versions/support, repair compatible WSL runtime later, pilot free/open-source tools locally, add required jobs after functional pilots and tie release to tested SHA/full gate; reserve WP-05/06/17.
- **Planned verification:** Record version and real PR/gate logs; missing/failed/skipped required jobs block; retain genuine blocked and corrected PR; EC-07.
- **Contingency:** Continue source/spec/CFG planning while tools blocked; use local OSS services/runner capacity with genuine logs, not fake CI or success overrides.
- **Residual risk:** NOT MEASURED; original L=4, I=4 remains the planning assessment until verified controls justify a recorded revision. Owner A1 proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### JR-03 — Coverage denominator/MCC infeasibility and six actor-goal UCs remain unapproved

- **Evidence / classification:** Q: assignment p2 says all server-side business logic and two UCs/member; Phase1 COVERAGE-BOUNDARY and WORKFLOW-TRACE disclose missing-balance MCC masking and only3 strong actor goals. Detailed API coverage checklist is unspecified in PDF. *v0.2: the use-case catalog is PROPOSED (USE-CASE-SPECIFICATIONS.md). Instructor decision D-1 is a single point of failure for both UC-08 and UC-09 (fallback: reserve UC-06). The API checklist is no longer unspecified (Lecture 20 TCL criteria); denominator/MCC questions remain open.* *Critical module: PROPOSED in DR-001 (W1 validation chain) after the PR #2 review; instructor confirmation pending.*
- **Mitigation:** Obtain instructor decisions on scope/critical module/infeasible rows/UC goals/API checklist; preserve counts and IDs; allocate WP-01/02/09/15 with review dependency.
- **Planned verification:** Written actual approval/correction linked to denominator/UC specs; all six UCs and complete applicable MCC/derived MC/DC still required; EC-04/06.
- **Contingency:** Escalate early, propose reviewed scope adjustment within LeaveFlow, continue independent tasks; no artificial goal inflation or silent denominator reduction.
- **Residual risk:** NOT MEASURED; original L=4, I=5 remains the planning assessment until verified controls justify a recorded revision. Owner Shared proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### JR-04 — Unconfirmed allocation, review bottlenecks or lost prompts/evidence impair delivery/viva

- **Evidence / classification:** Q/S: complete named membership/area agreement not found; Phase1 historical baseline docs absent on current tree; prompt.md now Phase2 replaces Phase1 prompt location. No actual final deadline or availability supplied. *v0.2: every SQE commit to date is under one identity, while the assignment requires each member to commit their own work. Mitigation: the attribution rule in TEAM-OWNERSHIP v0.2.*
- **Mitigation:** Confirm roster/areas/capacity and section registration; retain original prompts and raw results, session actual-effort logs; peer reviews and stacked branches student-managed.
- **Planned verification:** Actual ownership acknowledgments, weekly GQM/effort/RTM link checks, final PDF/ZIP with .git, individual viva reruns and AI disclosure; EC-10.
- **Contingency:** Reallocate with agreement, record pending reviews and residual risk, continue independent work on authorized local branch; no fabricated approvals/authorship or backfilled effort.
- **Residual risk:** NOT MEASURED; original L=3, I=4 remains the planning assessment until verified controls justify a recorded revision. Owner Shared proposes actual residual values/rationale; peer reviews evidence. Status OPEN, no control completion claimed.

### JR-05 — Unintended releases from the fork's main

- **Evidence / classification:** S: `.github/workflows/auto-release.yml` runs on `workflow_run` of CI with `contents: write` when the CI run on `main` succeeds. Whether Actions are enabled on the fork is not verifiable locally.
- **Mitigation:** a guarded workflow condition restricting releases to the upstream repository (prepared on local branch `ci/fork-release-guard`), or disabling the workflow in the fork's Actions settings (student action). The guard must land before any SQE merge into `main`.
- **Planned verification:** after merge, confirm on GitHub that a successful CI run on `main` produces no release or tag in the fork; record the run link.
- **Contingency:** if a release is created, delete it through the GitHub UI (student) and record the incident; do not rewrite history.
- **Residual risk:** NOT MEASURED; L=3, I=3 proposed. Owner A1 (Member 1). Status OPEN.

## Updating risk and control decisions

At each weekly review and material defect/tool failure, record previous/new L,I,score, rationale, tested SHA, actual evidence, mitigation owner and due milestone. Re-sort with the same tie-break; if highest product risks change, revise strategy/schedule/criteria through controlled review while retaining original ranking history. Separate verified defects (real issue links) from risks and policy questions. No PR/JR ID is a GitHub Issue number. Test-data contamination is a project assurance risk; resulting actual product corruption would be recorded as a separate defect linked to relevant product risks. Dependency vulnerabilities are possible product exposure; inability to run an audit is JR-02 tooling risk, not a CVE.
