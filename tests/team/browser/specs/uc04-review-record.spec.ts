import type { APIRequestContext } from '@playwright/test'
import { fixture } from '../support/harness'
import {
  apiDecide, apiSubmit, apiToken, createScenario, expect, filterButton, openRequests,
  readBalance, readRequests, rowByNote, signIn, test, waitForApi,
} from '../support/test'

async function reviewScenario(request: APIRequestContext) {
  const { users } = createScenario({
    teams: ['Orchid'],
    users: [
      { key: 'employee', first: 'Sage', role: 'employee', team: 'Orchid', allowance: 10 },
      { key: 'teammate', first: 'Rowan', role: 'employee', team: 'Orchid', allowance: 10 },
      { key: 'manager', first: 'Robin', role: 'manager', team: 'Orchid' },
    ],
  })
  const employeeToken = await apiToken(request, users.employee)
  const managerToken = await apiToken(request, users.manager)
  const rows = [
    { note: 'Approved record', start_date: '2027-04-05', end_date: '2027-04-07', status: 'approved' },
    { note: 'Rejected record', start_date: '2027-04-12', end_date: '2027-04-12', status: 'rejected' },
    { note: 'Pending record', start_date: '2027-04-13', end_date: '2027-04-13', status: 'pending' },
  ]
  let pendingId = 0
  for (const { status, ...body } of rows) {
    const submitted = await apiSubmit(request, employeeToken, body)
    expect(submitted.status()).toBe(201)
    const { id } = await submitted.json()
    if (status === 'pending') pendingId = id
    else expect((await apiDecide(request, managerToken, id, status)).status()).toBe(200)
  }
  const teammate = await apiToken(request, users.teammate)
  expect((await apiSubmit(request, teammate, {
    start_date: '2027-04-15', end_date: '2027-04-15', note: 'Teammate record',
  })).status()).toBe(201)
  return { employee: users.employee, managerToken, pendingId, rows }
}

test('TC-UC04-M employee sees own history, entitlement and status counts', async ({ page, request }) => {
  const data = await reviewScenario(request)
  const before = readRequests()
  await signIn(page, data.employee)
  await expect(page.locator('.aside-balance strong')).toHaveText('7 / 10')
  await expect(page.locator('.balance-copy')).toContainText(/3.*10/)
  await expect(page.locator('.stat-strip strong')).toHaveText(['1', '1', '3'])
  await openRequests(page)
  for (const row of data.rows) {
    await expect(rowByNote(page, row.note)).toContainText(new RegExp(row.status, 'i'))
  }
  await expect(rowByNote(page, 'Teammate record')).toHaveCount(0)
  expect(readRequests()).toEqual(before)
})

test('TC-UC04-A1 each outcome filter shows only its matching record', async ({ page, request }) => {
  const data = await reviewScenario(request)
  const before = readRequests()
  await signIn(page, data.employee)
  await openRequests(page)
  for (const row of data.rows) {
    await filterButton(page, new RegExp(`^${row.status}`, 'i')).click()
    await expect(page.locator('.requests-page article.request-row')).toHaveCount(1)
    await expect(rowByNote(page, row.note)).toBeVisible()
  }
  expect(readRequests()).toEqual(before)
})

test('TC-UC04-A2 reload refreshes a decision made by the manager', async ({ page, request }) => {
  const data = await reviewScenario(request)
  await signIn(page, data.employee)
  await openRequests(page)
  expect((await apiDecide(request, data.managerToken, data.pendingId, 'approved')).status()).toBe(200)
  const afterDecision = readRequests()
  await expect(rowByNote(page, 'Pending record')).toContainText('Pending')
  await page.reload()
  await expect(page.locator('.aside-balance strong')).toHaveText('6 / 10')
  await openRequests(page)
  await expect(rowByNote(page, 'Pending record').locator('.status')).toHaveText(/approved/i)
  expect(readBalance(data.employee.username)).toEqual({ available: 6, allowance: 10, used: 4 })
  expect(readRequests()).toEqual(afterDecision)
})

test('TC-UC04-E1 revoked session returns to sign-in and clears the token', async ({ page, request }) => {
  const data = await reviewScenario(request)
  const before = readRequests()
  await signIn(page, data.employee)
  fixture('revoke-token', { username: data.employee.username })
  const response = waitForApi(page, 'GET', /^\/api\/me\/$/)
  await page.reload()
  expect((await response).status()).toBe(401)
  await expect(page.getByLabel('Username')).toBeVisible()
  expect(await page.evaluate(() => localStorage.getItem('leaveflow_token'))).toBeNull()
  expect(readRequests()).toEqual(before)
})

test('TC-UC04-E2 read outage leaves records intact and reload restores their view', async ({ page, request }) => {
  const data = await reviewScenario(request)
  const before = readRequests()
  await signIn(page, data.employee)
  await page.route('**/api/requests/', route => route.fulfill({ status: 500, json: { detail: 'Unavailable' } }))
  const response = waitForApi(page, 'GET', /^\/api\/requests\/$/)
  await page.reload()
  expect((await response).status()).toBe(500)
  await openRequests(page)
  // GAP-15 baseline: the outage appears as an empty result. Recovery must still restore data.
  await expect(page.getByText('No requests found.')).toBeVisible()
  expect(readRequests()).toEqual(before)
  await page.unroute('**/api/requests/')
  await signIn(page, data.employee)
  await openRequests(page)
  await expect(rowByNote(page, 'Approved record')).toBeVisible()
  expect(readRequests()).toEqual(before)
})
