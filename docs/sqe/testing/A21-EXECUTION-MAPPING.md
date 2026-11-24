# A2.1 execution mapping — API case IDs → FR / BR

Local execution mapping for A2.1, created instead of editing the planning RTM (`docs/sqe/planning/REQUIREMENTS-TRACEABILITY-MATRIX.md` v0.1 stays the planning record; its rule is to retain planned IDs and add real node IDs without overwriting). Case IDs below are **children of existing planned RTM families** (`API-W1-00n`, `API-W2-00n`) using a `.NN` suffix; no new FR/BR identifiers were created.

Status vocabulary: **Passed** = executed and passed in the final evidence run [`docs/sqe/evidence/api/a21/final/api`](../evidence/api/a21/final/api/result.json); **Characterization** = passed, but pins current baseline behaviour whose business policy is unresolved (not an approved oracle); **Planned (A2.2)**, **Blocked**, **N/A** as stated.

Node IDs are relative to `tests.team.api.`.

## Implemented and executed cases

| Case ID | Node ID | FR | BR | Status |
|---|---|---|---|---|
| API-W1-001.01 | test_authentication.LoginTests.test_valid_login_returns_token_bound_to_that_user | FR-W1-01 | BR-04 | Passed |
| API-W1-001.02 | test_authentication.LoginTests.test_invalid_credentials_are_refused_without_issuing_tokens | FR-W1-01 | BR-04 | Passed |
| API-W1-001.03 | test_authentication.UnauthenticatedAccessTests.test_protected_endpoints_return_401_without_credentials | FR-W1-01, FR-W2-01, FR-W2-02 | BR-04 | Passed |
| API-W1-001.04 | test_authentication.UnauthenticatedAccessTests.test_malformed_and_invalid_tokens_return_401 | FR-W1-01 | BR-04 | Passed |
| API-W1-001.05 | test_authentication.IdentityAndOwnershipTests.test_token_identity_is_the_authenticated_user_only | FR-W1-01, FR-W2-01 | BR-04 | Passed |
| API-W1-001.06 | test_w1_submission.SuccessfulSubmissionTests.test_manager_and_admin_self_submission_is_owned_by_caller | FR-W1-01, FR-W1-06 | BR-04 | Characterization (FR-W1-01 note) |
| API-W1-001.07 | test_w1_submission.SuccessfulSubmissionTests.test_read_only_and_unknown_fields_cannot_set_owner_or_state | FR-W1-01, FR-W1-02 | BR-04, BR-05, BR-06 | Passed |
| API-W1-002.01 | test_w1_submission.SuccessfulSubmissionTests.test_each_leave_type_and_omitted_default | FR-W1-02 | BR-06 | Passed |
| API-W1-002.02 | test_w1_submission.SuccessfulSubmissionTests.test_note_optional_blank_and_length_boundaries | FR-W1-02 | BR-06 | Passed |
| API-W1-002.03 | test_w1_submission.PayloadValidationTests.test_missing_and_null_fields_rejected_without_insert | FR-W1-02 | BR-06 | Passed |
| API-W1-002.04 | test_w1_submission.PayloadValidationTests.test_invalid_date_type_and_note_values_rejected | FR-W1-02 | BR-06 | Passed |
| API-W1-002.05 | test_w1_submission.PayloadValidationTests.test_malformed_json_and_unsupported_media_type | FR-W1-02 | BR-06 | Passed |
| API-W1-003.01 | test_w1_submission.DateRuleTests.test_end_before_start_rejected_on_end_date | FR-W1-03 | BR-01 | Passed |
| API-W1-003.02 | test_w1_submission.DateRuleTests.test_inclusive_weekday_counts | FR-W1-03, FR-W1-06 | BR-01 | Passed |
| API-W1-003.03 | test_w1_submission.DateRuleTests.test_weekend_only_request_is_accepted_with_zero_days | FR-W1-03 | BR-01 | Characterization (no positive-day minimum) |
| API-W1-003.04 | test_w1_submission.DateRuleTests.test_past_dates_are_accepted | FR-W1-03 | BR-01 | Characterization (no date-vs-today rule) |
| API-W1-004.01 | test_w1_submission.OverlapTests.test_inclusive_boundaries_against_pending_request | FR-W1-04 | BR-02 | Passed |
| API-W1-004.02 | test_w1_submission.OverlapTests.test_approved_request_blocks_and_neighbour_passes | FR-W1-04 | BR-02, BR-05 | Passed |
| API-W1-004.03 | test_w1_submission.OverlapTests.test_rejected_request_dates_can_be_reused_as_new_row | FR-W1-04 | BR-02, BR-05 | Passed |
| API-W1-004.04 | test_w1_submission.OverlapTests.test_other_employee_may_request_same_dates | FR-W1-04, FR-W1-01 | BR-02, BR-04 | Passed |
| API-W1-005.01 | test_w1_submission.BalanceTests.test_requested_days_at_available_boundary | FR-W1-05 | BR-03, BR-01 | Passed |
| API-W1-005.02 | test_w1_submission.BalanceTests.test_available_counts_approved_history_only | FR-W1-05 | BR-03 | Passed |
| API-W1-005.03 | test_w1_submission.BalanceTests.test_zero_and_negative_available | FR-W1-05 | BR-03 | Passed (A=0); negative-A row Characterization (GAP-01) |
| API-W1-005.04 | test_w1_submission.BalanceTests.test_missing_balance_record_skips_the_check | FR-W1-05 | BR-03 | Characterization (GAP-07) |
| API-W1-005.05 | test_w1_submission.BalanceTests.test_pending_requests_reserve_no_allowance | FR-W1-05, FR-W1-06 | BR-03 | Characterization (GAP-01) |
| API-W1-006.01 | test_w1_submission.SuccessfulSubmissionTests.test_valid_employee_submission_persists_one_pending_owned_row | FR-W1-01, FR-W1-06 | BR-04, BR-05, BR-06 | Passed |
| API-W2-001.01 | test_w2_decisions.VisibilityTests.test_request_list_and_dashboard_scope_by_role | FR-W2-01 | BR-04 | Passed |
| API-W2-002.01 | test_w2_decisions.DeniedDecisionTests.test_employee_role_cannot_decide | FR-W2-02 | BR-04 | Passed |
| API-W2-002.02 + API-W2-005.01 | test_w2_decisions.AuthorizedDecisionTests.test_same_team_manager_approves_pending_and_balance_is_derived | FR-W2-02, FR-W2-04, FR-W2-05 | BR-03, BR-04, BR-05 | Passed |
| API-W2-002.03 | test_w2_decisions.AuthorizedDecisionTests.test_admin_decides_requests_of_any_team | FR-W2-02, FR-W2-05, FR-W2-06 | BR-04, BR-05 | Passed |
| API-W2-002.04 | test_w2_decisions.DeniedDecisionTests.test_out_of_scope_managers_receive_404 | FR-W2-01, FR-W2-02 | BR-04 | Passed |
| API-W2-002.05 | test_w2_decisions.DeniedDecisionTests.test_self_decision_forbidden_for_every_privileged_role | FR-W2-02 | BR-04, BR-05 | Passed |
| API-W2-002.06 | test_authentication.IdentityAndOwnershipTests.test_employee_cannot_decide_or_reach_another_users_request | FR-W2-02 | BR-04, BR-05 | Passed |
| API-W2-002.07 | test_w2_decisions.DeniedDecisionTests.test_nonexistent_and_unroutable_ids | FR-W2-02 | BR-04 | Passed |
| API-W2-003.01 | test_w2_decisions.DecisionValueTests.test_missing_null_and_invalid_status_values | FR-W2-03 | BR-05, BR-06 | Passed |
| API-W2-003.02 | test_w2_decisions.DecisionValueTests.test_guard_precedence | FR-W2-02, FR-W2-03 | BR-04, BR-05, BR-06 | Passed |
| API-W2-003.03 | test_w2_decisions.AuthorizedDecisionTests.test_extra_body_keys_cannot_override_audit_or_content | FR-W2-03, FR-W2-05 | BR-05, BR-06 | Passed |
| API-W2-004.01 | test_w2_decisions.FinalStateTests.test_approved_and_rejected_requests_cannot_be_decided_again | FR-W2-04 | BR-05 | Passed |
| API-W2-004.02 | test_w2_decisions.FinalStateTests.test_repeat_after_successful_decision_conflicts | FR-W2-04 | BR-05 | Passed |
| API-W2-006.01 | test_w2_decisions.AuthorizedDecisionTests.test_same_team_manager_rejects_pending_without_charging_allowance | FR-W2-02, FR-W2-04, FR-W2-06 | BR-03, BR-04, BR-05 | Passed |

