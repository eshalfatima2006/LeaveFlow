// PR #1 baseline evidence BL-UI-04: a manager's decision result, captured in a
// real browser. The employee submits W1 through the UI; the manager approves the
// same request through the UI (W2). Credentials come from the environment and are
// never written; the screenshot is taken only after the UI shows "Approved".
import { writeFileSync } from 'node:fs'

import { expect, test, type Page, type Response } from '@playwright/test'

function required(name: string): string {
  const value = process.env[name]
  if (!value) throw new Error(`${name} is not set`)
  return value
}

const NOTE = 'PR1 BL-UI-04 decision evidence'
const employee = { username: required('BL_EMPLOYEE_USERNAME'), password: required('BL_EMPLOYEE_PASSWORD') }
const manager = { username: required('BL_MANAGER_USERNAME'), password: required('BL_MANAGER_PASSWORD') }

async function signIn(page: Page, user: { username: string; password: string }) {
  await page.getByLabel('Username').fill(user.username)
  await page.getByLabel('Password').fill(user.password)
  await page.getByRole('button', { name: 'Enter the dashboard' }).click()
  await expect(page.getByRole('navigation', { name: 'Main navigation' })).toBeVisible()
}

const isPost = (pattern: RegExp) => (response: Response) =>
  response.request().method() === 'POST' && pattern.test(new URL(response.url()).pathname)

test('PR1-BL-UI-04 manager approves a request that the employee submitted in the browser', async ({ page, browser }) => {
  const assertions: string[] = []
  const passed = (text: string) => assertions.push(text)
  await page.addInitScript(() => window.localStorage.setItem('leaveflow_locale', 'en'))
  await page.goto('/')

  // W1 — employee submits through the request form.
  await signIn(page, employee)
  await page.locator('header').getByRole('button', { name: 'New request' }).click()
  const form = page.locator('form.modal')
  await expect(form).toBeVisible()
  await form.getByRole('combobox', { name: 'Type', exact: true }).selectOption('vacation')
  await form.getByRole('textbox', { name: 'From', exact: true }).fill('2027-03-01')
  await form.getByRole('textbox', { name: 'To', exact: true }).fill('2027-03-05')
  await form.getByRole('textbox', { name: 'Note optional', exact: true }).fill(NOTE)
  await expect(form.locator('.date-preview')).toContainText('5 working days')
  const [submitted] = await Promise.all([
    page.waitForResponse(isPost(/^\/api\/requests\/$/)),
    form.getByRole('button', { name: 'Submit request' }).click(),
  ])
  expect(submitted.status()).toBe(201)
  const created = await submitted.json()
  expect(created).toMatchObject({ status: 'pending', business_days: 5, employee: { username: employee.username } })
  const requestId: number = created.id
  await expect(form).toBeHidden()
  passed(`W1 POST /api/requests/ -> 201, id ${requestId}, pending, 5 business days, owner ${employee.username}`)

  await page.getByRole('button', { name: 'Log out' }).click()
  await expect(page.getByRole('button', { name: 'Enter the dashboard' })).toBeVisible()

  // W2 — manager approves the same request from the Requests screen.
  await signIn(page, manager)
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('button', { name: /^Requests/ }).click()
  await expect(page.getByRole('heading', { level: 1, name: 'Requests and decisions' })).toBeVisible()
  const filters = page.getByRole('group', { name: 'Filter requests' })
  await filters.getByRole('button', { name: /^Pending/ }).click()
  const row = page.locator('article.request-row').filter({ hasText: NOTE })
  await expect(row).toHaveCount(1)
  await expect(row.locator('.status')).toHaveText('Pending')
  passed('Manager sees exactly one Pending row for the submitted request')

  const [decided] = await Promise.all([
    page.waitForResponse(isPost(/^\/api\/requests\/\d+\/decision\/$/)),
    row.getByRole('button', { name: 'Approve' }).click(),
  ])
  expect(decided.status()).toBe(200)
  expect(new URL(decided.url()).pathname).toBe(`/api/requests/${requestId}/decision/`)
  const decision = await decided.json()
  expect(decision).toMatchObject({ id: requestId, status: 'approved' })
  passed(`W2 POST /api/requests/${requestId}/decision/ -> 200, same id, approved`)

  await filters.getByRole('button', { name: /^All/ }).click()
  await expect(row).toHaveCount(1)
  await expect(row.locator('.status')).toHaveText('Approved')
  await expect(row.getByRole('button', { name: 'Approve' })).toHaveCount(0)
  await expect(row.getByRole('button', { name: 'Reject' })).toHaveCount(0)
  passed('UI shows the row as Approved with no remaining decision buttons (single row)')

  // The summary counters animate for 700 ms (AnimatedNumber.vue); wait for their final
  // values with retrying assertions so the screenshot never shows an intermediate state.
  const insight = (label: string) => page.locator('.request-insights article').filter({ hasText: label }).locator('strong')
  await expect(insight('Requests in period')).toHaveText('1')
  await expect(insight('Days involved')).toHaveText('5')
  await expect(insight('To decide')).toHaveText('0')
  await expect(filters.getByRole('button', { name: /^Pending/ })).toHaveText(/Pending\s*0/)
  await expect(filters.getByRole('button', { name: /^Approved/ })).toHaveText(/Approved\s*1/)
  passed('Summary settled: 1 request, 5 days involved, 0 to decide; filters Pending 0 / Approved 1')

  const screenshot = required('BL_SCREENSHOT_PATH')
  await page.screenshot({ path: screenshot, fullPage: true })

  writeFileSync(required('BL_RESULT_PATH'), JSON.stringify({
    scenario: 'PR1-BL-UI-04',
    browser: `${browser.browserType().name()} ${browser.version()}`,
    request_id: requestId,
    w1_submit: { status: submitted.status(), body_status: created.status, business_days: created.business_days, owner: created.employee.username },
    w2_decision: { status: decided.status(), path: new URL(decided.url()).pathname, body_status: decision.status, body_id: decision.id },
    ui_assertions_passed: assertions,
    screenshot_taken_after: 'row status "Approved" asserted visible',
  }, null, 2) + '\n')
})
