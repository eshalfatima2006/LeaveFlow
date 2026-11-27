# PR #17 review update draft

Area 1 white-box tests, MC/DC evidence, mutation analysis and SonarQube measurements are updated. The CFG text now describes the short-circuit balance condition accurately. The 15 historical surviving mutants have individual classifications and final outcomes. The mutation gate requires 85% with no unresolved results, and the SonarQube findings include the same-function comparison (hand CFG 5, SonarQube 4).

The local combined verification with PR #10 recorded 384 team tests, 296 of
299 mutants killed and a passing SonarQube gate. Those are local measurements
on a different integration revision. PR #17's own hosted run 74 attempt 4
passed its current checks at 295/299 (98.66%). The four surviving mutants
were identified by a repeat run of the exact PR tree; the critical models,
serializers and views files killed 65/65. Three survivors are equivalent and
the event-recipient survivor was a missing-test gap. A new manager/admin
requester assertion kills that mutant in focused verification. The hosted
295/299 result remains the current PR result until CI runs on the revised head.
The complete revised local run records 296/299 (99.00%) with only three
equivalent survivors.

Team API, PostgreSQL and generator CI integration remains on
`ci/integrate-team-tests-and-area1-evidence` because that workflow needs PR
#10's files. It will be added to the final `dev` integration path after PR #10
is available. The active `CI_Checks` ruleset already requires `Area1 quality
gate` on `dev` and `main`. `Project quality gate` exists only in the unpushed
integration workflow and must not be required until it runs on GitHub. PR #27
has a failed Area1 check and should remain open and unmerged as the blocked
example.

Related to #11, #12, #13, #14, #15 and #16.
