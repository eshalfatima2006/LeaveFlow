# Mutation testing procedure and surviving-mutant analysis

Mutation testing is run with mutmut on Ubuntu/WSL through
`scripts/sqe/mutmut_custom.py`. The wrapper registers two project-specific
operators before loading the normal mutmut CLI:

1. `operator_calendar_step`: changes the one-day inclusive date-loop step to a
   reverse one-day step;
2. `operator_overlap_truth`: inverts `overlap.exists()` in the active-overlap
   rule.

The standard mutmut operators remain enabled. The target is `backend/leave`,
the test selection is the complete pytest suite, and `mutate_only_covered_lines`
keeps the run focused on executable business logic rather than producing
untestable mutations in uncovered support files. The exact commands are:

```text
python -m pip install -r requirements.txt -r requirements-sqe.txt
python scripts/sqe/mutmut_custom.py run --max-children 2
python scripts/sqe/mutmut_custom.py export-cicd-stats
python scripts/sqe/check_mutation_threshold.py
```

The quality gate uses a documented 60% killed-mutant threshold over tested
mutants. This is the current tested-mutant baseline and prevents future
changes from reducing mutation effectiveness. The final report must still
explain all survivors. At least 15 surviving mutants must be listed with the
mutation, affected rule, killability judgement, and either the test that kills
it or the reason it is equivalent/unreachable. The report is not considered
complete until that table is generated from the mutmut result for the
submitted commit; no survivor result is invented in this repository.

After the run, generate the candidate table with:

```text
python scripts/sqe/export_surviving_mutants.py
```

The command exits non-zero until at least 15 survivors exist, which prevents a
missing or incomplete survivor-analysis artifact from being mistaken for a
completed assignment requirement.
