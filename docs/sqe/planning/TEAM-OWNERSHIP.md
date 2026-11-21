# Proposed ownership and peer review

Version0.1, 22 November 2026; **allocation NOT CONFIRMED**. Three members are required. No existing project record inspected confirms the complete membership/roll numbers or their agreed areas; consequently this plan uses Member1/Member2/Member3 and A1/A2/A3, rather than treating the names in prompt.md as confirmed records. Students must fill names/rolls/section and acknowledge allocation before implementation ownership is reported as agreed.

| Area / proposed member | Accountable outputs | Cross-review | Agreement |
|---|---|---|---|
| A1 / Member1, identity PENDING | SonarQube metrics, manual CFG/complexity comparison, unit/statement/branch coverage, MCC/MC/DC, mutation operators/survivors, strict PR CI gates | A2 reviews rule/coverage assertions; A3 reviews CI evidence | PROPOSED |
| A2 / Member2, identity PENDING | Accurate OpenAPI, API EP/BVA/decision/state/integration tests, generator and two-constraint regeneration; returned-ID persistence readback | A1 reviews generator/rule combinations; A3 reviews HTTP/oracle evidence | PROPOSED |
| A3 / Member3, identity PENDING | Playwright architecture/use cases, task/keyboard/accessibility, local passive security/dependency audit, k6 and recovery | A2 reviews persistence/load datasets; A1 reviews failure/transaction controls | PROPOSED |

A3 coordinates browser infrastructure, **not all six UCs alone**. Proposed distribution preserving Phase1 candidates: Member1 UC-01/UC-04, Member2 UC-02/UC-05, Member3 UC-03/UC-06. UC-04–06 distinctness is unapproved; even UC-02/03 separation needs review under actor-goal interpretation. Allocation is conditional on six accepted goals and each member writing/automating two with main+≥2 alternatives+≥2 exceptions. Reallocate after scope/skill/capacity discussion without relabelling variations as new goals. Each author must explain their implementation and assertions in the viva; cross-area learning is mandatory.

## RACI-style collaboration matrix

R=does work, A=answerable owner, C=consulted reviewer, I=informed. For shared management, the lead rotates by report/session; record the actual lead before work so “shared” does not mean unowned. Allocation is proposed; no human agreement implied.

| Deliverable/activity | A1 | A2 | A3 |
|---|---|---|---|
| Static/CFG, white-box, MCC/MC/DC | A/R | C | I |
| Mutation and CI/gate evidence | A/R | C | C |
| OpenAPI/generator/API/decision/state | C | A/R | C |
| Shared-record integration | C | A/R | R (browser readback support) |
| Browser framework and UC review | C; R own two UCs | C; R own two UCs | A/R framework; R own two UCs |
| Accessibility/task/keyboard and before/after fix | C | C | A/R |
| Security/passive audit and access matrix | C | R API controls | A/R |
| k6 datasets and performance | C | R data review | A/R |
| Controlled write failure/recovery | R transaction review | R persisted assertions | A/R orchestration |
| Scope, requirements, strategy, risk/criteria/RTM | R (lead rotates) | R (lead rotates) | R (lead rotates) |
| Defect triage, 5Whys/fishbone/Pareto | R; A for own area defect | R; A for own area defect | R; A for own area defect |
| Weekly GQM/effort/completion/PDF/ZIP | R (lead rotates) | R (lead rotates) | R (lead rotates) |
| Release/hold decision, AI disclosure and viva | A/R shared review | A/R shared review | A/R shared review |

Shared accountability in final decision is intentional: record all three actual approvals or unresolved disagreements. Each artifact still has a named session lead and independent reviewer in its revision history. See [TEST-PLAN](TEST-PLAN.md) for release/hold process and [DEFECT-MANAGEMENT-PLAN](DEFECT-MANAGEMENT-PLAN.md) for individual defect ownership.

## Review and contribution procedure

Before execution, members confirm identities/section, chosen areas, availability, six UC goals, peer reviewers and estimates. Review scope/oracles with source, not only generated prose. One reviewer checks arithmetic/IDs/evidence, another samples technical assertions and gate limitations; record actual changes and review dates only when they occur. Students own PR reviews, protected-main decisions and genuine commits; no credential sharing, artificial author attribution or token contributions. Authorship reflects work actually performed, while AI drafting remains disclosed.

At every week-end reporting session, compare area hours and blockers, redistribute future work with agreement and leave past actual effort unchanged. All three participate in requirements, planning, risk, traceability, defect lifecycle/RCA, metrics, completion, peer reviews, AI record and viva rehearsal. Every member should rerun another area's selected test and explain why it asserts persisted state. Do not infer team approval from an AI-generated ownership table or a commit containing draft documentation.
