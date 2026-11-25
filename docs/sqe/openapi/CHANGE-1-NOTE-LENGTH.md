# Change 1 — `note` maxLength 280 → 200

Constraint-change demonstration for A2.4. The spec was changed temporarily, the tests were regenerated from it and run against the **unchanged** application, and then the spec was restored. Executed 24 November 2026 on branch `test/a2.4-openapi-gen` (base `cec9c07`) with the in-memory test profile. The development database was unchanged before and after (180224 bytes, same mtime and inode).

## 1. Spec change

Diff of `docs/sqe/openapi/leaveflow-api.yaml`, applied temporarily:

```diff
@@ -379,7 +379,7 @@   components.schemas.LeaveRequestInput.properties.note
         note:
           type: string
-          maxLength: 280
+          maxLength: 200
           default: ""
@@ -443,7 +443,7 @@   components.schemas.LeaveRequest.properties.note (response)
         note:
           type: string
-          maxLength: 280
+          maxLength: 200
```

| | SHA-256 |
|---|---|
| Original spec (restored afterwards) | `219e3766d5de18124f6c4380135373a372ebdf069fa03e3509cae96d040ed174` |
| Changed spec used for v2 | `89b9f3a51e73d38e600b342d2c2a16f83b5b2b1393c871a05d9d378d4e3bff74` (recorded in the v2 file header) |

The application model still has `note = models.CharField(max_length=280, blank=True)` (`backend/leave/models.py:61`). No application code was changed.

## 2. Generated-test diff (v1 → v2)

Commands:

```
python3 scripts/sqe/generate_api_tests.py                       # v1 (original spec)
python3 scripts/sqe/generate_api_tests.py docs/sqe/openapi/leaveflow-api.yaml \
    --output tests/team/generated/test_generated_api_v2.py --demo-env SQE_SPEC_CHANGE_DEMO=v2
```

Generator summary, `note` line: v1 `note: 3 BVA values (279, 280, 281)` → v2 `note: 3 BVA values (199, 200, 201)`. Totals are unchanged: 33 tests in both versions.

| v1 test (`maxLength 280`) | v2 test (`maxLength 200`) | Expectation |
|---|---|---|
| `test_note_bva_279_below` — 279 chars | `test_note_bva_199_below` — 199 chars | valid → 201 |
| `test_note_bva_280_at` — 280 chars | `test_note_bva_200_at` — 200 chars | valid → 201 |
| `test_note_bva_281_above` — 281 chars | `test_note_bva_201_above` — 201 chars | invalid → 4xx |
| `test_note_ep_invalid_over_max_length_560_chars_280` — 560 chars | `test_note_ep_invalid_over_max_length_400_chars_200` — 400 chars | invalid → 4xx |

The other 29 tests (login, the remaining W1 fields and W2) are generated with the same names and bodies in both versions.

## 3. Results against the unchanged application

```
SQE_SPEC_CHANGE_DEMO=v2 .venv/bin/python scripts/sqe/run_tests.py team \
    tests.team.generated.test_generated_api_v2 --verbosity 2
Ran 33 tests ... FAILED (failures=1)     process exit code 1
```

| v2 test | Length | Spec v2 expects | App returned | Result |
|---|---|---|---|---|
| `test_note_bva_199_below` | 199 | 2xx | 201 | pass |
| `test_note_bva_200_at` | 200 | 2xx | 201 | pass |
| **`test_note_bva_201_above`** | **201** | **4xx** | **201 (row created)** | **FAIL** |
| `test_note_ep_invalid_over_max_length_400_chars_200` | 400 | 4xx | 400 | pass |
| all other 29 tests | — | unchanged | as before | pass |

Failure message, with the 201-character note shortened:

```
AssertionError: False is not true : expected 4xx: POST /api/requests/ -> 201
{'id': 2, ..., 'note': 'nnnn…(201 chars)', 'status': 'pending', ...}
```

**Interpretation.** Under the changed spec, notes of 201–280 characters (after trimming) are invalid, but the application still accepts them, because its limit is 280. The generator probes this region only at the new boundary (201), and that is the test that fails. The 400-character over-max case still passes only because 400 is also above the application's own 280 limit. That pass is coincidental, not agreement with the new spec. Lengths 202–280 fall in the same failing equivalence class but are not generated separately. Conversely, nothing in v2 exercises 279–281 any more, so a regression at the application's real limit would go unnoticed by the v2 tests.

Bringing spec and application back into agreement needs one of two things: the application's `max_length` changed to 200 together with a migration (and the frontend/i18n checked), or the spec change withdrawn. This document does not make that decision, and no application change was made.

## 4. Suite isolation and restore

- `test_generated_api_v2.py` loads its tests only when `SQE_SPEC_CHANGE_DEMO=v2` (`load_tests` protocol). Without it, the module contributes 0 tests. Verified: running the v2 and v3 modules without the variable gives `Ran 0 tests`.
- The spec was restored byte-for-byte: its SHA-256 equals the original. Regenerating v1 afterwards gives identical summary output.
- Full team suite after the restore: `Ran 157 tests ... OK` (process exit 0). Upstream: `Ran 9 tests ... OK`.

## 5. Re-run on 25 November 2026

The generator was extended after the PR #10 review (path, token, optional-field and business-rule inputs; exact status instead of any documented 4xx), so the demonstration was regenerated and re-run against the same unchanged application on commit `3ebeb40`. Sections 1–4 keep the 24 November run as history; the numbers below are current, and the committed v2 file is the one of this run.

| | |
|---|---|
| Original spec SHA-256 (restored, byte-identical) | `00167b42eee65d5ae1ae55c1e56c6efff110aebea8fe50444a25fa48eb7fb61a` |
| Changed spec SHA-256 | `5bb59778f53ab5e9ced10815516e365f111b50d31fce78334639abb9b9792883` |
| Generated | v1: 68 tests; v2: 68 tests |
| Test-name diff | 4 `note` tests replaced (279/280/281/560 → 199/200/201/400); 64 unchanged |
| Result | 68 run, 67 passed, **1 failed** (exit code 1) |
| Failing test | `test_note_bva_201_above`: expected 400, application returned 201 |
| Evidence | `docs/sqe/evidence/generated/change-1-note-length-2026-11-25/` |
