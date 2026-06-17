from pathlib import Path
import subprocess
import json
import os
import socket
import textwrap

ROOT = Path(r"D:\PYTHON\Forge Francaise")
REMOTE_URL = "https://github.com/web-lizard/Forge-Fran-aise.git"

BACKEND_PORT = 8797
FRONTEND_PORT = 5197
PREVIEW_PORT = 4197

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

def run(cmd: list[str], cwd: Path = ROOT, check: bool = False) -> int:
    print("")
    print("RUN:", " ".join(cmd))
    try:
        result = subprocess.run(cmd, cwd=str(cwd), check=check)
        return result.returncode
    except FileNotFoundError:
        print(f"skip, command not found: {' '.join(cmd)}")
        return 127
    except subprocess.CalledProcessError as exc:
        print(f"command failed: {' '.join(cmd)}")
        print(f"exit code: {exc.returncode}")
        return exc.returncode

def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.35)
        return sock.connect_ex(("127.0.0.1", port)) != 0

def create_desktop_shortcut() -> None:
    desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
    shortcut_path = desktop / "Forge Francaise.lnk"
    launcher_path = ROOT / "scripts" / "Forge Francaise Launcher.cmd"

    ps = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{launcher_path}"
$Shortcut.WorkingDirectory = "{ROOT}"
$Shortcut.IconLocation = "$env:SystemRoot\\System32\\SHELL32.dll,44"
$Shortcut.Description = "Forge Francaise launcher"
$Shortcut.Save()
'''

    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        cwd=str(ROOT),
        check=False,
    )

    if shortcut_path.exists():
        print(f"desktop shortcut ok: {shortcut_path}")
    else:
        print("desktop shortcut was not created, launcher file still exists")

def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Project directory not found: {ROOT}")

    print("Forge Francaise patch 2")
    print(f"root: {ROOT}")
    print(f"backend port: {BACKEND_PORT}")
    print(f"frontend port: {FRONTEND_PORT}")
    print("")

    for port, label in [(BACKEND_PORT, "backend"), (FRONTEND_PORT, "frontend"), (PREVIEW_PORT, "preview")]:
        if port_is_free(port):
            print(f"port ok: {label} {port}")
        else:
            print(f"WARNING: port busy: {label} {port}")

    for rel in [
        ".vscode",
        "backend/app/api",
        "backend/app/storage",
        "backend/app/services",
        "backend/app/models",
        "frontend/src/components/layout",
        "frontend/src/components/learning",
        "frontend/src/components/audio",
        "frontend/src/components/imperial",
        "frontend/src/components/practice",
        "frontend/src/stores",
        "frontend/src/styles",
        "frontend/src/lib",
        "scripts",
    ]:
        mkdir(rel)

    w("project.config.json", json.dumps({
        "name": "Forge Francaise",
        "public_title_ru": "Имперский мозговыбиватель французского языка",
        "backend_port": BACKEND_PORT,
        "frontend_port": FRONTEND_PORT,
        "preview_port": PREVIEW_PORT,
        "api_base": f"http://127.0.0.1:{BACKEND_PORT}/api",
        "frontend_url": f"http://127.0.0.1:{FRONTEND_PORT}",
        "version": "0.2.0",
        "patch": "patch 2: ux infrastructure, settings, i18n, launcher"
    }, ensure_ascii=False, indent=2))

    w(".env.example", f"""
    VITE_API_BASE=http://127.0.0.1:{BACKEND_PORT}/api
    """)

    w("frontend/.env.local", f"""
    VITE_API_BASE=http://127.0.0.1:{BACKEND_PORT}/api
    """)

    w("scripts/dev_backend.cmd", f"""
    @echo off
    cd /d "%~dp0..\\backend"

    if not exist ".venv" (
      py -m venv .venv
    )

    call .venv\\Scripts\\activate.bat
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port {BACKEND_PORT}
    """)

    w("scripts/dev_frontend.cmd", f"""
    @echo off
    cd /d "%~dp0..\\frontend"

    if not exist ".env.local" (
      echo VITE_API_BASE=http://127.0.0.1:{BACKEND_PORT}/api> .env.local
    )

    npm install
    npm run dev -- --host 127.0.0.1 --port {FRONTEND_PORT}
    """)

    w("scripts/validate_content.cmd", """
    @echo off
    cd /d "%~dp0..\\backend"
    py scripts\\validate_content.py
    """)

    w("scripts/Forge Francaise Launcher.cmd", f"""
    @echo off
    title Forge Francaise Launcher
    cd /d "{ROOT}"

    echo.
    echo ==========================================
    echo  Forge Francaise
    echo  Backend:  http://127.0.0.1:{BACKEND_PORT}/api/health
    echo  Frontend: http://127.0.0.1:{FRONTEND_PORT}
    echo ==========================================
    echo.

    start "Forge Backend {BACKEND_PORT}" cmd /k scripts\\dev_backend.cmd
    timeout /t 4 /nobreak >nul
    start "Forge Frontend {FRONTEND_PORT}" cmd /k scripts\\dev_frontend.cmd
    timeout /t 7 /nobreak >nul
    start "" "http://127.0.0.1:{FRONTEND_PORT}"
    """)

    w("scripts/open_urls.cmd", f"""
    @echo off
    start "" "http://127.0.0.1:{FRONTEND_PORT}"
    start "" "http://127.0.0.1:{BACKEND_PORT}/api/health"
    """)

    w("scripts/git_push_patch2.cmd", """
    @echo off
    cd /d "%~dp0.."
    git status --short
    git add .
    git commit -m "patch 2: ux settings launcher and scalable frontend"
    git push -u origin main
    """)

    w(".vscode/settings.json", f"""
    {{
      "python.defaultInterpreterPath": "backend/.venv/Scripts/python.exe",
      "typescript.tsdk": "frontend/node_modules/typescript/lib",
      "terminal.integrated.defaultProfile.windows": "Command Prompt",
      "forgeFrancaise.backendPort": {BACKEND_PORT},
      "forgeFrancaise.frontendPort": {FRONTEND_PORT}
    }}
    """)

    w(".vscode/tasks.json", f"""
    {{
      "version": "2.0.0",
      "tasks": [
        {{
          "label": "Forge: validate content",
          "type": "shell",
          "command": "scripts\\\\validate_content.cmd",
          "problemMatcher": []
        }},
        {{
          "label": "Forge: backend {BACKEND_PORT}",
          "type": "shell",
          "command": "scripts\\\\dev_backend.cmd",
          "problemMatcher": []
        }},
        {{
          "label": "Forge: frontend {FRONTEND_PORT}",
          "type": "shell",
          "command": "scripts\\\\dev_frontend.cmd",
          "problemMatcher": []
        }},
        {{
          "label": "Forge: launch all",
          "type": "shell",
          "command": "scripts\\\\Forge Francaise Launcher.cmd",
          "problemMatcher": []
        }},
        {{
          "label": "Forge: git push patch",
          "type": "shell",
          "command": "scripts\\\\git_push_patch2.cmd",
          "problemMatcher": []
        }}
      ]
    }}
    """)

    w("backend/app/main.py", """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from app.api import audio, bootstrap, codex, health, lessons, practice, profiles, progress, sections, settings, vulgar

    app = FastAPI(
        title="Forge Française API",
        description="Imperial French learning engine",
        version="0.2.0",
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
    app.include_router(bootstrap.router, prefix="/api")
    app.include_router(sections.router, prefix="/api")
    app.include_router(lessons.router, prefix="/api")
    app.include_router(practice.router, prefix="/api")
    app.include_router(progress.router, prefix="/api")
    app.include_router(profiles.router, prefix="/api")
    app.include_router(audio.router, prefix="/api")
    app.include_router(codex.router, prefix="/api")
    app.include_router(vulgar.router, prefix="/api")
    """)

    w("backend/app/core/config.py", f"""
    from pydantic import BaseModel


    class AppConfig(BaseModel):
        app_name: str = "Forge Francaise"
        public_title_ru: str = "Имперский мозговыбиватель французского языка"
        version: str = "0.2.0"
        backend_port: int = {BACKEND_PORT}
        frontend_port: int = {FRONTEND_PORT}
        default_ui_language: str = "ru"
        learning_language: str = "fr"
        vulgar_library_enabled_by_default: bool = True
        tts_engine: str = "mock"


    config = AppConfig()
    """)

    w("backend/app/models/settings.py", """
    from pydantic import BaseModel


    class AppSettings(BaseModel):
        app_name: str
        public_title_ru: str
        version: str
        backend_port: int
        frontend_port: int
        default_ui_language: str
        learning_language: str
        vulgar_library_enabled_by_default: bool
        tts_engine: str
    """)

    w("backend/app/api/settings.py", """
    from fastapi import APIRouter

    from app.core.config import config

    router = APIRouter(tags=["settings"])


    @router.get("/settings")
    def get_settings():
        return config.model_dump()
    """)

    w("backend/app/storage/base.py", """
    from abc import ABC, abstractmethod
    from typing import Any


    class StorageAdapter(ABC):
        @abstractmethod
        def read(self, key: str, default: Any = None) -> Any:
            raise NotImplementedError

        @abstractmethod
        def write(self, key: str, payload: Any) -> None:
            raise NotImplementedError

        @abstractmethod
        def exists(self, key: str) -> bool:
            raise NotImplementedError
    """)

    w("backend/app/storage/json_storage.py", """
    from pathlib import Path
    from typing import Any

    from app.core.json_utils import read_json, write_json_atomic
    from app.storage.base import StorageAdapter


    class JsonStorage(StorageAdapter):
        def __init__(self, root: Path) -> None:
            self.root = root

        def path_for(self, key: str) -> Path:
            safe_key = key.strip().replace("\\\\", "/").strip("/")
            return self.root / f"{safe_key}.json"

        def read(self, key: str, default: Any = None) -> Any:
            path = self.path_for(key)
            if not path.exists():
                return default
            return read_json(path)

        def write(self, key: str, payload: Any) -> None:
            write_json_atomic(self.path_for(key), payload)

        def exists(self, key: str) -> bool:
            return self.path_for(key).exists()
    """)

    w("backend/app/services/settings_service.py", """
    from app.core.config import config


    class SettingsService:
        def app_settings(self) -> dict:
            return config.model_dump()


    def get_settings_service() -> SettingsService:
        return SettingsService()
    """)

    w("backend/app/services/profile_service.py", """
    from datetime import datetime, timezone
    from typing import Any

    from app.core.json_utils import read_json, write_json_atomic
    from app.core.paths import DATA_ROOT

    PROFILES_PATH = DATA_ROOT / "profiles.json"


    class ProfileService:
        def ensure_profiles(self) -> None:
            if PROFILES_PATH.exists():
                return

            payload = {
                "active_profile_id": "local_lizard",
                "profiles": [
                    {
                        "id": "local_lizard",
                        "display_name": "Monsieur Souveraineté",
                        "ui_language": "ru",
                        "learning_language": "fr",
                        "voice_id": "mock_fr_female",
                        "rank_id": "recrue",
                        "vulgar_library_enabled": True,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            }

            write_json_atomic(PROFILES_PATH, payload)

        def payload(self) -> dict[str, Any]:
            self.ensure_profiles()
            return read_json(PROFILES_PATH)

        def save_payload(self, payload: dict[str, Any]) -> None:
            write_json_atomic(PROFILES_PATH, payload)

        def list_profiles(self) -> list[dict[str, Any]]:
            return self.payload()["profiles"]

        def active_profile(self) -> dict[str, Any]:
            payload = self.payload()
            active_id = payload["active_profile_id"]
            return next(profile for profile in payload["profiles"] if profile["id"] == active_id)

        def update_profile(self, profile_id: str, patch: dict[str, Any]) -> dict[str, Any]:
            payload = self.payload()
            profiles = payload["profiles"]

            for index, profile in enumerate(profiles):
                if profile["id"] == profile_id:
                    merged = {**profile, **patch}
                    profiles[index] = merged
                    self.save_payload(payload)
                    return merged

            raise KeyError(f"Profile not found: {profile_id}")


    def get_profile_service() -> ProfileService:
        return ProfileService()
    """)

    w("backend/app/api/profiles.py", """
    from typing import Any

    from fastapi import APIRouter, HTTPException

    from app.services.profile_service import get_profile_service

    router = APIRouter(tags=["profiles"])


    @router.get("/profiles")
    def list_profiles():
        return get_profile_service().list_profiles()


    @router.get("/profiles/active")
    def active_profile():
        return get_profile_service().active_profile()


    @router.patch("/profiles/{profile_id}")
    def update_profile(profile_id: str, patch: dict[str, Any]):
        try:
            return get_profile_service().update_profile(profile_id, patch)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error))
    """)

    w("backend/scripts/validate_content.py", """
    import json
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[2]
    CONTENT_ROOT = ROOT / "content"

    errors: list[str] = []


    def read_json(path: Path):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Cannot read {path}: {exc}")
            return None


    def require_localized(obj: dict, field: str, path: Path) -> None:
        value = obj.get(field)
        if not isinstance(value, dict):
            errors.append(f"{path}: {field} must be localized object")
            return
        for lang in ["ru", "fr"]:
            if not value.get(lang):
                errors.append(f"{path}: {field}.{lang} is required")


    section_ids: set[str] = set()
    lesson_ids: set[str] = set()
    exercise_ids: set[str] = set()

    for section_path in sorted((CONTENT_ROOT / "sections").glob("*/section.json")):
        section = read_json(section_path)
        if not section:
            continue

        section_id = section.get("id")

        if not section_id:
            errors.append(f"{section_path}: missing id")
        elif section_id in section_ids:
            errors.append(f"{section_path}: duplicated section id {section_id}")
        else:
            section_ids.add(section_id)

        require_localized(section, "title", section_path)
        require_localized(section, "subtitle", section_path)

        if "order" not in section:
            errors.append(f"{section_path}: missing order")

        for lesson_id in section.get("lessons", []):
            lesson_file = next(CONTENT_ROOT.glob(f"sections/*/lessons/{lesson_id}.json"), None)
            if not lesson_file:
                errors.append(f"{section_path}: referenced lesson not found: {lesson_id}")

    for lesson_path in sorted((CONTENT_ROOT / "sections").glob("*/lessons/*.json")):
        lesson = read_json(lesson_path)
        if not lesson:
            continue

        lesson_id = lesson.get("id")

        if not lesson_id:
            errors.append(f"{lesson_path}: missing id")
        elif lesson_id in lesson_ids:
            errors.append(f"{lesson_path}: duplicated lesson id {lesson_id}")
        else:
            lesson_ids.add(lesson_id)

        if lesson.get("section_id") not in section_ids:
            errors.append(f"{lesson_path}: unknown section_id {lesson.get('section_id')}")

        require_localized(lesson, "title", lesson_path)

        for card in lesson.get("cards", []):
            card_type = card.get("type")
            if not card_type:
                errors.append(f"{lesson_path}: card without type")

            if card_type in ["word", "example"]:
                if not card.get("fr"):
                    errors.append(f"{lesson_path}: {card_type} card without fr")
                if not card.get("ru"):
                    errors.append(f"{lesson_path}: {card_type} card without ru")
                if not card.get("transcription"):
                    errors.append(f"{lesson_path}: {card_type} card without transcription")
                if not card.get("audio_text"):
                    errors.append(f"{lesson_path}: {card_type} card without audio_text")

        for exercise in lesson.get("exercises", []):
            exercise_id = exercise.get("id")

            if not exercise_id:
                errors.append(f"{lesson_path}: exercise without id")
            elif exercise_id in exercise_ids:
                errors.append(f"{lesson_path}: duplicated exercise id {exercise_id}")
            else:
                exercise_ids.add(exercise_id)

            if "answer" not in exercise:
                errors.append(f"{lesson_path}: exercise {exercise_id} has no answer")

            if "prompt" not in exercise:
                errors.append(f"{lesson_path}: exercise {exercise_id} has no prompt")
            else:
                require_localized(exercise, "prompt", lesson_path)

            if "explanation" not in exercise:
                errors.append(f"{lesson_path}: exercise {exercise_id} has no explanation")
            else:
                require_localized(exercise, "explanation", lesson_path)

    for pack_path in sorted((CONTENT_ROOT / "vulgar" / "packs").glob("*.json")):
        pack = read_json(pack_path)
        if not pack:
            continue

        require_localized(pack, "title", pack_path)

        for item in pack.get("items", []):
            for field in ["id", "fr", "transcription", "ru", "rudeness_level", "context", "audio_text"]:
                if field not in item:
                    errors.append(f"{pack_path}: vulgar item missing {field}: {item.get('id')}")

            if item.get("rudeness_level", 0) < 1 or item.get("rudeness_level", 0) > 5:
                errors.append(f"{pack_path}: invalid rudeness_level for {item.get('id')}")

    if errors:
        print("Content validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Content validation passed.")
    print(f"Sections: {len(section_ids)}")
    print(f"Lessons: {len(lesson_ids)}")
    print(f"Exercises: {len(exercise_ids)}")
    """)

    w("frontend/package.json", f"""
    {{
      "name": "forge-francaise",
      "private": true,
      "version": "0.2.0",
      "type": "module",
      "scripts": {{
        "dev": "vite --host 127.0.0.1 --port {FRONTEND_PORT}",
        "build": "vue-tsc --noEmit && vite build",
        "preview": "vite preview --host 127.0.0.1 --port {PREVIEW_PORT}"
      }},
      "dependencies": {{
        "pinia": "^2.1.7",
        "vue": "^3.4.0",
        "vue-router": "^4.3.0"
      }},
      "devDependencies": {{
        "@vitejs/plugin-vue": "^5.0.5",
        "typescript": "^5.4.0",
        "vite": "^5.2.0",
        "vue-tsc": "^2.0.0"
      }}
    }}
    """)

    w("frontend/src/stores/settingsStore.ts", """
    import { defineStore } from 'pinia'
    import { apiGet, apiPatch } from '../lib/api'
    import { useBootstrapStore } from './bootstrapStore'

    export type UiLanguage = 'ru' | 'fr'

    export const useSettingsStore = defineStore('settings', {
      state: () => ({
        uiLanguage: 'ru' as UiLanguage,
        voiceId: 'mock_fr_female',
        sheetOpen: false,
        sheetTitle: '',
        sheetBody: '',
      }),
      getters: {
        isFrenchUi: (state) => state.uiLanguage === 'fr',
      },
      actions: {
        hydrateFromBootstrap() {
          const bootstrap = useBootstrapStore()
          const profile = bootstrap.payload?.profile

          if (!profile) return

          this.uiLanguage = profile.ui_language as UiLanguage
          this.voiceId = profile.voice_id
        },
        async toggleLanguage() {
          this.uiLanguage = this.uiLanguage === 'ru' ? 'fr' : 'ru'

          const bootstrap = useBootstrapStore()
          const profileId = bootstrap.payload?.profile?.id

          if (profileId) {
            await apiPatch(`/profiles/${profileId}`, {
              ui_language: this.uiLanguage,
            })

            if (bootstrap.payload?.profile) {
              bootstrap.payload.profile.ui_language = this.uiLanguage
            }
          }
        },
        async setVoice(voiceId: string) {
          this.voiceId = voiceId

          const bootstrap = useBootstrapStore()
          const profileId = bootstrap.payload?.profile?.id

          if (profileId) {
            await apiPatch(`/profiles/${profileId}`, {
              voice_id: voiceId,
            })

            if (bootstrap.payload?.profile) {
              bootstrap.payload.profile.voice_id = voiceId
            }
          }
        },
        openSheet(title: string, body: string) {
          this.sheetTitle = title
          this.sheetBody = body
          this.sheetOpen = true
        },
        closeSheet() {
          this.sheetOpen = false
        },
      },
    })
    """)

    w("frontend/src/lib/api.ts", """
    export const apiBase = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8797/api'

    export async function apiGet<T>(path: string): Promise<T> {
      const response = await fetch(apiBase + path)

      if (!response.ok) {
        throw new Error('GET ' + path + ' failed: ' + response.status)
      }

      return response.json()
    }

    export async function apiPost<T>(path: string, payload: unknown): Promise<T> {
      const response = await fetch(apiBase + path, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('POST ' + path + ' failed: ' + response.status)
      }

      return response.json()
    }

    export async function apiPatch<T>(path: string, payload: unknown): Promise<T> {
      const response = await fetch(apiBase + path, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('PATCH ' + path + ' failed: ' + response.status)
      }

      return response.json()
    }

    export function publicApiUrl(path: string): string {
      return apiBase.replace('/api', '') + path
    }
    """)

    w("frontend/src/lib/i18n.ts", """
    import type { LocalizedText } from '../stores/bootstrapStore'

    export function t(value: LocalizedText | undefined, lang: 'ru' | 'fr'): string {
      if (!value) return ''
      return value[lang] || value.ru || value.fr || ''
    }

    export function ui(label: string, lang: 'ru' | 'fr'): string {
      const dict: Record<string, Record<'ru' | 'fr', string>> = {
        throne: { ru: 'Трон', fr: 'Trône' },
        lessons: { ru: 'Уроки', fr: 'Leçons' },
        drill: { ru: 'Дрель', fr: 'Drill' },
        codex: { ru: 'Кодекс', fr: 'Codex' },
        profile: { ru: 'Профиль', fr: 'Profil' },
        continue: { ru: 'Продолжить', fr: 'Continuer' },
        listen: { ru: 'Слушать', fr: 'Écouter' },
        why: { ru: 'Почему?', fr: 'Pourquoi ?' },
        next: { ru: 'Дальше', fr: 'Suivant' },
        correct: { ru: 'Верно', fr: 'Correct' },
        wrong: { ru: 'Мимо', fr: 'Raté' },
      }

      return dict[label]?.[lang] ?? label
    }
    """)

    w("frontend/src/components/layout/BottomSheet.vue", """
    <script setup lang="ts">
    import { useSettingsStore } from '../../stores/settingsStore'

    const settings = useSettingsStore()
    </script>

    <template>
      <Teleport to="body">
        <div v-if="settings.sheetOpen" class="sheet-backdrop" @click="settings.closeSheet">
          <section class="bottom-sheet" @click.stop>
            <div class="sheet-handle"></div>
            <div class="sheet-head">
              <h2>{{ settings.sheetTitle }}</h2>
              <button class="ghost-button" type="button" @click="settings.closeSheet">×</button>
            </div>
            <p>{{ settings.sheetBody }}</p>
          </section>
        </div>
      </Teleport>
    </template>
    """)

    w("frontend/src/components/layout/ImperialShell.vue", """
    <script setup lang="ts">
    import BottomNav from './BottomNav.vue'
    import TopBar from './TopBar.vue'
    import BottomSheet from './BottomSheet.vue'
    </script>

    <template>
      <div class="imperial-shell">
        <div class="flying-layer" aria-hidden="true">
          <span>é</span>
          <span>ç</span>
          <span>à</span>
          <span>œ</span>
        </div>

        <TopBar />

        <main class="shell-main">
          <slot />
        </main>

        <BottomNav />
        <BottomSheet />
      </div>
    </template>
    """)

    w("frontend/src/components/layout/TopBar.vue", """
    <script setup lang="ts">
    import { onMounted } from 'vue'
    import { useBootstrapStore } from '../../stores/bootstrapStore'
    import { useSettingsStore } from '../../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
    })
    </script>

    <template>
      <header class="top-bar">
        <div>
          <div class="eyebrow">Forge Française</div>
          <div class="top-title">Имперский мозговыбиватель</div>
        </div>

        <button class="ghost-button" type="button" @click="settings.toggleLanguage">
          {{ settings.uiLanguage.toUpperCase() }}
        </button>
      </header>
    </template>
    """)

    w("frontend/src/components/layout/BottomNav.vue", """
    <script setup lang="ts">
    import { ui } from '../../lib/i18n'
    import { useSettingsStore } from '../../stores/settingsStore'

    const settings = useSettingsStore()
    </script>

    <template>
      <nav class="bottom-nav">
        <RouterLink to="/">{{ ui('throne', settings.uiLanguage) }}</RouterLink>
        <RouterLink to="/campaign">{{ ui('lessons', settings.uiLanguage) }}</RouterLink>
        <RouterLink to="/practice">{{ ui('drill', settings.uiLanguage) }}</RouterLink>
        <RouterLink to="/codex">{{ ui('codex', settings.uiLanguage) }}</RouterLink>
        <RouterLink to="/profile">{{ ui('profile', settings.uiLanguage) }}</RouterLink>
      </nav>
    </template>
    """)

    w("frontend/src/components/learning/AudioButton.vue", """
    <script setup lang="ts">
    import { ref } from 'vue'
    import { apiPost, publicApiUrl } from '../../lib/api'
    import { useSettingsStore } from '../../stores/settingsStore'

    const props = defineProps<{
      text: string
      label?: string
      mode?: string
    }>()

    const settings = useSettingsStore()
    const loading = ref(false)

    async function play() {
      loading.value = true

      try {
        const result = await apiPost<{ url: string }>('/audio/speak', {
          text: props.text,
          lang: 'fr',
          voice_id: settings.voiceId,
          speed: props.mode === 'slow' ? 0.75 : 1,
          mode: props.mode ?? 'normal',
        })

        const audio = new Audio(publicApiUrl(result.url))
        await audio.play()
      } finally {
        loading.value = false
      }
    }
    </script>

    <template>
      <button class="audio-button" type="button" :disabled="loading" @click="play">
        <span v-if="loading">...</span>
        <span v-else>▶</span>
        {{ label ?? 'Слушать' }}
      </button>
    </template>
    """)

    w("frontend/src/components/audio/VoiceSelector.vue", """
    <script setup lang="ts">
    import { computed } from 'vue'
    import { useBootstrapStore } from '../../stores/bootstrapStore'
    import { useSettingsStore } from '../../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()

    const voices = computed(() => bootstrap.payload?.voices ?? [])
    </script>

    <template>
      <div class="voice-selector">
        <label for="voice">Голос</label>
        <select id="voice" :value="settings.voiceId" @change="settings.setVoice(($event.target as HTMLSelectElement).value)">
          <option v-for="voice in voices" :key="voice.id" :value="voice.id">
            {{ voice.label }}
          </option>
        </select>
      </div>
    </template>
    """)

    w("frontend/src/components/practice/ExerciseRenderer.vue", """
    <script setup lang="ts">
    import { ref } from 'vue'
    import { apiPost } from '../../lib/api'
    import { t, ui } from '../../lib/i18n'
    import { useSettingsStore } from '../../stores/settingsStore'
    import AudioButton from '../learning/AudioButton.vue'

    const props = defineProps<{
      lessonId: string
      exercise: any
    }>()

    const settings = useSettingsStore()
    const selected = ref('')
    const result = ref<any | null>(null)
    const loading = ref(false)

    async function answer(value: string) {
      selected.value = value
      loading.value = true

      try {
        result.value = await apiPost('/practice/answer', {
          profile_id: 'local_lizard',
          lesson_id: props.lessonId,
          exercise_id: props.exercise.id,
          answer: value,
        })
      } finally {
        loading.value = false
      }
    }
    </script>

    <template>
      <div class="exercise-renderer">
        <h2>{{ t(exercise.prompt, settings.uiLanguage) }}</h2>

        <AudioButton
          v-if="exercise.audio_text"
          :text="exercise.audio_text"
          :label="ui('listen', settings.uiLanguage)"
        />

        <div class="option-grid">
          <button
            v-for="option in exercise.options"
            :key="option"
            class="option-button"
            :class="{ selected: selected === option }"
            type="button"
            :disabled="loading"
            @click="answer(option)"
          >
            {{ option }}
          </button>
        </div>

        <div v-if="result" class="result-box" :class="{ good: result.correct, bad: !result.correct }">
          <strong>{{ result.correct ? ui('correct', settings.uiLanguage) : ui('wrong', settings.uiLanguage) }}</strong>
          <p>{{ t(result.explanation, settings.uiLanguage) }}</p>
        </div>
      </div>
    </template>
    """)

    w("frontend/src/pages/PracticePage.vue", """
    <script setup lang="ts">
    import { computed, onMounted, ref } from 'vue'
    import { apiGet } from '../lib/api'
    import { useSettingsStore } from '../stores/settingsStore'
    import ExerciseRenderer from '../components/practice/ExerciseRenderer.vue'

    const settings = useSettingsStore()
    const lesson = ref<any | null>(null)

    const exercise = computed(() => lesson.value?.exercises?.[0] ?? null)

    onMounted(async () => {
      lesson.value = await apiGet<any>('/lessons/le_la_001')
    })
    </script>

    <template>
      <section class="page">
        <div class="section-title">
          <div class="eyebrow">Drill</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Один удар по хаосу' : 'Un coup contre le chaos' }}</h1>
        </div>

        <div v-if="lesson && exercise" class="study-card">
          <ExerciseRenderer :lesson-id="lesson.id" :exercise="exercise" />
        </div>
      </section>
    </template>
    """)

    w("frontend/src/pages/LessonPage.vue", """
    <script setup lang="ts">
    import { onMounted, ref, watch } from 'vue'
    import { useRoute } from 'vue-router'
    import AudioButton from '../components/learning/AudioButton.vue'
    import ExerciseRenderer from '../components/practice/ExerciseRenderer.vue'
    import { apiGet } from '../lib/api'
    import { t, ui } from '../lib/i18n'
    import { useSettingsStore } from '../stores/settingsStore'

    const route = useRoute()
    const settings = useSettingsStore()
    const lesson = ref<any | null>(null)
    const loading = ref(false)

    async function loadLesson() {
      loading.value = true
      lesson.value = await apiGet<any>('/lessons/' + route.params.lessonId)
      loading.value = false
    }

    function exerciseById(exerciseId: string) {
      return lesson.value?.exercises?.find((item: any) => item.id === exerciseId)
    }

    function explain(card: any) {
      const title = settings.uiLanguage === 'ru' ? 'Пояснение' : 'Explication'
      const body = card.tooltip
        ? t(card.tooltip, settings.uiLanguage)
        : settings.uiLanguage === 'ru'
          ? 'Подробный разбор будет добавлен в Кодекс.'
          : 'Une explication détaillée sera ajoutée au Codex.'

      settings.openSheet(title, body)
    }

    onMounted(loadLesson)
    watch(() => route.params.lessonId, loadLesson)
    </script>

    <template>
      <section class="page lesson-page">
        <div v-if="loading" class="soft-card">Загрузка...</div>

        <template v-if="lesson">
          <div class="section-title">
            <div class="eyebrow">{{ lesson.level }}</div>
            <h1>{{ t(lesson.title, settings.uiLanguage) }}</h1>
          </div>

          <article v-for="card in lesson.cards" :key="JSON.stringify(card)" class="study-card">
            <template v-if="card.type === 'theory'">
              <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Теория' : 'Théorie' }}</div>
              <h2>{{ t(card.title, settings.uiLanguage) }}</h2>
              <p>{{ t(card.body, settings.uiLanguage) }}</p>
              <button class="ghost-button wide" type="button" @click="settings.openSheet(t(card.title, settings.uiLanguage), t(card.body, settings.uiLanguage))">
                {{ ui('why', settings.uiLanguage) }}
              </button>
            </template>

            <template v-else-if="card.type === 'word'">
              <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Слово' : 'Mot' }}</div>
              <h2>{{ card.fr }}</h2>
              <p class="transcription">{{ card.transcription }}</p>
              <p>{{ card.ru }}</p>
              <div class="button-row">
                <AudioButton :text="card.audio_text" :label="ui('listen', settings.uiLanguage)" />
                <button class="ghost-button" type="button" @click="explain(card)">
                  ?
                </button>
              </div>
            </template>

            <template v-else-if="card.type === 'example'">
              <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Пример' : 'Exemple' }}</div>
              <h2>{{ card.fr }}</h2>
              <p class="transcription">{{ card.transcription }}</p>
              <p>{{ card.ru }}</p>
              <AudioButton :text="card.audio_text" :label="ui('listen', settings.uiLanguage)" />
            </template>

            <template v-else-if="card.type === 'exercise'">
              <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Упражнение' : 'Exercice' }}</div>
              <ExerciseRenderer
                v-if="exerciseById(card.exercise_id)"
                :lesson-id="lesson.id"
                :exercise="exerciseById(card.exercise_id)"
              />
            </template>
          </article>
        </template>
      </section>
    </template>
    """)

    w("frontend/src/pages/ThronePage.vue", """
    <script setup lang="ts">
    import { computed, onMounted } from 'vue'
    import { RouterLink } from 'vue-router'
    import AudioButton from '../components/learning/AudioButton.vue'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'
    import { ui } from '../lib/i18n'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
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

          <RouterLink class="quick-card" to="/vulgar">
            <strong>{{ settings.uiLanguage === 'ru' ? 'Мат' : 'Gros mots' }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Грубый французский под замком' : 'Français vulgaire sous contrôle' }}</span>
          </RouterLink>

          <RouterLink class="quick-card" to="/codex">
            <strong>{{ ui('codex', settings.uiLanguage) }}</strong>
            <span>{{ settings.uiLanguage === 'ru' ? 'Артикли, de и прочая магия' : 'Articles, de et autres mystères' }}</span>
          </RouterLink>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/pages/CampaignPage.vue", """
    <script setup lang="ts">
    import { onMounted } from 'vue'
    import { t } from '../lib/i18n'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
    })
    </script>

    <template>
      <section class="page">
        <div class="section-title">
          <div class="eyebrow">Campagne</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Учебные секции' : 'Sections' }}</h1>
        </div>

        <div class="card-list">
          <RouterLink
            v-for="section in bootstrap.payload?.sections ?? []"
            :key="section.id"
            class="lesson-tile"
            :to="section.id === 'vulgar_french' ? '/vulgar' : '/lesson/' + section.lessons[0]"
          >
            <div class="tile-icon">{{ section.icon }}</div>
            <div>
              <strong>{{ t(section.title, settings.uiLanguage) }}</strong>
              <span>{{ t(section.subtitle, settings.uiLanguage) }}</span>
            </div>
          </RouterLink>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/pages/ProfilePage.vue", """
    <script setup lang="ts">
    import { onMounted } from 'vue'
    import VoiceSelector from '../components/audio/VoiceSelector.vue'
    import { useBootstrapStore } from '../stores/bootstrapStore'
    import { useSettingsStore } from '../stores/settingsStore'

    const bootstrap = useBootstrapStore()
    const settings = useSettingsStore()

    onMounted(async () => {
      await bootstrap.load()
      settings.hydrateFromBootstrap()
    })
    </script>

    <template>
      <section class="page">
        <div class="section-title">
          <div class="eyebrow">Profil</div>
          <h1>{{ bootstrap.payload?.profile?.display_name ?? 'Local Lizard' }}</h1>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Интерфейс' : 'Interface' }}</h2>
          <button class="primary-button" type="button" @click="settings.toggleLanguage">
            {{ settings.uiLanguage === 'ru' ? 'Переключить на французский' : 'Passer en russe' }}
          </button>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Текущий ранг' : 'Grade actuel' }}</h2>
          <p>{{ bootstrap.payload?.profile?.rank_id }}</p>
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Голос' : 'Voix' }}</h2>
          <VoiceSelector />
        </div>

        <div class="study-card">
          <h2>{{ settings.uiLanguage === 'ru' ? 'Доступные голоса' : 'Voix disponibles' }}</h2>
          <div v-for="voice in bootstrap.payload?.voices ?? []" :key="voice.id" class="codex-row">
            <strong>{{ voice.label }}</strong>
            <span>{{ voice.engine }} / {{ voice.quality }}</span>
          </div>
        </div>
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
    .lesson-tile {
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

    .hero-card p,
    .section-title p,
    .study-card p {
      color: var(--text-muted);
      line-height: 1.55;
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

    .profile-strip {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 12px 14px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.06);
    }

    .hero-actions,
    .quick-grid,
    .option-grid,
    .button-row {
      display: grid;
      gap: 10px;
    }

    .button-row {
      grid-template-columns: 1fr auto;
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

    .ghost-button.wide {
      width: 100%;
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

    .quick-card span,
    .lesson-tile span {
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
    }

    .study-card h2 {
      margin: 0;
      font-size: clamp(1.4rem, 9vw, 2.8rem);
    }

    .transcription {
      color: var(--antique-gold) !important;
      font-weight: 700;
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
    """)

    w("README.md", f"""
    # Forge Française

    Имперский мозговыбиватель французского языка.

    Mobile-first учебный движок французского языка на Vue 3, FastAPI и JSON-контенте.

    ## Ports

    Backend:
    http://127.0.0.1:{BACKEND_PORT}/api/health

    Frontend:
    http://127.0.0.1:{FRONTEND_PORT}

    ## Быстрый запуск

    Через ярлык на рабочем столе:

    Forge Francaise

    Или вручную:

    scripts\\Forge Francaise Launcher.cmd

    ## Backend only

    scripts\\dev_backend.cmd

    ## Frontend only

    scripts\\dev_frontend.cmd

    ## Проверка контента

    scripts\\validate_content.cmd

    ## Git push

    scripts\\git_push_patch2.cmd

    ## Что заложено

    - Vue 3 + TypeScript + Vite
    - FastAPI backend
    - JSON content engine
    - profiles / progress / ranks
    - TTS provider architecture
    - audio cache
    - vulgar French library
    - mobile-first UI
    - bottom navigation
    - bottom sheet
    - RU / FR UI switch
    - voice selector
    - storage adapter
    - scalable ExerciseRenderer

    ## Patch 2

    Patch 2 adds:

    - unique ports: backend {BACKEND_PORT}, frontend {FRONTEND_PORT}
    - desktop launcher
    - VS Code tasks
    - settings endpoint
    - profile patch endpoint
    - frontend settings store
    - language switch
    - voice selector
    - bottom sheet
    - unified exercise renderer
    - stronger content validation
    """)

    create_desktop_shortcut()

    print("")
    print("Running content validation...")
    run(["py", "scripts\\validate_content.py"], cwd=ROOT / "backend")

    print("")
    print("Git setup...")
    run(["git", "init"])
    run(["git", "branch", "-M", "main"])

    remote_result = subprocess.run(
        ["git", "remote"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    remotes = remote_result.stdout.splitlines() if remote_result.returncode == 0 else []

    if "origin" in remotes:
        run(["git", "remote", "set-url", "origin", REMOTE_URL])
    else:
        run(["git", "remote", "add", "origin", REMOTE_URL])

    print("")
    print("Git commit...")
    run(["git", "add", "."])
    commit_code = run(["git", "commit", "-m", "patch 2: ux settings launcher and scalable frontend"])

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
        print(r"scripts\git_push_patch2.cmd")

    print("")
    print("PATCH 2 DONE")
    print("Готовность проекта: примерно 30%")
    print("")
    print("Что добавлено:")
    print(f"- backend port: {BACKEND_PORT}")
    print(f"- frontend port: {FRONTEND_PORT}")
    print("- desktop launcher")
    print("- VS Code tasks")
    print("- settings API")
    print("- profile patch API")
    print("- storage adapter")
    print("- RU / FR switch")
    print("- voice selector")
    print("- bottom sheet")
    print("- ExerciseRenderer")
    print("- stronger content validation")
    print("")
    print("Launch:")
    print(r'scripts\Forge Francaise Launcher.cmd')

if __name__ == "__main__":
    main()