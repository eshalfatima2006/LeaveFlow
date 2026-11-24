import { defineConfig, devices } from '@playwright/test'

// Only valid when launched by scripts/sqe/capture_decision_screenshot.py, which
// starts the disposable backend/frontend and supplies these variables.
for (const name of ['BL_EVIDENCE_DIR', 'BL_ARTIFACTS_DIR', 'BL_FRONTEND_URL']) {
  if (!process.env[name]) throw new Error(`${name} is not set; run capture_decision_screenshot.py instead.`)
}

export default defineConfig({
  testDir: '.',
  testMatch: 'manager-decision.spec.ts',
  workers: 1,
  retries: 0,
  forbidOnly: true,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  outputDir: process.env.BL_ARTIFACTS_DIR,
  reporter: [['list'], ['json', { outputFile: `${process.env.BL_EVIDENCE_DIR}/08-playwright-results.json` }]],
  use: {
    baseURL: process.env.BL_FRONTEND_URL,
    locale: 'en-GB',
    timezoneId: 'Europe/Rome',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } } }],
})
