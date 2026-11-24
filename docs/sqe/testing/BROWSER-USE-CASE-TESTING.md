# B1 — browser use-case harness and UC-01/UC-02 automation

Implemented and executed 23 November 2026 (Asia/Karachi). AI-assisted draft; students must review before committing. No Git/GitHub operation, production change or development-database access was performed.

**Scope of B1:** the isolated Playwright harness, runtime verification of the UC-01/UC-02 flows, and their automation. Catalog basis: Strategy A (team decision) — UC-01, UC-02 (approve main, reject alternative), UC-04, UC-07, UC-08, UC-09. **Django Admin inclusion (UC-08, UC-09) and notification-service inclusion (UC-07) remain pending instructor scope decisions;** nothing here treats them as approved.

## Catalog refinements recorded before implementation

| Item | Change | Source basis |
|---|---|---|
| **TC-UC09-E2** (refined) | *Employee record removed while the reassignment form is open.* Admin opens E's change form; the employee is deleted (second administrator / fixture); admin saves the new team. Expected: Django Admin redirects to the admin index with the warning `user con ID "<id>" non esiste. Probabilmente è stato cancellato?`; no user is recreated and no team is written. This is an exception inside the administrator's own reassignment journey (replaces the generic non-staff login, which moves to the included admin sign-in). | `django/contrib/admin/options.py` `_get_obj_does_not_exist_redirect` (1783–1794) and the POST branch (1831); Italian catalogue `contrib/admin/locale/it/.../django.po:251–253` |
| **SUP-UC09-01** (kept) | Former approver's in-flight decision after reassignment → 404, k stays pending. Kept as a supplementary authorization/integration check of the reassignment postcondition (BR-04), **outside** the mandatory flow count. | `backend/leave/views.py:46–51,75–78` |
| **OBS-UC08-01** (kept) | Leave-balance changelist rows are expected to read `LeaveBalance object (n)`, not the employee, so an administrator cannot identify whose entitlement to edit. **Predicted from source; requires browser verification** in the UC-08 probe. | `backend/leave/admin.py:14` (no ModelAdmin), `models.py:29–43` (no `__str__`) |

## Coverage model

The registry [`tests/team/browser/flows.json`](../../../tests/team/browser/flows.json) is the single source:

- **30 mandatory flows** (6 use cases × main + 2 alternatives + 2 exceptions) — the only denominator for use-case flow coverage (Lecture 16 p10: flows tested ÷ total flows).
- **Blocked regression objectives** — `OBJ-UC02-01` (approval exceeding remaining entitlement; blocked by the unapproved approval-time error contract, GAP-01). Visible in the run as a `fixme`/skipped test, never counted as a mandatory flow.
- **Supplementary checks** — `SUP-UC09-01`, `SUP-UC07-01` (dedup). Separate.
- **Observations** — `OBS-*`, never counted.

Every test title starts with exactly one registry ID; `tools/flow-coverage.mjs` rejects unregistered or duplicate IDs and writes `flow-coverage.json/.md` into the evidence directory.

## Harness design and safety controls

| Concern | Control |
|---|---|
| Database | New profile `sqe-browser-v1` (`tests/team/browser_settings.py`). The only accepted database is `browser.sqlite3` inside a run directory created by `scripts/sqe/browser_harness.py init` **directly under the system temp directory**, named `leaveflow-sqe-browser-*` and containing a marker file. `tests/team/browser_safety.py` refuses: unset/relative paths, unmarked directories, anything inside the repository, `backend/db.sqlite3`, other engines/aliases, and a non-empty `REDIS_URL`. Checked before settings load and again on the live connection. Guard verified by negative tests (unset, `backend/`, unmarked temp dir, relative path) before first use. |
| Wrong server | `reuseExistingServer: false` and non-default ports (backend 8765, frontend 4765) make the run fail if a port is taken. Global setup creates a **sentinel account only in the harness database** and requires it to log in through the served API before any test runs. |
| Development database | Never opened or read: global setup/teardown record **metadata only** (size, mtime, inode for `db.sqlite3` and sidecars) and fail the run if it changes. |
| Isolation | One worker; an automatic fixture resets the disposable database before every test; each test builds its own synthetic scenario. No test depends on another. |
| Frontend | `vite build` (no `vue-tsc`) into the run directory, served by `vite preview`; `VITE_API_URL` points at the harness backend, `VITE_NOTIFICATIONS_URL` at an unused port. `frontend/` is unchanged. |
| External services | Redis disabled; notification centre unreachable by design (UC-07 is a separate, pending environment). |
| Credentials | Fixture passwords are random per scenario, held in memory only; tokens obtained through the real login API. Report step titles do not contain filled values (checked); no `Token <key>` string in any evidence file. |
| Dependencies | `tests/team/browser/package.json` pins `@playwright/test` 1.49.1 with its own lock file; the frontend lock is untouched. `node_modules/` is already ignored by the root `.gitignore`. Chromium Headless Shell 131.0.6778.33 (Playwright build 1148) runs in WSL without extra system packages. |

