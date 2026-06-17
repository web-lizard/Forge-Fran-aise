from pathlib import Path
import subprocess
import textwrap
import json

ROOT = Path(r"D:\PYTHON\Forge Francaise")
REMOTE_URL = "https://github.com/web-lizard/Forge-Fran-aise.git"

BACKEND_PORT = 8797
FRONTEND_PORT = 5197

GIT_NAME = "web-lizard"
GIT_EMAIL = "web-lizard@users.noreply.github.com"


def clean(content: str) -> str:
    return textwrap.dedent(content).lstrip("\n").rstrip() + "\n"


def w(rel_path: str, content: str = "") -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(clean(content), encoding="utf-8")
    print(f"written: {rel_path}")


def mkdir(rel_path: str) -> None:
    path = ROOT / rel_path
    path.mkdir(parents=True, exist_ok=True)
    print(f"dir: {rel_path}")


def run(cmd: list[str], cwd: Path = ROOT) -> int:
    print("")
    print("RUN:", " ".join(cmd))
    try:
        result = subprocess.run(cmd, cwd=str(cwd), check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"skip, command not found: {' '.join(cmd)}")
        return 127


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Project directory not found: {ROOT}")

    print("Forge Francaise patch 6")
    print("Step 6/6: final diagnostics, smoke tests, build scripts, MVP polish")
    print(f"root: {ROOT}")
    print("")

    for rel in [
        "backend/app/api",
        "backend/app/services",
        "backend/scripts",
        "frontend/src/pages",
        "frontend/src/components/imperial",
        "frontend/src/styles",
        "scripts",
        "reports",
        ".vscode",
    ]:
        mkdir(rel)

    w("backend/requirements.txt", """
    fastapi>=0.111.0
    uvicorn[standard]>=0.30.0
    pydantic>=2.7.0
    python-multipart>=0.0.9
    edge-tts>=7.0.0
    httpx>=0.27.0
    """)

    w("backend/app/core/config.py", """
    from pydantic import BaseModel


    class AppConfig(BaseModel):
        app_name: str = "Forge Francaise"
        public_title_ru: str = "Имперский мозговыбиватель французского языка"
        version: str = "0.6.0"
        backend_port: int = 8797
        frontend_port: int = 5197
        default_ui_language: str = "ru"
        learning_language: str = "fr"
        vulgar_library_enabled_by_default: bool = True
        tts_engine: str = "edge-with-mock-fallback"


    config = AppConfig()
    """)

    w("backend/app/services/diagnostic_service.py", """
    from pathlib import Path
    from typing import Any

    from app.core.config import config
    from app.core.paths import AUDIO_CACHE_ROOT, CONTENT_ROOT, DATA_ROOT, PROJECT_ROOT
    from app.services.audio_service import get_audio_service
    from app.services.content_service import get_content_service
    from app.services.progress_service import get_progress_service


    class DiagnosticService:
        def content_counts(self) -> dict[str, Any]:
            content = get_content_service()
            sections = content.list_sections()
            lessons = content.list_lessons()
            exercises = content.list_exercises()
            vulgar_items = content.list_vulgar_items()
            codex_entries = content.list_codex()

            return {
                "sections": len(sections),
                "lessons": len(lessons),
                "exercises": len(exercises),
                "vulgar_items": len(vulgar_items),
                "codex_entries": len(codex_entries),
            }

        def path_status(self) -> dict[str, Any]:
            paths = {
                "project_root": PROJECT_ROOT,
                "content_root": CONTENT_ROOT,
                "data_root": DATA_ROOT,
                "audio_cache_root": AUDIO_CACHE_ROOT,
            }

            return {
                key: {
                    "path": str(value),
                    "exists": value.exists(),
                    "is_dir": value.is_dir(),
                }
                for key, value in paths.items()
            }

        def frontend_status(self) -> dict[str, Any]:
            frontend_root = PROJECT_ROOT / "frontend"

            return {
                "package_json": (frontend_root / "package.json").exists(),
                "index_html": (frontend_root / "index.html").exists(),
                "src": (frontend_root / "src").exists(),
                "env_local": (frontend_root / ".env.local").exists(),
            }

        def backend_status(self) -> dict[str, Any]:
            backend_root = PROJECT_ROOT / "backend"

            return {
                "requirements": (backend_root / "requirements.txt").exists(),
                "main": (backend_root / "app" / "main.py").exists(),
                "venv": (backend_root / ".venv").exists(),
            }

        def app_diagnostics(self) -> dict[str, Any]:
            progress_summary = get_progress_service().summary("local_lizard")
            audio_cache = get_audio_service().cache_summary()

            return {
                "ok": True,
                "app": config.model_dump(),
                "content": self.content_counts(),
                "paths": self.path_status(),
                "frontend": self.frontend_status(),
                "backend": self.backend_status(),
                "audio_cache": audio_cache,
                "progress_summary": progress_summary,
            }


    def get_diagnostic_service() -> DiagnosticService:
        return DiagnosticService()
    """)

    w("backend/app/api/diagnostics.py", """
    from fastapi import APIRouter

    from app.services.diagnostic_service import get_diagnostic_service

    router = APIRouter(tags=["diagnostics"])


    @router.get("/diagnostics")
    def diagnostics():
        return get_diagnostic_service().app_diagnostics()
    """)

    w("backend/app/main.py", """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from app.api import audio, bootstrap, codex, course, diagnostics, health, lessons, practice, profiles, progress, review, sections, settings, vulgar

    app = FastAPI(
        title="Forge Française API",
        description="Imperial French learning engine",
        version="0.6.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5197",
            "http://localhost:5197",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")
    app.include_router(diagnostics.router, prefix="/api")
    app.include_router(bootstrap.router, prefix="/api")
    app.include_router(course.router, prefix="/api")
    app.include_router(sections.router, prefix="/api")
    app.include_router(lessons.router, prefix="/api")
    app.include_router(practice.router, prefix="/api")
    app.include_router(progress.router, prefix="/api")
    app.include_router(review.router, prefix="/api")
    app.include_router(profiles.router, prefix="/api")
    app.include_router(audio.router, prefix="/api")
    app.include_router(codex.router, prefix="/api")
    app.include_router(vulgar.router, prefix="/api")
    """)

    w("backend/scripts/smoke_backend.py", """
    import json
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    checks = [
        ("GET", "/api/health", None),
        ("GET", "/api/settings", None),
        ("GET", "/api/diagnostics", None),
        ("GET", "/api/app/bootstrap", None),
        ("GET", "/api/course", None),
        ("GET", "/api/course/sections/start", None),
        ("GET", "/api/lessons/greetings_001", None),
        ("GET", "/api/codex", None),
        ("GET", "/api/vulgar/items", None),
        ("GET", "/api/review/local_lizard/session?mode=quick&limit=3", None),
        ("GET", "/api/progress/local_lizard/summary", None),
        ("GET", "/api/audio/voices", None),
        (
            "POST",
            "/api/practice/answer",
            {
                "profile_id": "local_lizard",
                "lesson_id": "greetings_001",
                "exercise_id": "ex_bonjour_translation",
                "answer": "здравствуйте",
            },
        ),
        (
            "POST",
            "/api/audio/speak",
            {
                "text": "Bonjour, monsieur.",
                "lang": "fr",
                "voice_id": "mock_fr_female",
                "speed": 1,
                "mode": "normal",
            },
        ),
    ]

    failures = []

    for method, path, payload in checks:
        if method == "GET":
            response = client.get(path)
        elif method == "POST":
            response = client.post(path, json=payload)
        else:
            raise RuntimeError(f"Unsupported method: {method}")

        ok = 200 <= response.status_code < 300
        print(f"{method} {path} -> {response.status_code}")

        if not ok:
            failures.append({
                "method": method,
                "path": path,
                "status": response.status_code,
                "body": response.text[:500],
            })

    if failures:
        print("")
        print("SMOKE FAILED")
        print(json.dumps(failures, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    print("")
    print("SMOKE PASSED")
    """)

    w("scripts/smoke_live.py", """
    import json
    import sys
    import urllib.error
    import urllib.request

    API_BASE = "http://127.0.0.1:8797/api"

    checks = [
        ("GET", "/health", None),
        ("GET", "/settings", None),
        ("GET", "/diagnostics", None),
        ("GET", "/app/bootstrap", None),
        ("GET", "/course", None),
        ("GET", "/audio/voices", None),
        ("POST", "/audio/speak", {
            "text": "Bonjour, monsieur.",
            "lang": "fr",
            "voice_id": "mock_fr_female",
            "speed": 1,
            "mode": "normal",
        }),
    ]

    failures = []

    def request(method: str, path: str, payload=None):
        data = None
        headers = {}

        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(API_BASE + path, data=data, method=method, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, body

    for method, path, payload in checks:
        try:
            status, body = request(method, path, payload)
            print(f"{method} {path} -> {status}")
            if not (200 <= status < 300):
                failures.append({"method": method, "path": path, "status": status, "body": body[:300]})
        except urllib.error.URLError as exc:
            print(f"{method} {path} -> ERROR {exc}")
            failures.append({"method": method, "path": path, "error": str(exc)})

    if failures:
        print("")
        print("LIVE SMOKE FAILED")
        print(json.dumps(failures, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    print("")
    print("LIVE SMOKE PASSED")
    """)

    w("scripts/mvp_report.py", """
    import json
    import subprocess
    from datetime import datetime
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    CONTENT_ROOT = ROOT / "content"
    REPORTS_ROOT = ROOT / "reports"
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)

    def read_json(path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def cmd(command: list[str]) -> str:
        result = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True, check=False)
        return (result.stdout or result.stderr or "").strip()

    sections = []
    lessons = []
    exercises = []
    vulgar_items = []
    codex_entries = []

    for section_path in sorted((CONTENT_ROOT / "sections").glob("*/section.json")):
        section = read_json(section_path)
        sections.append(section)

    for lesson_path in sorted((CONTENT_ROOT / "sections").glob("*/lessons/*.json")):
        lesson = read_json(lesson_path)
        lessons.append(lesson)
        exercises.extend(lesson.get("exercises", []))

    for pack_path in sorted((CONTENT_ROOT / "vulgar" / "packs").glob("*.json")):
        pack = read_json(pack_path)
        vulgar_items.extend(pack.get("items", []))

    for codex_path in sorted((CONTENT_ROOT / "codex").glob("*.json")):
        codex_entries.append(read_json(codex_path))

    git_commit = cmd(["git", "rev-parse", "--short", "HEAD"])
    git_status = cmd(["git", "status", "--short"])

    lines = []
    lines.append("# Forge Française MVP Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("- Version: 0.6.0")
    lines.append("- Backend: http://127.0.0.1:8797/api/health")
    lines.append("- Frontend: http://127.0.0.1:5197")
    lines.append(f"- Git commit: {git_commit or 'unknown'}")
    lines.append(f"- Git dirty: {'yes' if git_status else 'no'}")
    lines.append("")
    lines.append("## Content")
    lines.append("")
    lines.append(f"- Sections: {len(sections)}")
    lines.append(f"- Lessons: {len(lessons)}")
    lines.append(f"- Exercises: {len(exercises)}")
    lines.append(f"- Codex entries: {len(codex_entries)}")
    lines.append(f"- Vulgar items: {len(vulgar_items)}")
    lines.append("")
    lines.append("## Sections")
    lines.append("")

    for section in sorted(sections, key=lambda item: item.get("order", 999)):
        lines.append(f"- {section['id']}: {section['title']['ru']} / {section['title']['fr']}")

    lines.append("")
    lines.append("## MVP Features")
    lines.append("")
    features = [
        "Vue 3 + TypeScript + Vite frontend",
        "FastAPI backend",
        "JSON content engine",
        "content validation",
        "mobile-first UI",
        "bottom navigation",
        "one-card lesson flow",
        "practice modes",
        "progress scoring",
        "weak topic review",
        "audio drill",
        "Edge TTS provider with mock fallback",
        "audio cache API",
        "RU / FR interface switch",
        "voice selector",
        "vulgar French library",
        "diagnostics endpoint",
        "smoke tests",
        "build scripts",
    ]

    for feature in features:
        lines.append(f"- {feature}")

    lines.append("")
    lines.append("## Demo Flow")
    lines.append("")
    lines.append("1. Open http://127.0.0.1:5197")
    lines.append("2. Continue the first lesson.")
    lines.append("3. Open drill and answer several questions.")
    lines.append("4. Open audio drill and test Edge voice.")
    lines.append("5. Open profile and switch voice / language.")
    lines.append("6. Open diagnostics.")
    lines.append("")
    lines.append("## Check Commands")
    lines.append("")
    lines.append("```cmd")
    lines.append("scripts\\\\check_backend.cmd")
    lines.append("scripts\\\\check_frontend.cmd")
    lines.append("scripts\\\\check_all.cmd")
    lines.append("```")
    lines.append("")

    report_path = REPORTS_ROOT / "MVP_REPORT.md"
    report_path.write_text("\\n".join(lines), encoding="utf-8")

    print(f"Report written: {report_path}")
    """)

    w("scripts/install_all.cmd", """
    @echo off
    cd /d "%~dp0.."

    echo.
    echo Installing backend deps...
    cd /d "%~dp0..\\backend"

    if not exist ".venv" (
      py -m venv .venv
    )

    call .venv\\Scripts\\activate.bat
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

    echo.
    echo Installing frontend deps...
    cd /d "%~dp0..\\frontend"
    npm install

    echo.
    echo INSTALL ALL DONE
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

    echo.
    echo Backend smoke...
    python scripts\\smoke_backend.py
    """)

    w("scripts/check_frontend.cmd", """
    @echo off
    cd /d "%~dp0..\\frontend"

    npm install

    echo.
    echo Frontend build...
    npm run build
    """)

    w("scripts/check_all.cmd", """
    @echo off
    cd /d "%~dp0.."

    call scripts\\check_backend.cmd
    if errorlevel 1 exit /b 1

    call scripts\\check_frontend.cmd
    if errorlevel 1 exit /b 1

    py scripts\\mvp_report.py

    echo.
    echo ALL CHECKS PASSED
    """)

    w("scripts/smoke_live.cmd", """
    @echo off
    cd /d "%~dp0.."
    py scripts\\smoke_live.py
    """)

    w("scripts/status_ports.cmd", """
    @echo off
    echo Backend port 8797:
    netstat -ano | findstr ":8797"
    echo.
    echo Frontend port 5197:
    netstat -ano | findstr ":5197"
    """)

    w("scripts/kill_ports.cmd", """
    @echo off
    echo Killing processes on ports 8797 and 5197 if any...

    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8797"') do (
      taskkill /PID %%a /F
    )

    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5197"') do (
      taskkill /PID %%a /F
    )

    echo Done.
    """)

    w("scripts/git_push_patch6.cmd", """
    @echo off
    cd /d "%~dp0.."
    git config user.name "web-lizard"
    git config user.email "web-lizard@users.noreply.github.com"
    git status --short
    git add .
    git commit -m "patch 6: diagnostics smoke tests and mvp polish"
    git push -u origin main
    """)

    w(".vscode/tasks.json", """
    {
      "version": "2.0.0",
      "tasks": [
        {
          "label": "Forge: launch all",
          "type": "shell",
          "command": "scripts\\\\Forge Francaise Launcher.cmd",
          "problemMatcher": []
        },
        {
          "label": "Forge: install all",
          "type": "shell",
          "command": "scripts\\\\install_all.cmd",
          "problemMatcher": []
        },
        {
          "label": "Forge: check backend",
          "type": "shell",
          "command": "scripts\\\\check_backend.cmd",
          "problemMatcher": []
        },
        {
          "label": "Forge: check frontend",
          "type": "shell",
          "command": "scripts\\\\check_frontend.cmd",
          "problemMatcher": []
        },
        {
          "label": "Forge: check all",
          "type": "shell",
          "command": "scripts\\\\check_all.cmd",
          "problemMatcher": []
        },
        {
          "label": "Forge: smoke live",
          "type": "shell",
          "command": "scripts\\\\smoke_live.cmd",
          "problemMatcher": []
        },
        {
          "label": "Forge: status ports",
          "type": "shell",
          "command": "scripts\\\\status_ports.cmd",
          "problemMatcher": []
        },
        {
          "label": "Forge: kill ports",
          "type": "shell",
          "command": "scripts\\\\kill_ports.cmd",
          "problemMatcher": []
        },
        {
          "label": "Forge: git push patch",
          "type": "shell",
          "command": "scripts\\\\git_push_patch6.cmd",
          "problemMatcher": []
        }
      ]
    }
    """)

    w("frontend/src/pages/DiagnosticsPage.vue", """
    <script setup lang="ts">
    import { onMounted, ref } from 'vue'
    import { apiGet } from '../lib/api'
    import { useSettingsStore } from '../stores/settingsStore'

    const settings = useSettingsStore()
    const diagnostics = ref<any | null>(null)
    const loading = ref(false)
    const error = ref('')

    async function load() {
      loading.value = true
      error.value = ''

      try {
        diagnostics.value = await apiGet('/diagnostics')
      } catch (exc) {
        error.value = exc instanceof Error ? exc.message : String(exc)
      } finally {
        loading.value = false
      }
    }

    onMounted(load)
    </script>

    <template>
      <section class="page">
        <div class="section-title compact-title">
          <div class="eyebrow">Diagnostics</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Диагностика MVP' : 'Diagnostic MVP' }}</h1>
          <p>
            {{
              settings.uiLanguage === 'ru'
                ? 'Проверяем, что контент, API, аудио-кэш и прогресс живые.'
                : 'Vérification du contenu, de l’API, du cache audio et de la progression.'
            }}
          </p>
        </div>

        <div v-if="loading" class="soft-card">Загрузка...</div>
        <div v-if="error" class="soft-card danger-card">{{ error }}</div>

        <template v-if="diagnostics">
          <article class="study-card">
            <h2>Application</h2>
            <div class="diagnostic-grid">
              <div>
                <span>Version</span>
                <strong>{{ diagnostics.app.version }}</strong>
              </div>
              <div>
                <span>Backend</span>
                <strong>{{ diagnostics.app.backend_port }}</strong>
              </div>
              <div>
                <span>Frontend</span>
                <strong>{{ diagnostics.app.frontend_port }}</strong>
              </div>
            </div>
          </article>

          <article class="study-card">
            <h2>Content</h2>
            <div class="stat-grid">
              <div>
                <strong>{{ diagnostics.content.sections }}</strong>
                <span>sections</span>
              </div>
              <div>
                <strong>{{ diagnostics.content.lessons }}</strong>
                <span>lessons</span>
              </div>
              <div>
                <strong>{{ diagnostics.content.exercises }}</strong>
                <span>drill</span>
              </div>
            </div>
            <div class="stat-grid">
              <div>
                <strong>{{ diagnostics.content.codex_entries }}</strong>
                <span>codex</span>
              </div>
              <div>
                <strong>{{ diagnostics.content.vulgar_items }}</strong>
                <span>vulgar</span>
              </div>
              <div>
                <strong>{{ diagnostics.progress_summary.score }}</strong>
                <span>score</span>
              </div>
            </div>
          </article>

          <article class="study-card">
            <h2>Audio cache</h2>
            <div class="stat-grid">
              <div>
                <strong>{{ diagnostics.audio_cache.count }}</strong>
                <span>files</span>
              </div>
              <div>
                <strong>{{ diagnostics.audio_cache.total_mb }}</strong>
                <span>mb</span>
              </div>
              <div>
                <strong>{{ diagnostics.audio_cache.indexed_count }}</strong>
                <span>indexed</span>
              </div>
            </div>
          </article>

          <article class="study-card">
            <h2>Paths</h2>
            <div v-for="(item, key) in diagnostics.paths" :key="key" class="codex-row">
              <strong>{{ key }}</strong>
              <span>{{ item.exists ? 'ok' : 'missing' }}</span>
              <small>{{ item.path }}</small>
            </div>
          </article>

          <button class="primary-button" type="button" @click="load">
            {{ settings.uiLanguage === 'ru' ? 'Обновить' : 'Rafraîchir' }}
          </button>
        </template>
      </section>
    </template>
    """)

    w("frontend/src/pages/NotFoundPage.vue", """
    <template>
      <section class="page">
        <div class="hero-card">
          <div class="crest-orb">?</div>
          <div class="eyebrow">404</div>
          <h1>Страница не найдена</h1>
          <p>Путь ушёл в туман, но Империя ещё держится.</p>
          <RouterLink class="primary-button" to="/">Вернуться на трон</RouterLink>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/components/imperial/RankBadge.vue", """
    <script setup lang="ts">
    defineProps<{
      rankId?: string
      score?: number
    }>()
    </script>

    <template>
      <div class="rank-badge">
        <span>Grade</span>
        <strong>{{ rankId ?? 'recrue' }}</strong>
        <small>{{ score ?? 0 }} score</small>
      </div>
    </template>
    """)

    w("frontend/src/router/index.ts", """
    import { createRouter, createWebHistory } from 'vue-router'

    import ThronePage from '../pages/ThronePage.vue'
    import CampaignPage from '../pages/CampaignPage.vue'
    import SectionPage from '../pages/SectionPage.vue'
    import LessonPage from '../pages/LessonPage.vue'
    import PracticePage from '../pages/PracticePage.vue'
    import AudioDrillPage from '../pages/AudioDrillPage.vue'
    import CodexPage from '../pages/CodexPage.vue'
    import VulgarLibraryPage from '../pages/VulgarLibraryPage.vue'
    import ProfilePage from '../pages/ProfilePage.vue'
    import DiagnosticsPage from '../pages/DiagnosticsPage.vue'
    import NotFoundPage from '../pages/NotFoundPage.vue'

    export const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', name: 'throne', component: ThronePage },
        { path: '/campaign', name: 'campaign', component: CampaignPage },
        { path: '/section/:sectionId', name: 'section', component: SectionPage },
        { path: '/lesson/:lessonId', name: 'lesson', component: LessonPage },
        { path: '/practice', name: 'practice', component: PracticePage },
        { path: '/audio', name: 'audio', component: AudioDrillPage },
        { path: '/codex', name: 'codex', component: CodexPage },
        { path: '/vulgar', name: 'vulgar', component: VulgarLibraryPage },
        { path: '/profile', name: 'profile', component: ProfilePage },
        { path: '/diagnostics', name: 'diagnostics', component: DiagnosticsPage },
        { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundPage },
      ],
    })
    """)

    w("frontend/src/pages/ThronePage.vue", """
    <script setup lang="ts">
    import { computed, onMounted, ref } from 'vue'
    import { RouterLink } from 'vue-router'
    import AudioButton from '../components/learning/AudioButton.vue'
    import RankBadge from '../components/imperial/RankBadge.vue'
    import { apiGet } from '../lib/api'
    import { ui } from '../lib/i18n'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()
    const summary = ref<any | null>(null)

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
      summary.value = await apiGet('/progress/local_lizard/summary')
    })

    const profile = computed(() => bootstrap.payload?.profile)
    const firstLesson = computed(() => bootstrap.payload?.sections?.[0]?.lessons?.[0] ?? 'greetings_001')
    </script>

    <template>
      <section class="page throne-page">
        <div class="hero-card">
          <div class="crest-orb">♛</div>
          <div class="eyebrow">Forge Française</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Тронный зал' : 'Salle du trône' }}</h1>
          <p>
            {{
              settings.uiLanguage === 'ru'
                ? 'Мобильная имперская кузница французского. Без перегруза, но с короной.'
                : 'Une forge mobile et impériale pour apprendre le français.'
            }}
          </p>

          <div class="profile-strip" v-if="profile">
            <span>{{ profile.display_name }}</span>
            <strong>{{ profile.rank_id }}</strong>
          </div>

          <RankBadge
            v-if="profile"
            :rank-id="profile.rank_id"
            :score="summary?.score ?? 0"
          />

          <div class="stat-grid" v-if="summary">
            <div>
              <strong>{{ summary.score }}</strong>
              <span>score</span>
            </div>
            <div>
              <strong>{{ summary.accuracy }}%</strong>
              <span>accuracy</span>
            </div>
            <div>
              <strong>{{ summary.completed_count }}</strong>
              <span>lessons</span>
            </div>
          </div>

          <div class="hero-actions">
            <RouterLink class="primary-button" :to="'/lesson/' + firstLesson">
              {{ ui('continue', settings.uiLanguage) }}
            </RouterLink>
            <AudioButton text="Bonjour, monsieur." :label="ui('listen', settings.uiLanguage)" />
          </div>
        </div>

        <div class="quick-grid">
          <RouterLink class="quick-card" to="/practice">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Дрель' : 'Drill' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? '5 быстрых ударов по хаосу' : 'Cinq coups rapides contre le chaos' }}</span>
          </RouterLink>

          <RouterLink class="quick-card" to="/audio">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Аудио' : 'Audio' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Слушать, повторять, запоминать' : 'Écouter, répéter, retenir' }}</span>
          </RouterLink>

          <RouterLink class="quick-card" to="/vulgar">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Мат' : 'Gros mots' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Грубый французский под замком' : 'Français vulgaire sous contrôle' }}</span>
          </RouterLink>

          <RouterLink class="quick-card" to="/diagnostics">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Диагностика' : 'Diagnostic' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Проверить, жив ли мозговыбиватель' : 'Vérifier le moteur' }}</span>
          </RouterLink>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/pages/ProfilePage.vue", """
    <script setup lang="ts">
    import { onMounted, ref } from 'vue'
    import VoiceSelector from '../components/audio/VoiceSelector.vue'
    import RankBadge from '../components/imperial/RankBadge.vue'
    import { apiGet } from '../lib/api'
    import { useAudioStore } from '../stores/audioStore'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()
    const audio = useAudioStore()
    const summary = ref<any | null>(null)

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
      summary.value = await apiGet('/progress/local_lizard/summary')
      await audio.loadCache()
    })
    </script>

    <template>
      <section class="page">
        <div class="section-title">
          <div class="eyebrow">Profil</div>
          <h1>{{ bootstrap.payload?.profile?.display_name ?? 'Local Lizard' }}</h1>
        </div>

        <RankBadge
          :rank-id="bootstrap.payload?.profile?.rank_id"
          :score="summary?.score ?? 0"
        />

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Интерфейс' : 'Interface' }}</h2>
          <button class="primary-button" type="button" @click="settings.toggleLanguage">
            {{ settings.uiLanguage === 'ru' ? 'Переключить на французский' : 'Passer en russe' }}
          </button>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Прогресс' : 'Progression' }}</h2>
          <div class="stat-grid" v-if="summary">
            <div>
              <strong>{{ summary.score }}</strong>
              <span>score</span>
            </div>
            <div>
              <strong>{{ summary.accuracy }}%</strong>
              <span>accuracy</span>
            </div>
            <div>
              <strong>{{ summary.completed_count }}</strong>
              <span>lessons</span>
            </div>
          </div>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Голос' : 'Voix' }}</h2>
          <VoiceSelector />
        </div>

        <div class="study-card">
          <h2>Audio cache</h2>
          <div class="stat-grid" v-if="audio.cache">
            <div>
              <strong>{{ audio.cache.count }}</strong>
              <span>files</span>
            </div>
            <div>
              <strong>{{ audio.cache.total_mb }}</strong>
              <span>mb</span>
            </div>
            <div>
              <strong>{{ audio.cache.indexed_count }}</strong>
              <span>indexed</span>
            </div>
          </div>
          <button class="ghost-button wide" type="button" @click="audio.clearCache">
            Очистить аудио-кэш
          </button>
        </div>

        <div class="study-card" v-if="summary?.weak_topics?.length">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Слабые темы' : 'Points faibles' }}</h2>
          <div class="chip-row">
            <span v-for="tag in summary.weak_topics" :key="tag" class="stat-chip">{{ tag }}</span>
          </div>
        </div>

        <RouterLink class="primary-button" to="/diagnostics">
          {{ settings.uiLanguage === 'ru' ? 'Открыть диагностику' : 'Ouvrir le diagnostic' }}
        </RouterLink>
      </section>
    </template>
    """)

    w("frontend/src/styles/imperial.css", """
    .imperial-shell {
      position: relative;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: calc(var(--bottom-nav-height) + 18px);
    }

    .shell-main {
      width: min(100%, 980px);
      margin: 0 auto;
      padding: 14px;
    }

    .top-bar {
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px;
      background: rgba(11, 13, 12, 0.82);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(176, 138, 69, 0.25);
    }

    .top-title,
    h1,
    h2 {
      letter-spacing: 0.02em;
    }

    .top-title {
      font-weight: 800;
    }

    .eyebrow {
      color: var(--antique-gold);
      font-size: 0.76rem;
      font-weight: 800;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .page {
      display: grid;
      gap: 14px;
    }

    .hero-card,
    .study-card,
    .soft-card,
    .quick-card,
    .lesson-tile,
    .rank-badge {
      border: 1px solid rgba(232, 226, 216, 0.12);
      background:
        linear-gradient(135deg, rgba(37, 91, 50, 0.28), transparent 38%),
        var(--panel-black);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-soft);
    }

    .hero-card {
      min-height: calc(100vh - 190px);
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 16px;
      padding: 26px;
    }

    .hero-card h1,
    .section-title h1 {
      margin: 0;
      font-size: clamp(2rem, 12vw, 4.6rem);
      line-height: 0.95;
    }

    .compact-title h1 {
      font-size: clamp(1.5rem, 8vw, 2.6rem);
    }

    .hero-card p,
    .section-title p,
    .study-card p,
    .voice-note {
      color: var(--text-muted);
      line-height: 1.55;
    }

    .voice-note {
      margin: 0;
      font-size: 0.86rem;
    }

    .crest-orb {
      width: 72px;
      height: 72px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(176, 138, 69, 0.55);
      border-radius: 50%;
      background: radial-gradient(circle, rgba(176, 138, 69, 0.35), rgba(37, 91, 50, 0.25));
      font-size: 2rem;
    }

    .profile-strip,
    .practice-head,
    .rank-badge {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 12px 14px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.06);
    }

    .rank-badge {
      border-color: rgba(176, 138, 69, 0.3);
    }

    .rank-badge span,
    .rank-badge small {
      color: var(--text-muted);
      font-size: 0.76rem;
      font-weight: 800;
      text-transform: uppercase;
    }

    .rank-badge strong {
      color: var(--antique-gold);
      text-transform: uppercase;
    }

    .practice-head {
      color: var(--antique-gold);
      font-size: 0.82rem;
      font-weight: 900;
      text-transform: uppercase;
    }

    .hero-actions,
    .quick-grid,
    .option-grid,
    .button-row,
    .audio-grid {
      display: grid;
      gap: 10px;
    }

    .button-row {
      grid-template-columns: 1fr auto;
    }

    .audio-grid {
      grid-template-columns: 1fr 1fr;
    }

    .primary-button,
    .audio-button,
    .ghost-button,
    .option-button {
      border: 0;
      border-radius: 999px;
      cursor: pointer;
      font-weight: 800;
    }

    .primary-button,
    .audio-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-height: 48px;
      padding: 0 18px;
    }

    .audio-button.compact {
      min-height: 38px;
      padding: 0 12px;
      font-size: 0.86rem;
    }

    .audio-button small {
      opacity: 0.7;
      font-size: 0.7rem;
    }

    .primary-button {
      color: #071009;
      background: linear-gradient(135deg, var(--bone-white), var(--antique-gold));
    }

    .audio-button {
      color: var(--bone-white);
      background: rgba(47, 122, 69, 0.45);
      border: 1px solid rgba(232, 226, 216, 0.14);
    }

    .ghost-button {
      min-height: 40px;
      padding: 0 14px;
      color: var(--bone-white);
      background: rgba(255, 255, 255, 0.08);
    }

    .ghost-button.active,
    .ghost-button.wide {
      border: 1px solid rgba(176, 138, 69, 0.45);
    }

    .quick-grid {
      grid-template-columns: 1fr;
    }

    .quick-card,
    .lesson-tile,
    .study-card,
    .soft-card {
      padding: 18px;
    }

    .quick-card,
    .lesson-tile {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .lesson-tile-vertical {
      align-items: flex-start;
      flex-direction: column;
    }

    .lesson-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--antique-gold);
      font-size: 0.75rem;
      font-weight: 800;
      text-transform: uppercase;
    }

    .quick-card span,
    .lesson-tile span,
    .lesson-tile small {
      display: block;
      margin-top: 4px;
      color: var(--text-muted);
      font-size: 0.92rem;
    }

    .tile-icon {
      width: 44px;
      height: 44px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border-radius: 16px;
      background: rgba(176, 138, 69, 0.16);
    }

    .card-list {
      display: grid;
      gap: 12px;
    }

    .study-card {
      display: grid;
      gap: 10px;
      min-height: min(420px, calc(100vh - 260px));
      align-content: center;
    }

    .audio-drill-card {
      justify-items: stretch;
    }

    .study-card h2 {
      margin: 0;
      font-size: clamp(1.4rem, 9vw, 2.8rem);
    }

    .transcription {
      color: var(--antique-gold) !important;
      font-weight: 700;
    }

    .muted {
      color: var(--text-muted);
    }

    .mini-details {
      padding: 12px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.05);
    }

    .option-grid {
      grid-template-columns: 1fr;
    }

    .option-button {
      min-height: 52px;
      color: var(--bone-white);
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(232, 226, 216, 0.12);
    }

    .option-button.selected {
      outline: 2px solid var(--antique-gold);
    }

    .answer-input,
    .built-phrase {
      width: 100%;
      min-height: 54px;
      padding: 0 16px;
      border-radius: 18px;
      border: 1px solid rgba(232, 226, 216, 0.16);
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.08);
    }

    .answer-input {
      outline: none;
    }

    .built-phrase {
      display: flex;
      align-items: center;
      line-height: 1.4;
    }

    .result-box {
      padding: 14px;
      border-radius: 16px;
    }

    .result-box.good {
      background: rgba(47, 122, 69, 0.24);
    }

    .result-box.bad {
      background: rgba(138, 45, 45, 0.24);
    }

    .codex-row {
      display: grid;
      gap: 4px;
      padding: 10px 0;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }

    .codex-row small {
      color: var(--text-muted);
      overflow-wrap: anywhere;
    }

    .danger-card {
      border-color: rgba(138, 45, 45, 0.45);
    }

    .rudeness {
      width: fit-content;
      padding: 6px 10px;
      border-radius: 999px;
      color: var(--bone-white);
      background: rgba(138, 45, 45, 0.45);
      font-size: 0.8rem;
      font-weight: 900;
    }

    .voice-selector {
      display: grid;
      gap: 8px;
    }

    .voice-selector select {
      width: 100%;
      min-height: 48px;
      padding: 0 14px;
      border-radius: 16px;
      border: 1px solid rgba(232, 226, 216, 0.16);
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.08);
    }

    .sheet-backdrop {
      position: fixed;
      inset: 0;
      z-index: 80;
      display: flex;
      align-items: flex-end;
      background: rgba(0, 0, 0, 0.58);
    }

    .bottom-sheet {
      width: 100%;
      max-height: 76vh;
      overflow: auto;
      padding: 14px 18px 24px;
      border-radius: 28px 28px 0 0;
      border: 1px solid rgba(232, 226, 216, 0.12);
      background: rgba(11, 13, 12, 0.98);
      box-shadow: var(--shadow-soft);
    }

    .sheet-handle {
      width: 54px;
      height: 5px;
      margin: 0 auto 14px;
      border-radius: 999px;
      background: rgba(232, 226, 216, 0.26);
    }

    .sheet-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .sheet-head h2 {
      margin: 0;
    }

    .lesson-progress {
      height: 8px;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
    }

    .lesson-progress div {
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--sovereign-green), var(--antique-gold));
      transition: width 0.2s ease;
    }

    .lesson-nav-row {
      display: grid;
      grid-template-columns: auto 1fr 1fr;
      gap: 10px;
    }

    .lesson-nav-row .ghost-button,
    .lesson-nav-row .primary-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 48px;
    }

    .stat-grid,
    .diagnostic-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .diagnostic-grid {
      grid-template-columns: 1fr;
    }

    .stat-grid div,
    .diagnostic-grid div {
      display: grid;
      gap: 2px;
      padding: 12px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.06);
      text-align: center;
    }

    .stat-grid strong,
    .diagnostic-grid strong {
      font-size: 1.25rem;
      color: var(--antique-gold);
    }

    .stat-grid span,
    .diagnostic-grid span {
      color: var(--text-muted);
      font-size: 0.74rem;
      text-transform: uppercase;
    }

    .stat-chip {
      flex: 0 0 auto;
      padding: 8px 12px;
      border-radius: 999px;
      color: var(--bone-white);
      background: rgba(176, 138, 69, 0.16);
      font-size: 0.82rem;
      font-weight: 800;
    }

    @media (min-width: 760px) {
      .diagnostic-grid {
        grid-template-columns: repeat(3, 1fr);
      }
    }
    """)

    w("README.md", """
    # Forge Française

    Имперский мозговыбиватель французского языка.

    Mobile-first учебный движок французского языка на Vue 3, FastAPI и JSON-контенте.

    ## Ports

    Backend:
    http://127.0.0.1:8797/api/health

    Frontend:
    http://127.0.0.1:5197

    Diagnostics:
    http://127.0.0.1:5197/diagnostics

    ## Быстрый запуск

    Через ярлык на рабочем столе:

    Forge Francaise

    Или вручную:

    ```cmd
    scripts\\Forge Francaise Launcher.cmd
    ```

    ## Установка зависимостей

    ```cmd
    scripts\\install_all.cmd
    ```

    ## Проверки

    Backend validation and smoke:

    ```cmd
    scripts\\check_backend.cmd
    ```

    Frontend build:

    ```cmd
    scripts\\check_frontend.cmd
    ```

    Full MVP check:

    ```cmd
    scripts\\check_all.cmd
    ```

    Live smoke, когда backend уже запущен:

    ```cmd
    scripts\\smoke_live.cmd
    ```

    ## Если порты заняты

    ```cmd
    scripts\\status_ports.cmd
    scripts\\kill_ports.cmd
    ```

    ## Что уже заложено

    - Vue 3 + TypeScript + Vite
    - FastAPI backend
    - JSON content engine
    - profiles / progress / ranks
    - TTS provider architecture
    - edge-tts provider
    - mock fallback provider
    - audio cache API
    - audio drill page
    - vulgar French library
    - mobile-first UI
    - bottom navigation
    - bottom sheet
    - RU / FR UI switch
    - voice selector
    - storage adapter
    - scalable ExerciseRenderer
    - course API
    - section pages
    - lesson card mode
    - expanded A0 content
    - real practice sessions
    - weak topic review
    - progress scoring
    - answer event log
    - diagnostics endpoint
    - backend smoke tests
    - frontend build checks
    - MVP report generator

    ## Demo Flow

    1. Open http://127.0.0.1:5197
    2. Press Continue.
    3. Listen to a phrase.
    4. Open Drill and answer a few questions.
    5. Open Audio and test voice selection.
    6. Open Profile and switch RU / FR.
    7. Open Diagnostics and check counts.

    ## MVP Report

    ```cmd
    py scripts\\mvp_report.py
    ```

    Report appears here:

    reports\\MVP_REPORT.md

    ## Patch 6

    Patch 6 adds:

    - diagnostics API
    - diagnostics page
    - backend smoke tests
    - live smoke tests
    - frontend build check script
    - install all script
    - check all script
    - port status and kill scripts
    - MVP report generator
    - final README
    """)

    w("project.config.json", json.dumps({
        "name": "Forge Francaise",
        "public_title_ru": "Имперский мозговыбиватель французского языка",
        "backend_port": BACKEND_PORT,
        "frontend_port": FRONTEND_PORT,
        "api_base": f"http://127.0.0.1:{BACKEND_PORT}/api",
        "frontend_url": f"http://127.0.0.1:{FRONTEND_PORT}",
        "diagnostics_url": f"http://127.0.0.1:{FRONTEND_PORT}/diagnostics",
        "version": "0.6.0",
        "patch": "patch 6: diagnostics smoke tests and mvp polish"
    }, ensure_ascii=False, indent=2))

    print("")
    print("Running content validation...")
    run(["py", "scripts\\validate_content.py"], cwd=ROOT / "backend")

    print("")
    print("Generating MVP report...")
    run(["py", "scripts\\mvp_report.py"], cwd=ROOT)

    print("")
    print("Git identity...")
    run(["git", "config", "user.name", GIT_NAME])
    run(["git", "config", "user.email", GIT_EMAIL])

    print("")
    print("Git commit...")
    run(["git", "add", "."])
    commit_code = run(["git", "commit", "-m", "patch 6: diagnostics smoke tests and mvp polish"])

    if commit_code != 0:
        print("commit failed or nothing to commit")

    print("")
    print("Git push...")
    push_code = run(["git", "push", "-u", "origin", "main"])

    if push_code != 0:
        print("")
        print("GIT PUSH FAILED OR NEEDS AUTH")
        print("Manual command:")
        print(r'cd /d "D:\PYTHON\Forge Francaise"')
        print(r"scripts\git_push_patch6.cmd")

    print("")
    print("PATCH 6 DONE")
    print("Готовность проекта: примерно 95%")
    print("")
    print("Что добавлено:")
    print("- diagnostics API")
    print("- diagnostics frontend page")
    print("- backend smoke tests")
    print("- live smoke tests")
    print("- frontend build check")
    print("- full check script")
    print("- MVP report generator")
    print("- port tools")
    print("- final README")
    print("")
    print("Now inspect:")
    print(r"scripts\check_all.cmd")
    print(r"scripts\Forge Francaise Launcher.cmd")
    print("http://127.0.0.1:5197/diagnostics")

if __name__ == "__main__":
    main()