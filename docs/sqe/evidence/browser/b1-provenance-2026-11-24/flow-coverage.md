# Use-case flow coverage (v0.2-2026-11-24)

Mandatory flows: 30 specified · 10 executed (33.3%) · 10 passed (33.3%) · 20 not yet automated.

| Use case | Specified | Executed | Passed |
|---|---|---|---|
| UC-01 | 5 | 5 | 5 |
| UC-02 | 5 | 5 | 5 |
| UC-04 | 5 | 0 | 0 |
| UC-07 | 5 | 0 | 0 |
| UC-08 | 5 | 0 | 0 |
| UC-09 | 5 | 0 | 0 |

## Mandatory flows

| ID | Kind | Status | Flow |
|---|---|---|---|
| TC-UC01-M | main | passed | Employee submits a valid request at the allowance boundary (D = A) |
| TC-UC01-A1 | alternative | passed | Employee revises the dates after the working-day preview |
| TC-UC01-A2 | alternative | passed | Employee abandons the request before submitting |
| TC-UC01-E1 | exception | passed | Overlap with an own active request (inclusive boundary), then corrected |
| TC-UC01-E2 | exception | passed | Requested days exceed remaining entitlement (D = A + 1), then shortened |
| TC-UC02-M | main | passed | Team manager approves pending request k (D = available) |
| TC-UC02-A1 | alternative | passed | Team manager rejects k: no charge, dates released |
| TC-UC02-A2 | alternative | passed | Administrator decides a pending request of another team |
| TC-UC02-E1 | exception | passed | k already decided by another approver after the page loaded (409) |
| TC-UC02-E2 | exception | passed | Manager attempts to decide their own pending request (403) |
| TC-UC04-M | main | not automated | Employee reviews own requests and remaining entitlement (no writes) |
| TC-UC04-A1 | alternative | not automated | Filter own requests by outcome (<<extend>>) |
| TC-UC04-A2 | alternative | not automated | Outcome changes during the journey; reload shows the new state |
| TC-UC04-E1 | exception | not automated | Session no longer valid on reload (not signed in) |
| TC-UC04-E2 | exception | not automated | Server error while loading requests (expected result set after runtime probe) |
| TC-UC07-M | main | not automated | Employee receives a live decision alert (feed, dedup key, ack, gateway) |
| TC-UC07-A1 | alternative | not automated | Managers/admins receive a new-request alert; outsiders and requester do not |
| TC-UC07-A2 | alternative | not automated | Recipient offline during the event sees it from the stored feed |
| TC-UC07-E1 | exception | not automated | Notification gateway unavailable: rendered unavailable message, core app usable |
| TC-UC07-E2 | exception | not automated | Event publication fails during a decision: decision persists, no alert |
| TC-UC08-M | main | not automated | Administrator changes an employee's entitlement |
| TC-UC08-A1 | alternative | not automated | Administrator creates a missing entitlement record |
| TC-UC08-A2 | alternative | not automated | Entitlement reduced below approved use (characterisation: no warning) |
| TC-UC08-E1 | exception | not automated | Invalid entitlement value (-1 rejected, 0 accepted, empty required; upper bound engine-dependent) |
| TC-UC08-E2 | exception | not automated | Duplicate entitlement for the same employee |
| TC-UC09-M | main | not automated | Administrator moves an employee to another approving team |
| TC-UC09-A1 | alternative | not automated | Administrator grants approval authority by role |
| TC-UC09-A2 | alternative | not automated | Administrator removes the employee from every team (characterisation) |
| TC-UC09-E1 | exception | not automated | Target team removed while the reassignment form is open (invalid choice, no change) |
| TC-UC09-E2 | exception | not automated | Employee record removed while the reassignment form is open (admin redirect warning, nothing recreated) |

## Blocked regression objectives (outside the mandatory denominator)

| ID | Status | Blocked by |
|---|---|---|
| OBJ-UC02-01 | skipped | Approval-time error contract not approved (TEST-BASIS GAP-01); baseline approves |

## Supplementary checks (outside the mandatory denominator)

| ID | Status | Purpose |
|---|---|---|
| SUP-UC09-01 | not automated | Authorization/integration check of the reassignment postcondition (BR-04); not a mandatory flow |
| SUP-UC07-01 | not automated | Dedup control (store NX key) |

## Observations

| ID | Status |
|---|---|
| OBS-UC08-01 | Predicted from source (no __str__, no list_display); requires browser verification |
| OBS-UC02-01 | Observed in browser on 2026-11-23 (console logs the unhandled error) |
| OBS-UC01-01 | Observed in browser on 2026-11-23 (recorded in runs b1/run-1 and run-2; added to the registry after those runs' coverage reports were generated) |
