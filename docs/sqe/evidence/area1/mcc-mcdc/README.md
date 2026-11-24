# MCC and MC/DC evidence for DR-001

The analysis is based on the current source, not on an assumed requirement.
The four assignment business rules are mapped to the repository's current
validation chain as follows:

| Rule | Source decision | Test evidence |
|---|---|---|
| BR-01 | ordered inclusive interval and weekday counting | `test_business_days_covers_weekend_weekday_and_mixed_interval`, `test_clean_rejects_reversed_dates_with_field_error` |
| BR-02 | active overlap query | `test_clean_accepts_nonoverlap_and_rejects_pending_and_approved_overlap`, `test_clean_ignores_rejected_requests_and_excludes_self` |
| BR-03 | approved-only balance aggregation | `test_approved_days_counts_only_approved_and_available_is_remaining` |
| BR-04 | missing/equal/insufficient available balance | serializer tests in `BalanceAndSerializerTests` |

## Multiple-condition coverage

For the serializer balance guard, define `B = balance exists` and
`E = business_days > available_days`. Because Python short-circuits `B and E`,
the two rows with `B = false` and an asserted value of `E` are infeasible: E
is not evaluated. The complete feasible combination set is therefore:

| Row | B | E | Evaluation | Result |
|---|---:|---:|---|---|
| MCC-01 | F | masked | `available_days` not evaluated | valid; missing-balance policy |
| MCC-02 | T | F | `available_days` evaluated | valid |
| MCC-03 | T | T | `available_days` evaluated | insufficient-balance error |

The clean-error decision has its own complete pair of observable outcomes:

| Row | P1: clean raises | P2: message dictionary | Result |
|---|---:|---:|---|
| MCC-04 | T | T | field-keyed error for reversed dates |
| MCC-05 | T | F | non-field error for active overlap |

These five rows cover every feasible control-flow combination in the critical
validation chain. The view visibility predicate is exercised separately by the
existing API suite and the direct `ViewBranchTests`.

## MC/DC pairs

For `B`, the pair MCC-01/MCC-02 keeps the successful validation outcome the
same while demonstrating that B independently controls whether the right-hand
balance expression is evaluated. This is the required short-circuit/masking
interpretation and is explicitly recorded rather than silently presenting an
infeasible `B = F, E = T` row.

For `E`, MCC-02/MCC-03 holds B true and changes only E; the outcome changes from
valid to insufficient-balance error.

For the error-shape decision P2, MCC-04/MCC-05 holds P1 true and changes only
P2; the result changes from a field-keyed error to a non-field error.

The instructor should confirm that this masking interpretation is acceptable
for the final report; the implementation preserves both concrete rows and
their evaluation evidence for auditability.
