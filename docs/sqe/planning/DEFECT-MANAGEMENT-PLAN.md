# Defect lifecycle and root-cause plan

Version0.1 — 22 November 2026; proposed workflow, no GitHub Issues created and no defect reproduced by Phase2. [RISK-REGISTER](RISK-REGISTER.md) contains risks, static observations and questions; they are **not** an issue list. A finding becomes a verified product defect only when evidence demonstrates deviation from a source/documented or explicitly reviewed desired requirement. Unclear zero-day/missing-balance/year policy requires an oracle decision before alleging noncompliance.

## Lifecycle, owners and allowed dispositions

Primary lifecycle: **New → Triaged → Assigned → In Progress → Fixed → Retest → Closed**. In Progress means actual change work, not a source observation. Fixed means proposed correction is ready for independent verification, not that the author has closed it.

| Transition / disposition | Required evidence and decision | Owner / reviewer |
|---|---|---|
| Finding→New | Repro steps, expected basis, observed result, synthetic data, tested SHA/config and raw evidence; source-only findings explicitly labelled unverified investigation | Discoverer submits manually |
| New→Triaged | Reproduce or document uncertainty; agree validity/severity/priority/risk/requirement links and affected scope | Shared triage, independent reproducer |
| Triaged→Assigned→In Progress | One actual owner, corrective plan and regression objective; active authorized work begins | Relevant A1/A2/A3 owner |
| In Progress→Fixed | Fix commit/PR, changed code/spec, failing-before/passing-after regression and impact analysis; no history mutation by Codex in this phase | Student fixer, peer review |
| Fixed→Retest | Independent reviewer runs regression and impacted suite on exact proposed candidate/environment | Independent tester |
| Retest→Closed | Expected behavior and persisted postconditions verified; evidence linked; CI/gates and residual risk assessed; no hidden failures | Independent retester + triage agreement |
| Retest/Closed→Reopened | Same underlying defect demonstrably persists/recurs, actual evidence and reason; preserve prior closure history | Any tester; triage reconfirms |
| New/Triaged→Duplicate | Link canonical verified issue, show same root cause/outcome; keep discovery evidence but count only canonical defect | Triage |
| New/Triaged→Rejected with justification | Evidence of expected behavior/nonreproducibility/incorrect oracle; state reason and source, not “cannot fix”; policy unresolved remains question/blocked investigation | Triage with reviewer |
| Triaged/Assigned→Deferred | Actual owner/risk acceptance/rationale/revisit milestone; cannot bypass release-blocking criteria or mandatory instructor work | Shared decision; instructor exception if needed |

Reopened returns to Assigned/In Progress after triage. A failed retest is not automatically a distinct new defect. New root cause merits a separate linked issue; one defect observed in API/UI/unit is counted once in Pareto/density. Invalid testware findings are tagged testware and excluded from product-defect density unless separately reporting that population.

## Severity, priority and escalation

Severity reflects verified impact; priority reflects urgency/order including exposure and dependencies. Both are proposals until triage; risk likelihood×impact is a separate planning measure.

| Severity | Meaning / examples of verified impact | Default response |
|---|---|---|
| S1 Critical | Broad unauthorized personnel exposure, destructive corruption or core system unusable with no safe workaround | Stop affected experiments; immediate shared triage; release HOLD |
| S2 Major | Material wrong entitlement, unauthorized decision, invalid irreversible state or repeat/recovery corruption in selected workflow | Prioritize regression/fix and persisted-state checks; affected EC blocks release |
| S3 Moderate | Task interruption, localized wrong feedback or recoverable function error with workaround; impact must be evidenced | Risk-based scheduling and retest; may still block mandatory usability criterion |
| S4 Minor | Cosmetic/local text or layout issue without material task failure | Backlog with explicit rationale; no promotion to major to fill RCA quota |

P1=next executable work before dependent activities; P2=within current dependency-ready milestone; P3=planned later milestone with accepted residual risk; P4=deferred future improvement with revisit condition. A verified balance overdraw is a strong S2/P1 candidate, not automatically an executed S1 incident. Missing keyboard feedback could block EC-06 without being a major integrity defect. Security severity also considers actual advisory/impact evidence; no unverified CVE gets a fabricated rating.

Escalate any suspected S1/S2 access/corruption issue to the shared team during the active session; suspend affected destructive/retry/load paths and preserve state (SU-02). Independently reproduce before final severity. Unavailable tooling or ambiguous oracle is a blocker/question, not a manufactured product issue. Routine triage occurs each shared session, with an explicit weekly review of open/high risks and deferred cases. No email/chat message or GitHub Issue is sent by this documentation work.

## Proposed GitHub Issue template (text only)

Students may manually copy the following template when a genuine finding is ready. No `.github/` template file is created and no issue number/URL is invented.

