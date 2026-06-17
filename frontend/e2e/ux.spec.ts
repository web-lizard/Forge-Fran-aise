import { expect, test, type Locator, type Page } from '@playwright/test'
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
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
  expect(overflow).toBeLessThanOrEqual(4)
}

async function firstVisible(locators: Locator[]): Promise<Locator | null> {
  for (const locator of locators) {
    if (await locator.isVisible().catch(() => false)) {
      return locator
    }
  }

  return null
}

async function expectClickableElementsHealthy(page: Page) {
  const clickables = page.locator('button:not([disabled]), a[href]')
  const count = await clickables.count()

  expect(count).toBeGreaterThan(0)

  const limit = Math.min(count, 60)

  for (let index = 0; index < limit; index += 1) {
    const item = clickables.nth(index)

    if (!(await item.isVisible())) continue

    await item.evaluate((node) => {
      node.scrollIntoView({ block: 'center', inline: 'nearest' })
    })
    await page.waitForTimeout(120)

    const box = await item.boundingBox()
    expect(box, `clickable #${index} should have bounding box`).not.toBeNull()
    if (!box) continue

    const viewport = page.viewportSize()
    if (!viewport) continue

    if (box.y + box.height < 0 || box.y > viewport.height) continue

    expect(box.width, `clickable #${index} width`).toBeGreaterThan(20)
    expect(box.height, `clickable #${index} height`).toBeGreaterThan(20)

    const result = await item.evaluate((node, itemIndex) => {
      const rect = node.getBoundingClientRect()
      const x = rect.left + rect.width / 2
      const y = rect.top + rect.height / 2
      const top = document.elementFromPoint(x, y)

      const same =
        top === node ||
        Boolean(top && node.contains(top)) ||
        top?.closest('button, a') === node

      return {
        ok: same,
        index: itemIndex,
        text: (node.textContent ?? '').trim().slice(0, 120),
        tag: node.tagName,
        className: String((node as HTMLElement).className ?? ''),
        rect: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height),
        },
        topTag: top?.tagName ?? null,
        topClass: top ? String((top as HTMLElement).className ?? '') : null,
        topText: top?.textContent?.trim().slice(0, 120) ?? null,
      }
    }, index)

    expect(result.ok, `clickable covered after centered scroll: ${JSON.stringify(result)}`).toBeTruthy()
  }
}

async function findAudioButton(page: Page): Promise<Locator | null> {
  await page.goto('/lesson/greetings_001')
  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(300)

  for (let step = 0; step < 10; step += 1) {
    const audio = await firstVisible([
      page.locator('.audio-button').first(),
      page.getByRole('button', { name: /Слушать|Écouter|Listen|▶/i }).first(),
    ])

    if (audio) return audio

    const next = await firstVisible([
      page.getByRole('button', { name: /Далее/i }).first(),
      page.getByRole('button', { name: /Следующая/i }).first(),
      page.getByRole('button', { name: /Следующий/i }).first(),
      page.getByRole('button', { name: /Продолжить/i }).first(),
      page.getByRole('button', { name: /Начать/i }).first(),
      page.getByRole('button', { name: /Next|Continue|Suivant/i }).first(),
    ])

    if (!next) break

    await next.click()
    await page.waitForTimeout(250)
  }

  await page.goto('/audio')
  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(300)

  return firstVisible([
    page.locator('.audio-button').first(),
    page.getByRole('button', { name: /Слушать|Écouter|Listen|Normal|Медленно|▶/i }).first(),
    page.locator('button').filter({ hasText: /Слушать|Normal|Медленно|▶/i }).first(),
  ])
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
  const audioButton = await findAudioButton(page)

  expect(audioButton, 'audio button should exist in lesson or audio page').not.toBeNull()
  if (!audioButton) return

  await expect(audioButton).toBeVisible()
  await audioButton.click()

  await expect(audioButton).toBeEnabled({ timeout: 5_000 })

  await expect
    .poll(async () => page.evaluate(() => (window as any).__speechCalls?.length ?? 0), { timeout: 5_000 })
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
