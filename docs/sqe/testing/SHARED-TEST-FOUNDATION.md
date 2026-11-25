# A2.0 shared test foundation

Implemented and verified 22 November 2026 (Asia/Karachi). Original baseline `bada9a03ecec53ef6945827230e3594d825da87a`; tested HEAD `0a9a3f00e30859adca969a2673fa3e7698357d34`, branch `test/isolated-fixtures-and-baseline`. Working tree was dirty: pre-existing .gitignore/prompt and new uncommitted foundation/evidence files; each result.json records actual Git status, tracked-diff hash and Python source hashes. No Git/GitHub mutation was performed. Code is AI-assisted draft work owned/reviewed by the students; no human review/authorship is invented.

## Choice and implemented files

Use installed **Django DiscoverRunner / unittest**, real DRF APIClient and Django TestCase isolation. No pytest, conftest, production dependency, test-only dependency or lockfile change was necessary. Team discovery is separate from unchanged upstream `leave.tests`.

| Repository-relative path | Purpose |
|---|---|
| `scripts/sqe/run_tests.py` | One root entry point: check/team/upstream/repeatability, real exit codes, optional nonoverwriting logs/JSON and development-file hashes |
| `tests/__init__.py`, `tests/team/__init__.py` | Importable repository test namespace, avoiding third-party tests package ambiguity |
| `tests/team/settings.py` | Original application settings plus explicitly isolated core profile, no external DB/Redis |
| `tests/team/safety.py` | Pure fail-closed config validation and runtime checks before fixture ORM calls/setup/teardown |
| `tests/team/runner.py` | Guarded DiscoverRunner, real unittest outcomes and per-run logical snapshot collection |
| `tests/team/fixtures/__init__.py`, `tests/team/fixtures/leave_data.py` | Fixed-date builders, returned objects/IDs, canonical logical state and later overapproval fixture |
| `tests/team/foundation/__init__.py`, `tests/team/foundation/test_foundation.py` | 12 meaningful A2.0 checks |
| `tests/team/api/__init__.py`, `tests/team/integration/__init__.py`, `tests/team/generated/__init__.py` | Future extension packages; no full API/integration/generated tests claimed |
| `docs/sqe/testing/SHARED-TEST-FOUNDATION.md` | This usage/results/contributor contract |
| `docs/sqe/AI-USE-RECORD.md` | Appended A2.0 disclosure; earlier text preserved |
| `docs/sqe/evidence/foundation/a20/` | Eight result.json files and corresponding stdout.log/stderr.log pairs, deliberate failure_probe.py and final verification.json |

Source links: [runner](../../../scripts/sqe/run_tests.py), [fixtures](../../../tests/team/fixtures/leave_data.py), [foundation tests](../../../tests/team/foundation/test_foundation.py), [guard](../../../tests/team/safety.py). Exact created-file inventory and preservation checks are in the final [verification manifest](../evidence/foundation/a20/verification.json).

## Database safety and actual reset mechanism

`tests.team.settings` is selected **before django.setup**. It imports the normal application configuration, then replaces DATABASES with one SQLite alias whose normal NAME and TEST.NAME are both `:memory:`; Redis URL is empty. Inherited POSTGRES_DB/REDIS_URL/DJANGO_SETTINGS_MODULE cannot redirect this entry point. No database CLI override, keepdb, flush, seed or custom destructive reset is exposed. Normal production files remain unchanged.

Guard requires profile `sqe-memory-v1`, sole default alias, exact SQLite engine, TEST.NAME=:memory:, no mirror and disabled Redis. Before setup it accepts only :memory: or Django's exact memory URI. Fixture creation requires the active target **`file:memorydb_default?mode=memory&cache=shared`**. File paths (including development SQLite), unknown URIs/profiles, external PostgreSQL and custom TEST targets are rejected before connection/query. The exact URI was verified against installed Django6.0.7's SQLite creation code. This foundation deliberately does not support external test databases.

