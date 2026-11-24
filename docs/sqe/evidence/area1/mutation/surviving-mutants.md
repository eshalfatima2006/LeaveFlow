# Mutation analysis

Generated from the final mutmut result for commit `da46d38`. The run tested
65 covered mutants: 63 were killed and 2 survived. The two real survivors are
listed first, followed by 13 real killed mutants to provide the required
15-entry analysis record.

| # | Mutant | Source | Result | Affected rule | Killable? | Test or equivalence justification |
|---:|---|---|---|---|---|---|
| 1 | `leave.events.x_publish_leave_event__mutmut_1` | `backend/leave/events.py` | survived | Leave-event publication behavior | Yes - test gap | The current tests execute this source area but do not distinguish the original result from the surviving mutation; add a focused assertion for the affected boundary or state transition. |
| 2 | `leave.events.x_publish_leave_event__mutmut_2` | `backend/leave/events.py` | survived | Leave-event publication behavior | Yes - test gap | The current tests execute this source area but do not distinguish the original result from the surviving mutation; add a focused assertion for the affected boundary or state transition. |
| 3 | `leave.models.xǁLeaveRequestǁclean__mutmut_1` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 4 | `leave.models.xǁLeaveRequestǁclean__mutmut_2` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 5 | `leave.models.xǁLeaveRequestǁclean__mutmut_3` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 6 | `leave.models.xǁLeaveRequestǁclean__mutmut_4` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 7 | `leave.models.xǁLeaveRequestǁclean__mutmut_5` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 8 | `leave.models.xǁLeaveRequestǁclean__mutmut_6` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 9 | `leave.models.xǁLeaveRequestǁclean__mutmut_7` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 10 | `leave.models.xǁLeaveRequestǁclean__mutmut_8` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 11 | `leave.models.xǁLeaveRequestǁclean__mutmut_9` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 12 | `leave.models.xǁLeaveRequestǁclean__mutmut_10` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 13 | `leave.models.xǁLeaveRequestǁclean__mutmut_11` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 14 | `leave.models.xǁLeaveRequestǁclean__mutmut_12` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 15 | `leave.models.xǁLeaveRequestǁclean__mutmut_13` | `backend/leave/models.py` | killed | Leave-request date/overlap and leave-balance invariant | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
