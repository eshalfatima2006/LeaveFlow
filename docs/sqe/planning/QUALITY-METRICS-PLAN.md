# GQM, weekly control and completion measurements

Version0.1 — 22 November 2026; proposed definitions, not measured results. Goal–Question–Metric chains below support decisions rather than reward a large test count. Targets not mandated numerically by the assignment are **provisional team choices**. Mandatory100% coverage/counts are not negotiable reductions. All current future-execution metrics are **NOT MEASURED**; no zero placeholder, fake Sonar score, vulnerability count, performance figure or PR evidence is supplied.

## Measurement rules

Use a fixed tested SHA/profile, approved source/requirement population, consistent reporting period and unique case/defect IDs. Retain raw reports and calculation inputs with hash/version. No data yet=NOT MEASURED; denominator0=N/A with reason; a mandatory unmet requirement stays blocked even if a formula is N/A. Define scoped vs whole-file/unit vs API vs browser populations explicitly. Upstream tests/coverage earn no student credit and are reported separately. Multiple tools finding/testing the same item do not create additional distinct coverage or defects.

A2 maintains requirement/input populations; A1 coverage/Sonar/mutation/CI; A3 browser/security/performance; shared weekly lead maintains defect/risk/actual-effort records. Peers review source data and any exclusion/denominator change before publication. Weekly snapshots retain older states; do not rewrite failures as if the later pass was the initial outcome.

## Ten GQM chains

### GQM-01 — Requirements coverage

- **Goal/question:** Show every selected actor requirement has meaningful implemented and passing assertions. Which requirements have executable tests? Which have passed on this candidate? Which are blocked despite planned links?
- **Metrics/formulas:** Planning trace completeness=`distinct FRs with reviewed planned objective /12 ×100`; implemented coverage=`distinct FRs with at least one meaningful implemented assertion /12 ×100`; passing coverage=`distinct FRs with required assertions passed on candidate /12 ×100`. Numerators count FRs once, not test IDs; denominator is the controlled12 FRs until approved scope changes. Also report6-BR assertion coverage separately.
- **Source/cadence/owner/target:** Reviewed RTM + actual runner/assertion evidence; update each run and report **weekly**; A2. Targets implemented/passing100% and all6 BRs verified (EC-04/05). Current structural planning links alone do not establish these targets.
- **Interpretation/limits:** One weak happy-path assertion cannot prove complete requirement behavior. Report required EP/decision/state/exception obligations and blocked IDs alongside the coarse FR ratio; never call75 proposed objective IDs75 implemented tests.

### GQM-02 — Defect density

- **Goal/question:** Understand defect discovery concentration in a stable selected source boundary. How many unique verified product defects were found relative to code size, and where?
- **Formula/population:** `D / (SLOC/1000)` defects/KLOC. D=distinct canonical, triaged **verified product** defects discovered from pinned-baseline testing start to reporting cutoff, including later closed defects; exclude duplicates/rejected/policy-only/testware items. SLOC=nonblank, noncomment production source lines in approved business boundary at stated SHA (exclude tests, generated/vendor code; keep tool definition and file list). Report Python and any separately approved TS/Elixir populations transparently; do not combine inconsistent denominators.
- **Source/cadence/owner/target:** Real Issue export/lifecycle history plus reproducible line-count tool/config/hash; shared lead, A1 supplies source denominator; **weekly** and completion. No universal “low density means good” release number is proposed; target100% valid classification/population disclosure and investigate sharp changes before release review.
- **Interpretation/limits:** Higher discovery may reflect better testing, not worse code. Unreproduced PR-01 is not yet counted as an executed defect. Changing scope/size needs a new labelled series or like-for-like recalculation, not apparent risk reduction.

### GQM-03 — Defect reopen rate