Django creates/migrates the framework-managed **in-memory test database**, then TestCase class transactions and per-test savepoints roll back fixture/test changes. The migration messages in logs concern that verified memory target, not development data. Fixtures never call seed_demo, delete old records, flush, or rebuild the development DB. The builder validates model fields/date/overlap and decision-actor invariants; an explicit allow_overlap=True constructs a deliberate invalid-overlap fixture. A fixture allowance safeguard is test-data protection, **not a fix or claim that W2 already checks balance**.

Before/after every invocation, the entry point reads bytes/hashes for backend/db.sqlite3 and -wal/-shm/-journal sidecars without opening SQLite. Any difference returns nonzero; concurrent external writes would invalidate this check rather than be ignored. Optional PostgreSQL credentials are never opened/logged; the core profile cannot select that engine. This is strong local file/configuration evidence, not a remote database audit or PostgreSQL locking guarantee.

Measured development file: **180224 bytes**, SHA-256 **`70155559be6dc448fa8eb05e804ff7a60532afbac881bac21bc42de47cbcd33d`** before and after all recorded invocations; all three sidecars absent before/after. No production/development data was reset. Results retain full fingerprints and the active test target.

## Fixed fixtures and isolation proof

build_people creates two synthetic teams, E1/E2, same-team M1, unrelated-team M2, admin and teamless manager, with example.invalid emails and dedicated test credentials. Default allowance10/year2026; per-identity allowance overrides and missing_balance_for support positive, exactly sufficient, zero-remaining and absent-balance scenarios. Credentials/token values are never included in logical snapshots or reports. Do not reuse fixture credentials for real accounts.

Reference employee: approved2026-12-07..08 (2 weekdays), pending12-14..16 (3), rejected12-21 (1). Used=2 and available=8; pending/rejected consume nothing. Final-history fixtures use an authorized non-self decider and fixed audit time. make_request returns the persisted object/ID, rejects unintended overlap/invalid actor/date/field/allowance setup, and never assumes primary keys. build_reference_fixture and build_overapproval_scenario compose builders atomically.

FND-008 records initial logical state, changes allowance to99/note and adds a transient team, and asserts state changed. FND-009 is a **later independent test** with a fresh savepoint, asserting exact initial state returned (allowance10, original note, only two teams). Both snapshots are retained. Test methods have explicit01/02 ordering for this demonstration; their initial-state assertions also stand independently. Other tests' token and variant fixtures roll back as normal.

The repeatability action launches **two separate Python processes**, each with a newly created memory DB and the full12-test suite. It compares canonical reference state by logical keys/content/status/dates/totals, omitting auto-increment IDs, creation timestamps, randomized password hashes and token values. Both reference hashes are **`0ccd88034572d556a2f9eab7887af1841ca313422e2e88e475c9b68b358465c7`**. reference_equal=true; mutation-then-next-test rollback=true for both runs; development files unchanged in both. This is comparison evidence beyond exit0; see [comparison](../evidence/foundation/a20/repeatability/result.json) and child snapshots.

## Measured environment and execution

Python **3.12.7**, Django **6.0.7**, DRF **3.17.1**, SQLite **3.46.1**. Other measured packages: django-cors-headers4.9.0, redis6.4.0, psycopg3.3.4. Redis/PG packages are installed dependencies, not services exercised here. Runner version is installed Django/Python; no separate unittest package version exists. Raw timestamps are genuine UTC (first team start `2026-11-21T21:56:37.806947+00:00`, which is22November in Asia/Karachi), not fabricated wall-clock values. No browser/OS/hardware version or coverage metric is asserted.

Commands below were executed from repository root with `.venv/bin/python scripts/sqe/run_tests.py`; suffixes specify exact arguments. All result directories contain actual command, timestamps, versions, source/Git state, counts, process status, active DB and hashes. Repeated runs are **12 unique team tests**, not36 independently authored tests.

