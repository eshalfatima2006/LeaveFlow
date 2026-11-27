# Passing fix pull-request evidence

## Documented fix within PR #17

- Before: [CI run 16](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/45453933225)
  at `5da5b953771e65ce8d94fc4de6d7ef036d0755ca` failed specifically at
  **Generate surviving-mutant analysis table**, after coverage, Sonar and mutmut passed.
- Fix: `5fe8483fd52ef25fcf9bd20e11bd14d5c7460c1c` corrected metadata path
  handling in `scripts/sqe/export_surviving_mutants.py`: pass the original source
  path to SourceFileMutationData, which adds the mutants prefix itself.
- After: [CI run 18](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/45457756653)
  passed that same evidence-generation step. Its overall run still failed at the
  subsequent mutation threshold, so it is not represented as an overall pass.
- Subsequent full pass: [run 74, attempt 4](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/46052602581)
  on `65e229da86c9563b15ac9a5ec240220025e97329` passed tests, critical
  coverage, SonarQube scan and gate, mutmut, and the 85% mutation threshold.
  Its historical raw score was 295/299 = 98.66%. Earlier attempts on that same commit
  failed when the temporary SonarQube tunnel was unavailable; they are not
  code-regression evidence.

This is an observed fail-before/pass-after code fix in the same PR. PR #27 is
the separate intentional blocked-check demonstration, not the before-state
of this exporter defect. These remote step conclusions were checked through
the GitHub Actions jobs API during this evidence audit.

This record demonstrates the pass-after state for the same Area 1 pull
request after the quality-gate fixes were applied.

- Pull request: [PR #17](https://github.com/eshalfatima2006/LeaveFlow/pull/17)
- Base branch: `dev`
- Head branch: `feat/area1-quality-engineering`
- Passing commit: `25253fff291e63795cbf19d7d64f37e5b694e3c8`
- Earlier verified remote workflow: [CI run 68](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/45705453697)

The passing run completed successfully for every required job. The Area 1
quality gate passed critical coverage enforcement, SonarQube analysis,
SonarQube quality-gate enforcement, mutmut execution, mutation evidence
generation, artifact upload, and the mutation-score threshold. The run
historical run 66 recorded 73 passing tests, 267 killed mutants, 30 surviving
mutants and an 89.90% mutation score against the former 60% threshold.
Run 68 confirms a successful gate at the updated documentation commit.
These historical figures must not be presented as the new integrated result.
The current PR #17 hosted run records 296 killed, 3 survivors and 99.00%
against the 85% threshold with no unresolved results. The historical 295/299
run is retained only as the earlier pass-before-the-latest-test update.

The fail-before and pass-after records are retained separately so the review
can verify that the workflow first blocked the change and then accepted the
corrected implementation.