- **Goal/question:** Check corrective-action and closure quality. Are independently verified fixes recurring, and are weak assertions allowing premature closure?
- **Formula/population:** C=distinct canonical verified product issues closed at least once up to reporting cutoff; R=distinct issues in C reopened at least once by cutoff. Cumulative reopen rate=`R/C ×100`; also list new/closed/reopen **events during the week**, without mixing event counts with distinct-issue denominator. C=0→N/A, not0%.
- **Source/cadence/owner/target:** Genuine issue transition history and independent retest evidence; shared triage lead; **weekly**. Provisional monitoring target≤10%; any S1/S2 reopen triggers root-cause review regardless of rate and blocks affected criterion until resolved.
- **Interpretation/limits:** Small cohorts are unstable; repeated reopen events on one issue are not multiple unique defects. Do not delay closure or reclassify real regressions merely to improve a percentage; report underlying counts/history.

### GQM-04 — Statement/branch coverage and rule-condition completeness

- **Goal/question:** Demonstrate all approved server business logic is exercised with meaningful outcomes. Which statements/arcs/conditions remain untested or infeasible?
- **Formulas:** Statement=`executed executable statements /all executable statements ×100`; branch=`executed measured branch destinations /all measured branch destinations ×100` from recorded coverage.py report. Retain raw whole-file and approved-boundary figures/exceptions. MCC=`feasible critical-module truth rows executed and asserted /all feasible rows ×100`, with theoretical row count and individually reviewed infeasibility separate; MC/DC=`required independent-condition demonstrations evidenced /approved required demonstrations ×100` with MCC pair references.
- **Source/cadence/owner/target:** Team runner/coverage raw JSON/XML/HTML, approved file/function list, CFG and truth tables, tool/config version; A1, each relevant change/CI run and weekly. Targets **100% statements/100% branches**, complete critical-module MCC and derived MC/DC (EC-04); no achieved percentages now.
- **Interpretation/limits:** Coverage is necessary but not proof of correct assertions. Short-circuit masked E when balance absent is not an observed false value. SQL query predicates are not automatically Python branches; cyclomatic complexity is not branch count. No source omitted solely to reach100%.

### GQM-05 — Mutation sensitivity

- **Goal/question:** Determine whether tests detect meaningful rule changes. Which live mutants reflect equivalent behavior, missing cases or weak assertions?
- **Formula/population:** K=killed valid completed mutants; L=live non-equivalent; E=independently justified equivalent. Raw score=`K/(K+L+E) ×100`; adjusted=`K/(K+L) ×100`. Report generated/invalid/timeout/unclassified separately; timeout is not a kill and blocks final evaluation. Zero denominator=N/A, never100%. Custom-operator counts and analyzed genuine survivors reported separately (≥2 and≥15 required).
- **Source/cadence/owner/target:** Mutation tool output/config, operator code when later implemented, survivor classification/evidence and rerun logs; A1; pilot, after relevant tests/fixes, required CI and weekly snapshot. Provisional adjusted gate≥85%, all killable analyzed survivors addressed, no unknown/timeouts; final threshold review before gate (EC-07).
- **Interpretation/limits:** Equivalent labels need proofs/peer review, not convenience. A score alone cannot replace15 survivor analyses, full coverage or custom operators. Fewer than15 genuine survivors requires documented scope/instructor resolution, not fabricated entries or silently relaxed count.

### GQM-06 — Test execution pass rate

- **Goal/question:** Understand actual regression outcome and execution gaps. Are required tests passing or merely skipped/unrun?
- **Formula/population:** `passed unique executed cases /(passed+failed+errored unique executed cases) ×100`, reported separately per unit/API/browser/nonfunctional level and tested candidate. Also report blocked/skipped/not-run obligations and executed/required count; they are not passes. A negative-input case expecting400 can pass; HTTP400 is not itself a test failure.
- **Source/cadence/owner/target:** Team JUnit/runner/Playwright manifests, deduplicated node IDs and actual expected assertions; each area owner, per run and weekly. Release requires100% required executed cases pass with no undisposed mandatory blocked/skipped obligations, not a green fraction after filtering failures.
- **Interpretation/limits:** Expected failures/xfails of the desired approval safeguard remain open failures of EC-01 even if runner exits0. Repeated tool invocations of the same case do not inflate coverage; preserve retry/flaky failures alongside final attempt. Zero executions=N/A/NOT MEASURED as appropriate.

### GQM-07 — Evidence-based risk reduction

