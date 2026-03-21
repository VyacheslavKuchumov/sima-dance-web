import { test, expect } from '@playwright/test'

test('user can sign up successfully', async ({ page }) => {
  const uniqueSuffix = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
  const username = `e2e_${uniqueSuffix}`
  const password = 'TestPass123!'

  await page.goto('/signup')

  await page.getByPlaceholder('Придумайте логин').fill(username)
  await page.getByPlaceholder('Придумайте пароль').fill(password)
  await page.getByPlaceholder('Подтвердите пароль').fill(password)

  const signupResponsePromise = page.waitForResponse((response) => {
    return response.url().includes('/api/backend/accounts/signup/') &&
      response.request().method() === 'POST'
  })
  const tokenResponsePromise = page.waitForResponse((response) => {
    return response.url().includes('/api/backend/accounts/token/') &&
      response.request().method() === 'POST'
  })

  await page.getByRole('button', { name: 'Регистрация' }).click()

  const signupResponse = await signupResponsePromise
  const tokenResponse = await tokenResponsePromise

  expect(signupResponse.status()).toBeGreaterThanOrEqual(200)
  expect(signupResponse.status()).toBeLessThan(300)
  expect(tokenResponse.status()).toBeGreaterThanOrEqual(200)
  expect(tokenResponse.status()).toBeLessThan(300)

  await expect(page).toHaveURL(/\/$/)
})
