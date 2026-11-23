// UC-02 Decide pending leave request (W2): approval is the main flow, rejection an
// alternative end. Primary actor: manager (admin as a per-actor repeat). Secondary
// actor: the affected employee. Request k is created through the real W1 API by the
// employee, never inserted directly, so W2 acts on the same persisted record.
import type { Page } from '@playwright/test'

import {
  apiDecide, apiSubmit, apiToken, attachJson, attachScreenshot, createScenario, expect, filterButton,
  observeFeedback, openPeople, openRequests, personCard, readBalance, readRequest, readRequests, rowByNote,
  signIn, test, waitForApi, type Scenario,
} from '../support/test'

const PRECONDITION = {
  teams: ['Team T', 'Team B'],
  users: [
    { key: 'mgr', role: 'manager', team: 'Team T', allowance: 10, first: 'Marco', last: 'Bianchi' },
    { key: 'emp', role: 'employee', team: 'Team T', allowance: 3, first: 'Elena', last: 'Rossi' },
    { key: 'mgrb', role: 'manager', team: 'Team B', allowance: 10, first: 'Bruno', last: 'Neri' },
    { key: 'empb', role: 'employee', team: 'Team B', allowance: 10, first: 'Giulia', last: 'Verdi' },
    { key: 'adm', role: 'admin', team: null, allowance: 10, first: 'Ada', last: 'Conti' },
  ],
  requests: [
    { key: 's', owner: 'mgr', start: '2027-06-07', end: '2027-06-08', note: 'UC02 manager own request s' },
    { key: 'b', owner: 'empb', start: '2027-06-14', end: '2027-06-15', note: 'UC02 team B request b' },
  ],
}
const K_NOTE = 'UC02 request k'
const DECIDED = 'La richiesta è già stata decisa.'
const SELF = 'Non puoi decidere una tua richiesta.'