- **Goal/question:** Check whether high-priority controls genuinely reduce residual exposure. Are PR-01/PR-02 verified and are major unknowns still blocking?
- **Formula/population:** For the fixed approved initial product-risk cohort, R0=sum(initial L×I), Rt=sum(actual peer-reviewed residual L×I for that **same cohort**). Reduction index=`(R0−Rt)/R0 ×100`; also report count of top risks with passing linked controls /top risks and open release-blocking risks. If any residual score is unknown, do not present a complete numeric reduction; show incomplete cohort/status.
- **Source/cadence/owner/target:** Versioned risk register, linked genuine tests/defects and residual rationale; shared risk lead, weekly and after major findings. Target both highest risks' linked ECs satisfied,100% residual dispositions evidenced and no release-blocking unknowns. No arbitrary percentage reduction promises release.
- **Interpretation/limits:** Ordinal-score sum is a planning index, not calibrated probability, loss or statistical proof. Merely writing mitigation or spending hours does not lower likelihood. New risks are shown separately and baseline changes disclosed.

### GQM-08 — API negative-input and generated-data completeness

- **Goal/question:** Verify systematic rejection and robustness rather than a few handpicked bad values. Are every identified invalid partition and applicable boundary tested with correct no-write outcomes?
- **Formulas/populations:** Negative EP coverage=`invalid classes with executed/asserted outcome /all reviewed applicable invalid classes ×100`; BVA coverage=`executed/asserted applicable below/at/above obligations /all reviewed applicable ordered-boundary obligations ×100`; generator consumption=`API data-case IDs actually consumed /all applicable generated API IDs ×100`. Track valid classes, decision rows/state-event obligations separately, and exact N/A/infeasible reasons. Each denominator comes from versioned spec/rule/case manifest, not arbitrary total request count.
- **Source/cadence/owner/target:** OpenAPI/manifest hashes, generator output and runner consumption IDs, persisted readback; A2, each spec/generator change and weekly. Targets100% applicable obligations, two changed constraints demonstrably regenerated and consumed; meet additional instructor API checklist when supplied (EC-05).
- **Interpretation/limits:** Categorical roles/types have EP, not fabricated numeric BVA. Omitted type/default and absent balance behavior must not be invented as reject rules. One invalid class per test except explicit compound-rule cases; invalid input receiving500 instead of reviewed400 is failure, not rejection success.

### GQM-09 — CI quality-gate compliance

- **Goal/question:** Ensure actual candidate PRs cannot merge/deploy with missing/failing quality evidence. Which PRs have the full required gate set on their exact SHA?
- **Formula/population:** `candidate PR SHAs with every required job and quality gate genuinely passed /all in-scope candidate PR SHAs evaluated in reporting period ×100`. Required set includes team tests, Sonar, mutation and applicable browser/API/generated obligations, with full coverage target. Missing/skipped/overridden job is noncompliance, not excluded denominator; zero PRs evaluated=N/A.
- **Source/cadence/owner/target:** Actual Actions job/task/gate outputs, tested SHA and required-check settings inspected by students; A1, each PR and weekly. Target100% release-candidate compliance; evidence of ≥1 genuinely blocked PR and documented fix failing before/passing after; no escape hatches (EC-07).
- **Interpretation/limits:** A current upstream green build is not the planned assignment gate. A local report alone is not a PR result. Staged tool implementation does not permit a final partial gate; auto-release/main CI linkage must be reviewed.

### GQM-10 — Performance and reliability

