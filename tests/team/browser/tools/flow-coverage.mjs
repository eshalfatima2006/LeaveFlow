#!/usr/bin/env node
// Usage: node tools/flow-coverage.mjs <evidence-dir>
// Reads flows.json and <evidence-dir>/results.json; writes flow-coverage.json/.md
// into the evidence dir (refuses to overwrite). Mandatory flow coverage (Lecture 16
// p10: flows tested / total flows) is computed ONLY over registry.mandatory_flows.
import { readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const evidence = process.argv[2]
if (!evidence) throw new Error('Usage: node tools/flow-coverage.mjs <evidence-dir>')
const registry = JSON.parse(readFileSync(path.join(here, '..', 'flows.json'), 'utf8'))
const results = JSON.parse(readFileSync(path.join(evidence, 'results.json'), 'utf8'))

const ID = /^((?:TC|OBJ|SUP)-UC\d\d-(?:M|A\d|E\d|\d\d))\b/
const outcomes = new Map()
function walk(suite) {
  for (const spec of suite.specs ?? []) {
    const match = ID.exec(spec.title)
    if (!match) continue
    if (outcomes.has(match[1])) throw new Error(`Duplicate registry ID in results: ${match[1]}`)
    // Playwright test.status: expected | unexpected | flaky | skipped
    const statuses = spec.tests.map((t) => t.status)
    const outcome = statuses.every((s) => s === 'expected') ? 'passed'
      : statuses.some((s) => s === 'unexpected') ? 'failed'
      : statuses.some((s) => s === 'flaky') ? 'flaky' : 'skipped'
    outcomes.set(match[1], { outcome, title: spec.title, file: spec.file })
  }
  for (const child of suite.suites ?? []) walk(child)
}
for (const suite of results.suites ?? []) walk(suite)

const known = new Set([
  ...registry.mandatory_flows, ...registry.blocked_regression_objectives, ...registry.supplementary_checks,
].map((entry) => entry.id))
const unregistered = [...outcomes.keys()].filter((id) => !known.has(id))
if (unregistered.length) throw new Error(`Results contain IDs missing from flows.json: ${unregistered.join(', ')}`)

const status = (id) => outcomes.get(id)?.outcome ?? 'not automated'
const mandatory = registry.mandatory_flows.map((flow) => ({ ...flow, status: status(flow.id) }))
const byUc = {}
for (const flow of mandatory) {
  const entry = (byUc[flow.uc] ??= { specified: 0, executed: 0, passed: 0 })
  entry.specified += 1
  if (['passed', 'failed', 'flaky'].includes(flow.status)) entry.executed += 1
  if (flow.status === 'passed') entry.passed += 1
}
const total = mandatory.length
const executed = mandatory.filter((f) => ['passed', 'failed', 'flaky'].includes(f.status)).length
const passed = mandatory.filter((f) => f.status === 'passed').length
const pct = (n) => `${((100 * n) / total).toFixed(1)}%`

const report = {
  generated_at: new Date().toISOString(),
  registry_version: registry.version,
  mandatory: {
    specified: total, executed, passed,
    failed: mandatory.filter((f) => f.status === 'failed').length,
    not_automated: mandatory.filter((f) => f.status === 'not automated').length,
    executed_coverage: pct(executed), passed_coverage: pct(passed), by_use_case: byUc, flows: mandatory,
  },
  blocked_regression_objectives: registry.blocked_regression_objectives.map((o) => ({ ...o, status: status(o.id) })),
  supplementary_checks: registry.supplementary_checks.map((o) => ({ ...o, status: status(o.id) })),
  observations: registry.observations,
}
writeFileSync(path.join(evidence, 'flow-coverage.json'), JSON.stringify(report, null, 2) + '\n', { flag: 'wx' })

const lines = [
  `# Use-case flow coverage (${registry.version})`, '',
  `Mandatory flows: ${total} specified · ${executed} executed (${pct(executed)}) · ${passed} passed (${pct(passed)}) · ${report.mandatory.not_automated} not yet automated.`,
  '', '| Use case | Specified | Executed | Passed |', '|---|---|---|---|',
  ...Object.entries(byUc).map(([uc, v]) => `| ${uc} | ${v.specified} | ${v.executed} | ${v.passed} |`),
  '', '## Mandatory flows', '', '| ID | Kind | Status | Flow |', '|---|---|---|---|',
  ...mandatory.map((f) => `| ${f.id} | ${f.kind} | ${f.status} | ${f.title} |`),
  '', '## Blocked regression objectives (outside the mandatory denominator)', '', '| ID | Status | Blocked by |', '|---|---|---|',
  ...report.blocked_regression_objectives.map((o) => `| ${o.id} | ${o.status} | ${o.blocked_by} |`),
  '', '## Supplementary checks (outside the mandatory denominator)', '', '| ID | Status | Purpose |', '|---|---|---|',
  ...report.supplementary_checks.map((o) => `| ${o.id} | ${o.status} | ${o.purpose} |`),
  '', '## Observations', '', '| ID | Status |', '|---|---|',
  ...registry.observations.map((o) => `| ${o.id} | ${o.status} |`), '',
]
writeFileSync(path.join(evidence, 'flow-coverage.md'), lines.join('\n'), { flag: 'wx' })
console.log(`mandatory: ${executed}/${total} executed, ${passed}/${total} passed; blocked objectives: ${report.blocked_regression_objectives.length}; supplementary: ${report.supplementary_checks.length}`)
