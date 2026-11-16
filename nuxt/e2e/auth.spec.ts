import { expect, test } from '@playwright/test'

test('Проверка авторизация и проверка работы куки', async ({ page }) => {
  await page.goto('http://localhost:3000/auth')

  await page.locator('#login').fill('lutece_')
  await page.locator('#password').fill('12345678')
  await page.locator('#rememberMe').check()

  // Listen for the authorization response BEFORE clicking
  const authResponsePromise = page.waitForResponse(response => {
    const pathname = new URL(response.url()).pathname.replace(/\/+$/, '')

    return pathname === '/authorization' &&
      response.request().method() === 'POST'
  })

  await page.locator('#loginBtn').click()

  // Wait for backend response
  const authResponse = await authResponsePromise

  console.log('Authorization status:', authResponse.status())
  console.log('Authorization body:', await authResponse.text())

  expect(authResponse.status()).toBe(200)

  // Check access cookie
  const cookies = await page.context().cookies()

  console.log('Cookies:', cookies)

  expect(
    cookies.some(cookie => cookie.name === 'access_token')
  ).toBeTruthy()

  // Check redirect
  await expect(page).not.toHaveURL('http://localhost:3000/auth')
})
