# Blocked pull-request evidence

This record demonstrates the fail-before state for the Area 1 quality gate.

- Pull request: [PR #17](https://github.com/eshalfatima2006/LeaveFlow/pull/17)
- Base branch: `dev`
- Head branch: `feat/area1-quality-engineering`
- Failing commit: `5da5b953771e65ce8d94fc4de6d7ef036d0755ca`
- Workflow run: [CI run 17](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/45453933225)

The regular tests, SonarQube analysis, SonarQube quality gate, and mutmut
execution completed. The Area 1 job was blocked because the first survivor
report exporter wrote zero rows and exited with code 1. The failed required
job prevented the pull request from being treated as merge-ready.
