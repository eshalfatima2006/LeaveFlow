// Node side of the disposable-database harness. All database work goes through
// scripts/sqe/browser_harness.py, which refuses anything but the harness run directory.
import { execFileSync } from 'node:child_process'
import { existsSync, statSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

export const BROWSER_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
export const ROOT = path.resolve(BROWSER_DIR, '../../..')
export const PYTHON = process.env.SQE_PYTHON ?? path.join(ROOT, '.venv', 'bin', 'python')
export const HARNESS = path.join(ROOT, 'scripts', 'sqe', 'browser_harness.py')

export const BACKEND_PORT = Number(process.env.SQE_BACKEND_PORT ?? 8765)
export const FRONTEND_PORT = Number(process.env.SQE_FRONTEND_PORT ?? 4765)
// Nothing listens here: the notification centre is outside UC-01/UC-02 and must
// never reach a developer's real gateway.
export const NOTIFICATIONS_PORT = Number(process.env.SQE_NOTIFICATIONS_PORT ?? 4766)
export const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`
export const FRONTEND_URL = `http://127.0.0.1:${FRONTEND_PORT}`

export function harnessEnv(): Record<string, string> {
  const env: Record<string, string> = {}
  for (const [key, value] of Object.entries(process.env)) {
    if (value !== undefined && key !== 'POSTGRES_DB' && key !== 'REDIS_URL') env[key] = value
  }
  env.SQE_BROWSER_ORIGIN = FRONTEND_URL
  return env
}

export function runHarness(args: string[]): any {
  const output = execFileSync(PYTHON, [HARNESS, ...args], {
    cwd: ROOT,
    env: harnessEnv(),
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  return JSON.parse(output)
}

export function fixture<T = any>(action: string, payload: object = {}): T {
  return runHarness(['fixture', action, '--payload', JSON.stringify(payload)])
}

/** Metadata-only fingerprint: the development database file is never opened or read. */
export function developmentDatabaseFingerprint() {
  const result: Record<string, unknown> = {}
  for (const suffix of ['', '-wal', '-shm', '-journal']) {
    const file = path.join(ROOT, 'backend', `db.sqlite3${suffix}`)
    if (!existsSync(file)) {
      result[path.basename(file)] = { exists: false }
      continue
    }
    const stat = statSync(file, { bigint: true })
    result[path.basename(file)] = {
      exists: true, size: Number(stat.size), mtime_ns: stat.mtimeNs.toString(), inode: stat.ino.toString(),
    }
  }
  return result
}
