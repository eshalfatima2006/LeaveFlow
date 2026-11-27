# Change 3 — `note` becomes nullable

Constraint-change demonstration added after the PR #10 completion report, which found that a nullability change did not alter the generated cases. It did not: null was generated only for required fields, and a nullable field gained no valid null case. Both are fixed in the generator.

| | |
|---|---|
| Change | `changes/change-3-nullable-note.patch`: `nullable: true` on `LeaveRequestInput.note` |
| Baseline spec SHA-256 (not edited) | `e5095486e105b397e3c32ea02c2ff7de6130100663dfa46218ced8159f042151` |
| Changed spec SHA-256 | `5067c18e2944dd76a31b07c1281cb74933d4aace6a67d71facbebf6357af937c` |
| Generated-test diff | `test_note_ep_invalid_null_not_nullable` (expects 400) → `test_note_ep_valid_null_nullable` (expects 201); 126 unchanged |
| Command | see [README](README.md), with `change-3-nullable-note` and v4 |
| Result | 127 run, 126 passed, **1 failed** (exit code 1) |
| Failing test | `test_note_ep_valid_null_nullable`: expected 201, application returned 400 `Il campo non può essere nullo.` |
| Evidence | `docs/sqe/evidence/generated/change-3-nullable-note-final-2026-11-25/` |

**Interpretation.** The spec becomes more permissive than the application. Agreement would need `null=True` on the model field with a migration, or the change withdrawn. No application change was made.
