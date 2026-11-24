# Critical-module evidence (DR-001), 24 November 2026

Commit under test: `44b8ef8` (branch `docs/uc-reconciliation`). The development database was never opened: the guards compare its metadata, and it was unchanged.

| File | What it is | Command (repository root, inside WSL) |
|---|---|---|
| `radon-cc.txt` | Cyclomatic complexity per function (radon 6.0.1; each boolean operator adds 1) | `PYTHONPATH=<tools> .venv/bin/python -m radon cc -s -a backend/leave/serializers.py backend/leave/models.py backend/leave/views.py` |
| `coverage-report.txt`, `coverage-candidates.json`, `coverage-run.log` | Statement/branch coverage that the **existing A2.1 API suite** (40 tests, profile sqe-memory-v1) already achieves on the candidate files. This is not white-box unit coverage | `COVERAGE_FILE=/tmp/... PYTHONPATH=<tools> .venv/bin/python -m coverage run --branch --include='backend/leave/serializers.py,backend/leave/views.py,backend/leave/models.py' scripts/sqe/run_tests.py team tests.team.api` then `coverage report -m` / `coverage json` |
| `feasibility_probe.py`, `feasibility.json`, `feasibility-probe.log` | Executes every feasible truth row of D1, H and D2 on the in-memory test database and counts evaluations of the D1 right operand | `.venv/bin/python docs/sqe/evidence/whitebox/critical-module-2026-11-24/feasibility_probe.py <out.json>` |

`<tools>` was a temporary `pip install --target` folder (coverage 7.6.10, radon 6.0.1), so the project `.venv` was not modified. Sonar was not run; its complexity convention may differ from radon's.
