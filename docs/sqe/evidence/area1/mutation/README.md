# Mutation testing procedure and surviving-mutant analysis

Mutation testing is run with mutmut on Ubuntu/WSL through
`scripts/sqe/mutmut_custom.py`. The wrapper registers two project-specific
operators before loading the normal mutmut CLI:

1. `operator_calendar_step`: changes the one-day inclusive date-loop step to a
   reverse one-day step;
2. `operator_overlap_truth`: inverts `overlap.exists()` in the active-overlap
   rule.

The standard mutmut operators remain enabled. The target is the application
code under `backend/leave` plus the runtime configuration in
`backend/config/settings.py`; migrations and the legacy upstream test module
are excluded. The complete pytest suite is used so the report can identify
both well-tested critical logic and under-tested supporting logic. The exact
commands are:

```text
python -m pip install -r requirements.txt -r requirements-sqe.txt
python scripts/sqe/mutmut_custom.py run --max-children 4
python scripts/sqe/mutmut_custom.py export-cicd-stats
python scripts/sqe/check_mutation_threshold.py
```

The quality gate uses a documented 60% killed-mutant threshold over tested
mutants. This is the current tested-mutant baseline and prevents future
changes from reducing mutation effectiveness. The final report must still
explain any survivors. At least 15 evaluated mutants must be listed with the
mutation, result, affected rule, killability judgement, and either the test
that kills it or the reason it survives. If the submitted run has no
survivors, the report records 15 real killed mutants and states that no
survivor result exists; no survivor result is invented in this repository.

After the run, generate the candidate table with:

```text
python scripts/sqe/export_surviving_mutants.py
```

The command exits non-zero until at least 15 evaluated mutants exist, which
prevents a missing or incomplete mutation-analysis artifact from being
mistaken for a completed assignment requirement.
