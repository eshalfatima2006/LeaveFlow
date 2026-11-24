import { expect, test as base, type APIRequestContext, type Locator, type Page, type TestInfo } from '@playwright/test'

import { BACKEND_URL, fixture } from './harness'

export { expect }

export type FixtureUser = { id: number; username: string; password: string; display_name: string }
export type Scenario = { users: Record<string, FixtureUser>; requests: Record<string, number> }
export type RowState = {
  id: number; employee: string; leave_type: string; start_date: string; end_date: string; note: string
  status: string; decided_by: string | null; decided_at: string | null; business_days: number; created_at: string
}

export const test = base.extend<{ resetDatabase: void; consoleLog: string[] }>({
  // Every test starts from an empty disposable database: no ordering dependencies.
  resetDatabase: [async ({}, use) => {
    fixture('reset')
    await use()
  }, { auto: true }],
  consoleLog: [async ({ page }, use, testInfo) => {
    const log: string[] = []
    page.on('console', (message) => {
      if (message.type() === 'error' || message.type() === 'warning') log.push(`${message.type()}: ${message.text()}`)
    })
    page.on('pageerror', (error) => log.push(`pageerror: ${error.message}`))
    await use(log)
    await testInfo.attach('browser-console.json', { body: JSON.stringify(log, null, 2), contentType: 'application/json' })
  }, { auto: true }],
  page: async ({ page }, use) => {
    await page.addInitScript(() => window.localStorage.setItem('leaveflow_locale', 'en'))
    await use(page)
  },
})

// ---------- fixtures and readback (disposable database only) ----------
export const createScenario = (spec: object) => fixture<Scenario>('scenario', spec)
export const readRequest = (id: number) => fixture<RowState | null>('request', { id })
export const readRequests = () => fixture<RowState[]>('requests')
export const readBalance = (username: string) =>
  fixture<{ allowance: number; used: number; available: number } | null>('balance', { username })

// ---------- API helpers (setup actions by other actors) ----------
export async function apiToken(request: APIRequestContext, user: FixtureUser): Promise<string> {
  const response = await request.post(`${BACKEND_URL}/api/auth/login/`, {
    data: { username: user.username, password: user.password },
  })
  expect(response.status(), 'setup login').toBe(200)
  return (await response.json()).token
}

export async function apiSubmit(request: APIRequestContext, token: string, data: object) {
  return request.post(`${BACKEND_URL}/api/requests/`, { data, headers: { Authorization: `Token ${token}` } })
}

export async function apiDecide(request: APIRequestContext, token: string, id: number, status: string) {
  return request.post(`${BACKEND_URL}/api/requests/${id}/decision/`, {
    data: { status }, headers: { Authorization: `Token ${token}` },
  })
}

// ---------- UI helpers (selectors are accessible names from the English locale) ----------
export async function signIn(page: Page, user: FixtureUser) {
  await page.goto('/')
  await page.getByLabel('Username').fill(user.username)
  await page.getByLabel('Password').fill(user.password)
  await page.getByRole('button', { name: 'Enter the dashboard' }).click()
  await expect(page.getByRole('navigation', { name: 'Main navigation' })).toBeVisible()
}

export function nav(page: Page, name: RegExp) {
  return page.getByRole('navigation', { name: 'Main navigation' }).getByRole('button', { name })
}

export async function openRequests(page: Page) {
  await nav(page, /^Requests/).click()
  await expect(page.getByRole('heading', { level: 1, name: 'Requests and decisions' })).toBeVisible()
}

export async function openPeople(page: Page) {
  await nav(page, /^People/).click()
  await expect(page.getByRole('heading', { level: 1, name: 'People and availability' })).toBeVisible()
}

export function filterButton(page: Page, name: RegExp) {
  return page.getByRole('group', { name: 'Filter requests' }).getByRole('button', { name })
}

export function rowByNote(page: Page, note: string): Locator {
  return page.locator('article.request-row').filter({ hasText: note })
}

export function personCard(page: Page, displayName: string): Locator {
  return page.locator('article.person-card').filter({ hasText: displayName })
}

export function waitForApi(page: Page, method: string, pattern: RegExp) {
  return page.waitForResponse((response) =>
    response.request().method() === method && pattern.test(new URL(response.url()).pathname))
}

// ---------- evidence ----------
export async function attachJson(testInfo: TestInfo, name: string, data: unknown) {
  await testInfo.attach(name, { body: JSON.stringify(data, null, 2), contentType: 'application/json' })
}

export async function attachScreenshot(page: Page, testInfo: TestInfo, name: string) {
  await testInfo.attach(name, { body: await page.screenshot({ fullPage: true }), contentType: 'image/png' })
}

/**
 * Records (does not assert) what the UI shows after a failed action, so that the
 * missing-feedback oracle can be decided by the team from real observations.
 */
export async function observeFeedback(page: Page, knownMessages: string[]) {
  const bodyText = await page.locator('body').innerText()
  return {
    visible_form_errors: await page.locator('.form-error').allInnerTexts(),
    known_messages_visible: Object.fromEntries(knownMessages.map((message) => [message, bodyText.includes(message)])),
  }
}
