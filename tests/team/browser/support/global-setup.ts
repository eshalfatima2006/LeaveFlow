import { execFileSync } from 'node:child_process'
import { readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

import {
  BACKEND_URL, BROWSER_DIR, FRONTEND_URL, NOTIFICATIONS_ENABLED, ROOT, developmentDatabaseFingerprint, fixture,
} from './harness'

function git(...args: string[]) {
  return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8' }).trim()
}

function write(name: string, data: unknown) {
  writeFileSync(path.join(process.env.SQE_EVIDENCE_RESOLVED!, name), JSON.stringify(data, null, 2) + '\n', { flag: 'wx' })
}

export default async function globalSetup() {
  write('development-db-before.json', { taken_at: new Date().toISOString(), files: developmentDatabaseFingerprint() })

  // Prove the served backend uses the harness database: a sentinel account created
  // only in that database must be able to log in through the served API.
  const whoami = fixture('whoami')
  fixture('reset')
  const sentinel = fixture<{ username: string; password: string }>('sentinel')
  const response = await fetch(`${BACKEND_URL}/api/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: sentinel.username, password: sentinel.password }),
  })
  const body = await response.json().catch(() => ({}))
  if (response.status !== 200 || body?.user?.username !== sentinel.username) {
    throw new Error('Served backend is not using the harness database; refusing to run.')
  }
  fixture('reset')

  const playwrightVersion = JSON.parse(
    readFileSync(path.join(BROWSER_DIR, 'node_modules', '@playwright', 'test', 'package.json'), 'utf8'),
  ).version
  write('environment.json', {
    started_at: new Date().toISOString(),
    git_sha: git('rev-parse', 'HEAD'),
    git_branch: git('branch', '--show-current'),
    git_status: git('status', '--short', '--untracked-files=all').split('\n').filter(Boolean),
    node: process.version,
    playwright: playwrightVersion,
    browser_project: 'chromium (Playwright-managed build for this version)',
    backend: { url: BACKEND_URL, profile: whoami.profile, python: whoami.python, django: whoami.django },
    frontend: { url: FRONTEND_URL, build: 'vite build of frontend/src into the run directory' },
    database: whoami.database,
    redis: NOTIFICATIONS_ENABLED ? 'isolated loopback test service on port 16386' : 'disabled',
    sentinel_identity_check: 'passed',
  })
}
