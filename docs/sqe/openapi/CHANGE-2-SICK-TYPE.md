# Change 2 — add `leave_type` value `sick`

Constraint-change demonstration for A2.4. The spec was changed temporarily, the tests were regenerated from it and run against the **unchanged** application, and then the spec was restored. Executed 24 November 2026 on branch `test/a2.4-openapi-gen` (base `cec9c07`) with the in-memory test profile. The development database was unchanged.

## 1. Spec change

Diff of `docs/sqe/openapi/leaveflow-api.yaml`, applied temporarily:

```diff
@@ -364,7 +364,7 @@   components.schemas.LeaveRequestInput.properties.leave_type
         leave_type:
           type: string
-          enum: [vacation, permit, personal]
+          enum: [vacation, permit, personal, sick]
           default: vacation
@@ -432,7 +432,7 @@   components.schemas.LeaveRequest.properties.leave_type (response)
         leave_type:
           type: string
-          enum: [vacation, permit, personal]
+          enum: [vacation, permit, personal, sick]
```

| | SHA-256 |
|---|---|
| Original spec (restored afterwards) | `219e3766d5de18124f6c4380135373a372ebdf069fa03e3509cae96d040ed174` |
| Changed spec used for v3 | `a56ada99788d81cf38f7747d9f575b96651ff6ffd4d96b51d46b4ca5e1b238ac` (recorded in the v3 file header) |

The application's choices are still `LeaveRequest.Type` = vacation / permit / personal (`backend/leave/models.py:47–50`). No application code was changed.

## 2. Generated-test diff (v1 → v3)

```
python3 scripts/sqe/generate_api_tests.py docs/sqe/openapi/leaveflow-api.yaml \
    --output tests/team/generated/test_generated_api_v3.py --demo-env SQE_SPEC_CHANGE_DEMO=v3
```

Generator summary: `leave_type: 3 valid EP, 2 invalid EP` → `leave_type: 4 valid EP, 2 invalid EP`. Totals: W1 goes from 20 to 21 tests, and the whole file from 33 to 34.

| Change | Test | Expectation |
|---|---|---|
| added | `test_leave_type_ep_valid_enum_value_sick` — body `leave_type: "sick"`, other fields at the example | valid → 201 |
| unchanged | the 33 v1 tests, including the out-of-enum class `'zzz_not_in_enum'` and the wrong-type class `true` | as in v1 |

The out-of-enum probe value is a fixed sentinel, so adding `sick` does not move any invalid class. No test is removed.

## 3. Results against the unchanged application

```
SQE_SPEC_CHANGE_DEMO=v3 .venv/bin/python scripts/sqe/run_tests.py team \
    tests.team.generated.test_generated_api_v3 --verbosity 2
Ran 34 tests ... FAILED (failures=1)     process exit code 1
```

| v3 test | Spec v3 expects | App returned | Result |
|---|---|---|---|
| `test_leave_type_ep_valid_enum_value_vacation` / `permit` / `personal` | 2xx | 201 | pass |
| **`test_leave_type_ep_valid_enum_value_sick`** | **2xx** | **400, no row** | **FAIL** |
| `test_leave_type_ep_invalid_out_of_enum_zzz_not_in_enum` | 4xx | 400 | pass |
| `test_leave_type_ep_invalid_wrong_type_true` | 4xx | 400 | pass |
| all other 28 tests | unchanged | as before | pass |

Failure message:

```
AssertionError: False is not true : expected 2xx: POST /api/requests/ -> 400
{'leave_type': [ErrorDetail(string='"sick" non è una scelta valida.', code='invalid_choice')]}
```

**Interpretation.** The application does not recognise `sick`. DRF's ChoiceField, derived from the model's `choices`, rejects it as `invalid_choice`. This is the opposite direction to Change 1: the spec is now *more permissive* than the application, and the gap shows up as a valid-class test failing.

Supporting `sick` would take more than the enum. The changes needed would be:

- a new `LeaveRequest.Type` member with an Italian label, plus a migration for the choices;
- the frontend type selector, and the English/Italian strings;
- a decision on whether sick leave consumes the vacation allowance (BR-03 currently counts every approved type);
- the event and notification payloads.

That is a product decision, outside the scope of this demonstration. No application change was made.

## 4. Suite isolation and restore

- `test_generated_api_v3.py` loads its tests only when `SQE_SPEC_CHANGE_DEMO=v3`. Without it, the module contributes 0 tests (verified: `Ran 0 tests`).
- The spec was restored byte-for-byte; its SHA-256 equals the original.
- Full team suite after the restore: `Ran 157 tests ... OK` (process exit 0). Upstream: `Ran 9 tests ... OK`.

## 5. Re-run on 25 November 2026

The generator was extended after the PR #10 review (path, token, optional-field and business-rule inputs; exact status instead of any documented 4xx), so the demonstration was regenerated and re-run against the same unchanged application on commit `3ebeb40`. Sections 1–4 keep the 24 November run as history; the numbers below are current, and the committed v3 file is the one of this run.

| | |
|---|---|
| Original spec SHA-256 (restored, byte-identical) | `00167b42eee65d5ae1ae55c1e56c6efff110aebea8fe50444a25fa48eb7fb61a` |
| Changed spec SHA-256 | `60ad933a87f6ced0f7dfb6a78ecbc3b3bb143e4ac6edc2f99bafaceab0a49400` |
| Generated | v1: 68 tests; v3: 69 tests |
| Test-name diff | `test_leave_type_ep_valid_enum_value_sick` added; 68 unchanged |
| Result | 69 run, 68 passed, **1 failed** (exit code 1) |
| Failing test | `test_leave_type_ep_valid_enum_value_sick`: expected 201, application returned 400 `invalid_choice` |
| Evidence | `docs/sqe/evidence/generated/change-2-sick-type-2026-11-25/` |

## 6. Final run on 25 November 2026 (current)

Supersedes section 5. The limit is now applied after trimming in the spec, as the application does, and the change is applied with `--patch`, so the baseline spec is never edited. Commands: [README](README.md).

| | |
|---|---|
| Change | `changes/change-2-sick-type.patch` |
| Baseline spec SHA-256 (not edited) | `e5095486e105b397e3c32ea02c2ff7de6130100663dfa46218ced8159f042151` |
| Changed spec SHA-256 | `ff887cd86d9667c3cc6b15f4db1339dc5a16d05670fac5f99ebb02928c33e400` |
| Generated-test diff | `test_leave_type_ep_valid_enum_value_sick` added; 127 unchanged |
| Result | 128 run, 127 passed, **1 failed** (exit code 1) |
| Failing | `test_leave_type_ep_valid_enum_value_sick`: expected 201, application returned 400 `invalid_choice` |
| Evidence | `docs/sqe/evidence/generated/change-2-sick-type-final-2026-11-25/` (commit `707a5b3`) |
