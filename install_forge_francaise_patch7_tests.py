from pathlib import Path
import json
import subprocess
import textwrap

ROOT = Path(r"D:\PYTHON\Forge Francaise")
REMOTE_URL = "https://github.com/web-lizard/Forge-Fran-aise.git"

GIT_NAME = "web-lizard"
GIT_EMAIL = "web-lizard@users.noreply.github.com"


def clean(content: str) -> str:
    return textwrap.dedent(content).lstrip("\n").rstrip() + "\n"


def w(rel_path: str, content: str = "") -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(clean(content), encoding="utf-8")
    print(f"written: {rel_path}")


def write_json_no_bom(rel_path: str, payload: dict) -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written json: {rel_path}")


def run(cmd: list[str], cwd: Path = ROOT) -> int:
    print("")
    print("RUN:", " ".join(cmd))
    try:
        result = subprocess.run(cmd, cwd=str(cwd), check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"skip, command not found: {' '.join(cmd)}")
        return 127


def patch_package_json() -> None:
    package_path = ROOT / "frontend" / "package.json"

    if package_path.exists():
        package = json.loads(package_path.read_text(encoding="utf-8-sig"))
    else:
        package = {
            "name": "forge-francaise",
            "private": True,
            "version": "0.7.0",
            "type": "module",
            "scripts": {},
            "dependencies": {},
            "devDependencies": {},
        }

    package["version"] = "0.7.0"
    package.setdefault("scripts", {})
    package["scripts"].update({
        "dev": "vite --host 127.0.0.1 --port 5197",
        "build": "vue-tsc --noEmit && vite build",
        "preview": "vite preview --host 127.0.0.1 --port 4197",
        "test:e2e": "playwright test",
        "test:e2e:headed": "playwright test --headed",
        "test:e2e:report": "playwright show-report"
    })

    package.setdefault("dependencies", {})
    package["dependencies"].update({
        "pinia": "^2.1.7",
        "vue": "^3.4.0",
        "vue-router": "^4.3.0"
    })

    package.setdefault("devDependencies", {})
    package["devDependencies"].update({
        "@playwright/test": "^1.49.0",
        "@vitejs/plugin-vue": "^5.0.5",
        "typescript": "^5.4.0",
        "vite": "^5.2.0",
        "vue-tsc": "^2.0.0"
    })

    write_json_no_bom("frontend/package.json", package)


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Project directory not found: {ROOT}")

    print("Forge Francaise patch 7")
    print("UX autotests, Playwright, no-stuck-buttons guard")
    print(f"root: {ROOT}")

    patch_package_json()

    w("frontend/playwright.config.ts", """
    import { defineConfig } from '@playwright/test'

    export default defineConfig({
      testDir: './e2e',
      timeout: 35_000,
      expect: {
        timeout: 8_000,
      },
      fullyParallel: false,
      reporter: [
        ['list'],
        ['html', { outputFolder: 'playwright-report', open: 'never' }],
      ],
      use: {
        baseURL: 'http://127.0.0.1:5197',
        trace: 'retain-on-failure',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        viewport: { width: 390, height: 844 },
      },
      webServer: {
        command: 'npm run dev',
        url: 'http://127.0.0.1:5197',
        reuseExistingServer: true,
        timeout: 120_000,
      },
    })
    """)

    w("frontend/e2e/mockApi.ts", """
    import type { Page, Route } from '@playwright/test'

    const profile = {
      id: 'local_lizard',
      display_name: 'Monsieur Souveraineté',
      ui_language: 'ru',
      learning_language: 'fr',
      voice_id: 'edge_fr_denise',
      rank_id: 'recrue',
      vulgar_library_enabled: true,
    }

    const progressSummary = {
      profile_id: 'local_lizard',
      score: 120,
      current_level: 'A0',
      completed_lessons: [],
      completed_count: 0,
      total_answers: 3,
      correct_answers: 2,
      wrong_answers: 1,
      accuracy: 67,
      weak_topics: ['article', 'audio'],
      tag_stats: [],
      recent_events: [],
    }

    const sections = [
      {
        id: 'start',
        slug: 'start',
        order: 0,
        icon: 'crown',
        title: { ru: 'Вход во французский', fr: 'Entrée dans le français' },
        subtitle: { ru: 'Приветствия, вежливость и первые фразы.', fr: 'Salutations et premières phrases.' },
        level: 'A0',
        tone: 'basic',
        lessons: ['greetings_001'],
        is_adult: false,
      },
      {
        id: 'articles',
        slug: 'articles',
        order: 2,
        icon: 'shield',
        title: { ru: 'Артикли', fr: 'Les articles' },
        subtitle: { ru: 'Le, la, les без тумана.', fr: 'Le, la, les.' },
        level: 'A0',
        tone: 'grammar',
        lessons: ['le_la_001'],
        is_adult: false,
      },
      {
        id: 'vulgar_french',
        slug: 'vulgar-french',
        order: 7,
        icon: 'flame',
        title: { ru: 'Французский мат', fr: 'Les gros mots français' },
        subtitle: { ru: 'Грубые фразы и регистр.', fr: 'Registre vulgaire.' },
        level: 'A1',
        tone: 'vulgar',
        lessons: ['vulgar_intro_001'],
        is_adult: true,
      },
    ]

    const ranks = [
      {
        id: 'recrue',
        order: 1,
        fr: 'Recrue',
        transcription: '[рёкрю]',
        ru: 'новобранец',
        min_score: 0,
      },
      {
        id: 'soldat',
        order: 2,
        fr: 'Soldat',
        transcription: '[сольда]',
        ru: 'солдат',
        min_score: 100,
      },
    ]

    const voices = [
      {
        id: 'edge_fr_denise',
        label: 'Denise Neural, France',
        lang: 'fr',
        engine: 'edge',
        quality: 'neural-online',
        gender: 'female',
      },
      {
        id: 'mock_fr_female',
        label: 'Voix impériale féminine, mock',
        lang: 'fr',
        engine: 'mock',
        quality: 'dev',
        gender: 'female',
      },
    ]

    const greetingLesson = {
      id: 'greetings_001',
      section_id: 'start',
      order: 1,
      level: 'A0',
      title: {
        ru: 'Bonjour, merci и базовая вежливость',
        fr: 'Bonjour, merci et la politesse de base',
      },
      cards: [
        {
          type: 'theory',
          title: { ru: 'Первый принцип', fr: 'Premier principe' },
          body: {
            ru: 'Сначала учим короткие живые фразы.',
            fr: 'On commence par des phrases courtes.',
          },
        },
        {
          type: 'word',
          fr: 'Bonjour',
          transcription: '[бонжур]',
          ru: 'здравствуйте / добрый день',
          audio_text: 'Bonjour',
          tooltip: {
            ru: 'Универсальное вежливое приветствие.',
            fr: 'Salutation polie.',
          },
        },
        {
          type: 'exercise',
          exercise_id: 'ex_bonjour_translation',
        },
      ],
      exercises: [
        {
          id: 'ex_bonjour_translation',
          type: 'choose_option',
          lesson_id: 'greetings_001',
          section_id: 'start',
          prompt: {
            ru: 'Что значит Bonjour?',
            fr: 'Que signifie Bonjour ?',
          },
          options: ['спасибо', 'здравствуйте', 'пожалуйста', 'до свидания'],
          answer: 'здравствуйте',
          explanation: {
            ru: 'Bonjour значит здравствуйте или добрый день.',
            fr: 'Bonjour signifie bonjour.',
          },
          audio_text: 'Bonjour',
          tags: ['greeting', 'basic'],
          difficulty: 1,
        },
      ],
    }

    const leLaLesson = {
      id: 'le_la_001',
      section_id: 'articles',
      order: 1,
      level: 'A0',
      title: {
        ru: 'Le и la',
        fr: 'Le et la',
      },
      cards: [
        {
          type: 'word',
          fr: 'la maison',
          transcription: '[ля мэзон]',
          ru: 'дом',
          audio_text: 'la maison',
          tooltip: {
            ru: 'maison женского рода.',
            fr: 'maison est féminin.',
          },
        },
        {
          type: 'exercise',
          exercise_id: 'ex_la_maison_001',
        },
      ],
      exercises: [
        {
          id: 'ex_la_maison_001',
          type: 'choose_option',
          lesson_id: 'le_la_001',
          section_id: 'articles',
          prompt: {
            ru: 'Выбери правильный артикль: ___ maison',
            fr: 'Choisis le bon article : ___ maison',
          },
          options: ['le', 'la', 'les'],
          answer: 'la',
          explanation: {
            ru: 'maison женского рода, поэтому la maison.',
            fr: 'maison est féminin, donc la maison.',
          },
          audio_text: 'la maison',
          tags: ['article', 'gender'],
          difficulty: 1,
        },
      ],
    }

    const course = {
      sections: sections.map((section) => ({
        ...section,
        lesson_items: [
          {
            id: section.lessons[0],
            section_id: section.id,
            order: 1,
            level: section.level,
            title: section.id === 'articles' ? leLaLesson.title : greetingLesson.title,
            card_count: 3,
            exercise_count: 1,
          },
        ],
      })),
      total_sections: sections.length,
      total_lessons: sections.length,
    }

    const diagnostics = {
      ok: true,
      app: {
        app_name: 'Forge Francaise',
        version: '0.7.0',
        backend_port: 8797,
        frontend_port: 5197,
      },
      content: {
        sections: 8,
        lessons: 13,
        exercises: 17,
        vulgar_items: 6,
        codex_entries: 4,
      },
      paths: {
        project_root: { path: 'mock', exists: true, is_dir: true },
        content_root: { path: 'mock/content', exists: true, is_dir: true },
      },
      frontend: {
        package_json: true,
        index_html: true,
        src: true,
        env_local: true,
      },
      backend: {
        requirements: true,
        main: true,
        venv: true,
      },
      audio_cache: {
        count: 1,
        indexed_count: 1,
        total_bytes: 1024,
        total_mb: 0.001,
        items: [],
      },
      progress_summary: progressSummary,
    }

    function json(route: Route, body: unknown, status = 200) {
      return route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(body),
      })
    }

    function courseSection(sectionId: string) {
      const section = course.sections.find((item) => item.id === sectionId || item.slug === sectionId)
      return section ?? course.sections[0]
    }

    function lessonById(lessonId: string) {
      if (lessonId === 'le_la_001') return leLaLesson
      return greetingLesson
    }

    export async function installMockApi(page: Page) {
      await page.addInitScript(() => {
        ;(window as any).__speechCalls = []

        const fakeSpeech = {
          cancel: () => {},
          speak: (utterance: SpeechSynthesisUtterance) => {
            ;(window as any).__speechCalls.push(utterance.text)
          },
          getVoices: () => [],
        }

        Object.defineProperty(window, 'speechSynthesis', {
          value: fakeSpeech,
          configurable: true,
        })
      })

      await page.route('**/api/**', async (route) => {
        const request = route.request()
        const url = new URL(request.url())
        let path = url.pathname

        const apiIndex = path.indexOf('/api')
        if (apiIndex >= 0) {
          path = path.slice(apiIndex + 4) || '/'
        }

        if (request.method() === 'PATCH' && path.startsWith('/profiles/')) {
          return json(route, profile)
        }

        if (request.method() === 'DELETE' && path === '/audio/cache') {
          return json(route, { ok: true, removed: 1 })
        }

        if (request.method() === 'POST' && path === '/audio/speak') {
          return json(route, {
            audio_id: 'mock-audio',
            url: '/api/audio/file/mock-audio',
            cached: false,
            duration_ms: 600,
            provider: 'mock',
            format: 'wav',
            fallback: true,
          })
        }

        if (request.method() === 'POST' && path === '/practice/answer') {
          return json(route, {
            correct: true,
            expected: 'здравствуйте',
            explanation: {
              ru: 'Тестовый ответ засчитан.',
              fr: 'Réponse acceptée.',
            },
            score: 130,
            weak_topics: [],
          })
        }

        if (path.startsWith('/audio/file/')) {
          return route.fulfill({
            status: 200,
            contentType: 'audio/wav',
            body: '',
          })
        }

        if (path === '/health') return json(route, { ok: true, app: 'forge-francaise' })
        if (path === '/settings') return json(route, { app_name: 'Forge Francaise', version: '0.7.0' })
        if (path === '/diagnostics') return json(route, diagnostics)
        if (path === '/app/bootstrap') {
          return json(route, {
            profile,
            progress: progressSummary,
            sections,
            ranks,
            voices,
          })
        }

        if (path === '/course') return json(route, course)

        if (path.startsWith('/course/sections/')) {
          const sectionId = decodeURIComponent(path.split('/').pop() ?? 'start')
          return json(route, courseSection(sectionId))
        }

        if (path.startsWith('/lessons/')) {
          const lessonId = decodeURIComponent(path.split('/').pop() ?? 'greetings_001')
          return json(route, lessonById(lessonId))
        }

        if (path === '/codex') {
          return json(route, [
            {
              id: 'articles',
              title: { ru: 'Артикли', fr: 'Les articles' },
              summary: { ru: 'Тестовая статья.', fr: 'Article de test.' },
              items: [
                { fr: 'le', transcription: '[лё]', ru: 'артикль мужского рода' },
              ],
            },
          ])
        }

        if (path === '/vulgar/items') {
          return json(route, [
            {
              id: 'putain_j_en_ai_marre',
              fr: 'Putain, j’en ai marre.',
              transcription: '[пютэн, жанэ мар]',
              ru: 'Блядь, меня это достало.',
              rudeness_level: 4,
              context: { ru: 'Грубо.', fr: 'Vulgaire.' },
              audio_text: 'Putain, j’en ai marre.',
              tags: ['vulgar'],
              softer_versions: [
                { fr: 'J’en ai assez.', transcription: '[жанэ асэ]', ru: 'Мне хватит.' },
              ],
            },
          ])
        }

        if (path === '/audio/voices') return json(route, voices)
        if (path === '/audio/cache') {
          return json(route, {
            count: 1,
            indexed_count: 1,
            total_bytes: 1024,
            total_mb: 0.001,
            items: [],
          })
        }

        if (path.startsWith('/progress/local_lizard/summary')) return json(route, progressSummary)
        if (path.startsWith('/progress/local_lizard')) return json(route, progressSummary)

        if (path.startsWith('/review/local_lizard/session')) {
          return json(route, {
            profile_id: 'local_lizard',
            mode: url.searchParams.get('mode') ?? 'quick',
            limit: Number(url.searchParams.get('limit') ?? 7),
            count: 2,
            exercises: [
              {
                ...greetingLesson.exercises[0],
                lesson_id: 'greetings_001',
                section_id: 'start',
                lesson_title: greetingLesson.title,
                level: 'A0',
              },
              {
                ...leLaLesson.exercises[0],
                lesson_id: 'le_la_001',
                section_id: 'articles',
                lesson_title: leLaLesson.title,
                level: 'A0',
              },
            ],
          })
        }

        return json(route, { ok: true, path })
      })
    }
    """)

    w("frontend/e2e/ux.spec.ts", """
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
    """)

    w("scripts/strip_bom.py", """
    from pathlib import Path
    import argparse

    ROOT = Path(__file__).resolve().parents[1]

    PATTERNS = [
        "frontend/**/*.json",
        "frontend/**/*.ts",
        "frontend/**/*.vue",
        "frontend/**/*.css",
        "frontend/**/*.html",
        "backend/**/*.py",
        "content/**/*.json",
        ".vscode/*.json",
        "*.json",
    ]


    def main() -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--check", action="store_true")
        args = parser.parse_args()

        changed = []

        for pattern in PATTERNS:
            for path in ROOT.glob(pattern):
                if not path.is_file():
                    continue

                data = path.read_bytes()

                if data.startswith(b"\\xef\\xbb\\xbf"):
                    changed.append(path.relative_to(ROOT).as_posix())

                    if not args.check:
                        path.write_bytes(data[3:])

        if changed:
            print("BOM found:")
            for item in changed:
                print(f"- {item}")

            if args.check:
                raise SystemExit(1)

            print("BOM stripped.")
        else:
            print("BOM check passed.")


    if __name__ == "__main__":
        main()
    """)

    w("backend/scripts/smoke_audio_config.py", """
    import json
    from pathlib import Path
    import sys

    ROOT = Path(__file__).resolve().parents[1]
    PROJECT_ROOT = ROOT.parent

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    errors = []

    profiles_path = ROOT / "data" / "profiles.json"

    if profiles_path.exists():
        payload = json.loads(profiles_path.read_text(encoding="utf-8-sig"))
        profiles = payload.get("profiles", [])
        local = next((item for item in profiles if item.get("id") == "local_lizard"), None)

        if not local:
            errors.append("local_lizard profile is missing")
        elif str(local.get("voice_id", "")).startswith("mock_"):
            errors.append("local_lizard voice_id still points to mock voice")
    else:
        errors.append("profiles.json is missing")

    voices_response = client.get("/api/audio/voices")
    if voices_response.status_code != 200:
        errors.append(f"/api/audio/voices failed: {voices_response.status_code}")
    else:
        voices = voices_response.json()
        edge_voices = [voice for voice in voices if voice.get("engine") == "edge"]

        if not edge_voices:
            errors.append("No edge voices exposed by /api/audio/voices")

    mock_response = client.post(
        "/api/audio/speak",
        json={
            "text": "Bonjour, monsieur.",
            "lang": "fr",
            "voice_id": "mock_fr_female",
            "speed": 1,
            "mode": "normal",
        },
    )

    if mock_response.status_code != 200:
        errors.append(f"mock /api/audio/speak failed: {mock_response.status_code}")
    else:
        body = mock_response.json()
        if body.get("provider") != "mock":
            errors.append(f"mock /api/audio/speak returned unexpected provider: {body.get('provider')}")

    if errors:
        print("AUDIO CONFIG SMOKE FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("AUDIO CONFIG SMOKE PASSED")
    """)

    w("scripts/test_ui.cmd", """
    @echo off
    cd /d "%~dp0..\\frontend"

    call npm install
    call npx playwright install chromium
    call npm run test:e2e
    """)

    w("scripts/test_ui_headed.cmd", """
    @echo off
    cd /d "%~dp0..\\frontend"

    call npm install
    call npx playwright install chromium
    call npm run test:e2e:headed
    """)

    w("scripts/playwright_report.cmd", """
    @echo off
    cd /d "%~dp0..\\frontend"
    call npm run test:e2e:report
    """)

    w("scripts/check_backend.cmd", """
    @echo off
    cd /d "%~dp0..\\backend"

    if not exist ".venv" (
      py -m venv .venv
    )

    call .venv\\Scripts\\activate.bat
    python -m pip install -r requirements.txt

    echo.
    echo Content validation...
    python scripts\\validate_content.py
    if errorlevel 1 exit /b 1

    echo.
    echo Backend smoke...
    python scripts\\smoke_backend.py
    if errorlevel 1 exit /b 1

    echo.
    echo Audio config smoke...
    python scripts\\smoke_audio_config.py
    if errorlevel 1 exit /b 1
    """)

    w("scripts/check_frontend.cmd", """
    @echo off
    cd /d "%~dp0..\\frontend"

    call npm install

    echo.
    echo Frontend build...
    call npm run build
    if errorlevel 1 exit /b 1
    """)

    w("scripts/test_guard.cmd", """
    @echo off
    cd /d "%~dp0.."

    echo.
    echo === BOM CHECK ===
    py scripts\\strip_bom.py --check
    if errorlevel 1 exit /b 1

    echo.
    echo === BACKEND CHECK ===
    call scripts\\check_backend.cmd
    if errorlevel 1 exit /b 1

    echo.
    echo === FRONTEND BUILD CHECK ===
    call scripts\\check_frontend.cmd
    if errorlevel 1 exit /b 1

    echo.
    echo === UI / UX PLAYWRIGHT CHECK ===
    call scripts\\test_ui.cmd
    if errorlevel 1 exit /b 1

    echo.
    echo TEST GUARD PASSED
    """)

    w("scripts/test_guard_fast.cmd", """
    @echo off
    cd /d "%~dp0.."

    py scripts\\strip_bom.py --check
    if errorlevel 1 exit /b 1

    call scripts\\check_frontend.cmd
    if errorlevel 1 exit /b 1

    call scripts\\test_ui.cmd
    if errorlevel 1 exit /b 1

    echo.
    echo FAST UI GUARD PASSED
    """)

    w("scripts/git_push_patch7.cmd", """
    @echo off
    cd /d "%~dp0.."
    git config user.name "web-lizard"
    git config user.email "web-lizard@users.noreply.github.com"
    git status --short
    git add .
    git commit -m "patch 7: add ui ux autotest guard"
    git push -u origin main
    """)

    w("reports/TESTING_STRATEGY.md", """
    # Forge Française Testing Strategy

    ## What this catches

    - Vite red overlay and parser errors.
    - BOM in JSON / TS / Vue / CSS / HTML files.
    - Broken main routes.
    - Missing main UI.
    - Buttons and links with zero size.
    - Buttons and links covered by another element.
    - Horizontal overflow on mobile.
    - Audio button click path.
    - Audio button stuck disabled/loading state.
    - Browser speech fallback path.
    - Practice answer flow.
    - Frontend build failure.
    - Backend API smoke failure.
    - Default profile accidentally using mock voice.

    ## Main command

    ```cmd
    scripts\\test_guard.cmd
    ```

    ## Faster UI-only command

    ```cmd
    scripts\\test_guard_fast.cmd
    ```

    ## Open Playwright report

    ```cmd
    scripts\\playwright_report.cmd
    ```
    """)

    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8-sig") if readme_path.exists() else ""
    if "## Autotests" not in readme:
        readme += clean("""
        ## Autotests

        Full guard:

        ```cmd
        scripts\\test_guard.cmd
        ```

        Fast UI guard:

        ```cmd
        scripts\\test_guard_fast.cmd
        ```

        Headed UI tests:

        ```cmd
        scripts\\test_ui_headed.cmd
        ```

        Playwright report:

        ```cmd
        scripts\\playwright_report.cmd
        ```

        These tests check routes, visible click targets, no red Vite overlay, no horizontal overflow, audio button behavior, practice flow, BOM, backend smoke and frontend build.
        """)
        readme_path.write_text(readme, encoding="utf-8")
        print("updated: README.md")

    print("")
    print("Running cheap guards...")
    run(["py", "scripts\\strip_bom.py", "--check"])
    run(["py", "scripts\\validate_content.py"], cwd=ROOT / "backend")

    print("")
    print("Git identity...")
    run(["git", "config", "user.name", GIT_NAME])
    run(["git", "config", "user.email", GIT_EMAIL])

    print("")
    print("Git commit...")
    run(["git", "add", "."])
    commit_code = run(["git", "commit", "-m", "patch 7: add ui ux autotest guard"])

    if commit_code != 0:
        print("commit failed or nothing to commit")

    print("")
    print("Git push...")
    push_code = run(["git", "push", "-u", "origin", "main"])

    if push_code != 0:
        print("")
        print("GIT PUSH FAILED OR NEEDS AUTH")
        print("Manual command:")
        print(r'cd /d "D:\\PYTHON\\Forge Francaise"')
        print(r"scripts\\git_push_patch7.cmd")

    print("")
    print("PATCH 7 DONE")
    print("Autotests added.")
    print("")
    print("Run full guard:")
    print(r'scripts\\test_guard.cmd')
    print("")
    print("Run faster UI guard:")
    print(r'scripts\\test_guard_fast.cmd')


if __name__ == "__main__":
    main()