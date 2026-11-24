# A2.1 core API functional testing

Implemented and executed 23 November 2026 (Asia/Karachi; raw UTC timestamps in evidence read 22 November ~19:53–20:06Z). Builds on the A2.0 foundation (commit `b65ca6a`). AI-assisted draft; students must review before committing. No Git/GitHub operation was performed.

## Tested state

| Item | Value (measured) |
|---|---|
| HEAD / branch | `b65ca6a4f59bdc0c543ed1cf3eed786e29bed24c` / `test/isolated-fixtures-and-baseline` |
| Worktree | Dirty: modified `.gitignore` (pre-existing), `tests/team/runner.py`, `tests/team/safety.py`, `scripts/sqe/run_tests.py`; untracked A2.1 files, `tests/__init__.py`, `prompt.md`. Exact list and tracked-diff SHA-256 in each `result.json` |
| Python / Django / DRF / SQLite | 3.12.7 / 6.0.7 / 3.17.1 / 3.46.1 (also django-cors-headers 4.9.0, redis 6.4.0, psycopg 3.3.4 installed, not exercised) |
| Runner | Django DiscoverRunner + unittest via `scripts/sqe/run_tests.py`; profile `sqe-memory-v1` |
| Test DB | `file:memorydb_default?mode=memory&cache=shared` (verified active in every run); Redis disabled |

## Pre-execution findings

- **`tests/__init__.py` is required and is NOT in commit `b65ca6a`.** Without it `tests` becomes a namespace package and unittest discovery of `tests.team` crashes (`TypeError` in `unittest.loader._get_directory_containing_module`); reproduced on a scratch copy under `/tmp`, real tree untouched. A clean checkout of `b65ca6a` cannot run the team suite until the student commits this file.
- `tests/team/safety.py` ended with an extra blank line; removed (formatting only).
- Shared runner: failed **subtests** were not recorded per case, and `passed` was computed as `executed − failure entries`, which under-reports when several subtest rows of one method fail (first-run probe showed 33 "passed" when 38 methods passed). Fixed minimally: `RecordingResult.addSubTest` records failing rows with their owning `method_id`; `passed = executed − distinct non-passing methods − expected failures − unexpected successes`; new `non_passing_test_methods` count. `failed`/`errors` keep their meaning (unittest failure entries). Green runs are unaffected. This is a shared-infrastructure change: the A2.0 contract requires peer review of it.

## Files

| Path | Purpose |
|---|---|
| `tests/team/api/support.py` | Reusable helpers for A2.1/A2.2: real-token `APIClient`, payload builder, `row_state`/`all_rows` DB readback, `balance_view`, `add_member`, per-row `rolled_back()` savepoint, exact response field sets |
| `tests/team/api/test_authentication.py` | Group A — 6 tests |
| `tests/team/api/test_w1_submission.py` | Group B — 21 tests |
| `tests/team/api/test_w2_decisions.py` | Group C — 13 tests |
| `docs/sqe/testing/A21-EXECUTION-MAPPING.md` | Case ID → node ID → FR/BR → status, plus per-FR open items |
| `docs/sqe/evidence/api/a21/sensitivity_probe.py` | In-memory fault injection self-check (not a discovered test) |
| `docs/sqe/evidence/api/a21/final/` | **Authoritative** evidence (below) |
| `docs/sqe/evidence/api/a21/{check,upstream,foundation,api,team,repeatability,sensitivity}/`, `summary.json`, `development-db-fingerprint.txt` | First complete run, kept unedited. **Superseded**: produced before the duplicate case-ID fix (API-W2-002.01 used twice) and runner count fix; its green results agree with the final run |

## Commands (repository root, inside WSL)

```bash
E=docs/sqe/evidence/api/a21/final
.venv/bin/python scripts/sqe/run_tests.py check --evidence-dir $E/check
.venv/bin/python scripts/sqe/run_tests.py upstream --evidence-dir $E/upstream
.venv/bin/python scripts/sqe/run_tests.py team tests.team.foundation --evidence-dir $E/foundation
.venv/bin/python scripts/sqe/run_tests.py team tests.team.api --evidence-dir $E/api
.venv/bin/python scripts/sqe/run_tests.py team --evidence-dir $E/team
.venv/bin/python scripts/sqe/run_tests.py repeatability --evidence-dir $E/repeatability
.venv/bin/python docs/sqe/evidence/foundation/a20/failure_probe.py $E/failure-propagation   # expect exit 1
.venv/bin/python docs/sqe/evidence/api/a21/sensitivity_probe.py <fault> $E/sensitivity/<fault>  # expect exit 1
```

Run one module or test: `.venv/bin/python scripts/sqe/run_tests.py team tests.team.api.test_w2_decisions.FinalStateTests`.

## Results (final run)

