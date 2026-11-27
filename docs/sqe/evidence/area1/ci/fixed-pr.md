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
- Final passing candidate: run 68 below completed the whole quality job.

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
- Latest verified remote workflow: [CI run 68](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/45705453697)

The passing run completed successfully for every required job. The Area 1
quality gate passed critical coverage enforcement, SonarQube analysis,
SonarQube quality-gate enforcement, mutmut execution, mutation evidence
generation, artifact upload, and the mutation-score threshold. The run
historical run 66 recorded 73 passing tests, 267 killed mutants, 30 surviving
mutants and an 89.90% mutation score against the former 60% threshold.
Run 68 confirms a successful gate at the updated documentation commit.
These historical figures must not be presented as the new integrated result.
The local integrated run now records 296 killed, 3 equivalent survivors and
99.00%; its score gate requires at least 85%, with no unresolved results.
It still needs a new hosted run after the user authorizes pushing this branch.

The fail-before and pass-after records are retained separately so the review
can verify that the workflow first blocked the change and then accepted the
corrected implementation.
