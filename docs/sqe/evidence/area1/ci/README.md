# CI quality-gate evidence

The `Area1 quality gate` job runs on every push and pull request. It executes
the complete pytest suite, enforces 100% statement and branch coverage for the
three server-side critical files, imports the coverage report into SonarQube,
waits for the SonarQube quality gate, and runs mutmut with the two custom
operators. No step uses `continue-on-error` or `|| true`.

## Repository configuration required

The active `CI_Checks` ruleset was read through GitHub on 28 November 2026.
It targets the default branch and `dev` and requires the current six CI jobs:
`backend`, `Area1 quality gate`, `frontend`, `notification-worker`,
`notifications`, and `kubernetes-manifests`. No additional check needs to be
added for the current PR #17 workflow. The separate integration branch defines
`Team API and integration tests` and aggregate `Project quality gate` jobs;
those names must be reconsidered as required checks only after that workflow
is pushed and observed on GitHub. Do not require a name that has not yet run.

The workflow uses these repository secrets:

| Secret | Purpose |
|---|---|
| `SONAR_HOST_URL` | SonarQube URL reachable from GitHub-hosted runners |
| `SONAR_TOKEN` | Project-scoped SonarQube analysis token |

The local Docker server is mapped to `localhost:19000` on this machine; the
GitHub-hosted runner uses a reachable Cloudflare tunnel URL in `SONAR_HOST_URL`.
That URL is temporary. Run 74 attempt 4 verified the scanner and gate passed.

## Required demonstration

To satisfy the assignment demonstration requirement, retain two linked PRs in
the final evidence:

1. a deliberately failing quality-gate PR, showing the check blocked the merge;
2. the documented fix in PR #17, showing its failed step before and passing
   step after the correction; the latest full run also passed.

Record the PR URLs, commit SHAs, check summaries, and before/after result in
the final report. PR #27 still carries the older synthetic failing test; the
revised real-regression evidence is local and has not been pushed. Its merge
box should be captured while `Area1 quality gate` is failing and required.