```text
Title: [workflow] concise observed failure
Evidence classification: executed / static unverified / policy question
Tested commit and working diff:
Environment/profile, tool versions, DB/fixture/spec hashes:
FR / BR / risk IDs / planned or implemented test IDs:
Severity proposal / priority proposal / rationale:
Preconditions and synthetic initial state:
Reproduction steps (HTTP/UI actions and original request k):
Expected result and exact test-basis source or reviewed assumption:
Observed result (status/body/UI; raw evidence link):
Persisted before/after (owner/status/decided_by/decided_at/count/balance):
Frequency and independent reproduction evidence:
Logs, sanitized request/response, screenshots/trace and correlation IDs:
Assigned owner / triage decision / status:
Root cause and RCA link (if verified major):
Corrective action / preventive action:
Fix commit / real PR URL / regression ID:
Retest SHA, independent tester, actual result and evidence:
Residual risk / closure or reopen reason:
```

Protect tokens, cookies/passwords and real user data; keep synthetic IDs/correlation sufficient for replay. Do not edit raw reports/screenshots to misrepresent behavior. Link genuine future issues back into the RTM's defect field only after creation. Distinguish designed expected values, measured actuals and source predictions in every report.

## Two major-defect RCA cases — planned, not fabricated

**RCA case1 candidate:** PR-01 approval-time balance guard absent (`backend/leave/views.py:81–86`); reproduce Phase1 allowance5/two nonoverlapping4-day pending requests scenario through W1→W2 original IDs. Source predicts second approval succeeds and remaining becomes−3; that is a prediction, not this phase's observed result. The desired rule and error contract are confirmed (25 Nov 2026: 400 `{"detail": "Insufficient leave balance"}`; GAP-01), and the −3 has since been executed (API-INT-001.09, [RCA 1](../defects/RCA-MAJOR-01-BALANCE-OVERDRAW.md)). Still first: reproduce independently, record state and triage actual major severity. Then investigate the true cause rather than populate a plausible five-whys narrative as fact.

**RCA case2:** **UNIDENTIFIED — depends on an independently verified major defect.** Candidates for investigation include PR-03/PR-10 concurrency/recovery, not guaranteed second defects. Must have distinct verified impact/root cause, actual reproduction and triage; multiple symptoms of case1 cannot satisfy two independent cases. If no second major finding emerges, broaden legitimate high-risk testing and seek instructor guidance; never relabel a minor UI issue as major or invent an issue to meet the rubric.

For **each** verified major case, retain:

1. Problem statement, requirement/risk, genuine issue URL, exact build/fixture/environment and independent reproduction.
2. **Five Whys:** each why asks why the preceding evidenced failure occurred, with source/log/process evidence, alternative explanation and confidence. Stop at a supported actionable cause; five numbered guesses are not analysis. Separate technical cause from process/control failure.
3. **Fishbone:** structured categories **Code/logic**, **Data/state**, **Concurrency/transactions**, **Specification/policy**, **Tools/environment**, **Process/review/test design**, **People/knowledge**. Under each record causal hypothesis, validating/refuting evidence and verified cause status; an exported diagram may be made later. No diagram is falsely presented as completed here.
4. **Corrective action:** precise reviewed fix restoring the rule, with pre/post DB assertions, actual fix SHA/PR and regression. **Preventive action:** rule review, stronger boundary/decision/mutation assertions, isolation/locking design or CI control addressing recurrence; name owner, completion evidence and effectiveness review.
5. Independent retest, impacted regression suite, same-SHA gates and explicit residual risk/closure verdict. Demonstrate a real failing check before and passing after; no manufactured screenshots/CI logs.
6. Assign one primary root-cause category for Pareto; link related causes without double counting.

## Pareto, regression and evidence control

Use only canonical triaged verified product defects in a stated reporting window (exclude duplicates/rejected/questions and separately label testware defects). Group primary cause into validation/boundary, authorization, state/transaction, schema/contract, UI/accessibility, dependency/configuration, notification/recovery or other justified category. Count actual distinct defects, sort descending frequency then category name for ties, calculate cumulative count/total×100 and plot later with retained input data. A defect found by Lighthouse and axe or API and UI is one finding if the same underlying issue. No frequencies or 80/20 conclusion exist now; see [QUALITY-METRICS](QUALITY-METRICS-PLAN.md).

Closed fixes remain linked to team regression tests under `tests/team/` when implemented; changing an expected assertion to match the defect does not close it. Current upstream tests remain separate and are not student-authored evidence. [EC-01/02/03/07/10](ENTRY-EXIT-CRITERIA.md) control integrity, gates and required RCA completion; deferred defects cannot silently remove a blocker. Keep creation/triage/fix/retest/reopen history for weekly density/reopen calculations and final release/hold report.
