# Hosted mutation result for PR #17

Source: [CI run 74, attempt 4](https://github.com/eshalfatima2006/LeaveFlow/actions/runs/46052602581),
commit `65e229da86c9563b15ac9a5ec240220025e97329`. The uploaded
`area1-quality-evidence` artifact contains the copied
[`mutmut-cicd-stats.json`](mutmut-cicd-stats.json): 295 killed, 4 survived,
299 total, no unresolved categories, raw score 98.66%. The 85% quality
threshold passed. The artifact did **not** upload mutation metadata or the
generated candidate list, so the JSON alone does not identify the four names.

The local exact-tree rerun and the curated analysis in
[`../surviving-mutants.md`](../surviving-mutants.md) distinguish those mutants
from the combined local run, which included PR #10 tests and killed one more.
The later manager/admin self-exclusion test is a proposed kill for that
additional survivor; it must be verified in a new run before updating this
hosted result.
