## Description

This PR demonstrates a failed quality check for the inclusive overlap rule.
The evidence branch deliberately changes the start-date comparison from
inclusive to exclusive. An existing boundary test catches the regression:
the API accepts a leave request touching an existing request's first day
instead of rejecting it.

This PR must stay open and unmerged. Once CI runs on the revised branch and
the required check is enabled, the failing job and merge box will provide the
blocked-PR evidence. The original business rule remains on the passing branch.
