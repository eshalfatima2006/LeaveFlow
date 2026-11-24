# CFG and hand-calculated complexity

Critical module: the DR-001 W1 validation chain, with `LeaveRequestSerializer.validate`
as the decision-heavy entry point.

## `LeaveRequestSerializer.validate`

The four observable predicates are:

| ID | Predicate | True path | False path |
|---|---|---|---|
| P1 | `instance.clean()` raises `ValidationError` | Normalize and raise the validation error | Continue to balance lookup |
| P2 | `hasattr(exc, "message_dict")` | Raise field-keyed errors | Raise message-list errors |
| P3 | `balance` exists | Evaluate remaining allowance | Return validated attributes |
| P4 | `business_days > balance.available_days` | Raise insufficient-balance error | Return validated attributes |

P2 is evaluated only on P1's true path, and P4 is evaluated only on P3's true
path.  These are control-flow decisions, not four operands in one Python
boolean expression.

## Hand calculation

The CFG has one connected component (`P = 1`). Counting each predicate branch,
the entry/exit nodes and the four decision nodes gives `E = 13` and `N = 10`.

`M = E - N + 2P = 13 - 10 + 2(1) = 5`

This matches the radon complexity result for `LeaveRequestSerializer.validate`
(complexity 5). The five independent paths are:

1. clean error with a field dictionary;
2. clean error with a message list;
3. no balance, successful validation;
4. balance present with enough allowance;
5. balance present with insufficient allowance.

The tests in `tests/team/unit/test_critical_module.py` identify each path and
the MCC/MC/DC evidence records the feasible rows used to reach it.