| Invocation / suffix | Executed | Pass | Fail | Error | Skip / expected fail | Exit | Genuine evidence |
|---|---|---|---|---|---|---|---|---|
| check --evidence-dir docs/sqe/evidence/foundation/a20/check | N/A system check | N/A system check | N/A system check | N/A system check | N/A | 0 | [result](../evidence/foundation/a20/check/result.json) |
| team --evidence-dir docs/sqe/evidence/foundation/a20/team | 12 | 12 | 0 | 0 | 0 / 0 | 0 | [result](../evidence/foundation/a20/team/result.json) |
| upstream --evidence-dir docs/sqe/evidence/foundation/a20/upstream | 9 | 9 | 0 | 0 | 0 / 0 | 0 | [result](../evidence/foundation/a20/upstream/result.json) |
| repeatability child1 (command in JSON) | 12 | 12 | 0 | 0 | 0 / 0 | 0 | [result](../evidence/foundation/a20/repeatability/run-1/result.json) |
| repeatability child2 (command in JSON) | 12 | 12 | 0 | 0 | 0 / 0 | 0 | [result](../evidence/foundation/a20/repeatability/run-2/result.json) |
| team tests.team.foundation.test_foundation.FoundationTests.test_pending_record_and_approved_only_consumption --evidence-dir docs/sqe/evidence/foundation/a20/environment-override | 1 | 1 | 0 | 0 | 0 / 0 | 0 | [result](../evidence/foundation/a20/environment-override/result.json) |
| failure_probe.py wrapper (deliberate non-product failure) | 1 | 0 | 1 | 0 | 0 / 0 | 1 | [result](../evidence/foundation/a20/failure-propagation/result.json) |

The parent repeatability command was `... repeatability --evidence-dir docs/sqe/evidence/foundation/a20/repeatability`, exit0, with12/12 passing in each child. Do not add a separate test count for its comparison. Original system check passed with zero reported issues under the protected profile; original application checks/settings were retained except documented test-only overrides. Upstream9 passed separately and earn no student-owned test credit.

Environment-override invocation was prefixed with **`POSTGRES_DB=sqe_never_connect POSTGRES_HOST=127.0.0.1 POSTGRES_PORT=1 REDIS_URL=redis://127.0.0.1:1/0 DJANGO_SETTINGS_MODULE=config.settings`**. One real selected fixture test passed in the memory DB with Redis disabled, showing inherited external-service choices did not redirect execution. These were sentinel values, not real credentials or a service test.

Failure propagation was verified with `.venv/bin/python docs/sqe/evidence/foundation/a20/failure_probe.py docs/sqe/evidence/foundation/a20/failure-propagation`. This evidence wrapper patches one method **in child-process memory only**, prints distinct stdout/stderr markers, then deliberately fails. Actual tool/process status was1, JSON reports1 failure, both markers and traceback remain in separate logs. This is **not** an application defect, not an upstream failure and not a permanently failing test in discovery. The runner's JSON command records the invoked team selector; the wrapper source documents its deliberate injection. No raw result/log was edited to turn failure into success.

## Foundation IDs and limited traceability

Each test's docstring has FND/FR/BR references (slash notation expands within the same prefix). IDs below are new foundation checks, not a silent completion of the75 planned Phase2 objective families.

| ID | Actual check | Requirement/rule support |
|---|---|---|
| FND-001 | Synthetic identity/team/role/balance relationship | FR-W1-01, FR-W2-01; BR-04 |
| FND-002 | Persisted pending row, fixed weekday count, approved-only consumption | FR-W1-03, FR-W1-05, FR-W1-06; BR-01, BR-03, BR-05 |
| FND-003 | Real login/token lookup, unauthorized401, identity/dashboard and original request IDs | FR-W1-01, FR-W1-05, FR-W2-01; BR-03, BR-04 |
| FND-004 | Stable logical initial snapshot | FR-W1-06, FR-W2-01; BR-03, BR-04, BR-05 |
| FND-005 | Zero remaining, missing balance and exactly sufficient fixtures | FR-W1-05; BR-03 |
| FND-006 | Overlap rejected by default builder, explicit deliberate-overlap opt-in | FR-W1-04; BR-02 |
| FND-007 | Two valid pending4-day scenarios without any approval | FR-W1-05, FR-W1-06; BR-03, BR-05 |
| FND-008/009 | Own-record mutation followed by independent clean test | FR-W1-06; BR-03, BR-05 |
| FND-010/011/012 | Unknown profile/file/URI/external DB/test target refusal and active memory requirement | Infrastructure/data isolation; no fictional application FR |

