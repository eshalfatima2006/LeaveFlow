# Repository structure, file inventory and cleanup record

Version 1.0 — 24 November 2026. Covers the SQE work on both local lines: `test/isolated-fixtures-and-baseline` (with the reconciliation branch `docs/uc-reconciliation`) and `setup/local-baseline` (PR #1). Application code (`backend/`, `frontend/`, `notifications/`, `notification_worker/`, `deploy/`) is upstream baseline `bada9a0` and is not restructured.

## Canonical structure (compact)

Only directories with real content exist. Planned locations are created when their first file is written; Git does not track empty directories.

```text
LeaveFlow/
├── .github/workflows/            upstream CI and auto-release (fork guard: branch ci/fork-release-guard)
├── backend/ frontend/ ...        upstream application, unchanged
├── scripts/sqe/                  SQE entry points (flat: one command per purpose)
│   ├── run_tests.py              A2 runner: check / team / upstream / repeatability (sqe-memory-v1)
│   ├── browser_harness.py        Playwright harness backend: init / serve / fixture (sqe-browser-v1)
│   ├── check_docs.py             documentation link and traceability-ID checker
│   ├── reproduce_baseline.py     PR #1 baseline reproduction (on setup/local-baseline)
│   ├── capture_decision_screenshot.py   PR #1 BL-UI-04 capture (on setup/local-baseline)
│   └── baseline-browser/         pinned Playwright package for BL-UI-04 (on setup/local-baseline)
├── tests/
│   ├── __init__.py               required for unittest discovery of tests.team
│   └── team/                     team-owned tests (upstream tests stay in backend/leave/tests.py)
│       ├── settings.py safety.py runner.py      sqe-memory-v1 profile, guard and recording runner
│       ├── browser_settings.py browser_safety.py   sqe-browser-v1 profile and guard
│       ├── fixtures/ foundation/ api/          A2.0 and A2.1 suites
│       ├── integration/ generated/             planned A2.2 locations (placeholders)
│       ├── browser/                            Playwright: specs/, support/, tools/, flows.json
│       └── unit/ mutation/ security/ performance/   create when that work starts
└── docs/sqe/
    ├── requirements/ planning/ testing/        controlled documents
    ├── evidence/<area>/<run-id>/               immutable run evidence
    ├── AI-USE-RECORD.md                        AI disclosure (PR #1 record: see consolidation below)
    └── REPOSITORY-STRUCTURE.md                 this file
```

**Conventions:**
- **New test areas** go under `tests/team/<area>/`.
- **New commands** go in `scripts/sqe/` only when no existing command serves the purpose.
- **Evidence** is written once to a new `docs/sqe/evidence/<area>/<run-id>/` directory and never edited.
- **Defect and report documents** go to `docs/sqe/defects/` and `docs/sqe/reports/` when the first real one exists.

## File inventory (maintained, non-evidence files)

| Current path | Final path | Action | Justification | Dependencies verified | Status |
|---|---|---|---|---|---|
| `scripts/sqe/run_tests.py` | same | KEEP | Only runner for A2.0/A2.1 suites and repeatability | Commands in SHARED-TEST-FOUNDATION, API-FUNCTIONAL-TESTING; recorded in evidence `result.json` | Verified (team 52/52) |
| `scripts/sqe/browser_harness.py` | same | KEEP | Disposable database for Playwright | `tests/team/browser/support/harness.ts`, `playwright.config.ts` | Verified (B1 runs) |
| `scripts/sqe/check_docs.py` | same | KEEP (added 24 Nov) | One command for link/anchor and flow-ID consistency | Negative test with injected faults detected all three | Verified |
| `scripts/sqe/reproduce_baseline.py` (setup line) | same | KEEP | PR #1 reproduction; different purpose from `run_tests.py` (baseline checks, migrations, API smoke on a temporary file database) | `BASELINE-VERIFICATION.md` §13; SHA-256 recorded in BL-UI-04 `execution-record.json` | Verified on `setup/local-baseline` |
| `scripts/sqe/capture_decision_screenshot.py` (setup line) | same | KEEP | Reproduces the BL-UI-04 browser evidence | Report §12; hashed in its execution record | Verified |
| `scripts/sqe/baseline-browser/` (setup line) | same | KEEP; REVIEW REQUIRED after integration | Duplicates `@playwright/test` 1.49.1 of `tests/team/browser/`, but merging them would change hashed provenance of PR #1 evidence | `capture_decision_screenshot.py`, report §12 | Kept deliberately |
| `tests/__init__.py` | same | KEEP | Without it discovery of `tests.team` fails (`TypeError` in unittest loader) | A2.1 finding, clean-export run 52/52 | Verified |
| `tests/team/{settings,safety,runner}.py` | same | KEEP | sqe-memory-v1 profile, fail-closed guard, per-case recording | `run_tests.py`; pyflakes clean except the intentional settings star import | Verified |
| `tests/team/browser_{settings,safety}.py` | same | KEEP | sqe-browser-v1 profile and guard (Python package `tests.team`; `tests/team/browser/` is a Node project) | `browser_harness.py` | Verified |
| `tests/team/fixtures/leave_data.py`, `tests/team/api/support.py` | same | KEEP | Shared fixtures/helpers used by foundation and API suites | Imports in suites | Verified |
| `tests/team/integration/__init__.py`, `tests/team/generated/__init__.py` | same | KEEP (placeholders) | Planned A2.2 locations named in SHARED-TEST-FOUNDATION | Discovery runs them harmlessly | Verified |
| `tests/team/browser/**` | same | KEEP | B1 harness, specs, registry and coverage tool | npm script `coverage`; config webServer/globalSetup | Verified |
| `docs/sqe/evidence/api/a21/sensitivity_probe.py`, `docs/sqe/evidence/foundation/a20/failure_probe.py` | same | KEEP | Reproduction tools for their own evidence; moving them breaks recorded commands | API-FUNCTIONAL-TESTING, SHARED-TEST-FOUNDATION | Verified |
| `docs/sqe/evidence/api/a21/{check,upstream,...}` first run | same | KEEP | Superseded but genuine history, labelled in API-FUNCTIONAL-TESTING | — | Kept |
| `docs/sqe/AI-USE-RECORD-PR1-REMEDIATION.md` (setup line) | merged into `AI-USE-RECORD.md` after integration | CONSOLIDATE (after integration) | Two records must become one disclosure | See below | Pending integration |
| `.github/workflows/auto-release.yml` | same | KEEP, guarded | Upstream function preserved; fork releases prevented by a condition (branch `ci/fork-release-guard`) | YAML parsed; condition reviewed | Prepared, not merged |

## Deletion ledger

**No tracked file was deleted.** Each candidate was considered and kept for a recorded reason:

| Candidate | Reason considered | Why it was kept |
|---|---|---|
| `scripts/sqe/baseline-browser/` vs `tests/team/browser/` | Two Playwright packages | Different purposes; merging changes hashed PR #1 provenance; review after integration |
| `fingerprint` logic in `run_tests.py`, `harness.ts`, `reproduce_baseline.py` | Three implementations | Different languages and evidence formats already recorded; consolidation would alter evidence schemas |
| Empty `integration/` and `generated/` packages | No tests yet | Planned locations referenced by documentation |
| Superseded A2.1 first-run evidence | Duplicate results | Genuine history; deleting it would hide the defect-fix trail |
| Exported but module-internal TypeScript helpers (`FixtureUser`, `RowState`, `nav`) | Unused outside `test.ts` | Used inside the module; needed by planned UC-04 specs |

Static checks behind this ledger:
- `pyflakes` on all SQE Python files on both lines: no findings except the intentional Django settings star imports;
- an export-usage scan of the browser support modules;
- a reference scan (code, configs, npm scripts, documentation commands) for every entry point.

## Local (untracked) artefacts — do not clean blindly

Ignored local files are not repository content. `git clean -ndX` (dry run, 24 Nov 2026) shows that **`git clean -X` would delete**:

- `backend/db.sqlite3` (the development database);
- `.venv/`;
- the assignment PDF;
- `frontend/node_modules/` and the Playwright `node_modules/`;
- stale `frontend/dist/` and `*.tsbuildinfo`;
- Python `__pycache__/` folders.

**Never run `git clean -X` or `git clean -x` in this repository.** If caches must be removed, delete specific `__pycache__/` directories or the stale `frontend/dist/` by path. `prompt.md` and the assignment PDF are personal files and are never removed by tooling.

## AI-use record consolidation (at integration)

After `setup/local-baseline` and the test line are both in `main`:

1. Append the content of `docs/sqe/AI-USE-RECORD-PR1-REMEDIATION.md` to `docs/sqe/AI-USE-RECORD.md` under a heading "PR #1 review remediation", unchanged.
2. Replace the separate file's body with a one-line pointer, or remove it in the same reviewed commit (team choice).
3. Run `python3 scripts/sqe/check_docs.py`.

Historical disclosures are never rewritten.