40 test methods, 40 case IDs (API-W2-002.02 and API-W2-005.01 share one method). Earlier foundation checks FND-001..012 remain in `tests/team/foundation/` and are not recounted here.

## Per-requirement status — what A2.1 does and does not establish

A reference from a test is not full verification. "API-level: exercised" means the stated API behaviour is executed with DB readback; the other planned levels (unit, browser, generated EP/BVA, integration, events) are still open.

| FR | A2.1 API status | Still open (planned elsewhere) |
|---|---|---|
| FR-W1-01 | Exercised: 401/no-row, token binding, injected owner/status ignored | Browser login→submit (A3/UCs); UT-W1-001 (A1) |
| FR-W1-02 | Exercised: required/null/enum/default/note 279/280/281/trim, protocol 400/415 | Generated EP/BVA (A2.2 GEN-001); scalar-coercion edge cases not asserted |
| FR-W1-03 | Exercised: reversed 400, 0/1/2/3/5/6-day counts, cross-year, leap day | UI preview agreement (browser); date.max/huge-span robustness (Blocked: robustness scope not approved) |
| FR-W1-04 | Exercised: before/touch/inside/after/enclose vs pending; approved blocks; rejected reusable; other owner | Concurrent duplicate submission (later, PostgreSQL profile) |
| FR-W1-05 | Exercised: A−1/A/A+1, approved-only aggregate, A=0, A<0, missing balance | MCC/MC/DC D1 (A1); policy decisions GAP-01/GAP-07 |
| FR-W1-06 | Exercised: 201 contract, single pending row, list/dashboard readback, allowance unchanged | Event publication after commit (Redis disabled here — Blocked in this profile); UI refresh (browser) |
| FR-W2-01 | Exercised: 7 roles/teams, exact ID sets, dashboard counts | People/team endpoint boundaries not asserted |
| FR-W2-02 | Exercised: employee 403, out-of-scope/teamless 404, self 403 (3 roles), admin cross-team, missing IDs | UI self-decision button mismatch GAP-04 (browser) |
| FR-W2-03 | Exercised: 11 invalid bodies → 400, precedence, extra keys ignored | Schema/OpenAPI accuracy (A2.2) |
| FR-W2-04 | Exercised: both final states × both values × manager/admin → 409; repeat after success | Lock behaviour under concurrency (not reproduced; SQLite) |
| FR-W2-05 | Exercised single-step: approval actor/time, used +D | **Same-record W1→W2 flow and approval-time over-allowance regression: Planned (A2.2, API-INT-001)**; event recipient |
| FR-W2-06 | Exercised single-step: rejection actor/time, used unchanged | Rejection→later W1 reuse of the same k (A2.2, API-INT-002); event recipient |
