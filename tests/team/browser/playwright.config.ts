import { defineConfig, devices } from '@playwright/test'
import { existsSync, mkdirSync } from 'node:fs'
import path from 'node:path'

import {
  BACKEND_PORT, BACKEND_URL, FRONTEND_PORT, FRONTEND_URL, HARNESS, NOTIFICATIONS_PORT, PYTHON, ROOT,
  harnessEnv, runHarness,
} from './support/harness'

// The runner evaluates this file first; workers inherit the variables set here.
if (!process.env.SQE_BROWSER_RUN_DIR) {
  process.env.SQE_BROWSER_RUN_DIR = runHarness(['init']).run_dir
}
const RUN_DIR = process.env.SQE_BROWSER_RUN_DIR

if (!process.env.SQE_EVIDENCE_RESOLVED) {
  const requested = process.env.SQE_EVIDENCE_DIR
    ? path.resolve(process.env.SQE_EVIDENCE_DIR)
    : path.join(RUN_DIR, 'evidence')
  if (existsSync(requested)) throw new Error(`Evidence directory must be new: ${requested}`)
  mkdirSync(requested, { recursive: true })
  process.env.SQE_EVIDENCE_RESOLVED = requested
}
const EVIDENCE = process.env.SQE_EVIDENCE_RESOLVED
const FRONTEND_DIST = path.join(RUN_DIR, 'frontend-dist')

export default defineConfig({
  testDir: './specs',
  fullyParallel: false,
  workers: 1, // one shared disposable SQLite file; every test resets it first
  retries: 0,
  forbidOnly: true,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  outputDir: path.join(EVIDENCE, 'artifacts'),
  reporter: [
    ['list'],
    ['html', { outputFolder: path.join(EVIDENCE, 'html-report'), open: 'never' }],
    ['json', { outputFile: path.join(EVIDENCE, 'results.json') }],
  ],
  globalSetup: './support/global-setup.ts',
  globalTeardown: './support/global-teardown.ts',
  use: {
    baseURL: FRONTEND_URL,
    locale: 'en-GB',
    timezoneId: 'Europe/Rome',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      // reuseExistingServer:false makes the run fail if the port is taken, so a
      // developer's own server (and its database) can never be used by mistake.
      command: `"${PYTHON}" "${HARNESS}" serve --port ${BACKEND_PORT}`,
      cwd: ROOT,
      url: `${BACKEND_URL}/health/`,
      env: harnessEnv(),
      reuseExistingServer: false,
      timeout: 120_000,
      stdout: 'ignore',
      stderr: 'pipe',
    },
    {
      // Vite only (no vue-tsc): nothing is written to frontend/dist or tsbuildinfo files.
      command: `npx vite build --outDir "${FRONTEND_DIST}" --emptyOutDir --logLevel warn && npx vite preview --outDir "${FRONTEND_DIST}" --host 127.0.0.1 --port ${FRONTEND_PORT} --strictPort`,
      cwd: path.join(ROOT, 'frontend'),
      url: FRONTEND_URL,
      env: {
        ...harnessEnv(),
        VITE_API_URL: `${BACKEND_URL}/api`,
        VITE_NOTIFICATIONS_URL: `http://127.0.0.1:${NOTIFICATIONS_PORT}`,
      },
      reuseExistingServer: false,
      timeout: 180_000,
      stdout: 'ignore',
      stderr: 'pipe',
    },
  ],
})
