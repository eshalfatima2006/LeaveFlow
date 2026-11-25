import { BACKEND_URL } from '../support/harness'
import { signInToAdmin } from '../support/admin'
import {
  apiSubmit, apiToken, attachJson, createScenario, expect, openRequests, readBalance, readRequest,
  readRequests, rowByNote, signIn, test, waitForApi,
} from '../support/test'

function workflow() {
  return createScenario({
    teams: ['Orchid', 'Willow'],
    users: [
      { key: 'employee', role: 'employee', team: 'Orchid', allowance: 3 },
      { key: 'manager', role: 'manager', team: 'Orchid' },
      { key: 'other-employee', role: 'employee', team: 'Willow', allowance: 3 },
    ],
  }).users
}

test('employee corrects invalid dates and submits the form using the keyboard', async ({ page }, info) => {
  const users = workflow()
  await signIn(page, users.employee)
  const trigger = page.locator('header').getByRole('button', { name: 'New request' })
  await trigger.click()
  const modal = page.locator('form.modal')
  const type = modal.locator('select')
  const start = modal.locator('input[type=date]').nth(0)
  const end = modal.locator('input[type=date]').nth(1)
  const note = modal.locator('textarea')
  const submit = modal.locator('button[type=submit]')
  await expect(type).toBeFocused()
  await modal.locator('button[type=button]').focus()
  for (const field of [type, start, end, note, submit]) {
    // Chromium date controls have multiple focusable segments within a field.
    for (let attempts = 0; attempts < 5; attempts++) {
      await page.keyboard.press('Tab')
      if (await field.evaluate(element => element === document.activeElement)) break
    }
    await expect(field).toBeFocused()
    if (field === start) await start.fill('2027-04-07')
    if (field === end) await end.fill('2027-04-05')
    if (field === note) await note.fill('Keyboard task')
  }
  const invalid = waitForApi(page, 'POST', /^\/api\/requests\/$/)
  await page.keyboard.press('Enter')
  expect((await invalid).status()).toBe(400)
  await expect(modal.locator('.form-error')).toContainText(/finale.*iniziale|end date.*start date/i)
  expect(readRequests()).toEqual([])
  await end.fill('2027-04-08')
  await submit.focus()
  const corrected = waitForApi(page, 'POST', /^\/api\/requests\/$/)
  await page.keyboard.press('Enter')
  expect((await corrected).status()).toBe(201)
  await expect(modal).toHaveCount(0)
  await expect(trigger).toBeFocused()
  await openRequests(page)
  await expect(rowByNote(page, 'Keyboard task').locator('.status')).toHaveText('Pending')
  expect(readRequests()).toHaveLength(1)
  expect(readRequests()[0]).toMatchObject({ employee: 'employee', status: 'pending', business_days: 2 })
  await attachJson(info, 'access-decision', { role: 'employee', action: 'submit', expected: 201, observed: 201 })
})

test('team manager approves a request and sees the persisted outcome', async ({ page, request }, info) => {
  const users = workflow()
  const token = await apiToken(request, users.employee)
  const created = await apiSubmit(request, token, {
    start_date: '2027-04-05', end_date: '2027-04-07', note: 'Manager task',
  })
  expect(created.status()).toBe(201)
  const { id } = await created.json()
  await signIn(page, users.manager)
  await openRequests(page)
  const row = rowByNote(page, 'Manager task')
  const decision = waitForApi(page, 'POST', /^\/api\/requests\/\d+\/decision\/$/)
  await row.getByRole('button', { name: 'Approve' }).click()
  expect((await decision).status()).toBe(200)
  await expect(row.locator('.status')).toHaveText('Approved')
  expect(readRequest(id)).toMatchObject({ id, status: 'approved', decided_by: 'manager' })
  expect(readBalance(users.employee.username)).toEqual({ allowance: 3, used: 3, available: 0 })
  await attachJson(info, 'access-decision', { role: 'manager', action: 'approve team request', expected: 200, observed: 200 })
})

test('INC-02 admin login enforces staff access and sets the expected local session cookie', async ({ page }, info) => {
  const { users } = createScenario({
    users: [{ key: 'admin', role: 'admin' }, { key: 'employee', role: 'employee' }],
  })
  await page.goto(`${BACKEND_URL}/admin/`)
  await page.locator('#id_username').fill(users.employee.username)
  await page.locator('#id_password').fill(users.employee.password)
  await page.locator('input[type="submit"]').click()
  await expect(page.locator('.errornote')).toBeVisible()
  expect((await page.context().cookies(BACKEND_URL)).some(cookie => cookie.name === 'sessionid')).toBe(false)
  await signInToAdmin(page, users.admin)
  const session = (await page.context().cookies(BACKEND_URL)).find(cookie => cookie.name === 'sessionid')
  expect(session).toMatchObject({ httpOnly: true, sameSite: 'Lax', secure: false })
  await attachJson(info, 'session-cookie-attributes', {
    role: 'administrator', httpOnly: session?.httpOnly, sameSite: session?.sameSite, secure: session?.secure,
  })
})

for (const { actor, owner, expected, description } of [
  { actor: 'employee', owner: 'employee', expected: 403, description: 'employee cannot decide their own request' },
  { actor: 'manager', owner: 'other-employee', expected: 404, description: 'manager cannot decide an outside-team request' },
]) {
  test(description, async ({ page, request }, info) => {
    const users = workflow()
    const token = await apiToken(request, users[owner])
    const created = await apiSubmit(request, token, {
      start_date: '2027-04-05', end_date: '2027-04-05', note: 'Access decision record',
    })
    expect(created.status()).toBe(201)
    const { id } = await created.json()
    const before = readRequests()
    await signIn(page, users[actor])
    await openRequests(page)
    await expect(rowByNote(page, 'Access decision record').getByRole('button', { name: 'Approve' })).toHaveCount(0)
    const observed = await page.evaluate(async (url) => {
      const session = localStorage.getItem('leaveflow_token')
      const result = await fetch(url, {
        method: 'POST',
        headers: { Authorization: `Token ${session}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'approved' }),
      })
      return result.status
    }, `${BACKEND_URL}/api/requests/${id}/decision/`)
    expect(observed).toBe(expected)
    expect(readRequests()).toEqual(before)
    await attachJson(info, 'access-decision', { role: actor, action: description, expected, observed })
  })
}
