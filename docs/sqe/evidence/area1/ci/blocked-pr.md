# Blocked pull-request evidence

This record demonstrates the fail-before state for the Area 1 quality gate.

- Pull request: [PR #27](https://github.com/eshalfatima2006/LeaveFlow/pull/27)
- Base branch: `dev`
- Head branch: `evidence/blocked-quality-gate`
- Failing commit: `8d3f3d9f826e983f3a438c63db486bbe68d00dae`
- Workflow run: [CI run 40](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/45657735906)

The regular repository checks passed, but the `Area1 quality gate` failed on
the intentional evidence-only test
`tests/team/unit/test_quality_gate_block_demo.py`. The test reported
`AssertionError: Intentional failure for the blocked-PR evidence`, so the
required quality check failed before SonarQube and mutation testing could run.
PR #27 remains open and must not be merged into `dev` or `main`.
