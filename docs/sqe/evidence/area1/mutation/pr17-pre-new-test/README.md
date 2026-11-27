# Exact PR #17 tree before the event-recipient assertion

The unchanged application source and test suite from PR #17 commit
`65e229d` were copied to a disposable Linux directory and run through mutmut
3.8.1. The [complete metadata export](results.json) records **295 killed,
4 survived, 299 total, 0 unresolved**, matching [hosted run 74, attempt 4](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/46052602581).
The source SHA-256 values and every mutant's exact diff are in `results.json`.

| Source file | Killed | Survived | Total |
|---|---:|---:|---:|
| `backend/leave/models.py` | 24 | 0 | 24 |
| `backend/leave/serializers.py` | 36 | 0 | 36 |
| `backend/leave/views.py` | 5 | 0 | 5 |
| **Critical three files** | **65** | **0** | **65** |
| `backend/leave/events.py` | 88 | 2 | 90 |
| `backend/leave/management/commands/seed_demo.py` | 142 | 2 | 144 |

The four survivors are E-8, E-10, S-69 and S-123 as defined in
[`../surviving-mutants.md`](../surviving-mutants.md). E-10 is killable; the
other three are equivalent under the current model and stored behavior.
This exact-branch score is separate from the combined local result with PR #10.
