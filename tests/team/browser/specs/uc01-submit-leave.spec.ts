// UC-01 Submit leave request (W1). Primary actor: employee.
// Precondition (every flow): employee "emp" in Team T, allowance A=5, no approved
// history, own pending request P 2027-03-15..19. Pending requests reserve nothing,
// so available = 5 before every flow. Postconditions are read back from the
// disposable database, not only from the UI.
import type { Locator, Page } from '@playwright/test'

import {
  attachJson, attachScreenshot, createScenario, expect, openRequests, readBalance, readRequests,
  rowByNote, signIn, test, waitForApi, type Scenario,
} from '../support/test'

const PRECONDITION = {
  teams: ['Team T'],
  users: [{ key: 'emp', role: 'employee', team: 'Team T', allowance: 5, first: 'Elena', last: 'Rossi' }],
  requests: [{ key: 'P', owner: 'emp', start: '2027-03-15', end: '2027-03-19', note: 'UC01 existing pending P' }],
}

async function openForm(page: Page): Promise<Locator> {
  await page.locator('header').getByRole('button', { name: 'New request' }).click()
  const form = page.locator('form.modal')
  await expect(form).toBeVisible()
  return form
}

// Accessible names verified from the form's ARIA snapshot (combobox "Type", textboxes
// "From", "To", "Note optional"). getByLabel is not used: each <label> wraps its
// control, so label text matching also sees the <option> texts.
const field = {
  type: (form: Locator) => form.getByRole('combobox', { name: 'Type', exact: true }),
  from: (form: Locator) => form.getByRole('textbox', { name: 'From', exact: true }),
  to: (form: Locator) => form.getByRole('textbox', { name: 'To', exact: true }),
  note: (form: Locator) => form.getByRole('textbox', { name: 'Note optional', exact: true }),
}

async function fill(form: Locator, values: { type?: string; start?: string; end?: string; note?: string }) {
  if (values.type) await field.type(form).selectOption(values.type)
  if (values.start) await field.from(form).fill(values.start)
  if (values.end) await field.to(form).fill(values.end)
  if (values.note !== undefined) await field.note(form).fill(values.note)
}

async function submit(page: Page, form: Locator) {
  const [response] = await Promise.all([
    waitForApi(page, 'POST', /^\/api\/requests\/$/),
    form.getByRole('button', { name: 'Submit request' }).click(),
  ])
  return response
}

