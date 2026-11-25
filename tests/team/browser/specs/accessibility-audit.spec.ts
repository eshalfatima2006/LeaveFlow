import AxeBuilder from '@axe-core/playwright'
import { chromium, type Page } from '@playwright/test'
import { startFlow } from 'lighthouse'
import puppeteer from 'puppeteer-core'
import { NOTIFICATIONS_ENABLED } from '../support/harness'
import { openEmployee, openEntitlement, signInToAdmin } from '../support/admin'
import { apiDecide, apiSubmit, apiToken, createScenario, expect, openRequests, signIn, test } from '../support/test'

test.skip(process.env.SQE_ACCESSIBILITY_AUDIT !== '1', 'Enable the authenticated audit profile explicitly.')

const screens = ['UC-01 request form', 'UC-02 review queue', 'UC-04 own records',
  'UC-07 notification panel', 'UC-08 entitlement form', 'UC-09 user form']

for (const screen of screens) {
  test(`authenticated accessibility audit ${screen}`, async ({ request }, info) => {
    test.setTimeout(150_000)
    const { users } = createScenario({
      teams: ['Orchid'],
      users: [
        { key: 'employee', first: 'Sage', role: 'employee', team: 'Orchid', allowance: 10 },
        { key: 'manager', first: 'Morgan', role: 'manager', team: 'Orchid' },
        { key: 'admin', role: 'admin' },
      ],
    })
    const token = await apiToken(request, users.employee)
    const submitted = await apiSubmit(request, token, {
      start_date: '2027-04-05', end_date: '2027-04-07', note: 'Audit fixture request',
    })
    expect(submitted.status()).toBe(201)
    if (screen.startsWith('UC-07') && NOTIFICATIONS_ENABLED) {
      const manager = await apiToken(request, users.manager)
      expect((await apiDecide(request, manager, (await submitted.json()).id, 'approved')).status()).toBe(200)
    }

    const chrome = await puppeteer.launch({
      executablePath: process.env.SQE_AUDIT_CHROME ?? chromium.executablePath(),
      defaultViewport: { width: 1360, height: 900 },
    })
    try {
      const nativePage = (await chrome.pages())[0]
      const connection = await chromium.connectOverCDP(chrome.wsEndpoint())
      const view = connection.contexts()[0].pages()[0] as Page
      await view.addInitScript(() => localStorage.setItem('leaveflow_locale', 'en'))
      if (screen.startsWith('UC-08') || screen.startsWith('UC-09')) {
        await signInToAdmin(view, users.admin)
        if (screen.startsWith('UC-08')) await openEntitlement(view, users.employee)
        else await openEmployee(view, users.employee)
      } else {
        await signIn(view, screen.startsWith('UC-02') ? users.manager : users.employee)
        if (screen.startsWith('UC-01')) {
          await view.locator('header').getByRole('button', { name: 'New request' }).click()
          await expect(view.locator('form.modal')).toBeVisible()
        } else if (screen.startsWith('UC-07')) {
          await view.locator('.notification-trigger').click()
          await expect(view.locator('.notification-panel')).toBeVisible()
        } else {
          await openRequests(view)
        }
      }
      await view.evaluate(() => document.fonts.ready.then(() => undefined))

      const axe = await new AxeBuilder({ page: view }).analyze()
      await info.attach('axe.json', { body: JSON.stringify(axe, null, 2), contentType: 'application/json' })
      const flow = await startFlow(nativePage, {
        name: screen,
        config: {
          extends: 'lighthouse:default',
          settings: {
            onlyCategories: ['accessibility', 'best-practices', 'seo'],
            formFactor: 'desktop',
            screenEmulation: { disabled: true },
            disableStorageReset: true,
          },
        },
      })
      // Snapshot the actual authenticated SPA state, including dialogs and panels.
      await flow.snapshot({ stepName: screen })
      await info.attach('lighthouse.json', {
        body: JSON.stringify(await flow.createFlowResult(), null, 2), contentType: 'application/json',
      })
      await info.attach('lighthouse.html', { body: await flow.generateReport(), contentType: 'text/html' })
    } finally {
      await chrome.close()
    }
  })
}
