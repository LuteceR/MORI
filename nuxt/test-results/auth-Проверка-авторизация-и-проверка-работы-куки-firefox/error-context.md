# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Проверка авторизация и проверка работы куки
- Location: e2e\auth.spec.ts:3:1

# Error details

```
Error: expect(page).not.toHaveURL(expected) failed

Expected: not "http://localhost:3000/auth"
Received: "http://localhost:3000/auth"
Timeout:  5000ms

Call log:
  - Expect "not toHaveURL" with timeout 5000ms
    13 × locator resolved to <html lang="ru" class="light">…</html>
       - unexpected value "http://localhost:3000/auth"

```

```yaml
- banner:
  - link:
    - /url: /
    - img
  - button "Show popup": System
- main:
  - main:
    - heading "МОРИ" [level=1]
    - paragraph: "Машинное Обучение :"
    - paragraph: Разворачивание и Исследование
    - text: логин
    - textbox "логин":
      - /placeholder: MyLogin
      - text: lutece_
    - text: пароль
    - textbox "пароль":
      - /placeholder: ••••••••
      - text: "12345678"
    - button
    - switch [checked]
    - text: Запомнить меня
    - link "Не зарегистрированы?":
      - /url: /reg
    - button "Войти"
- alert: Notification Ошибка входаНеправильный логин или пароль
- region "Notifications (F8)":
  - list:
    - listitem:
      - text: Ошибка входа Неправильный логин или пароль
      - button "Close"
      - progressbar "7%"
- img
- button "Toggle Nuxt DevTools":
  - img
- text: 133 ms
- button "Toggle Component Inspector":
  - img
```

# Test source

```ts
  1  | import { expect, test } from '@playwright/test'
  2  | 
  3  | test('Проверка авторизация и проверка работы куки', async ({ page }) => {
  4  |   await page.goto('http://localhost:3000/auth')
  5  | 
  6  |   await page.locator('#login').fill('lutece_')
  7  |   await page.locator('#password').fill('12345678')
  8  |   await page.locator('#rememberMe').check()
  9  | 
  10 |   // Listen for the authorization response BEFORE clicking
  11 |   const authResponsePromise = page.waitForResponse(response => {
  12 |     const pathname = new URL(response.url()).pathname.replace(/\/+$/, '')
  13 | 
  14 |     return pathname === '/authorization' &&
  15 |       response.request().method() === 'POST'
  16 |   })
  17 | 
  18 |   await page.locator('#loginBtn').click()
  19 | 
  20 |   // Wait for backend response
  21 |   const authResponse = await authResponsePromise
  22 | 
  23 |   console.log('Authorization status:', authResponse.status())
  24 |   console.log('Authorization body:', await authResponse.text())
  25 | 
  26 |   expect(authResponse.status()).toBe(200)
  27 | 
  28 |   // Check access cookie
  29 |   const cookies = await page.context().cookies()
  30 | 
  31 |   console.log('Cookies:', cookies)
  32 | 
  33 |   expect(
  34 |     cookies.some(cookie => cookie.name === 'access_token')
  35 |   ).toBeTruthy()
  36 | 
  37 |   // Check redirect
> 38 |   await expect(page).not.toHaveURL('http://localhost:3000/auth')
     |                          ^ Error: expect(page).not.toHaveURL(expected) failed
  39 | })
  40 | 
```