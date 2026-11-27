# DT-001 W2 half — 27 November 2026

- `default/`: `tests.team.structural.test_decision_table` as the default suite runs it (W2 rows R1, R2, R4 included): 13/13 passed.
- `desired-rule-regression/`: R3 alone with `SQE_DESIRED_RULES=1` against the unchanged application: **fails** with 200 instead of the agreed 400 (DEF-A2-01, issue #25). This failure is the expected result until the fix.
- Not stored here: in a throwaway clone with a candidate fix (the RCA 1 experiment diff, returning the agreed 400 and text), the same module with `SQE_DESIRED_RULES=1` passed 14/14. The clone was deleted; the application in this repository is unchanged.

Both runs record the working tree before the commit that adds these tests (`git_status` in `result.json`).
