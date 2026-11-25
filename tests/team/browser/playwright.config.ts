import { defineConfig, devices } from '@playwright/test'
import { existsSync, mkdirSync } from 'node:fs'
import path from 'node:path'

import {
  BACKEND_PORT, BACKEND_URL, FRONTEND_PORT, FRONTEND_URL, HARNESS, NOTIFICATIONS_ENABLED,
  NOTIFICATIONS_PORT, NOTIFICATIONS_URL, PYTHON, ROOT,
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
    proxy: process.env.SQE_ZAP_PROXY ? {
      server: process.env.SQE_ZAP_PROXY,
      bypass: '<-loopback>',
    } : undefined,
    // Network traces include live fixture authorization headers.
    trace: 'off',
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
        VITE_NOTIFICATIONS_URL: NOTIFICATIONS_URL,
      },
      reuseExistingServer: false,
      timeout: 180_000,
      stdout: 'ignore',
      stderr: 'pipe',
    },
    ...(NOTIFICATIONS_ENABLED ? [{
      command: 'node dist/src/index.js',
      cwd: path.join(ROOT, 'notifications'),
      url: `${NOTIFICATIONS_URL}/health`,
      env: {
        PORT: String(NOTIFICATIONS_PORT),
        BACKEND_URL,
        REDIS_URL: 'redis://127.0.0.1:16386/0',
      },
      reuseExistingServer: false,
      timeout: 60_000,
    }] : []),
  ],
})