Request `k` in UC-02 is created through the **real W1 API** by the employee; ORM fixtures create only preconditions (users, balances, other actors' requests). Postconditions are read back from the disposable database through the harness CLI (`request`, `requests`, `balance`).

## Commands (inside WSL)

```bash
cd tests/team/browser
npm ci
npx playwright install chromium
SQE_EVIDENCE_DIR=../../../docs/sqe/evidence/browser/<new-dir> npx playwright test
node tools/flow-coverage.mjs ../../../docs/sqe/evidence/browser/<new-dir>
```

Without `SQE_EVIDENCE_DIR`, evidence goes to the temporary run directory. Do not pass `--reporter` when producing evidence (it replaces the configured HTML/JSON reporters). Remove leftover `/tmp/leaveflow-sqe-browser-*` run directories after use (they contain only disposable data).

## Results

Evidence: [`docs/sqe/evidence/browser/b1/`](../evidence/browser/b1/) — `run-1/` and `run-2/` (two independent processes, each with its own run directory): HTML report, `results.json`, `flow-coverage.{json,md}`, `environment.json`, development-database metadata before/after, console log.

| Run | Mandatory flows passed | Blocked objectives | Duration | Dev DB metadata | Exit |
|---|---|---|---|---|---|
| b1/run-1 | 10 / 10 automated (UC-01 ×5, UC-02 ×5) | OBJ-UC02-01 skipped (fixme) | 46.3 s | unchanged | 0 |
| b1/run-2 | 10 / 10 automated | OBJ-UC02-01 skipped (fixme) | 46.1 s | unchanged | 0 |
| A2 regression (`run_tests.py team`) | 52 / 52 (in-memory profile) | — | — | unchanged | 0 |

**Mandatory flow coverage: 10 of 30 executed and passed (33.3%).** UC-04, UC-07, UC-08 and UC-09 flows are registered but not yet automated.

## Runtime verification findings

| ID | Finding (observed in both evidence runs) | Consequence |
|---|---|---|
| OBS-UC02-01 | After a 409 (stale decision, TC-UC02-E1) or 403 (own request, TC-UC02-E2) the UI shows **no message**; the row still reads Pending with Approve/Reject visible until reload; the browser console logs `Error: La richiesta è già stata decisa.` / `Non puoi decidere una tua richiesta.` | Prediction confirmed. Tests assert the **safe state** (exact API status/body, unchanged row, correct state after reload) and attach the UI observation; they do not assert absence of a message. Whether "message shown" becomes part of the expected result is a **team oracle decision** (would then fail before a UI fix). |
| GAP-04 | The Approve button is offered on the manager's own pending request. | Asserted as actual baseline UI in TC-UC02-E2. |
| OBS-UC01-01 | Closing the form without submitting keeps the abandoned values; reopening shows them. | Recorded only (no requirement defines reset-on-close). |
| — | Server business-rule messages appear in Italian in the English UI (`Esiste già una richiesta sovrapposta.`, `Saldo ferie insufficiente.`). | Asserted as actual text; localisation finding for the usability work. |
| — | Pending requests reserve no entitlement (available stays 5 with a 5-day pending request). | Asserted as GAP-01 characterisation, not an approved policy. |
| Harness | `getByLabel` does not match the request form's fields because each `<label>` wraps its control (label text includes option values); the accessible names (verified by ARIA snapshot) are combobox "Type", textboxes "From", "To", "Note optional". | Role locators used. First two exploratory runs failed only on this selector; they were temporary and are not evidence. |

## Limitations

- SQLite only (no PostgreSQL locking/engine-dependent limits); single Chromium project; one worker.
- Two fixed 1-second observation windows (UC-02 E1/E2) are used only for recording UI state after a failed call, never for pass/fail.
- Traces are retained only on failure; every flow attaches its own end-state screenshot and DB readback JSON.
- `flow-coverage` reports inside run-1/run-2 were generated before `OBS-UC01-01` was added to the registry; counts are unaffected.
- UC-07 requires a separate disposable Compose environment; UC-08/UC-09 require the Django Admin scope decision.

## Next steps (not started)

UC-04 runtime probes (session invalid on reload; `/api/requests/` 500 at login) then automation; then UC-08/UC-09 once the instructor decides Django Admin scope (including the OBS-UC08-01 browser check and SQLite vs PostgreSQL upper bound); UC-07 after the notification-scope decision and Compose environment.

## v0.2 reconciliation update (24 Nov 2026)

- **Catalog and flows:** [USE-CASE-SPECIFICATIONS.md](../requirements/USE-CASE-SPECIFICATIONS.md) (PROPOSED; D-1/D-2 pending). The RTM catalog maps every v0.1 `E2E-UC*` ID to a TC flow or a disposition.
- **Registry:** `flows.json` is now version `v0.2-2026-11-24`. It adds `owner` and `legacy_ids` to each flow and registers the included use cases INC-01/INC-02 (outside the 30). Test titles and IDs are unchanged.
- **Proposed ownership:** UC-01 Member 1, UC-02 Member 2 (both already automated in B1, under one commit identity — see TEAM-OWNERSHIP v0.2 attribution rule), UC-04 Member 3, UC-07 Member 2, UC-08 Member 1, UC-09 Member 3.
- **Provenance re-run (closes audit finding X-18):** run-1 and run-2 executed with uncommitted sources at `b65ca6a`. The suite was re-run unchanged from committed sources at `73cfc93`, where the recorded git status lists only new evidence files and the untracked `prompt.md`, into [`b1-provenance-2026-11-24`](../evidence/browser/b1-provenance-2026-11-24/flow-coverage.md). Result: 10 passed, OBJ-UC02-01 skipped (blocked), exit 0, development-database metadata unchanged, no token values in the evidence. The earlier runs are kept unchanged.
- **Regression at the same commit:** [`r5-2026-11-24`](../evidence/regression/r5-2026-11-24/team/result.json) — Django check exit 0, upstream 9/9, team 52/52 (in-memory profile).
- **Two Playwright packages:** `tests/team/browser/` (team tests) and `scripts/sqe/baseline-browser/` (PR #1 baseline evidence on `setup/local-baseline`) both pin `@playwright/test` 1.49.1. They stay separate by design; see [REPOSITORY-STRUCTURE.md](../REPOSITORY-STRUCTURE.md).
