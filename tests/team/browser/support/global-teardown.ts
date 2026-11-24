import { readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

import { developmentDatabaseFingerprint } from './harness'

export default async function globalTeardown() {
  const evidence = process.env.SQE_EVIDENCE_RESOLVED!
  const before = JSON.parse(readFileSync(path.join(evidence, 'development-db-before.json'), 'utf8')).files
  const after = developmentDatabaseFingerprint()
  const unchanged = JSON.stringify(before) === JSON.stringify(after)
  writeFileSync(
    path.join(evidence, 'development-db-after.json'),
    JSON.stringify({ taken_at: new Date().toISOString(), files: after, unchanged_since_setup: unchanged }, null, 2) + '\n',
    { flag: 'wx' },
  )
  if (!unchanged) throw new Error('Development database metadata changed during the browser run.')
}
