# Area 3 performance protocol

The measured operation is the authenticated team-scoped `GET /api/requests/` list opened by a manager before a decision. It reads the same record set throughout the run, which keeps the workload comparable and isolates read performance from approval balances and future deployment tuning. The database contains 20 synthetic pending requests for one employee in the manager’s team.

Before running k6, set budgets of **p95 ≤ 500 ms** and **unexpected failures < 1%** for both workloads. A half-second response keeps the decision queue responsive in a local demo. The error budget tolerates isolated measurement noise while treating an authorization error, wrong dataset size, or sustained backend error as a failure. Run 1 VU and 5 VUs twice each at a constant level for 70 seconds, with a 200 ms pause per VU after each request. Exclude authentication in setup from the operation metrics.

Run all four repeats with the same checkout, machine, disposable backend, and unchanged request rows. Record measured milliseconds, completion rate in requests per second, unexpected failures as a percentage, exact tool versions, and exit codes. Save the raw logs and k6 summaries alongside the comparison. A nonzero exit code or a missing metric fails verification and belongs in the evidence.

```powershell
python scripts/sqe/run_performance.py --k6 k6 --evidence-dir .venv/evidence/performance
```
