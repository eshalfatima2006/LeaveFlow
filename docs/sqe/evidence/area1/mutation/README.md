# Mutation testing procedure and surviving-mutant analysis

Mutation testing is run with mutmut on Ubuntu/WSL through
`scripts/sqe/mutmut_custom.py`. The wrapper registers two project-specific
operators before loading the normal mutmut CLI:

1. `operator_overlap_boundary`: changes inclusive interval comparisons to
   exclusive comparisons, generating two boundary mutants;
2. `operator_overlap_truth`: inverts `overlap.exists()` in the active-overlap
   rule.

The standard mutmut operators remain enabled. The target is the application
code under `backend/leave` plus the Django runtime configuration in
`backend/config`; migrations and the legacy upstream test module are excluded.
The complete pytest suite is used so the report can identify both well-tested
critical logic and under-tested supporting logic. The exact commands are:

```text
python -m pip install -r requirements.txt -r requirements-sqe.txt
python scripts/sqe/mutmut_custom.py run --max-children 4
python scripts/sqe/mutmut_custom.py export-cicd-stats
python scripts/sqe/check_mutation_threshold.py
```

The quality gate now requires **85% raw killed/total**, aligned with the proposed
project strategy rather than the former 60% placeholder. This retains room for
equivalent mutants while rejecting material loss of test effectiveness.
No untested, skipped, timed-out, suspicious, interrupted or unclassified mutants
are accepted. The combined local measurement is **296/299 = 99.00%**; the
latest hosted PR #17 measurement is **295/299 = 98.66%**. Both custom operator
families generated mutants that were killed. The three critical files have a
separate combined-local result of **65/65 killed** (models 24, serializers 36,
views 5). These denominators and provenance are documented in
`surviving-mutants.md`.
The exact PR #17 tree had a fourth, killable event-recipient survivor, E-10.
`tests/team/unit/test_events.py` now covers manager/admin self-exclusion,
and `scripts/sqe/verify_event_recipient_mutant.py` demonstrates a passing
baseline and a failing exact mutant in a disposable source copy. The next
hosted full run must confirm the aggregate score after this test addition.
The individually reviewed first 15 historical survivors and their final outcomes
are in `surviving-mutants.md`; raw diffs and metadata are in `final/results.json`.
Support-code survivors are explicitly distinguished from the DR-001 rule scope.

After the run, generate the candidate table with:

```text
python scripts/sqe/export_surviving_mutants.py
```

The exporter creates `mutation-candidates.md`, including actual diffs. It never
overwrites the curated analysis or labels every survivor a missing test.
Counting 15 evaluated or killed mutants is not a substitute for reviewing 15
actual historical survivors. The completed analysis cites the historical report
at `25253fff` and the new run separately; it does not invent additional survivors.

For WSL, `bash scripts/sqe/verify_mutation_linux.sh` runs in a temporary Linux
directory and copies the mutation metadata/log back. The optional path argument
allows an unchanged historical checkout to be investigated separately.
