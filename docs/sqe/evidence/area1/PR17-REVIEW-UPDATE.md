# PR #17 review update draft

Area 1 white-box tests, MC/DC evidence, mutation analysis and SonarQube measurements are updated. The CFG text now describes the short-circuit balance condition accurately. The 15 historical surviving mutants have individual classifications and final outcomes. The mutation gate requires 85% with no unresolved results, and the SonarQube findings include the same-function comparison (hand CFG 5, SonarQube 4).

The local combined verification with PR #10 recorded 384 team tests, 296 of 299 mutants killed and a passing SonarQube gate. These are local measurements on the combined integration revision, not results of the current PR #17 head. The PR's hosted results must be updated after its branch is pushed and checked.

Team API, PostgreSQL and generator CI integration remains on `ci/integrate-team-tests-and-area1-evidence` because that workflow needs PR #10's files. It will be added to the final `dev` integration path after PR #10 is available. The repository admin must enable the required `Project quality gate` check on `dev` and `main` and confirm PR #27 is blocked by its failed check.

Related to #11, #12, #13, #14, #15 and #16.
