# Mutation analysis

Generated from the successful GitHub Actions mutation run for commit
`de3a60b`. The run tested 153 mutants: 151 were killed and 2 survived. The
mutation score was 98.69%, above the documented 60% threshold. The two real
survivors are listed first, followed by 13 killed mutants to provide the
required 15-entry analysis record.

| # | Mutant | Source | Result | Affected rule | Killable? | Test or equivalence justification |
|---:|---|---|---|---|---|---|
| 1 | `leave.events.x_build_leave_event__mutmut_8` | `backend/leave/events.py` | survived | Leave-event payload construction | Yes - test gap | The focused event tests cover the observable payload and recipient behavior, but do not distinguish this remaining mutation; add a narrower assertion for the affected payload boundary if this behavior becomes critical. |
| 2 | `leave.events.x_build_leave_event__mutmut_10` | `backend/leave/events.py` | survived | Leave-event payload construction | Yes - test gap | The focused event tests cover the observable payload and recipient behavior, but do not distinguish this remaining mutation; add a narrower assertion for the affected payload boundary if this behavior becomes critical. |
| 3 | `leave.events.x_build_leave_event__mutmut_1` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 4 | `leave.events.x_build_leave_event__mutmut_2` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 5 | `leave.events.x_build_leave_event__mutmut_3` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 6 | `leave.events.x_build_leave_event__mutmut_4` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 7 | `leave.events.x_build_leave_event__mutmut_5` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 8 | `leave.events.x_build_leave_event__mutmut_6` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 9 | `leave.events.x_build_leave_event__mutmut_7` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 10 | `leave.events.x_build_leave_event__mutmut_9` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 11 | `leave.events.x_build_leave_event__mutmut_11` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 12 | `leave.events.x_build_leave_event__mutmut_12` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 13 | `leave.events.x_build_leave_event__mutmut_13` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 14 | `leave.events.x_build_leave_event__mutmut_14` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
| 15 | `leave.events.x_build_leave_event__mutmut_15` | `backend/leave/events.py` | killed | Leave-event publication behavior | No - killed by suite | The mutation changed observable behavior and was detected by the executed pytest suite. |
