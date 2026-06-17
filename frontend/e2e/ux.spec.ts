import { expect, test, type Page } from '@playwright/test'
import { installMockApi } from './mockApi'

async function expectNoErrorOverlay(page: Page) {
  const bodyText = await page.locator('body').innerText()

  expect(bodyText).not.toMatch(/Failed to load PostCSS config/i)
  expect(bodyText).not.toMatch(/Failed to parse source/i)
  expect(bodyText).not.toMatch(/Unexpected token/i)
  expect(bodyText).not.toMatch(/Internal server error/i)
  await expect(page.locator('vite-error-overlay')).toHaveCount(0)
}

async function expectNoHorizontalOverflow(page: Page) {
  const overflow = await page.evaluate(() => {
    return document.documentElement.scrollWidth - window.innerWidth
  })

  expect(overflow).toBeLessThanOrEqual(4)
}

async function expectClickableElementsHealthy(page: Page) {
  const clickables = page.locator('button:not([disabled]), a[href]')
  const count = await clickables.count()

  expect(count).toBeGreaterThan(0)

  const limit = Math.min(count, 45)

  for (let index = 0; index < limit; index += 1) {
    const item = clickables.nth(index)

    if (!(await item.isVisible())) {
      continue
    }

    const box = await item.boundingBox()
    expect(box, `clickable #${index} should have bounding box`).not.toBeNull()

    if (!box) continue

    expect(box.width, `clickable #${index} width`).toBeGreaterThan(24)
    expect(box.height, `clickable #${index} height`).toBeGreaterThan(24)

    const topOk = await item.evaluate((node) => {
      const rect = node.getBoundingClientRect()
      const x = rect.left + rect.width / 2
      const y = rect.top + rect.height / 2
      const top = document.elementFromPoint(x, y)

      if (!top) return false
      if (top === node) return true
      if (node.contains(top)) return true

      const clickableParent = top.closest('button, a')
      return clickableParent === node
    })

    expect(topOk, `clickable #${index} should not be covered`).toBeTruthy()
  }
}

test.beforeEach(async ({ page }) => {
  await installMockApi(page)

  page.on('pageerror', (error) => {
    throw error
  })
})

test('main routes open without red overlay and dead layout', async ({ page }) => {
  const routes = [
    '/',
    '/campaign',
    '/section/start',
    '/lesson/greetings_001',
    '/practice',
    '/audio',
    '/vulgar',
    '/profile',
    '/diagnostics',
    '/codex',
  ]

  for (const route of routes) {
    await page.goto(route)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(250)

    await expect(page.locator('main')).toBeVisible()
    await expectNoErrorOverlay(page)
    await expectNoHorizontalOverflow(page)
    await expectClickableElementsHealthy(page)
  }
})

test('audio button is clickable, does not stay disabled, and calls speech fallback', async ({ page }) => {
  await page.goto('/lesson/greetings_001')
  await page.waitForLoadState('domcontentloaded')

  const audioButton = page.getByRole('button', { name: /Слушать|Écouter|Listen|Normal/i }).first()
  await expect(audioButton).toBeVisible()

  await audioButton.click()

  await expect(audioButton).toBeEnabled({ timeout: 5_000 })

  await expect
    .poll(async () => page.evaluate(() => (window as any).__speechCalls?.length ?? 0), {
      timeout: 5_000,
    })
    .toBeGreaterThan(0)

  await expectNoErrorOverlay(page)
})

test('practice answer flow does not leave buttons stuck', async ({ page }) => {
  await page.goto('/practice')
  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(300)

  const firstOption = page.locator('.option-button').first()
  await expect(firstOption).toBeVisible()
  await firstOption.click()

  await expect(page.locator('.result-box')).toBeVisible()
  await expect(firstOption).toBeEnabled({ timeout: 5_000 })

  const nextButton = page.getByRole('button', { name: /Следующий удар|Coup suivant/i })
  await expect(nextButton).toBeVisible()
  await nextButton.click()

  await expectNoErrorOverlay(page)
  await expectNoHorizontalOverflow(page)
})

test('mobile and desktop viewports have no covered navigation', async ({ page }) => {
  const viewports = [
    { width: 390, height: 844 },
    { width: 1366, height: 768 },
  ]

  for (const viewport of viewports) {
    await page.setViewportSize(viewport)
    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(250)

    await expect(page.locator('.bottom-nav')).toBeVisible()
    await expectNoHorizontalOverflow(page)
    await expectClickableElementsHealthy(page)
  }
})