test.describe('UC-02 Decide pending leave request', () => {
  let scenario: Scenario
  let k: number

  test.beforeEach(async ({ request }) => {
    scenario = createScenario(PRECONDITION)
    // W1 through the real API: k is Mon..Wed, D = 3 = employee's available days.
    const token = await apiToken(request, scenario.users.emp)
    const response = await apiSubmit(request, token, {
      leave_type: 'vacation', start_date: '2027-05-03', end_date: '2027-05-05', note: K_NOTE,
    })
    expect(response.status(), 'W1 precondition').toBe(201)
    k = (await response.json()).id
  })

  async function decideInRow(page: Page, note: string, action: 'Approve' | 'Reject') {
    const [response] = await Promise.all([
      waitForApi(page, 'POST', /^\/api\/requests\/\d+\/decision\/$/),
      rowByNote(page, note).getByRole('button', { name: action }).click(),
    ])
    return response
  }

  function unchangedContent(before: any, after: any) {
    for (const field of ['id', 'employee', 'leave_type', 'start_date', 'end_date', 'note', 'business_days', 'created_at']) {
      expect(after[field], field).toEqual(before[field])
    }
  }

  test('TC-UC02-M main: team manager approves pending request k at the balance boundary (D = available)', async ({ page }, testInfo) => {
    const before = readRequest(k)!
    const count = readRequests().length
    await signIn(page, scenario.users.mgr)
    await openRequests(page)
    await filterButton(page, /^Pending/).click()
    await expect(rowByNote(page, K_NOTE).locator('.status')).toHaveText('Pending')

    const started = Date.now()
    const response = await decideInRow(page, K_NOTE, 'Approve')
    const finished = Date.now()
    expect(response.status()).toBe(200)
    await expect(rowByNote(page, K_NOTE)).toHaveCount(0) // leaves the Pending filter
    await filterButton(page, /^All/).click()
    await expect(rowByNote(page, K_NOTE).locator('.status')).toHaveText('Approved')
    await expect(rowByNote(page, K_NOTE).getByRole('button', { name: 'Approve' })).toHaveCount(0)
    await openPeople(page)
    await expect(personCard(page, 'Elena Rossi').locator('.availability strong')).toHaveText('0 / 3 days')

    const after = readRequest(k)!
    unchangedContent(before, after)
    expect(after.status).toBe('approved')
    expect(after.decided_by).toBe('mgr')
    const decidedAt = Date.parse(after.decided_at!)
    expect(decidedAt).toBeGreaterThanOrEqual(started - 2000)
    expect(decidedAt).toBeLessThanOrEqual(finished + 2000)
    expect(readRequests()).toHaveLength(count)
    expect(readBalance('emp')).toEqual({ allowance: 3, used: 3, available: 0 })
    await attachJson(testInfo, 'db-readback.json', { before, after, balance: readBalance('emp') })
    await attachScreenshot(page, testInfo, 'end-state.png')
  })

  test('TC-UC02-A1 alternative: team manager rejects k; no allowance is charged and the dates are released', async ({ page, request }, testInfo) => {
    const before = readRequest(k)!
    await signIn(page, scenario.users.mgr)
    await openRequests(page)
    await expect(filterButton(page, /^Rejected/)).toHaveCount(0) // only rendered once a rejection exists
    await filterButton(page, /^Pending/).click()

    expect((await decideInRow(page, K_NOTE, 'Reject')).status()).toBe(200)
    await filterButton(page, /^Rejected/).click()
    await expect(rowByNote(page, K_NOTE).locator('.status')).toHaveText('Rejected')
    await openPeople(page)
    await expect(personCard(page, 'Elena Rossi').locator('.availability strong')).toHaveText('3 / 3 days')

    const after = readRequest(k)!
    unchangedContent(before, after)
    expect(after).toMatchObject({ status: 'rejected', decided_by: 'mgr' })
    expect(readBalance('emp')).toEqual({ allowance: 3, used: 0, available: 3 })
    // Postcondition: a rejected request no longer blocks the same dates (BR-02).
    const reuse = await apiSubmit(request, await apiToken(request, scenario.users.emp), {
      leave_type: 'vacation', start_date: '2027-05-03', end_date: '2027-05-05', note: 'UC02-A1 same dates again',
    })
    expect(reuse.status()).toBe(201)
    expect((await reuse.json()).id).not.toBe(k)
    expect(readRequest(k)!.status).toBe('rejected')
    await attachJson(testInfo, 'db-readback.json', { before, after, requests: readRequests() })
    await attachScreenshot(page, testInfo, 'end-state.png')
  })

  test('TC-UC02-A2 alternative: administrator approves a pending request of another team', async ({ page }, testInfo) => {
    const b = scenario.requests.b
    const before = readRequest(b)!
    await signIn(page, scenario.users.adm)
    await openRequests(page)
    await expect(rowByNote(page, K_NOTE)).toHaveCount(1) // admin sees every team

    expect((await decideInRow(page, 'UC02 team B request b', 'Approve')).status()).toBe(200)
    await expect(rowByNote(page, 'UC02 team B request b').locator('.status')).toHaveText('Approved')

    const after = readRequest(b)!
    unchangedContent(before, after)
    expect(after).toMatchObject({ status: 'approved', decided_by: 'adm' })
    expect(readBalance('empb')).toEqual({ allowance: 10, used: 2, available: 8 })
    expect(readRequest(k)!.status).toBe('pending') // other requests untouched
    await attachJson(testInfo, 'db-readback.json', { before, after })
    await attachScreenshot(page, testInfo, 'end-state.png')
  })

  test('TC-UC02-E1 exception: k was decided by another approver after the page loaded (stale view)', async ({ page, request }, testInfo) => {
    await signIn(page, scenario.users.mgr)
    await openRequests(page)
    await expect(rowByNote(page, K_NOTE).locator('.status')).toHaveText('Pending')

    // Concurrent action by the administrator (second actor) through the real API.
    const adminDecision = await apiDecide(request, await apiToken(request, scenario.users.adm), k, 'rejected')
    expect(adminDecision.status()).toBe(200)
    const decidedByAdmin = readRequest(k)!

    const response = await decideInRow(page, K_NOTE, 'Approve')
    expect(response.status()).toBe(409)
    expect(await response.json()).toEqual({ detail: DECIDED })
    // Safe state: the first decision is preserved exactly.
    expect(readRequest(k)).toEqual(decidedByAdmin)
    expect(decidedByAdmin).toMatchObject({ status: 'rejected', decided_by: 'adm' })

    // Runtime verification of the predicted missing feedback (recorded, not asserted).
    await page.waitForTimeout(1000) // fixed observation window after the failed call
    await attachJson(testInfo, 'observation-ui-feedback.json', {
      row_status_after_failure: await rowByNote(page, K_NOTE).locator('.status').innerText(),
      approve_button_still_visible: await rowByNote(page, K_NOTE).getByRole('button', { name: 'Approve' }).isVisible(),
      ...(await observeFeedback(page, [DECIDED, 'Something went wrong.'])),
    })
    await attachScreenshot(page, testInfo, 'after-failed-decision.png')

    await page.reload()
    await openRequests(page)
    await expect(rowByNote(page, K_NOTE).locator('.status')).toHaveText('Rejected')
    await attachScreenshot(page, testInfo, 'after-reload.png')
  })

  test('TC-UC02-E2 exception: manager attempts to decide their own pending request', async ({ page }, testInfo) => {
    const s = scenario.requests.s
    const before = readRequest(s)!
    await signIn(page, scenario.users.mgr)
    await openRequests(page)
    const row = rowByNote(page, 'UC02 manager own request s')
    // Actual baseline UI offers the action on the manager's own row (TEST-BASIS GAP-04).
    await expect(row.getByRole('button', { name: 'Approve' })).toBeVisible()

    const response = await decideInRow(page, 'UC02 manager own request s', 'Approve')
    expect(response.status()).toBe(403)
    expect(await response.json()).toEqual({ detail: SELF })
    expect(readRequest(s)).toEqual(before) // still pending, no audit fields written

    await page.waitForTimeout(1000) // fixed observation window after the failed call
    await attachJson(testInfo, 'observation-ui-feedback.json', {
      row_status_after_failure: await row.locator('.status').innerText(),
      approve_button_still_visible: await row.getByRole('button', { name: 'Approve' }).isVisible(),
      ...(await observeFeedback(page, [SELF, 'Something went wrong.'])),
    })
    await attachScreenshot(page, testInfo, 'after-failed-decision.png')
  })

  // Blocked regression objective, NOT one of the 30 mandatory flows. Its expected
  // result needs the approved approval-time error contract (TEST-BASIS GAP-01).
  test.fixme('OBJ-UC02-01 blocked: approval that exceeds the employee remaining entitlement is refused', async () => {})
})