| Invocation | Executed | Passed | Failed / Errors / Skipped | Exit |
|---|---|---|---|---|
| check | system check | no issues | – | 0 |
| upstream `leave.tests` | 9 | 9 | 0 / 0 / 0 | 0 |
| A2.0 foundation | 12 | 12 | 0 / 0 / 0 | 0 |
| **A2.1 API** | **40** | **40** | 0 / 0 / 0 | 0 |
| combined team (foundation + API) | 52 | 52 | 0 / 0 / 0 | 0 |
| repeatability run-1 / run-2 (separate processes) | 52 / 52 | 52 / 52 | 0 / 0 / 0 | 0 |
| A2.0 failure probe (deliberate) | 1 | 0 | 1 / 0 / 0 | 1 (expected) |

Repeatability: per-case `(id, outcome)` lists identical across both runs; foundation reference hashes equal; mutation-then-rollback true in both. Upstream tests are reported separately and carry no team credit. Repeated runs are not additional tests.

### Assertion sensitivity (fault injection in child-process memory only)

| Injected fault | Exit | Non-passing methods (passed) | Methods that detected it |
|---|---|---|---|
| no-balance-check (serializer skips D>A) | 1 | 3 (37) | BalanceTests: boundary, approved-history, zero/negative |
| no-overlap-check (model clean skips overlap) | 1 | 2 (38) | OverlapTests: pending boundaries, approved blocks |
| count-weekends (business_days = calendar days) | 1 | 4 (36) | DateRuleTests ×2, BalanceTests ×2 |
| visibility-all (every role sees every row) | 1 | 4 (36) | visibility, out-of-scope 404, guard precedence, token identity |

These show the suite detects each targeted behaviour change; they are not mutation-testing scores and do not replace A1's mutation work. No source file was edited by the probes.

## Response and database oracles asserted

Every success asserts the exact `LeaveRequestSerializer` field set, owner, status and the persisted row (`row_state`), row counts and derived balance. Every denial asserts status code, exact `detail` body where the application defines it, that only `detail` is returned, and that **all** request rows are byte-for-byte unchanged (`all_rows()` before/after). Decision successes assert `decided_by` = actor, `decided_at` inside the call window, and all content fields unchanged.

Verified guard order: authentication (401) → role (403) → decision value (400) → visible lookup (404) → self (403) → pending (409).

| Situation | Observed |
|---|---|
| No/malformed/unknown/inactive-user token | 401, `WWW-Authenticate: Token`, only `detail` |
| Bad login (wrong, unknown, missing, blank, inactive) | 400 `{"detail": "Credenziali non valide."}`, no token row |
| Valid W1 | 201, one pending row, allowance/used unchanged |
| Field errors | 400 keyed by field; overlap and balance → `non_field_errors` |
| Malformed JSON / `text/plain` | 400 / 415 |
| Employee decision | 403 even with invalid value |
| Other-team or teamless manager, absent ID, ID 0 | 404 |
| Non-integer or negative path ID | 404 (route does not match) |
| Self-decision (manager, admin, teamless manager) | 403 |
| Decide approved/rejected (incl. admin, repeat) | 409, audit fields preserved |

## Deviations and unresolved oracles (no new defects claimed)

No test failed in the final run, and A2.1 found **no new application defect**. The following baseline behaviours are pinned as **CHARACTERIZATION** tests (passing against current behaviour, policy not approved). Each references existing TEST-BASIS IDs:

- GAP-01: pending requests reserve no allowance (two 4-day pendings at A=5 both accepted); negative available blocks even a 0-day request. The **approval-time over-allowance defect is not exercised or fixed here** — it needs the same-record W1→W2 regression in A2.2.
- GAP-07: no balance record → balance check skipped (25-day request accepted); dashboard reports 0/0/0.
- FR-W1-01 note: managers/admins (incl. teamless) may submit their own requests.
- FR-W1-03 note: weekend-only (0-day) and past-dated requests are accepted.
- FR-W2-06 note: decision response omits `decided_by`/`decided_at`; verified via ORM.
- BR-06: read-only and unknown keys in W1 and W2 bodies are silently ignored (owner/status/audit cannot be injected).
- Observation: DRF matches the `Token` keyword case-insensitively (`token <key>` authenticates). Framework behaviour, not asserted as a defect.

## Isolation

The guard validated the profile before setup, and every run reported the active memory URI. `backend/db.sqlite3` was 180224 bytes, SHA-256 `70155559be6dc448fa8eb05e804ff7a60532afbac881bac21bc42de47cbcd33d`, mtime 2026-11-21T19:39:13, with no sidecars, both before (19:53:51Z) and after (20:06:23Z) the final run — see `final/development-db-fingerprint.txt`. Every `result.json` also records `development_database_unchanged: true`. No seed, flush, migrate or Redis/PostgreSQL connection was run against non-test targets. Evidence contains no token values or fixture passwords (pattern search).

## Known limitations

- Event publication (`leave.requested/approved/rejected`) is untested: Redis is disabled by the profile.
- SQLite only; `select_for_update` locking and concurrent submissions are not exercised.
- Decision tests use fixture-created pending rows; same-record W1→W2 integration is deliberately left to A2.2.
- `/api/team/` content is not asserted beyond 401.
- Error message text is Italian (`LANGUAGE_CODE=it-it`); assertions use exact application-defined strings, but framework `detail` strings (401/404) are checked by shape only.
- Scalar coercion (e.g. numeric note) is not asserted, per BR-06 guidance.
