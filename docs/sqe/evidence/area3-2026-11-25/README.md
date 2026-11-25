# Area 3 raw verification evidence

Download [raw-reports.zip](raw-reports.zip) for the Playwright HTML and JSON reports, the AxeBuilder and Lighthouse reports, the passive ZAP results, Python and npm dependency inventories and advisory outputs, k6 logs and native summaries, and Django recovery results. The [machine-readable summary](results.json) maps 30 unique mandatory flows to results and retains the original combined and isolated retest totals. The [interpretation and issue links](../../testing/AREA3-RESULTS.md) explain the open findings.

| Archive path | Contents |
|---|---|
| `browser/final/` | Combined execution, including the original UC-07 failures |
| `browser/before-worker-fix/` | Notification flows before the OTP release repair |
| `browser/notification-retest/` | All five passing UC-07 cases and the Redis group counts |
| `accessibility/before/` and `accessibility/after/` | Request form before and after with HTML reports and original attachments |
| `accessibility/screens/` | Lighthouse HTML/JSON and axe JSON for the other five authenticated screens |
| `security/` | Passive local ZAP observations and the five proxied browser checks |
| `dependency-audit/` | Installed packages and advisories from pip-audit and npm audit |
| `performance/` | All four 70-second runs with original output and thresholds |
| `recovery-final/` and `team-regression/` | Controlled retry and default-hasher Django regression output |

The public ZAP copy masks credential evidence text on cookie or token alerts. The public k6 summaries mask synthetic setup authorization and preserve the measured values. Browser scenarios use synthetic fixtures and network traces are disabled. The original run files remain in the local working session’s evidence directories.

The archive SHA-256 is `fc5393c38d81c38e316c2e305fe37e9163ab487e6982cf75d93264c70ceecbcd`.
