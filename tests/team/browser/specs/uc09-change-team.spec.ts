import type { APIRequestContext, Browser, Page } from '@playwright/test'
import { BACKEND_URL, FRONTEND_URL, fixture } from '../support/harness'
import { expectAdminSaved, openEmployee, saveAdminForm, signInToAdmin } from '../support/admin'
import {
  apiSubmit, apiToken, createScenario, expect, openRequests, readRequest, rowByNote, signIn, test,
  type FixtureUser,
} from '../support/test'

const note = 'Reassignment request'

async function handover(request: APIRequestContext) {
  const { users, teams } = createScenario({
    teams: ['Orchid', 'Willow', 'Temporary'],
    users: [
      { key: 'handover-admin', role: 'admin' },
      { key: 'employee', role: 'employee', team: 'Orchid', allowance: 10 },
      { key: 'promote', role: 'employee', team: 'Willow' },
      { key: 'old-manager', role: 'manager', team: 'Orchid' },
      { key: 'new-manager', role: 'manager', team: 'Willow' },
    ],
  })
  const token = await apiToken(request, users.employee)
  const created = await apiSubmit(request, token, { start_date: '2027-04-05', end_date: '2027-04-05', note })
  expect(created.status()).toBe(201)
  const { id } = await created.json()
  return { users, teams, id, original: readRequest(id) }
}

async function openAuthorizedRequests(browser: Browser, user: FixtureUser, check: (page: Page) => Promise<void>) {
  const ctx = await browser.newContext({ baseURL: FRONTEND_URL })
  try {
    const page = await ctx.newPage()
    await page.addInitScript(() => localStorage.setItem('leaveflow_locale', 'en'))
    await signIn(page, user)
    await openRequests(page)
    await check(page)
  } finally {
    await ctx.close()
  }
}

test('TC-UC09-M changing teams transfers decision authority and preserves the request', async ({ page, browser, request }) => {
  const { users, teams, id, original } = await handover(request)
  await signInToAdmin(page, users['handover-admin'])
  await openEmployee(page, users.employee)
  await page.locator('#id_team').selectOption(String(teams.Willow))
  await saveAdminForm(page)
  await expectAdminSaved(page)

  await openAuthorizedRequests(browser, users['new-manager'], async view => {
    await expect(rowByNote(view, note).getByRole('button', { name: 'Approve' })).toBeVisible()
  })
  await openAuthorizedRequests(browser, users['old-manager'], async view => {
    await expect(rowByNote(view, note)).toHaveCount(0)
  })
  expect(fixture('user', { id: users.employee.id })).toEqual({ role: 'employee', team_id: teams.Willow })
  expect(readRequest(id)).toEqual(original)
})

test('TC-UC09-A1 promotion grants manager controls for the current team', async ({ page, browser, request }) => {
  const { users, teams } = await handover(request)
  const token = await apiToken(request, users['new-manager'])
  const created = await apiSubmit(request, token, { start_date: '2027-04-05', end_date: '2027-04-05', note: 'Willow request' })
  expect(created.status()).toBe(201)
  const { id } = await created.json()
  const before = readRequest(id)
  await signInToAdmin(page, users['handover-admin'])
  await openEmployee(page, users.promote)
  await page.locator('#id_role').selectOption('manager')
  await saveAdminForm(page)
  await expectAdminSaved(page)
  await openAuthorizedRequests(browser, users.promote, async view => {
    await expect(rowByNote(view, 'Willow request').getByRole('button', { name: 'Approve' })).toBeVisible()
    await expect(rowByNote(view, note)).toHaveCount(0)
  })
  expect(fixture('user', { id: users.promote.id })).toEqual({ role: 'manager', team_id: teams.Willow })
  expect(readRequest(id)).toEqual(before)
})

test('TC-UC09-A2 teamless request remains visible to administrators', async ({ page, browser, request }) => {
  const { users, id, original } = await handover(request)
  await signInToAdmin(page, users['handover-admin'])
  await openEmployee(page, users.employee)
  await page.locator('#id_team').selectOption('')
  await saveAdminForm(page)
  await expectAdminSaved(page)
  await openAuthorizedRequests(browser, users['old-manager'], async view => {
    await expect(rowByNote(view, note)).toHaveCount(0)
  })
  await openAuthorizedRequests(browser, users['handover-admin'], async view => {
    await expect(rowByNote(view, note).getByRole('button', { name: 'Approve' })).toBeVisible()
  })
  expect(fixture('user', { id: users.employee.id })).toEqual({ role: 'employee', team_id: null })
  expect(readRequest(id)).toEqual(original)
})

test('TC-UC09-E1 a target team deleted during edit is rejected', async ({ page, request }) => {
  const { users, teams, id, original } = await handover(request)
  await signInToAdmin(page, users['handover-admin'])
  await openEmployee(page, users.employee)
  await page.locator('#id_team').selectOption(String(teams.Temporary))
  fixture('delete-team', { id: teams.Temporary })
  await saveAdminForm(page)
  await expect(page.locator('.errorlist').first()).toContainText(/opzione valida|scelta valida/i)
  expect(fixture('user', { id: users.employee.id })).toEqual({ role: 'employee', team_id: teams.Orchid })
  expect(readRequest(id)).toEqual(original)
})

test('TC-UC09-E2 a user deleted during edit is never recreated', async ({ page, request }) => {
  const { users, teams, id } = await handover(request)
  await signInToAdmin(page, users['handover-admin'])
  await openEmployee(page, users.employee)
  await page.locator('#id_team').selectOption(String(teams.Willow))
  fixture('delete-user', { id: users.employee.id })
  await saveAdminForm(page)
  await expect(page).toHaveURL(`${BACKEND_URL}/admin/`)
  await expect(page.locator('.messagelist')).toContainText(/non esiste|cancellat/i)
  expect(fixture('user', { id: users.employee.id })).toBeNull()
  expect(readRequest(id)).toBeNull()
})
