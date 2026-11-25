# Area 3 verification

Member 3 owns the 20 remaining browser flows for UC-04, UC-07, UC-08, and UC-09 under the group’s confirmed split. Use the same fixed flow IDs in the Playwright registry and the traceability matrix. UC-01 and UC-02 are the original workflows whose submission and decision screens are used for the two usability tasks. Run the baseline browser regressions alongside Area 3.

## Local setup and browser evidence

Use Python 3.13 with the project requirements, Node.js with `npm ci` in `frontend`, `notifications`, and `tests/team/browser`, and Chromium from `npx playwright install chromium` run in the browser package. Build the gateway with `npm run build` from `notifications`. Set `SQE_PYTHON` to the installed test interpreter if it lives outside `.venv`.

From the repository root, start the dedicated notification services. The Redis port is bound to loopback and Redis data is temporary. The browser harness starts a separate loopback Django server, creates its own SQLite database, starts the test gateway, and builds Vue into the run directory.

```powershell
docker compose -p leaveflow-sqe-area3 -f tests/team/browser/notifications.compose.yml up --build --detach --wait
$env:SQE_ENABLE_NOTIFICATIONS = '1'
$env:SQE_EVIDENCE_DIR = (Join-Path (Get-Location) '.venv/evidence/area3-browser')
npm --prefix tests/team/browser run test -- --grep-invert 'authenticated accessibility audit'
npm --prefix tests/team/browser run coverage -- "$env:SQE_EVIDENCE_DIR"
docker compose -p leaveflow-sqe-area3 -f tests/team/browser/notifications.compose.yml down
```

Use a fresh Redis project for each full browser run. It prevents consecutive harness databases with independent primary-key sequences from sharing notification feeds. Keep operational logs and test evidence in a fresh directory. Playwright includes the JSON and HTML reports and the development database fingerprints.

An isolated UC-07 run also lets you verify the whole group’s pending count with `docker compose -p leaveflow-sqe-area3 -f tests/team/browser/notifications.compose.yml exec -T redis redis-cli XINFO GROUPS leaveflow:events`. The browser cases verify delivery and acknowledgement of the specific stream entries they create.

## Accessibility and usability

Set `SQE_ACCESSIBILITY_AUDIT=1` and run `accessibility-audit` with the browser runner. If the Lighthouse version requires a newer Chromium build than Playwright uses, set `SQE_AUDIT_CHROME` to a compatible installed Chrome executable. Each audit opens the authenticated state, saves a full axe report, and saves Lighthouse JSON and HTML for accessibility, best practices, and SEO. A snapshot targets the dialog, queue or panel after the user reaches it. Compare the same key screen, browser settings, and scenario before and after the fix, and count overlapping tool findings once.

The `tasks-and-access` suite contains the W1 keyboard task, correction after a rejection, the W2 decision task, and the two denied role cases. It also checks Django Admin staff access and logs only the session cookie attributes. It excludes cookie values and token strings from evidence attachments.

## Defensive security and package audit

Run the ZAP Crossplatform package with Java through the passive runner. Keep the run local and use a new evidence directory. The script proxies the two workflow tasks, waits for the passive queue to drain, and checks that the two application origins were captured.

```powershell
python scripts/sqe/run_passive_zap.py --zap '<path-to-zap.jar>' --evidence-dir .venv/evidence/area3-zap
python -m pip install --target .venv/backend-runtime -r requirements.txt
python scripts/sqe/run_dependency_audit.py --python-packages .venv/backend-runtime --evidence-dir .venv/evidence/area3-dependencies
```

Install `pip-audit` in the test interpreter. The audit records the Python distributions and the locked frontend, gateway, and browser npm inventories. An advisory-related nonzero result is evidence to triage. Keep the runtime and development dependencies distinct when assigning severity and risk. Verify controls against the server or configuration and attach the role, action, expected outcome, observed outcome, and evidence.

## Performance and recovery

Follow the [predeclared k6 protocol](AREA3-PERFORMANCE-PROTOCOL.md). The recovery test injects a failure after the decision write but before commit, checks rollback of the same row and balance, restores normal behavior, then retries and checks that a duplicate decision leaves the same persisted state.

```powershell
python scripts/sqe/run_tests.py team tests.team.integration.test_decision_recovery --evidence-dir .venv/evidence/area3-recovery
```
