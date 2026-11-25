import type { APIRequestContext, Page } from '@playwright/test'
import { NOTIFICATIONS_ENABLED, NOTIFICATIONS_URL, fixture } from '../support/harness'
import {
  apiDecide, apiSubmit, apiToken, createScenario, expect, openRequests,
  readRequest, readRequests, rowByNote, signIn, test, type FixtureUser,
} from '../support/test'

test.skip(!NOTIFICATIONS_ENABLED, 'Start isolated Redis and worker and enable the notification profile.')

const body = { start_date: '2027-04-05', end_date: '2027-04-05', note: 'Notification request' }

function recipients() {
  return createScenario({
    teams: ['Orchid', 'Willow'],
    users: [
      { key: 'employee', first: 'Sage', role: 'employee', team: 'Orchid', allowance: 10 },
      { key: 'manager', first: 'Morgan', role: 'manager', team: 'Orchid' },
      { key: 'outsider', role: 'manager', team: 'Willow' },
      { key: 'admin', role: 'admin' },
    ],
  }).users
}

async function submit(request: APIRequestContext, employee: FixtureUser) {
  const token = await apiToken(request, employee)
  const response = await apiSubmit(request, token, body)
  expect(response.status()).toBe(201)
  return Number((await response.json()).id)
}

async function decide(request: APIRequestContext, manager: FixtureUser, id: number) {
  const token = await apiToken(request, manager)
  expect((await apiDecide(request, token, id, 'approved')).status()).toBe(200)
}

async function feed(request: APIRequestContext, user: FixtureUser) {
  const token = await apiToken(request, user)
  return async (id: number, type: string) => {
    const response = await request.get(`${NOTIFICATIONS_URL}/notifications`, {
      headers: { Authorization: `Token ${token}` },
    })
    expect(response.status()).toBe(200)
    const { notifications } = await response.json()
    return notifications.filter((item: { request_id: number; type: string }) => item.request_id === id && item.type === type)
  }
}

function state(id: number) {
  return fixture<{
    events: Array<{ type: string; recipients: number[] }>; unacknowledged: number | null; publish_errors: number
  }>('notification-state', { id })
}

async function openPanel(page: Page) {
  await page.locator('.notification-trigger').click()
  return page.locator('.notification-panel')
}

async function connect(page: Page, user: FixtureUser) {
  const opened = page.waitForResponse(response => response.url() === `${NOTIFICATIONS_URL}/events`)
  await signIn(page, user)
  expect((await opened).status()).toBe(200)
}

test('TC-UC07-M employee receives one live approval without reloading', async ({ page, request }) => {
  const users = recipients()
  const id = await submit(request, users.employee)
  await connect(page, users.employee)
  const panel = await openPanel(page)
  await expect(panel.locator('article')).toHaveCount(0)
  await decide(request, users.manager, id)
  await expect(panel.getByText('Request approved')).toBeVisible()
  await expect(panel.locator('article')).toContainText(/Morgan.*Apr.*2027/i)
  await expect(page.locator('.notification-trigger span')).toHaveText('1')
  const employeeFeed = await feed(request, users.employee)
  expect(await employeeFeed(id, 'leave.approved')).toHaveLength(1)
  expect(state(id).events.find(event => event.type === 'leave.approved')?.recipients).toEqual([users.employee.id])
  await expect.poll(() => state(id).unacknowledged).toBe(0)
  expect(readRequest(id)?.status).toBe('approved')
})

test('TC-UC07-A1 new-request alerts reach the team manager and administrator only', async ({ page, request }) => {
  const users = recipients()
  await connect(page, users.manager)
  const panel = await openPanel(page)
  const id = await submit(request, users.employee)
  await expect(panel.getByText('New request to review')).toBeVisible()
  for (const [role, count] of [['employee', 0], ['manager', 1], ['admin', 1], ['outsider', 0]] as const) {
    const getFeed = await feed(request, users[role])
    await expect.poll(async () => (await getFeed(id, 'leave.requested')).length).toBe(count)
  }
  expect(new Set(state(id).events[0].recipients)).toEqual(new Set([users.manager.id, users.admin.id]))
  await expect.poll(() => state(id).unacknowledged).toBe(0)
  expect(readRequest(id)?.status).toBe('pending')
})

test('TC-UC07-A2 offline recipient reads the stored approval on a later sign-in', async ({ page, request }) => {
  const users = recipients()
  const id = await submit(request, users.employee)
  await decide(request, users.manager, id)
  const getFeed = await feed(request, users.employee)
  await expect.poll(async () => (await getFeed(id, 'leave.approved')).length).toBe(1)
  const before = readRequests()
  await signIn(page, users.employee)
  const panel = await openPanel(page)
  await expect(panel.getByText('Request approved')).toBeVisible()
  await expect(panel.locator('article')).toHaveCount(1)
  await expect.poll(() => state(id).unacknowledged).toBe(0)
  expect(readRequests()).toEqual(before)
})

test('TC-UC07-E1 an unavailable feed reports the outage while requests remain usable', async ({ page, request }) => {
  const users = recipients()
  await page.route(`${NOTIFICATIONS_URL}/notifications`, route => route.fulfill({ status: 503 }))
  await signIn(page, users.employee)
  const panel = await openPanel(page)
  await expect(panel.getByText('The notification service is unavailable.')).toBeVisible()
  const id = await submit(request, users.employee)
  await page.reload()
  await openRequests(page)
  await expect(rowByNote(page, body.note).locator('.status')).toHaveText('Pending')
  expect(readRequest(id)?.status).toBe('pending')
})

test('TC-UC07-E2 a controlled publish failure preserves the approval but produces no alert', async ({ page, request }) => {
  const users = recipients()
  const id = await submit(request, users.employee)
  await connect(page, users.employee)
  const panel = await openPanel(page)
  const before = state(id)
  fixture('notification-fault')
  await decide(request, users.manager, id)
  expect(readRequest(id)?.status).toBe('approved')
  const after = state(id)
  expect(after.events).toEqual(before.events)
  expect(after.publish_errors).toBe(before.publish_errors + 1)
  const getFeed = await feed(request, users.employee)
  expect(await getFeed(id, 'leave.approved')).toHaveLength(0)
  await expect(panel.locator('article')).toHaveCount(0)
  await expect.poll(() => state(id).unacknowledged).toBe(0)
})
