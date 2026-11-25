# Area 3 verification results

Member 3 tested UC-04, UC-07, UC-08, and UC-09 under the group’s confirmed allocation. The tests use synthetic employees, disposable databases, loopback services, and the public application actions appropriate to each role. The evidence supports the Area 3 rubric and the local LeaveFlow demonstration. [Tracking issue #18](https://github.com/eshalfatima2006/LeaveFlow/issues/18) · [Area 3 PR #20](https://github.com/eshalfatima2006/LeaveFlow/pull/20)

## Browser flows and usability

The four new use cases exercise filtered leave history and session recovery, live and offline notifications, entitlement changes and form errors, and transfer of decision authority. Each mandatory flow has a stable ID and asserts its relevant persisted postcondition. The W1 usability task uses the keyboard to reach the leave type, dates, note, and submit button in order. It first verifies an explained date-order rejection and zero writes, then corrects the dates and confirms one pending row. The W2 usability task verifies that a manager sees the approval and that the same request and employee balance reflect the decision.

| Browser cases | Passed |
|---|---:|
| UC-04, UC-08, and UC-09 | 15 / 15 |
| UC-07, isolated Redis retest | 5 / 5 |
| Member 3 assignment total | **20 / 20** |
| Original UC-01 and UC-02 flows | 10 / 10 |

The combined browser run reported 37 passes, four UC-07 failures, and one skipped overapproval objective outside the mandatory catalogue. Three UC-07 assertions had compared the global Redis pending count with zero. The fourth read the former fixture field while the readback helper was being updated. The isolated retest passed all five UC-07 cases and ended with zero group pending entries and seven entries read. Across the retained runs, all 30 unique mandatory flow IDs passed. The Django team regression passed 53 of 53 and the production frontend build passed. [Evidence index](../evidence/area3-2026-11-25/README.md)

### Notification image defect

The initial end-to-end run passed 17 of the 20 Area 3 cases. The live, new-request, and offline notification flows failed. Redis held 52 events and had no worker consumer group. The built worker image exited at startup when Mix tried to load dependencies through Hex, which was present only in the build stage.

The Dockerfile now assembles a self-contained OTP release. The rebuilt image started and created the consumer group with one consumer and zero pending entries. The end-to-end cases also verify recipients, persisted feeds, authorized live updates, and a controlled failure to publish after a committed approval. Add the isolated build-and-start smoke check to changes touching the notification packaging. Severity high, priority P1, risk PR-12. [Defect #19](https://github.com/eshalfatima2006/LeaveFlow/issues/19)

The combined run also found five unrelated submission events pending with `invalid_recipients`. Django can produce an empty recipient list and the worker requires at least one recipient. The case assertions now verify only the matching stream entries, and the separate UC-07 run measures the whole group on a clean Redis instance. Decide the zero-recipient contract before changing the producer or consumer. Severity medium, priority P2, risk PR-12. [Defect #24](https://github.com/eshalfatima2006/LeaveFlow/issues/24)

### Observed workflow limitations

- **UC-04 loading feedback, medium severity, PR-08.** A failed requests read produces the same empty state as a successful response containing zero requests. The aggregated refresh rejects when one read fails, and the bootstrap handler clears authentication. The test records the misleading state, verifies unchanged rows, and proves the list recovers after sign-in. Preserve an authenticated session across a transient load failure and show a localized retryable error. [Defect #23](https://github.com/eshalfatima2006/LeaveFlow/issues/23)
- **UC-08 reduced allowance, policy review under PR-01.** The admin form accepts a new allowance of two days for an employee who has already used three. The available balance becomes −1. The form validates the allowance field’s nonnegative range and the remaining balance is computed separately. The test characterizes the existing behavior. Agree on an administrative validation or warning policy before changing the entitlement rule.

## Accessibility findings and repair

Authenticated AxeBuilder scans and Lighthouse snapshots cover the request form, decision queue, employee records, notifications, and both admin forms. The report treats a rule surfaced by both tools on the same screen as one finding. The underlying raw reports retain the tool-specific nodes and results. [Lighthouse user-flow documentation](https://github.com/GoogleChrome/lighthouse/blob/main/docs/user-flows.md)

| Finding | Affected element and user impact | Disposition |
|---|---|---|
| Text contrast | The request form’s helper copy and optional-field label were too light on the card. Other screens include muted sidebar, status, and table text. Users with low vision can miss context or status. | Darkened the request form’s two text classes and rescanned the same authenticated state. Review the selectors listed in the evidence for contrast on other pages. |
| Visible and accessible names differ | The LeaveFlow brand button displayed the product name while its accessible name conveyed only the destination. Voice-control users could have trouble invoking the visible label. | Preserved the visible label as the button’s name and the localized destination as its tooltip. |
| Notification count label | `.notification-trigger` presents a visible count that its accessible name omits on the review queue and notification panel. Voice-control users may have difficulty addressing the visible label, and screen-reader users may miss the count. | Include the localized count in the trigger name and verify plural forms. |
| Landmarks and keyboard focus | The dashboard content lacked a main landmark and the request modal lacked a named dialog and focus management. Keyboard and screen-reader users could continue into background controls. | Added the main landmark, a named modal dialog, initial focus, focus containment, Escape, focus return, and an announced validation error. |
| ARIA attributes on admin help icons | Django Admin’s group and permission filter labels contain decorative help tooltip icons with unsupported ARIA attributes. Assistive technology may announce inconsistent help. | Review the Django markup after the planned dependency update. If the issue persists, use a semantic description attached to each labelled control. |
| Robots document | The development SPA serves its HTML fallback for `/robots.txt`. Lighthouse flags the result as invalid. | Add an explicit deployment robots policy for private workflow screens. This is an SEO configuration item. |
| Admin page descriptions | The two authenticated Django Admin forms have no meta description. Lighthouse flags the documents for missing search summaries. | Document the intended indexing policy for private admin pages before adding page metadata. |

The before-and-after request-form scan used the same viewport, synthetic fixture, locale, and Chrome major version. Lighthouse accessibility improved from **96 to 100** and axe violation rules dropped from **3 to 0**. Best practices stayed at **100** and SEO at **80**. The follow-up Playwright run passed the five original W1 flows, the keyboard task, and the final screen audit. The fix preserved the approval and submission contracts, English/Italian strings, and existing reduced-motion behavior.

| Authenticated screen | Lighthouse accessibility | Best practices | SEO | axe violation rules |
|---|---:|---:|---:|---:|
| UC-01 request form after repair | 100 | 100 | 80 | 0 |
| UC-02 review queue | 95 | 100 | 80 | 2 |
| UC-04 own records | 95 | 100 | 80 | 1 |
| UC-07 notification panel | 95 | 100 | 80 | 2 |
| UC-08 entitlement form | 100 | 100 | 80 | 0 |
| UC-09 user form | 97 | 100 | 80 | 1 |

## Defensive security

### Access matrix

| Role | Ordinary application action | Expected | Observed | Persisted check |
|---|---|---:|---:|---|
| Employee | Submit a corrected request | 201 | 201 | One owned pending row |
| Employee | Attempt to decide the employee's own request | 403 | 403 | Row snapshot unchanged |
| Team manager | Approve a visible teammate’s pending request | 200 | 200 | Same row, actor recorded, balance charged once |
| Team manager | Attempt to decide a request from another team | 404 | 404 | No visible action and unchanged rows |

Django’s protected decision view checks the role, then scopes the object lookup by team. The browser cases observe both denied outcomes and persisted state. The Django Admin check also distinguishes staff from a nonstaff employee, then verifies that the local authenticated admin session cookie is HttpOnly, SameSite=Lax, and available over the local HTTP profile. The deployed Django secure-cookie settings are configured separately. ZAP observed a missing HttpOnly flag on the CSRF cookie, which is a different cookie from the admin session cookie. [Authorization source](../../../backend/leave/views.py) · [Cookie configuration](../../../backend/config/settings.py)

### ZAP passive observations

ZAP 2.17.0 proxied the five Playwright checks, including both workflow tasks, and captured both application origins. The passive queue drained before reporting. Findings with equivalent causes are grouped below. The report records local observations and uses the application and proxy configuration to inform triage.

| Observation | Severity and risk | Impact and correction |
|---|---|---|
| CSP and frame protection headers | Medium, PR-02 and JR-01 | Local preview responses lack some browser-side defensive headers. Configure CSP and a frame policy at the deployed serving boundary and verify the final response headers. |
| Version disclosure and missing content-type protection | Low, PR-02 and JR-01 | Local development servers expose runtime metadata and some responses lack an explicit MIME-sniffing directive. Verify server header minimization and `X-Content-Type-Options: nosniff` in the target environment. |
| CSRF cookie scan alert | Low scanner observation | ZAP’s flag applies to `csrftoken`. The browser separately verified HttpOnly on `sessionid`. Keep correct token handling in the admin form and verify deployment cookie settings with HTTPS. |
| Authentication detection and reflected form attributes | Informational | ZAP identified normal login/session traffic and reported potentially controllable HTML attributes. These passive observations establish neither a bypass nor script execution. Retain the source and browser role evidence. |

### Dependency audit

pip-audit checked 11 installed backend distributions. Django 6.0.7 and Django REST Framework 3.17.1 had advisories. The audit reported fixes in the respective newer compatible release lines. npm audit reported six high-severity frontend package entries, 11 gateway entries (three critical, five high, three moderate), and two high-severity browser-tool entries. Gateway runtime dependencies such as `proxy-addr` and `zod` need exposure triage. Vitest and tinypool need separate test-tool triage. These counts describe the report entries by ecosystem. Risk PR-09 remains open. Adjust the pinned requirements and locks in the dependency update, then rerun the audit and affected tests. [Dependency issue #21](https://github.com/eshalfatima2006/LeaveFlow/issues/21)

## Performance and recovery

The measured operation was `GET /api/requests/` using a team manager and 20 persisted synthetic requests. All runs used the same disposable backend and unchanged dataset, with 70 seconds per constant-VU workload. The limits were set in advance at p95 ≤ 500 ms and unexpected failures < 1%. Authentication in k6 setup was excluded from the operation metrics. [Protocol](AREA3-PERFORMANCE-PROTOCOL.md)

| Workload | Repeat | p95 (ms) | Requests/s | Unexpected failures | Result |
|---|---:|---:|---:|---:|---|
| 1 VU | 1 | 42.63 | 4.39 | 0.00% | Both limits met |
| 1 VU | 2 | 155.95 | 3.91 | 0.00% | Both limits met |
| 5 VUs | 1 | 649.88 | 10.22 | 0.00% | Latency limit missed |
| 5 VUs | 2 | 261.00 | 16.38 | 0.00% | Both limits met |

The first five-user run failed the p95 threshold with k6 exit code 99. Browser and audit work ran on the same development machine during the measurement window, so the source of the run-to-run latency variation remains undetermined. Repeat on an idle host and trace Django list serialization and per-row calculations before selecting an optimization. The latency threshold remains open under EC-09. [Performance issue #22](https://github.com/eshalfatima2006/LeaveFlow/issues/22)

The controlled W2 recovery test passed. It raises a dependency error after the decision write and before commit, verifies HTTP 500 and the original pending row and allowance, removes the fault, then approves the same record. A duplicate attempt returns 409 and preserves the first approval’s audit fields and one balance charge. This evidence applies to the disposable SQLite test profile.

## Release decision

**Hold release.** EC-06 has complete browser flow evidence and a verified request-form improvement, with serious accessibility findings still open on other screens. EC-08 has the required observed access checks, passive evidence, and dependency inventories, with runtime advisory triage open. EC-09 has four measured repeats and a successful recovery test, with one latency miss. See the [Area 3 verification guide](AREA3-VERIFICATION.md) for reproducible commands.