test.describe('UC-01 Submit leave request', () => {
  let scenario: Scenario

  test.beforeEach(async ({ page }) => {
    scenario = createScenario(PRECONDITION)
    await signIn(page, scenario.users.emp)
  })

  test('TC-UC01-M main: employee submits a valid request at the allowance boundary (D = A = 5)', async ({ page }, testInfo) => {
    const note = 'UC01-M family trip'
    const before = readRequests()
    const form = await openForm(page)
    await fill(form, { type: 'vacation', start: '2027-03-01', end: '2027-03-05', note })
    await expect(form.locator('.date-preview')).toContainText('5 working days')

    expect((await submit(page, form)).status()).toBe(201)
    await expect(form).toBeHidden()
    await openRequests(page)
    const row = rowByNote(page, note)
    await expect(row.locator('.status')).toHaveText('Pending')
    await expect(row).toContainText('Vacation · 5 days')

    const after = readRequests()
    expect(after).toHaveLength(before.length + 1)
    const created = after.find((item) => item.note === note)!
    expect(created).toMatchObject({
      employee: 'emp', status: 'pending', leave_type: 'vacation', start_date: '2027-03-01',
      end_date: '2027-03-05', business_days: 5, decided_by: null, decided_at: null,
    })
    // Pending reserves nothing (baseline behaviour, TEST-BASIS GAP-01 characterisation).
    expect(readBalance('emp')).toEqual({ allowance: 5, used: 0, available: 5 })
    await attachJson(testInfo, 'db-readback.json', { created, balance: readBalance('emp') })
    await attachScreenshot(page, testInfo, 'end-state.png')
  })

  test('TC-UC01-A1 alternative: employee revises the dates after the working-day preview', async ({ page }, testInfo) => {
    const note = 'UC01-A1 revised dates'
    const form = await openForm(page)
    await fill(form, { type: 'vacation', start: '2027-03-05', end: '2027-03-09', note }) // Fri..Tue
    await expect(form.locator('.date-preview')).toContainText('3 working days')
    await fill(form, { end: '2027-03-08' }) // revise to Fri..Mon
    await expect(form.locator('.date-preview')).toContainText('2 working days')

    expect((await submit(page, form)).status()).toBe(201)
    await expect(form).toBeHidden()
    await openRequests(page)
    await expect(rowByNote(page, note)).toContainText('Vacation · 2 days')

    // The revised value, not the first one, must reach the record (data kept between steps).
    const created = readRequests().find((item) => item.note === note)!
    expect(created).toMatchObject({ start_date: '2027-03-05', end_date: '2027-03-08', business_days: 2, status: 'pending' })
    await attachJson(testInfo, 'db-readback.json', created)
    await attachScreenshot(page, testInfo, 'end-state.png')
  })

  test('TC-UC01-A2 alternative: employee abandons the request before submitting', async ({ page }, testInfo) => {
    const before = readRequests()
    const posts: string[] = []
    page.on('request', (request) => {
      if (request.method() === 'POST' && new URL(request.url()).pathname === '/api/requests/') posts.push(request.url())
    })
    const form = await openForm(page)
    await fill(form, { type: 'permit', start: '2027-03-02', end: '2027-03-02', note: 'UC01-A2 abandoned' })
    await form.getByRole('button', { name: 'Close' }).click()
    await expect(form).toBeHidden()

    expect(posts).toEqual([])
    expect(readRequests()).toEqual(before)

    // Observation only: whether the abandoned values are still in the form on reopening.
    const reopened = await openForm(page)
    await attachJson(testInfo, 'observation-reopened-form.json', {
      type: await field.type(reopened).inputValue(),
      from: await field.from(reopened).inputValue(),
      to: await field.to(reopened).inputValue(),
      note: await field.note(reopened).inputValue(),
    })
    await attachScreenshot(page, testInfo, 'end-state.png')
  })

  test('TC-UC01-E1 exception: overlap with an active request at the inclusive boundary, then corrected', async ({ page }, testInfo) => {
    const note = 'UC01-E1 overlap corrected'
    const before = readRequests()
    const form = await openForm(page)
    // 2027-03-19 is P's last day: inclusive overlap must block it.
    await fill(form, { type: 'vacation', start: '2027-03-19', end: '2027-03-19', note })

    expect((await submit(page, form)).status()).toBe(400)
    await expect(form).toBeVisible()
    await expect(form.locator('.form-error')).toHaveText('Esiste già una richiesta sovrapposta.')
    expect(readRequests()).toEqual(before)
    await attachScreenshot(page, testInfo, 'rejected-state.png')

    await fill(form, { start: '2027-03-22', end: '2027-03-22' }) // first free weekday after P
    expect((await submit(page, form)).status()).toBe(201)
    await expect(form).toBeHidden()
    const after = readRequests()
    expect(after).toHaveLength(before.length + 1)
    expect(after.find((item) => item.note === note)).toMatchObject({ start_date: '2027-03-22', end_date: '2027-03-22', status: 'pending' })
    await attachJson(testInfo, 'db-readback.json', after)
  })

  test('TC-UC01-E2 exception: requested days exceed the remaining entitlement (D = A + 1), then shortened', async ({ page }, testInfo) => {
    const note = 'UC01-E2 shortened to fit'
    const before = readRequests()
    const form = await openForm(page)
    await fill(form, { type: 'vacation', start: '2027-04-05', end: '2027-04-12', note }) // Mon..Mon
    await expect(form.locator('.date-preview')).toContainText('6 working days')

    expect((await submit(page, form)).status()).toBe(400)
    await expect(form).toBeVisible()
    await expect(form.locator('.form-error')).toHaveText('Saldo ferie insufficiente.')
    expect(readRequests()).toEqual(before)
    await attachScreenshot(page, testInfo, 'rejected-state.png')

    await fill(form, { end: '2027-04-09' }) // Mon..Fri = 5 = A
    await expect(form.locator('.date-preview')).toContainText('5 working days')
    expect((await submit(page, form)).status()).toBe(201)
    await expect(form).toBeHidden()
    const created = readRequests().find((item) => item.note === note)!
    expect(created).toMatchObject({ end_date: '2027-04-09', business_days: 5, status: 'pending' })
    expect(readBalance('emp')).toEqual({ allowance: 5, used: 0, available: 5 })
    await attachJson(testInfo, 'db-readback.json', created)
  })
})