- **Goal/question:** Check response budgets under reproducible local loads and verify safe restoration after controlled failure. Do all required runs satisfy budgets and preserve state?
- **Formulas/populations:** Per declared steady-state run p95 from k6 samples (including failed-operation latency, setup excluded); throughput=`completed selected-operation requests /measured seconds`; unexpected failure rate=`requests with unexpected status/body/check or transport error /all selected-operation requests ×100` (count a request once even with multiple failed checks). PERF-001 expects201, so4xx/5xx/transport/wrong body are unexpected. Recovery pass requires persisted no-write on injected prewrite failure then exactly one correct result on restore/retry, not merely a successful HTTP call.
- **Source/cadence/owner/target:** k6 raw series/summary and environment/fixture manifest; controlled fault/retry DB logs; A3 with A2 verification; four required runs after stable build and on impactful change, weekly summary. Provisional per-run p95≤500ms, unexpected failure<1%;1VU/5VUs twice each, ≥60s after target reached; recovery integrity100% of planned assertions (EC-03/09).
- **Interpretation/limits:** No measured values now. Compare runs individually; same build/machine/profile/initial data; row growth, pacing, SQLite locks and disabled notifications limit generalization. Do not average away a failing run, omit errors or change budgets after observation without new approved protocol.

## Weekly progress and control template

Copy for each real reporting period; retain actual date range/timezone, reviewed SHA and links. All absent measurements below intentionally say NOT MEASURED, not0. Required weekly management metrics are **defect density, requirements coverage and defect reopen rate**; report source populations and numerator/denominator even when small.

| Weekly field | Value to enter from genuine records |
|---|---|
| Actual period / lead / reviewers | PENDING |
| Commit/build, dirty diff, DB/profile/tool/fixture/spec hashes | PENDING |
| Milestones/packages planned vs delivered | PENDING; link [effort estimates](EFFORT-ESTIMATION.md) and [roadmap](EXECUTION-ROADMAP.md) |
| Tests implemented, executed, passed/failed/errored/blocked/skipped by level | NOT MEASURED; include unique IDs and rerun/flaky history |
| Statement/branch coverage, denominator/exceptions | NOT MEASURED |
| Requirements coverage (planned /implemented /passing) and BR coverage | NOT MEASURED for execution; planning links separately labelled |
| Open verified defects by severity; new/closed/reopened this week | NOT MEASURED |
| Defect density /D/SLOC/population | NOT MEASURED |
| Reopen rate /R/C/history | NOT MEASURED |
| Mutation raw/adjusted /K/L/E/invalid/timeouts/survivors | NOT MEASURED |
| API valid/invalid/BVA/decision/state coverage; generator consumption | NOT MEASURED |
| CI gate compliance, real blocked/fix PR links | NOT MEASURED |
| Browser flows/accessibility/security observations and before/after links | NOT MEASURED |
| Performance p95/rps/errors per run, recovery verdict | NOT MEASURED |
| Top product/project risks, prior→current scores and actual controls | PENDING review; proposed ranking in register is not measured residual reduction |
| Estimated vs actual person-hours and remaining forecast by package | Actual/variance NOT MEASURED until session logs exist |
| Blockers, deviations and suspension/resumption records | PENDING |
| Control actions with actual owner/next milestone and effectiveness check | PENDING |
| Next dependency-ready tasks and evidence links | PENDING |

A weekly report must interpret change and select control action: e.g. if schema review blocks generated cases, prioritize A2 spec review and continue A1 CFG; if high-risk regression persists, hold dependent load work and assign reproduction/retest. Examples are planning instructions, not a claim these actions occurred. Record actual estimate variance only from logs; do not backfill human effort from AI runtime or commit timestamps.

## Pareto and completion use

Use canonical verified product defects and a stated discovery window; assign one primary causal category per defect after triage/RCA, group and sort descending count (ties category name), cumulative percentage=`cumulative distinct defect count /total distinct defects ×100`. Retain raw issue-ID→category input and classification rationale. Duplicate tool discoveries/cross-workflow symptoms of one issue count once. With no verified dataset, frequencies/chart are NOT MEASURED, not empty evidence of quality. Do not assume an80/20 distribution in advance.

Final completion report must state tested/not tested, scope deviations, actual vs planned effort, open defects, residual risk **per risk**, targets vs actual for EC-01/02/04 headline criteria and every other gate, and release/hold rationale with real evidence/reviewers. Weekly trends and Pareto help explain causes/control effectiveness; they do not override a failed mandatory criterion. See [DEFECT-MANAGEMENT](DEFECT-MANAGEMENT-PLAN.md) and [ENTRY-EXIT](ENTRY-EXIT-CRITERIA.md).
