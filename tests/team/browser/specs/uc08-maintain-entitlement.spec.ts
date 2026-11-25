import { BACKEND_URL, fixture } from '../support/harness'
import { expectAdminSaved, openEntitlement, saveAdminForm, signInToAdmin } from '../support/admin'
import {
  apiDecide, apiSubmit, apiToken, createScenario, expect, readBalance, readRequests, signIn, test,
} from '../support/test'

function entitlements() {
  return createScenario({
    teams: ['Orchid'],
    users: [
      { key: 'entitlement-admin', role: 'admin' },
      { key: 'employee', role: 'employee', team: 'Orchid', allowance: 10 },
      { key: 'new-employee', role: 'employee', team: 'Orchid' },
      { key: 'manager', role: 'manager', team: 'Orchid' },
    ],
  }).users
}

const addUrl = `${BACKEND_URL}/admin/leave/leavebalance/add/`
const sixDays = { start_date: '2027-04-05', end_date: '2027-04-12' }

test('TC-UC08-M updated entitlement is reflected in the Overview and W1 limit', async ({ page, request }) => {
  const users = entitlements()
  await signInToAdmin(page, users['entitlement-admin'])
  await openEntitlement(page, users.employee)
  await page.locator('#id_allowance').fill('12')
  await saveAdminForm(page)
  await expectAdminSaved(page)
  expect(readBalance(users.employee.username)).toEqual({ allowance: 12, used: 0, available: 12 })
  await signIn(page, users.employee)
  await expect(page.locator('.aside-balance strong')).toHaveText('12 / 12')
  const token = await apiToken(request, users.employee)
  const accepted = await apiSubmit(request, token, { start_date: '2027-04-05', end_date: '2027-04-20' })
  expect(accepted.status()).toBe(201)
  const persisted = readRequests()
  const denied = await apiSubmit(request, token, { start_date: '2027-05-03', end_date: '2027-05-19' })
  expect(denied.status()).toBe(400)
  expect(readRequests()).toEqual(persisted)
})

test('TC-UC08-A1 added entitlement applies to the previously unbounded employee', async ({ page, request }) => {
  const users = entitlements()
  const employee = users['new-employee']
  expect(readBalance(employee.username)).toBeNull()
  await signInToAdmin(page, users['entitlement-admin'])
  await page.goto(addUrl)
  await page.locator('#id_user').selectOption(String(employee.id))
  await page.locator('#id_allowance').fill('5')
  await saveAdminForm(page)
  await expectAdminSaved(page)
  expect(readBalance(employee.username)).toEqual({ allowance: 5, used: 0, available: 5 })
  const token = await apiToken(request, employee)
  const response = await apiSubmit(request, token, sixDays)
  expect(response.status()).toBe(400)
  expect(await response.json()).toHaveProperty('non_field_errors')
  expect(readRequests()).toEqual([])
})

test('TC-UC08-A2 reducing below approved use persists a negative balance on the baseline', async ({ page, request }) => {
  const users = entitlements()
  const token = await apiToken(request, users.employee)
  const created = await apiSubmit(request, token, { start_date: '2027-04-05', end_date: '2027-04-07' })
  expect(created.status()).toBe(201)
  const manager = await apiToken(request, users.manager)
  expect((await apiDecide(request, manager, (await created.json()).id, 'approved')).status()).toBe(200)
  const before = readRequests()
  await signInToAdmin(page, users['entitlement-admin'])
  await openEntitlement(page, users.employee)
  await page.locator('#id_allowance').fill('2')
  await saveAdminForm(page)
  await expectAdminSaved(page)
  expect(readBalance(users.employee.username)).toEqual({ allowance: 2, used: 3, available: -1 })
  expect(readRequests()).toEqual(before)
  await signIn(page, users.employee)
  await expect(page.locator('.aside-balance strong')).toHaveText('-1 / 2')
})

test('TC-UC08-E1 invalid allowance is rejected server-side and zero is accepted', async ({ page }) => {
  const users = entitlements()
  await signInToAdmin(page, users['entitlement-admin'])
  await openEntitlement(page, users.employee)
  await page.locator('form#leavebalance_form').evaluate(form => ((form as HTMLFormElement).noValidate = true))
  await page.locator('#id_allowance').fill('-1')
  await saveAdminForm(page)
  await expect(page.locator('.errorlist').first()).toContainText(/maggiore.*0/i)
  expect(readBalance(users.employee.username)?.allowance).toBe(10)
  await page.locator('form#leavebalance_form').evaluate(form => ((form as HTMLFormElement).noValidate = true))
  await page.locator('#id_allowance').fill('')
  await saveAdminForm(page)
  await expect(page.locator('.errorlist').first()).toContainText(/obbligatorio/i)
  expect(readBalance(users.employee.username)?.allowance).toBe(10)
  await page.locator('#id_allowance').fill('0')
  await saveAdminForm(page)
  await expectAdminSaved(page)
  expect(readBalance(users.employee.username)?.allowance).toBe(0)
})

test('TC-UC08-E2 adding a duplicate entitlement preserves the existing record', async ({ page }) => {
  const users = entitlements()
  const id = fixture('balance-id', { id: users.employee.id })
  await signInToAdmin(page, users['entitlement-admin'])
  await page.goto(addUrl)
  await page.locator('#id_user').selectOption(String(users.employee.id))
  await page.locator('#id_allowance').fill('8')
  await saveAdminForm(page)
  await expect(page.locator('.errorlist').first()).toContainText(/già esiste|esiste già/i)
  expect(fixture('balance-id', { id: users.employee.id })).toBe(id)
  expect(readBalance(users.employee.username)).toEqual({ allowance: 10, used: 0, available: 10 })
})