No complete EP/BVA/decision/state, HTTP create/decision coverage, MCC/MC/DC, mutation, CI, security/performance/accessibility or browser coverage has been measured. These smoke/fixture checks do not complete EC-01–10 or resolve instructor policies.

## Independent verification and usage

From repository root, with existing dependencies installed:

```bash
.venv/bin/python scripts/sqe/run_tests.py check
.venv/bin/python scripts/sqe/run_tests.py upstream
.venv/bin/python scripts/sqe/run_tests.py team
# One area or one actual test:
.venv/bin/python scripts/sqe/run_tests.py team tests.team.foundation
.venv/bin/python scripts/sqe/run_tests.py team tests.team.foundation.test_foundation.FoundationTests.test_real_login_and_token_authenticated_dashboard
```

For new preserved evidence, use a **fresh parent** and new child targets (existing directories are refused without overwriting):

```bash
SQE_VERIFY_DIR="$(mktemp -d /tmp/leaveflow-a20-XXXXXX)"
.venv/bin/python scripts/sqe/run_tests.py check --evidence-dir "$SQE_VERIFY_DIR/check"
.venv/bin/python scripts/sqe/run_tests.py upstream --evidence-dir "$SQE_VERIFY_DIR/upstream"
.venv/bin/python scripts/sqe/run_tests.py team --evidence-dir "$SQE_VERIFY_DIR/team"
.venv/bin/python scripts/sqe/run_tests.py repeatability --evidence-dir "$SQE_VERIFY_DIR/repeatability"
# Separate deliberate harness probe; EXPECT status1, with both streams preserved:
.venv/bin/python docs/sqe/evidence/foundation/a20/failure_probe.py "$SQE_VERIFY_DIR/failure-propagation"
echo $?  # expected1 only for this deliberate self-check
```

No external server, Redis, Docker, Postgres, migrations command or seed/reset command is needed. The suite's test DB is migrated by Django after guards; do not run seed_demo/flush manually. No target override is supported. By default team means only tests.team; upstream must be requested explicitly. A selected empty future package returns nonzero rather than being called a passing suite. Failures/errors/skips/expected failures return nonzero; genuine logs and JSON are retained. Unexpected harness errors return2. No `|| true` or hidden success override is present. Use unique evidence directories, and do not overwrite old raw output.

## Shared contributor contract

- A1: add white-box Python tests under a new importable `tests/team/unit/` package, retaining existing foundation IDs and assertions. A2: add full API/integration cases under existing `tests/team/api/` and `integration/`; generator outputs/tests later under `generated/`. A3: add Python API/browser support under a reviewed `tests/team/helpers/` package; Playwright browser execution needs a later dedicated server/DB profile, not this process-local memory DB or the development server.
- Import `build_people`, `make_request`, `build_reference_fixture`, `build_overapproval_scenario` from `tests.team.fixtures.leave_data` **inside Django TestCase setup/setUpTestData**, after runner DB setup. Never create records at module import. Return/store objects and actual IDs; use unique synthetic prefixes for multiple scenarios in a test.
- Keep all ordinary fixtures fixed-date and nonoverlapping; create invalid states only with explicit scenario intent/flags. Do not change defaults to make one test pass. Password hashes/token values/current timestamps must not enter logical signatures; use a fresh APIClient per test and real token auth where relevant. Keep fixture/environment globals immutable; the runner's context-local snapshot collector resets after each suite.
- Use unique meaningful `test_...` method names and controlled planned IDs/FR/BR references; new FND IDs are for infrastructure, not a substitute for the existing RTM. Expand planned families with actual node IDs and evidence as later suites arrive. Do not copy upstream test bodies or count repeated execution as new coverage.
- Shared fixture changes require coordinated student peer review: one agreed owner per change, discuss affected assumptions/IDs, preserve APIs or add explicit optional parameters, rerun foundation+upstream+two-run comparison, link evidence and let students resolve their own Git/PR conflicts. No shared mutable test data, unchecked SQL cleanup, production seed, external environment switch or application fix to force green.
- Keep failed stdout/stderr/JSON and the exact tested SHA/source hashes; redact credentials before publishing new evidence, never fabricate or edit outcomes. All student commits/reviews remain student-owned; no contributions or approvals are attributed to absent people.

