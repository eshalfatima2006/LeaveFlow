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

P2 is evaluated only on P1's true path. P3 and P4 form the short-circuit
Boolean expression `if balance and instance.business_days > balance.available_days:`;
P4 is evaluated only when P3 is true. The exception path and the error-shape
choice are separate control-flow decisions.

## Hand calculation

The CFG has one connected component (`P = 1`). Counting each predicate branch,
the entry/exit nodes and the four decision nodes in `critical-module.mmd`
gives `E = 14` and `N = 11` (all terminal paths share one exit).

`M = E - N + 2P = 14 - 11 + 2(1) = 5`

This matches the radon complexity result for `LeaveRequestSerializer.validate`
(complexity 5). The five independent paths are:

1. clean error with a field dictionary;
2. clean error with a message list;
3. no balance, successful validation;
4. balance present with enough allowance;
5. balance present with insufficient allowance.

The tests in `tests/team/unit/test_critical_module.py` identify each path and
the MCC/MC/DC evidence records the feasible rows used to reach it.

## Measured SonarQube comparison

SonarQube Community Build 26.11.0.134175 measured **4** for the same function
on 27 November 2026; radon and the exception-aware hand CFG give **5**.
The difference is the exception-handler edge: Sonar counts the function entry,
the conditional expression choosing the error shape, the `if`, and its `and`.
Its Python complexity visitor does not add a decision for `except`.
See [SonarSource's ComplexityVisitor](https://github.com/SonarSource/sonar-python/blob/master/python-frontend/src/main/java/org/sonar/python/metrics/ComplexityVisitor.java).

The normal Sonar API exposes file aggregates. To avoid comparing a file or
project total with one function, `scripts/sqe/extract_critical_function.py`
extracts the original `validate` definition unchanged except indentation.
The separate `leaveflow-dr001-complexity` project analyzes that single function.
Its copied source and API result are in [sonar-function/](sonar-function/README.md).
That project's 0% coverage is irrelevant to this syntax-only comparison;
coverage for the real project comes from the full integrated test run.

The real project's complexity is **49**, across its production-source scope.
Neither 49 nor the historical project value 59 is the complexity of `validate`.
