# CI quality-gate evidence

The `Area1 quality gate` job runs on every push and pull request. It executes
the complete pytest suite, enforces 100% statement and branch coverage for the
three server-side critical files, imports the coverage report into SonarQube,
waits for the SonarQube quality gate, and runs mutmut with the two custom
operators. No step uses `continue-on-error` or `|| true`.

## Repository configuration required

The `dev` and `main` branch protection rules must require the check named
`Area1 quality gate`. Configure the following repository secrets before the
first remote run:

| Secret | Purpose |
|---|---|
| `SONAR_HOST_URL` | SonarQube URL reachable from GitHub-hosted runners |
| `SONAR_TOKEN` | Project-scoped SonarQube analysis token |

The local Docker server at `localhost:9000` cannot serve GitHub-hosted runners;
use a hosted/reachable SonarQube instance for the remote workflow.

## Required demonstration

To satisfy the assignment demonstration requirement, retain two linked PRs in
the final evidence:

1. a deliberately failing quality-gate PR, showing the check blocked the merge;
2. a follow-up fix PR, showing the same check passed after the defect and/or
   quality threshold issue was corrected.

Record the PR URLs, commit SHAs, check summaries, and before/after result in
the final report. This repository contains the executable workflow and the
evidence format, but no result is claimed until those remote runs exist.