## Remaining A2.1 / A2.2 work

Proposed next sequencing: **A2.1** implements full source-grounded W1/W2 API/integration cases, ordered permission/value/state failures, persisted readback/repeats and the genuine failing-before approval-balance regression through the same returned IDs. The prepared allowance5/two4-day pending scenario does not approve requests here, does not assert negative available is correct, and does not fix or suppress the suspected defect. Obtain desired rejection/error contract (agreed 25 Nov 2026: 400, GAP-01) and implement any later fix only under separate reviewed authorization. PostgreSQL concurrency/recovery and browser server isolation need their own approved profiles.

**A2.2** authors accurate OpenAPI/rule metadata and the generator, generated EP/three-point BVA cases consumed by APIs, decision/state coverage and two-constraint regeneration demonstration. Full white-box/MCC/MC/DC, mutations, strict PR CI, six accepted UCs, security/accessibility/performance/recovery and major-defect RCA remain later work. Policy/scope/UC ambiguities stay unresolved; original planning/requirements files were not rewritten as completed results.

All seven instructor PDF pages and relevant Phase1/2/source/config/migration/seed/upstream files informed this implementation; no lecture PDF was found. See [AI disclosure](../AI-USE-RECORD.md). Students still need to review the code, proof and usage before committing/submitting.

## Independent re-verification (23 November 2026, Asia/Karachi)

An audit session re-inspected the uncommitted A2.0 files and re-ran the full verification set without changing any test, fixture, runner, settings or production file. New evidence is in `docs/sqe/evidence/foundation/a20-reverify-20261123/` (new directory; the 22 November evidence is untouched). Same tested HEAD `0a9a3f00e30859adca969a2673fa3e7698357d34`, branch `test/isolated-fixtures-and-baseline`; Python source SHA-256 values in the team result match the 22 November run for every file.

| Invocation | Executed | Pass | Fail/Error/Skip | Exit |
|---|---|---|---|---|
| check | system check | passed | - | 0 |
| upstream | 9 | 9 | 0/0/0 | 0 |
| team | 12 | 12 | 0/0/0 | 0 |
| repeatability (run-1, run-2; separate processes) | 12 + 12 | 12 + 12 | 0/0/0 | 0 |
| environment-override (sentinel POSTGRES_*/REDIS_URL, single test) | 1 | 1 | 0/0/0 | 0 |
| failure_probe.py (deliberate harness self-check) | 1 | 0 | 1/0/0 | 1 (expected) |

Repeatability comparison: reference_equal=true; both reference hashes `0ccd88034572d556a2f9eab7887af1841ca313422e2e88e475c9b68b358465c7` (same as 22 November); mutation-then-independent-test rollback true in both runs. `backend/db.sqlite3` stayed 180224 bytes, SHA-256 `70155559be6dc448fa8eb05e804ff7a60532afbac881bac21bc42de47cbcd33d`, no sidecars, before and after. All runs used the active target `file:memorydb_default?mode=memory&cache=shared`. A search of the new evidence for token-like strings and the fixture password found none.

Known limitations noted during the audit: FND-008/009 rely on explicit `test_01`/`test_02` method ordering to demonstrate rollback (FND-009 also asserts the initial state independently); the runner calls `git` for metadata, which on a Windows-side checkout of a WSL path needs a per-command `safe.directory` exception, so run it from inside WSL; the approval-time balance defect remains unfixed and unasserted, as required.

## Changes after A2.0 (25 November 2026)

- **Hasher:** the core profile now uses Django's MD5 hasher for its synthetic accounts, as the browser profile already did (277 tests: 429 s before, 10 s after). Earlier evidence was recorded with the default hasher.
- **PostgreSQL profile `sqe-postgres-v1`:** `tests/team/postgres_safety.py` and `postgres_settings.py`, selected only by `scripts/sqe/run_concurrency.py`. That script starts its own container (random name, password and loopback port, data in memory, no volume) and removes exactly that container. The guard accepts only 127.0.0.1, a `sqe_disposable_<random>` database, and a live server that reports this run's random `cluster_name`. The statement above that the foundation supports no external database still holds for `run_tests.py`.
