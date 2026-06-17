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
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
  expect(overflow).toBeLessThanOrEqual(4)
}

async function expectClickableElementsHealthy(page: Page) {
  const clickables = page.locator('button:not([disabled]), a[href]')
  const count = await clickables.count()

  expect(count).toBeGreaterThan(0)

  const limit = Math.min(count, 60)

  for (let index = 0; index < limit; index += 1) {
    const item = clickables.nth(index)

    if (!(await item.isVisible())) continue

    await item.scrollIntoViewIfNeeded()
    await page.waitForTimeout(80)

    const box = await item.boundingBox()
    expect(box, `clickable #${index} should have bounding box`).not.toBeNull()
    if (!box) continue

    if (box.y + box.height < 0 || box.y > page.viewportSize()!.height) continue

    expect(box.width, `clickable #${index} width`).toBeGreaterThan(20)
    expect(box.height, `clickable #${index} height`).toBeGreaterThan(20)

    const result = await item.evaluate((node, itemIndex) => {
      const rect = node.getBoundingClientRect()
      const points = [
        [rect.left + rect.width / 2, rect.top + rect.height / 2],
        [rect.left + Math.min(14, rect.width / 2), rect.top + rect.height / 2],
        [rect.right - Math.min(14, rect.width / 2), rect.top + rect.height / 2],
      ]

      const ok = points.some(([x, y]) => {
        const top = document.elementFromPoint(x, y)

        if (!top) return false
        if (top === node) return true
        if (node.contains(top)) return true

        const clickableParent = top.closest('button, a')
        return clickableParent === node
      })

      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2
      const top = document.elementFromPoint(centerX, centerY)

      return {
        ok,
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

    expect(result.ok, `clickable covered after scrollIntoView: ${JSON.stringify(result)}`).toBeTruthy()
  }
}

async function clickForwardUntilAudio(page: Page) {
  for (let step = 0; step < 10; step += 1) {
    const audio = page.locator('.audio-button').first()

    if (await audio.isVisible().catch(() => false)) {
      return audio
    }

    const anyListen = page.getByRole('button', { name: /Слушать|Écouter|Listen|▶/i }).first()

    if (await anyListen.isVisible().catch(() => false)) {
      return anyListen
    }

    const nextCandidates = [
      /Далее/i,
      /Следующая/i,
      /Следующий/i,
      /Продолжить/i,
      /Начать/i,
      /Вперёд/i,
      /Next/i,
      /Continue/i,
      /Suivant/i,
    ]

    let clicked = false

    for (const pattern of nextCandidates) {
      const next = page.getByRole('button', { name: pattern }).first()

      if (await next.isVisible().catch(() => false)) {
        await next.click()
        await page.waitForTimeout(250)
        clicked = true
        break
      }
    }

    if (!clicked) break
  }

  return null
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
  await page.waitForTimeout(300)

  const audioButton = await clickForwardUntilAudio(page)

  expect(audioButton, 'audio button should exist in lesson flow').not.toBeNull()
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
