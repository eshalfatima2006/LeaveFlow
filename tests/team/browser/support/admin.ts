import type { Page } from '@playwright/test'
import { BACKEND_URL, fixture } from './harness'
import { expect, type FixtureUser } from './test'

export async function signInToAdmin(page: Page, admin: FixtureUser) {
  await page.goto(`${BACKEND_URL}/admin/`)
  await page.locator('#id_username').fill(admin.username)
  await page.locator('#id_password').fill(admin.password)
  await page.locator('input[type="submit"]').click()
  await expect(page.locator('#user-tools')).toContainText(admin.username)
}

export async function openEntitlement(page: Page, employee: FixtureUser) {
  const id = fixture<number>('balance-id', { id: employee.id })
  await page.goto(`${BACKEND_URL}/admin/leave/leavebalance/${id}/change/`)
  await expect(page.locator('#id_user')).toHaveValue(String(employee.id))
}

export async function openEmployee(page: Page, employee: FixtureUser) {
  await page.goto(`${BACKEND_URL}/admin/leave/user/${employee.id}/change/`)
  await expect(page.locator('#id_username')).toHaveValue(employee.username)
}

export function saveAdminForm(page: Page) {
  return page.locator('input[name="_save"]').click()
}

export async function expectAdminSaved(page: Page) {
  await expect(page.locator('.messagelist .success')).toBeVisible()
}
