# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Проверка авторизация и проверка работы куки
- Location: e2e\auth.spec.ts:3:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.waitForResponse: Test timeout of 30000ms exceeded.
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e2]:
    - banner [ref=e3]:
      - generic [ref=e4]:
        - link [ref=e6] [cursor=pointer]:
          - /url: /
        - button "Show popup" [ref=e15]:
          - generic: System
    - main [ref=e20]:
      - main [ref=e21]:
        - generic [ref=e25]:
          - heading "МОРИ" [level=1] [ref=e26]
          - paragraph [ref=e27]: "Машинное Обучение :"
          - paragraph [ref=e28]: Разворачивание и Исследование
        - generic [ref=e30]:
          - generic [ref=e31]:
            - generic [ref=e33]:
              - generic [ref=e34]: логин
              - textbox "логин" [ref=e39]:
                - /placeholder: MyLogin
                - text: lutece_
            - generic [ref=e41]:
              - generic [ref=e42]: пароль
              - generic [ref=e46]:
                - textbox "пароль" [ref=e48]:
                  - /placeholder: ••••••••
                  - text: "12345678"
                - button [ref=e49]
          - generic [ref=e51]:
            - generic [ref=e52]:
              - switch [checked] [ref=e55]
              - generic [ref=e56]: Запомнить меня
            - link "Не зарегистрированы?" [ref=e60] [cursor=pointer]:
              - /url: /reg
          - button "Войти" [active] [ref=e61]
  - region "Notifications (F8)":
    - list
  - generic [ref=e63]:
    - button "Toggle Nuxt DevTools" [ref=e64] [cursor=pointer]
    - generic "Page load time" [ref=e68]:
      - generic [ref=e69]: "109"
      - generic [ref=e70]: ms
    - button "Toggle Component Inspector" [ref=e72] [cursor=pointer]
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
> 11 |   const authResponsePromise = page.waitForResponse(response => {
     |                                    ^ Error: page.waitForResponse: Test timeout of 30000ms exceeded.
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
  38 |   await expect(page).not.toHaveURL('http://localhost:3000/auth')
  39 | })
  40 | 
```