from pathlib import Path
import subprocess
import json
import sys

ROOT = Path(r"D:\PYTHON\Forge Francaise")
REMOTE_URL = "https://github.com/web-lizard/Forge-Fran-aise.git"

def w(rel_path: str, content: str = "") -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n"), encoding="utf-8")
    print(f"written: {rel_path}")

def mkdir(rel_path: str) -> None:
    path = ROOT / rel_path
    path.mkdir(parents=True, exist_ok=True)
    print(f"dir: {rel_path}")

def run(cmd: list[str], cwd: Path = ROOT, check: bool = False) -> None:
    try:
        subprocess.run(cmd, cwd=str(cwd), check=check)
    except FileNotFoundError:
        print(f"skip, command not found: {' '.join(cmd)}")
    except subprocess.CalledProcessError as exc:
        print(f"command failed: {' '.join(cmd)}")
        print(f"exit code: {exc.returncode}")

def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    print(f"Forge Française patch 1 installer")
    print(f"target: {ROOT}")
    print("")

    dirs = [
        "backend/app/api",
        "backend/app/core",
        "backend/app/models",
        "backend/app/services",
        "backend/app/storage",
        "backend/app/tts",
        "backend/data/progress",
        "backend/data/events",
        "backend/data/audio_cache",
        "backend/scripts",
        "frontend/src/components/layout",
        "frontend/src/components/learning",
        "frontend/src/components/audio",
        "frontend/src/components/imperial",
        "frontend/src/pages",
        "frontend/src/router",
        "frontend/src/stores",
        "frontend/src/styles",
        "frontend/src/lib",
        "content/i18n",
        "content/ranks",
        "content/codex",
        "content/vulgar/packs",
        "content/sections/00_start/lessons",
        "content/sections/02_articles/lessons",
        "content/sections/03_de_du/lessons",
        "content/sections/07_vulgar_french/lessons",
        "scripts",
    ]

    for d in dirs:
        mkdir(d)

    for rel in [
        "backend/app/__init__.py",
        "backend/app/api/__init__.py",
        "backend/app/core/__init__.py",
        "backend/app/models/__init__.py",
        "backend/app/services/__init__.py",
        "backend/app/storage/__init__.py",
        "backend/app/tts/__init__.py",
        "backend/data/audio_cache/.gitkeep",
    ]:
        w(rel, "")

    w(".gitignore", r"""
# Python
__pycache__/
*.py[cod]
.venv/
.env
.pytest_cache/
.mypy_cache/

# Node
node_modules/
dist/
.vite/

# Runtime data
backend/data/audio_cache/*
!backend/data/audio_cache/.gitkeep
backend/data/events/*.jsonl
backend/data/progress/*.runtime.json

# OS / IDE
.DS_Store
Thumbs.db
.vscode/
.idea/
""")

    w(".env.example", r"""
VITE_API_BASE=http://127.0.0.1:8787/api
""")

    w("README.md", r"""
# Forge Française

Имперский мозговыбиватель французского языка.

Mobile-first учебный движок французского языка на Vue 3, FastAPI и JSON-контенте.

## Заложено в первом патче

- Vue 3 + TypeScript + Vite
- FastAPI backend
- JSON как база учебного контента
- профили
- прогресс
- ранги по мотивам французской армии эпохи Наполеона
- TTS-архитектура через провайдеры
- audio cache
- матная библиотека
- русский / французский интерфейс
- mobile-first UI
- нижняя навигация
- подсказки и шторки как UX-принцип

## Запуск backend

scripts\dev_backend.cmd

## Запуск frontend

scripts\dev_frontend.cmd

## Проверка контента

scripts\validate_content.cmd

## URL

Backend:
http://127.0.0.1:8787/api/health

Frontend:
http://127.0.0.1:5173
""")

    w("scripts/dev_backend.cmd", r"""
@echo off
cd /d "%~dp0..\backend"

if not exist ".venv" (
  py -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
""")

    w("scripts/dev_frontend.cmd", r"""
@echo off
cd /d "%~dp0..\frontend"
npm install
npm run dev
""")

    w("scripts/validate_content.cmd", r"""
@echo off
cd /d "%~dp0..\backend"
py scripts\validate_content.py
""")

    w("backend/requirements.txt", r"""
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
pydantic>=2.7.0
python-multipart>=0.0.9
""")

    w("backend/app/main.py", r"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audio, bootstrap, codex, health, lessons, practice, profiles, progress, sections, vulgar

app = FastAPI(
    title="Forge Française API",
    description="Imperial French learning engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
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

    w("backend/app/core/paths.py", r"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
CONTENT_ROOT = PROJECT_ROOT / "content"
DATA_ROOT = BACKEND_ROOT / "data"
AUDIO_CACHE_ROOT = DATA_ROOT / "audio_cache"
""")

    w("backend/app/core/json_utils.py", r"""
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
""")

    w("backend/app/models/audio.py", r"""
from pydantic import BaseModel, Field


class Voice(BaseModel):
    id: str
    label: str
    lang: str = "fr"
    engine: str
    quality: str = "mock"


class AudioRequest(BaseModel):
    text: str = Field(min_length=1)
    lang: str = "fr"
    voice_id: str = "mock_fr_female"
    speed: float = 1.0
    mode: str = "normal"


class AudioResponse(BaseModel):
    audio_id: str
    url: str
    cached: bool
    duration_ms: int
""")

    w("backend/app/models/practice.py", r"""
from typing import Any
from pydantic import BaseModel


class PracticeAnswerRequest(BaseModel):
    profile_id: str = "local_lizard"
    lesson_id: str
    exercise_id: str
    answer: Any


class PracticeAnswerResponse(BaseModel):
    correct: bool
    expected: Any
    explanation: dict[str, str]
""")

    w("backend/app/services/content_service.py", r"""
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.json_utils import read_json
from app.core.paths import CONTENT_ROOT


class ContentService:
    def __init__(self, content_root: Path = CONTENT_ROOT) -> None:
        self.content_root = content_root

    def list_sections(self) -> list[dict[str, Any]]:
        sections_root = self.content_root / "sections"
        sections: list[dict[str, Any]] = []

        for section_path in sorted(sections_root.glob("*/section.json")):
            sections.append(read_json(section_path))

        return sorted(sections, key=lambda item: item.get("order", 999))

    def get_section(self, section_id: str) -> dict[str, Any]:
        for section in self.list_sections():
            if section["id"] == section_id or section.get("slug") == section_id:
                return section
        raise KeyError(f"Section not found: {section_id}")

    def iter_lesson_files(self) -> list[Path]:
        return sorted(self.content_root.glob("sections/*/lessons/*.json"))

    def get_lesson(self, lesson_id: str) -> dict[str, Any]:
        for lesson_path in self.iter_lesson_files():
            lesson = read_json(lesson_path)
            if lesson.get("id") == lesson_id:
                return lesson
        raise KeyError(f"Lesson not found: {lesson_id}")

    def list_ranks(self) -> list[dict[str, Any]]:
        payload = read_json(self.content_root / "ranks" / "napoleonic_ranks.json")
        return payload["ranks"]

    def list_codex(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for entry_path in sorted((self.content_root / "codex").glob("*.json")):
            entries.append(read_json(entry_path))
        return entries

    def get_codex_entry(self, entry_id: str) -> dict[str, Any]:
        for entry in self.list_codex():
            if entry["id"] == entry_id:
                return entry
        raise KeyError(f"Codex entry not found: {entry_id}")

    def vulgar_index(self) -> dict[str, Any]:
        return read_json(self.content_root / "vulgar" / "index.json")

    def list_vulgar_items(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []

        for pack_path in sorted((self.content_root / "vulgar" / "packs").glob("*.json")):
            pack = read_json(pack_path)
            for item in pack.get("items", []):
                item = dict(item)
                item["pack_id"] = pack["id"]
                items.append(item)

        return items

    def get_vulgar_item(self, item_id: str) -> dict[str, Any]:
        for item in self.list_vulgar_items():
            if item["id"] == item_id:
                return item
        raise KeyError(f"Vulgar item not found: {item_id}")


@lru_cache(maxsize=1)
def get_content_service() -> ContentService:
    return ContentService()
""")

    w("backend/app/services/profile_service.py", r"""
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

    def list_profiles(self) -> list[dict[str, Any]]:
        return self.payload()["profiles"]

    def active_profile(self) -> dict[str, Any]:
        payload = self.payload()
        active_id = payload["active_profile_id"]
        return next(profile for profile in payload["profiles"] if profile["id"] == active_id)


def get_profile_service() -> ProfileService:
    return ProfileService()
""")

    w("backend/app/services/progress_service.py", r"""
from datetime import datetime, timezone
import json
from typing import Any

from app.core.json_utils import read_json, write_json_atomic
from app.core.paths import DATA_ROOT

PROGRESS_ROOT = DATA_ROOT / "progress"
EVENTS_ROOT = DATA_ROOT / "events"


class ProgressService:
    def progress_path(self, profile_id: str):
        return PROGRESS_ROOT / f"{profile_id}.json"

    def events_path(self, profile_id: str):
        return EVENTS_ROOT / f"{profile_id}.jsonl"

    def get_progress(self, profile_id: str) -> dict[str, Any]:
        path = self.progress_path(profile_id)

        if not path.exists():
            payload = {
                "profile_id": profile_id,
                "current_level": "A0",
                "completed_lessons": [],
                "lesson_progress": {},
                "weak_topics": [],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            write_json_atomic(path, payload)

        return read_json(path)

    def append_event(self, profile_id: str, event: dict[str, Any]) -> None:
        EVENTS_ROOT.mkdir(parents=True, exist_ok=True)
        event["ts"] = datetime.now(timezone.utc).isoformat()

        with self.events_path(profile_id).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def get_progress_service() -> ProgressService:
    return ProgressService()
""")

    w("backend/app/services/practice_service.py", r"""
from typing import Any

from app.services.content_service import get_content_service
from app.services.progress_service import get_progress_service


def normalize(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(item).strip() for item in value).strip().lower()
    return str(value).strip().lower()


class PracticeService:
    def check_answer(self, profile_id: str, lesson_id: str, exercise_id: str, answer: Any) -> dict[str, Any]:
        lesson = get_content_service().get_lesson(lesson_id)
        exercise = next((item for item in lesson.get("exercises", []) if item["id"] == exercise_id), None)

        if not exercise:
            raise KeyError(f"Exercise not found: {exercise_id}")

        expected = exercise.get("answer")
        correct = normalize(answer) == normalize(expected)

        get_progress_service().append_event(
            profile_id,
            {
                "event": "exercise_answered",
                "lesson_id": lesson_id,
                "exercise_id": exercise_id,
                "answer": answer,
                "expected": expected,
                "correct": correct,
                "tags": exercise.get("tags", []),
            },
        )

        return {
            "correct": correct,
            "expected": expected,
            "explanation": exercise.get("explanation", {"ru": "", "fr": ""}),
        }


def get_practice_service() -> PracticeService:
    return PracticeService()
""")

    w("backend/app/tts/base.py", r"""
from abc import ABC, abstractmethod
from pathlib import Path

from app.models.audio import AudioRequest, Voice


class TTSProvider(ABC):
    @abstractmethod
    def voices(self) -> list[Voice]:
        raise NotImplementedError

    @abstractmethod
    def synthesize(self, request: AudioRequest, output_path: Path) -> int:
        raise NotImplementedError
""")

    w("backend/app/tts/mock_provider.py", r"""
from pathlib import Path
import wave

from app.models.audio import AudioRequest, Voice
from app.tts.base import TTSProvider


class MockProvider(TTSProvider):
    def voices(self) -> list[Voice]:
        return [
            Voice(
                id="mock_fr_female",
                label="Voix impériale féminine, mock",
                engine="mock",
                quality="dev",
            ),
            Voice(
                id="mock_fr_male",
                label="Voix impériale masculine, mock",
                engine="mock",
                quality="dev",
            ),
        ]

    def synthesize(self, request: AudioRequest, output_path: Path) -> int:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        sample_rate = 16000
        duration_seconds = 0.45 if request.mode == "normal" else 0.75
        frame_count = int(sample_rate * duration_seconds)
        silence = b"\x00\x00" * frame_count

        with wave.open(str(output_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(silence)

        return int(duration_seconds * 1000)
""")

    w("backend/app/tts/piper_provider.py", r"""
from pathlib import Path

from app.models.audio import AudioRequest, Voice
from app.tts.base import TTSProvider


class PiperProvider(TTSProvider):
    def voices(self) -> list[Voice]:
        return []

    def synthesize(self, request: AudioRequest, output_path: Path) -> int:
        raise RuntimeError("PiperProvider is reserved for the next patch.")
""")

    w("backend/app/tts/kokoro_provider.py", r"""
from pathlib import Path

from app.models.audio import AudioRequest, Voice
from app.tts.base import TTSProvider


class KokoroProvider(TTSProvider):
    def voices(self) -> list[Voice]:
        return []

    def synthesize(self, request: AudioRequest, output_path: Path) -> int:
        raise RuntimeError("KokoroProvider is reserved for the next patch.")
""")

    w("backend/app/services/audio_service.py", r"""
import hashlib
import json

from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.core.paths import AUDIO_CACHE_ROOT
from app.models.audio import AudioRequest, AudioResponse, Voice
from app.tts.mock_provider import MockProvider


class AudioService:
    def __init__(self) -> None:
        self.provider = MockProvider()

    def voices(self) -> list[Voice]:
        return self.provider.voices()

    def audio_id(self, request: AudioRequest) -> str:
        payload = request.model_dump()
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def speak(self, request: AudioRequest) -> AudioResponse:
        audio_id = self.audio_id(request)
        output_path = AUDIO_CACHE_ROOT / f"{audio_id}.wav"
        cached = output_path.exists()

        if not cached:
            duration_ms = self.provider.synthesize(request, output_path)
        else:
            duration_ms = 450

        return AudioResponse(
            audio_id=audio_id,
            url=f"/api/audio/file/{audio_id}",
            cached=cached,
            duration_ms=duration_ms,
        )

    def file_response(self, audio_id: str) -> FileResponse:
        path = AUDIO_CACHE_ROOT / f"{audio_id}.wav"

        if not path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")

        return FileResponse(path, media_type="audio/wav", filename=f"{audio_id}.wav")


def get_audio_service() -> AudioService:
    return AudioService()
""")

    w("backend/app/api/health.py", r"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"ok": True, "app": "forge-francaise"}
""")

    w("backend/app/api/bootstrap.py", r"""
from fastapi import APIRouter

from app.services.audio_service import get_audio_service
from app.services.content_service import get_content_service
from app.services.profile_service import get_profile_service
from app.services.progress_service import get_progress_service

router = APIRouter(tags=["bootstrap"])


@router.get("/app/bootstrap")
def bootstrap():
    profile = get_profile_service().active_profile()

    return {
        "profile": profile,
        "progress": get_progress_service().get_progress(profile["id"]),
        "sections": get_content_service().list_sections(),
        "ranks": get_content_service().list_ranks(),
        "voices": [voice.model_dump() for voice in get_audio_service().voices()],
    }
""")

    w("backend/app/api/sections.py", r"""
from fastapi import APIRouter, HTTPException

from app.services.content_service import get_content_service

router = APIRouter(tags=["sections"])


@router.get("/sections")
def list_sections():
    return get_content_service().list_sections()


@router.get("/sections/{section_id}")
def get_section(section_id: str):
    try:
        return get_content_service().get_section(section_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
""")

    w("backend/app/api/lessons.py", r"""
from fastapi import APIRouter, HTTPException

from app.services.content_service import get_content_service

router = APIRouter(tags=["lessons"])


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: str):
    try:
        return get_content_service().get_lesson(lesson_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
""")

    w("backend/app/api/practice.py", r"""
from fastapi import APIRouter, HTTPException

from app.models.practice import PracticeAnswerRequest
from app.services.practice_service import get_practice_service

router = APIRouter(tags=["practice"])


@router.post("/practice/answer")
def answer(request: PracticeAnswerRequest):
    try:
        return get_practice_service().check_answer(
            profile_id=request.profile_id,
            lesson_id=request.lesson_id,
            exercise_id=request.exercise_id,
            answer=request.answer,
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
""")

    w("backend/app/api/progress.py", r"""
from fastapi import APIRouter

from app.services.progress_service import get_progress_service

router = APIRouter(tags=["progress"])


@router.get("/progress/{profile_id}")
def get_progress(profile_id: str):
    return get_progress_service().get_progress(profile_id)
""")

    w("backend/app/api/profiles.py", r"""
from fastapi import APIRouter

from app.services.profile_service import get_profile_service

router = APIRouter(tags=["profiles"])


@router.get("/profiles")
def list_profiles():
    return get_profile_service().list_profiles()
""")

    w("backend/app/api/audio.py", r"""
from fastapi import APIRouter

from app.models.audio import AudioRequest
from app.services.audio_service import get_audio_service

router = APIRouter(tags=["audio"])


@router.get("/audio/voices")
def voices():
    return [voice.model_dump() for voice in get_audio_service().voices()]


@router.post("/audio/speak")
def speak(request: AudioRequest):
    return get_audio_service().speak(request)


@router.get("/audio/file/{audio_id}")
def audio_file(audio_id: str):
    return get_audio_service().file_response(audio_id)
""")

    w("backend/app/api/codex.py", r"""
from fastapi import APIRouter, HTTPException

from app.services.content_service import get_content_service

router = APIRouter(tags=["codex"])


@router.get("/codex")
def list_codex():
    return get_content_service().list_codex()


@router.get("/codex/{entry_id}")
def get_codex_entry(entry_id: str):
    try:
        return get_content_service().get_codex_entry(entry_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
""")

    w("backend/app/api/vulgar.py", r"""
from fastapi import APIRouter, HTTPException

from app.services.content_service import get_content_service

router = APIRouter(tags=["vulgar"])


@router.get("/vulgar/categories")
def categories():
    return get_content_service().vulgar_index()


@router.get("/vulgar/items")
def items():
    return get_content_service().list_vulgar_items()


@router.get("/vulgar/items/{item_id}")
def item(item_id: str):
    try:
        return get_content_service().get_vulgar_item(item_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
""")

    w("backend/scripts/validate_content.py", r"""
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

for pack_path in sorted((CONTENT_ROOT / "vulgar" / "packs").glob("*.json")):
    pack = read_json(pack_path)
    if not pack:
        continue

    for item in pack.get("items", []):
        for field in ["id", "fr", "transcription", "ru", "rudeness_level", "context", "audio_text"]:
            if field not in item:
                errors.append(f"{pack_path}: vulgar item missing {field}: {item.get('id')}")

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

    w("content/index.json", r"""
{
  "app": "forge-francaise",
  "version": "0.1.0",
  "default_locale": "ru",
  "available_locales": ["ru", "fr"]
}
""")

    w("content/i18n/ru.json", r"""
{
  "throne": "Трон",
  "lessons": "Уроки",
  "practice": "Тренировка",
  "codex": "Кодекс",
  "profile": "Профиль",
  "continue": "Продолжить",
  "listen": "Слушать"
}
""")

    w("content/i18n/fr.json", r"""
{
  "throne": "Trône",
  "lessons": "Leçons",
  "practice": "Entraînement",
  "codex": "Codex",
  "profile": "Profil",
  "continue": "Continuer",
  "listen": "Écouter"
}
""")

    w("content/ranks/napoleonic_ranks.json", r"""
{
  "ranks": [
    {
      "id": "recrue",
      "order": 1,
      "fr": "Recrue",
      "transcription": "[рёкрю]",
      "ru": "новобранец",
      "min_score": 0
    },
    {
      "id": "soldat",
      "order": 2,
      "fr": "Soldat",
      "transcription": "[сольда]",
      "ru": "солдат",
      "min_score": 100
    },
    {
      "id": "caporal",
      "order": 3,
      "fr": "Caporal",
      "transcription": "[капораль]",
      "ru": "капрал",
      "min_score": 250
    },
    {
      "id": "sergent",
      "order": 4,
      "fr": "Sergent",
      "transcription": "[сэржан]",
      "ru": "сержант",
      "min_score": 500
    },
    {
      "id": "lieutenant",
      "order": 5,
      "fr": "Lieutenant",
      "transcription": "[льётнан]",
      "ru": "лейтенант",
      "min_score": 900
    },
    {
      "id": "capitaine",
      "order": 6,
      "fr": "Capitaine",
      "transcription": "[капитэн]",
      "ru": "капитан",
      "min_score": 1400
    },
    {
      "id": "chef_de_bataillon",
      "order": 7,
      "fr": "Chef de bataillon",
      "transcription": "[шеф дэ батайон]",
      "ru": "командир батальона",
      "min_score": 2200
    },
    {
      "id": "colonel",
      "order": 8,
      "fr": "Colonel",
      "transcription": "[колонэль]",
      "ru": "полковник",
      "min_score": 3200
    },
    {
      "id": "general_de_brigade",
      "order": 9,
      "fr": "Général de brigade",
      "transcription": "[женераль дэ бригад]",
      "ru": "бригадный генерал",
      "min_score": 4600
    },
    {
      "id": "marechal_de_l_empire",
      "order": 10,
      "fr": "Maréchal de l’Empire",
      "transcription": "[марэшаль дэ ланпир]",
      "ru": "маршал Империи",
      "min_score": 7000
    }
  ]
}
""")

    w("content/codex/articles.json", r"""
{
  "id": "articles",
  "title": {
    "ru": "Артикли",
    "fr": "Les articles"
  },
  "summary": {
    "ru": "Артикль показывает род, число и определённость существительного.",
    "fr": "L’article indique le genre, le nombre et le degré de précision du nom."
  },
  "items": [
    {
      "fr": "le",
      "transcription": "[лё]",
      "ru": "определённый артикль мужского рода"
    },
    {
      "fr": "la",
      "transcription": "[ля]",
      "ru": "определённый артикль женского рода"
    },
    {
      "fr": "les",
      "transcription": "[ле]",
      "ru": "определённый артикль множественного числа"
    }
  ]
}
""")

    w("content/codex/de.json", r"""
{
  "id": "de",
  "title": {
    "ru": "De, du, de la, des",
    "fr": "De, du, de la, des"
  },
  "summary": {
    "ru": "de может обозначать из, от, принадлежность, количество. du = de + le.",
    "fr": "de peut exprimer l’origine, la possession ou la quantité."
  },
  "items": [
    {
      "fr": "de",
      "transcription": "[дэ]",
      "ru": "из, от, принадлежность, количество"
    },
    {
      "fr": "du",
      "transcription": "[дю]",
      "ru": "de + le"
    },
    {
      "fr": "de la",
      "transcription": "[дэ ля]",
      "ru": "часть или неопределённое количество для женского рода"
    }
  ]
}
""")

    w("content/vulgar/index.json", r"""
{
  "title": {
    "ru": "Французский мат",
    "fr": "Les gros mots français"
  },
  "is_adult": true,
  "categories": [
    {
      "id": "anger_basic",
      "title": {
        "ru": "Базовая злость",
        "fr": "Colère de base"
      }
    },
    {
      "id": "go_away",
      "title": {
        "ru": "Как послать человека",
        "fr": "Envoyer quelqu’un balader"
      }
    }
  ]
}
""")

    w("content/vulgar/packs/anger_basic.json", r"""
{
  "id": "anger_basic",
  "title": {
    "ru": "Базовая злость",
    "fr": "Colère de base"
  },
  "items": [
    {
      "id": "putain_j_en_ai_marre",
      "fr": "Putain, j’en ai marre.",
      "transcription": "[пютэн, жанэ мар]",
      "ru": "Блядь, меня это достало.",
      "literal_ru": "Блядь, мне этого достаточно.",
      "register": "vulgar",
      "rudeness_level": 4,
      "danger_level": 3,
      "context": {
        "ru": "Грубо, эмоционально, но очень разговорно. Не для официальной ситуации.",
        "fr": "Vulgaire, très familier, à éviter dans un contexte formel."
      },
      "softer_versions": [
        {
          "fr": "J’en ai assez.",
          "transcription": "[жанэ асэ]",
          "ru": "Мне этого достаточно / я устал от этого."
        }
      ],
      "audio_text": "Putain, j’en ai marre.",
      "tags": ["vulgar", "anger", "basic"]
    },
    {
      "id": "vous_me_faites_tous_chier",
      "fr": "Vous me faites tous chier.",
      "transcription": "[ву мё фэт тус шье]",
      "ru": "Вы все меня заебали.",
      "literal_ru": "Вы все заставляете меня срать.",
      "register": "vulgar",
      "rudeness_level": 5,
      "danger_level": 4,
      "context": {
        "ru": "Очень грубо. Это уже прямое агрессивное высказывание.",
        "fr": "Très vulgaire et agressif."
      },
      "softer_versions": [
        {
          "fr": "Vous me fatiguez.",
          "transcription": "[ву мё фатигэ]",
          "ru": "Вы меня утомляете."
        }
      ],
      "audio_text": "Vous me faites tous chier.",
      "tags": ["vulgar", "anger", "group"]
    }
  ]
}
""")

    w("content/vulgar/packs/go_away.json", r"""
{
  "id": "go_away",
  "title": {
    "ru": "Как послать человека",
    "fr": "Envoyer quelqu’un balader"
  },
  "items": [
    {
      "id": "va_te_faire_foutre",
      "fr": "Va te faire foutre.",
      "transcription": "[ва тэ фэр футр]",
      "ru": "Пошёл ты нахуй.",
      "literal_ru": "Иди сделай так, чтобы тебя трахнули.",
      "register": "vulgar",
      "rudeness_level": 5,
      "danger_level": 5,
      "context": {
        "ru": "Очень грубо. Использовать только если действительно хочешь жёстко послать человека.",
        "fr": "Très vulgaire et très agressif."
      },
      "softer_versions": [
        {
          "fr": "Laisse-moi tranquille.",
          "transcription": "[лэс-муа транкиль]",
          "ru": "Оставь меня в покое."
        }
      ],
      "audio_text": "Va te faire foutre.",
      "tags": ["vulgar", "go_away", "direct"]
    },
    {
      "id": "allez_tous_vous_faire_foutre",
      "fr": "Allez tous vous faire foutre.",
      "transcription": "[але тус ву фэр футр]",
      "ru": "Идите вы все нахуй.",
      "literal_ru": "Идите все сделайте так, чтобы вас трахнули.",
      "register": "vulgar",
      "rudeness_level": 5,
      "danger_level": 5,
      "context": {
        "ru": "Грубое коллективное посылание. В живом конфликте может резко обострить ситуацию.",
        "fr": "Insulte collective très agressive."
      },
      "softer_versions": [
        {
          "fr": "Laissez-moi tranquille.",
          "transcription": "[лэсэ-муа транкиль]",
          "ru": "Оставьте меня в покое."
        }
      ],
      "audio_text": "Allez tous vous faire foutre.",
      "tags": ["vulgar", "go_away", "group"]
    }
  ]
}
""")

    w("content/sections/00_start/section.json", r"""
{
  "id": "start",
  "slug": "start",
  "order": 0,
  "icon": "crown",
  "title": {
    "ru": "Вход во французский",
    "fr": "Entrée dans le français"
  },
  "subtitle": {
    "ru": "Приветствия, вежливость и первые фразы.",
    "fr": "Salutations, politesse et premières phrases."
  },
  "level": "A0",
  "tone": "basic",
  "lessons": ["greetings_001"],
  "is_adult": false
}
""")

    w("content/sections/00_start/lessons/greetings_001.json", r"""
{
  "id": "greetings_001",
  "section_id": "start",
  "order": 1,
  "level": "A0",
  "title": {
    "ru": "Bonjour, merci и базовая вежливость",
    "fr": "Bonjour, merci et la politesse de base"
  },
  "cards": [
    {
      "type": "theory",
      "title": {
        "ru": "Первый принцип",
        "fr": "Premier principe"
      },
      "body": {
        "ru": "Сначала учим короткие живые фразы, которые можно сразу слушать и повторять.",
        "fr": "On commence par des phrases courtes, utiles et faciles à répéter."
      }
    },
    {
      "type": "word",
      "fr": "Bonjour",
      "transcription": "[бонжур]",
      "ru": "здравствуйте / добрый день",
      "audio_text": "Bonjour",
      "tooltip": {
        "ru": "Универсальное вежливое приветствие.",
        "fr": "Salutation polie et très courante."
      }
    },
    {
      "type": "word",
      "fr": "Merci",
      "transcription": "[мэрси]",
      "ru": "спасибо",
      "audio_text": "Merci",
      "tooltip": {
        "ru": "Базовое спасибо. Подходит почти везде.",
        "fr": "Remerciement simple et courant."
      }
    },
    {
      "type": "example",
      "fr": "Bonjour, monsieur.",
      "transcription": "[бонжур, месьё]",
      "ru": "Здравствуйте, месье.",
      "audio_text": "Bonjour, monsieur."
    },
    {
      "type": "exercise",
      "exercise_id": "ex_bonjour_translation"
    }
  ],
  "exercises": [
    {
      "id": "ex_bonjour_translation",
      "type": "choose_option",
      "prompt": {
        "ru": "Что значит Bonjour?",
        "fr": "Que signifie Bonjour ?"
      },
      "options": ["спасибо", "здравствуйте", "пожалуйста", "до свидания"],
      "answer": "здравствуйте",
      "explanation": {
        "ru": "Bonjour значит здравствуйте или добрый день.",
        "fr": "Bonjour signifie bonjour ou bonne journée selon le contexte."
      },
      "audio_text": "Bonjour",
      "tags": ["greeting", "basic"],
      "difficulty": 1
    }
  ]
}
""")

    w("content/sections/02_articles/section.json", r"""
{
  "id": "articles",
  "slug": "articles",
  "order": 2,
  "icon": "shield",
  "title": {
    "ru": "Артикли",
    "fr": "Les articles"
  },
  "subtitle": {
    "ru": "Le, la, les, un, une, des без мозгового тумана.",
    "fr": "Le, la, les, un, une, des sans brouillard."
  },
  "level": "A0",
  "tone": "grammar",
  "lessons": ["le_la_001"],
  "is_adult": false
}
""")

    w("content/sections/02_articles/lessons/le_la_001.json", r"""
{
  "id": "le_la_001",
  "section_id": "articles",
  "order": 1,
  "level": "A0",
  "title": {
    "ru": "Le и la: первый удар по хаосу",
    "fr": "Le et la : premier coup contre le chaos"
  },
  "cards": [
    {
      "type": "theory",
      "title": {
        "ru": "Что делает артикль",
        "fr": "Le rôle de l’article"
      },
      "body": {
        "ru": "Во французском существительное почти всегда ходит с маленьким служебным словом перед ним. Это слово показывает род, число и определённость.",
        "fr": "En français, le nom est souvent accompagné d’un petit mot qui indique le genre, le nombre et la précision."
      }
    },
    {
      "type": "word",
      "fr": "le",
      "transcription": "[лё]",
      "ru": "определённый артикль мужского рода",
      "audio_text": "le",
      "tooltip": {
        "ru": "Ставится перед существительным мужского рода: le livre.",
        "fr": "Article défini masculin singulier."
      }
    },
    {
      "type": "word",
      "fr": "la",
      "transcription": "[ля]",
      "ru": "определённый артикль женского рода",
      "audio_text": "la",
      "tooltip": {
        "ru": "Ставится перед существительным женского рода: la maison.",
        "fr": "Article défini féminin singulier."
      }
    },
    {
      "type": "example",
      "fr": "le livre",
      "transcription": "[лё ливр]",
      "ru": "книга",
      "audio_text": "le livre"
    },
    {
      "type": "example",
      "fr": "la maison",
      "transcription": "[ля мэзон]",
      "ru": "дом",
      "audio_text": "la maison"
    },
    {
      "type": "exercise",
      "exercise_id": "ex_la_maison_001"
    }
  ],
  "exercises": [
    {
      "id": "ex_la_maison_001",
      "type": "choose_option",
      "prompt": {
        "ru": "Выбери правильный артикль: ___ maison",
        "fr": "Choisis le bon article : ___ maison"
      },
      "options": ["le", "la", "les"],
      "answer": "la",
      "explanation": {
        "ru": "maison женского рода, поэтому la maison.",
        "fr": "maison est féminin, donc la maison."
      },
      "audio_text": "la maison",
      "tags": ["article", "gender", "la"],
      "difficulty": 1
    }
  ]
}
""")

    w("content/sections/03_de_du/section.json", r"""
{
  "id": "de_du",
  "slug": "de-du",
  "order": 3,
  "icon": "key",
  "title": {
    "ru": "De, du, de la",
    "fr": "De, du, de la"
  },
  "subtitle": {
    "ru": "Главный французский узел, который надо приручить.",
    "fr": "Le grand nœud français à apprivoiser."
  },
  "level": "A0",
  "tone": "grammar",
  "lessons": ["de_basic_001"],
  "is_adult": false
}
""")

    w("content/sections/03_de_du/lessons/de_basic_001.json", r"""
{
  "id": "de_basic_001",
  "section_id": "de_du",
  "order": 1,
  "level": "A0",
  "title": {
    "ru": "De: из, от, принадлежность и количество",
    "fr": "De : origine, possession et quantité"
  },
  "cards": [
    {
      "type": "theory",
      "title": {
        "ru": "Почему de важно",
        "fr": "Pourquoi de est important"
      },
      "body": {
        "ru": "Во французском de часто делает работу, которую в русском делают падежи. Поэтому это не мусорное слово, а ключ.",
        "fr": "En français, de exprime souvent l’origine, la possession ou la quantité."
      }
    },
    {
      "type": "example",
      "fr": "un verre de vin",
      "transcription": "[эн вэр дэ вэн]",
      "ru": "бокал вина",
      "audio_text": "un verre de vin"
    },
    {
      "type": "example",
      "fr": "du pain",
      "transcription": "[дю пэн]",
      "ru": "хлеба / немного хлеба",
      "audio_text": "du pain"
    },
    {
      "type": "exercise",
      "exercise_id": "ex_du_pain_001"
    }
  ],
  "exercises": [
    {
      "id": "ex_du_pain_001",
      "type": "choose_option",
      "prompt": {
        "ru": "Выбери форму: Je veux ___ pain.",
        "fr": "Choisis la forme : Je veux ___ pain."
      },
      "options": ["de", "du", "de la", "les"],
      "answer": "du",
      "explanation": {
        "ru": "pain мужского рода. Когда говорим про неопределённое количество хлеба, используется du.",
        "fr": "pain est masculin. Pour une quantité non précisée, on utilise du."
      },
      "audio_text": "Je veux du pain.",
      "tags": ["de", "du", "partitif"],
      "difficulty": 1
    }
  ]
}
""")

    w("content/sections/07_vulgar_french/section.json", r"""
{
  "id": "vulgar_french",
  "slug": "vulgar-french",
  "order": 7,
  "icon": "flame",
  "title": {
    "ru": "Французский мат",
    "fr": "Les gros mots français"
  },
  "subtitle": {
    "ru": "Грубые фразы, злость и реальный разговорный регистр.",
    "fr": "Insultes, colère et registre très familier."
  },
  "level": "A1",
  "tone": "vulgar",
  "lessons": ["vulgar_intro_001"],
  "is_adult": true
}
""")

    w("content/sections/07_vulgar_french/lessons/vulgar_intro_001.json", r"""
{
  "id": "vulgar_intro_001",
  "section_id": "vulgar_french",
  "order": 1,
  "level": "A1",
  "title": {
    "ru": "Введение в французский мат",
    "fr": "Introduction aux gros mots français"
  },
  "cards": [
    {
      "type": "theory",
      "title": {
        "ru": "Зачем это учить",
        "fr": "Pourquoi apprendre ça"
      },
      "body": {
        "ru": "Мат и грубые фразы нужны не только чтобы ругаться. Они помогают понимать фильмы, песни, живую речь и уровень агрессии.",
        "fr": "Les gros mots aident à comprendre les films, les chansons et le vrai registre familier."
      }
    },
    {
      "type": "example",
      "fr": "Putain, j’en ai marre.",
      "transcription": "[пютэн, жанэ мар]",
      "ru": "Блядь, меня это достало.",
      "audio_text": "Putain, j’en ai marre."
    },
    {
      "type": "exercise",
      "exercise_id": "ex_vulgar_rudeness_001"
    }
  ],
  "exercises": [
    {
      "id": "ex_vulgar_rudeness_001",
      "type": "choose_option",
      "prompt": {
        "ru": "Какой это регистр: Putain, j’en ai marre?",
        "fr": "Quel est le registre : Putain, j’en ai marre ?"
      },
      "options": ["официальный", "нейтральный", "грубый разговорный", "детский"],
      "answer": "грубый разговорный",
      "explanation": {
        "ru": "Putain делает фразу грубой и разговорной. В официальной ситуации так лучше не говорить.",
        "fr": "Putain rend la phrase vulgaire et très familière."
      },
      "audio_text": "Putain, j’en ai marre.",
      "tags": ["vulgar", "register"],
      "difficulty": 1
    }
  ]
}
""")

    w("frontend/package.json", r"""
{
  "name": "forge-francaise",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host 127.0.0.1 --port 5173",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview --host 127.0.0.1 --port 4173"
  },
  "dependencies": {
    "pinia": "^2.1.7",
    "vue": "^3.4.0",
    "vue-router": "^4.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.5",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "vue-tsc": "^2.0.0"
  }
}
""")

    w("frontend/index.html", r"""
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Forge Française</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
""")

    w("frontend/tsconfig.json", r"""
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "allowJs": false,
    "strict": true,
    "noEmit": true,
    "moduleResolution": "Bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve"
  },
  "include": ["src/**/*.ts", "src/**/*.vue"]
}
""")

    w("frontend/vite.config.ts", r"""
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue],
})
""")

    w("frontend/src/main.ts", r"""
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'

import './styles/tokens.css'
import './styles/base.css'
import './styles/imperial.css'
import './styles/mobile.css'
import './styles/animations.css'

createApp(App).use(createPinia()).use(router).mount('#app')
""")

    w("frontend/src/App.vue", r"""
<script setup lang="ts">
import ImperialShell from './components/layout/ImperialShell.vue'
</script>

<template>
  <ImperialShell>
    <RouterView />
  </ImperialShell>
</template>
""")

    w("frontend/src/lib/api.ts", r"""
export const apiBase = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8787/api'

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

export function publicApiUrl(path: string): string {
  return apiBase.replace('/api', '') + path
}
""")

    w("frontend/src/stores/bootstrapStore.ts", r"""
import { defineStore } from 'pinia'
import { apiGet } from '../lib/api'

export interface LocalizedText {
  ru: string
  fr: string
}

export interface Profile {
  id: string
  display_name: string
  ui_language: string
  learning_language: string
  voice_id: string
  rank_id: string
  vulgar_library_enabled: boolean
}

export interface Voice {
  id: string
  label: string
  lang: string
  engine: string
  quality: string
}

export interface Section {
  id: string
  slug: string
  order: number
  icon: string
  title: LocalizedText
  subtitle: LocalizedText
  level: string
  tone: string
  lessons: string[]
  is_adult: boolean
}

export interface BootstrapPayload {
  profile: Profile
  progress: Record<string, unknown>
  sections: Section[]
  ranks: Record<string, unknown>[]
  voices: Voice[]
}

export const useBootstrapStore = defineStore('bootstrap', {
  state: () => ({
    payload: null as BootstrapPayload | null,
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async load() {
      if (this.payload || this.loading) return

      this.loading = true
      this.error = null

      try {
        this.payload = await apiGet<BootstrapPayload>('/app/bootstrap')
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
      } finally {
        this.loading = false
      }
    },
  },
})
""")

    w("frontend/src/router/index.ts", r"""
import { createRouter, createWebHistory } from 'vue-router'

import ThronePage from '../pages/ThronePage.vue'
import CampaignPage from '../pages/CampaignPage.vue'
import LessonPage from '../pages/LessonPage.vue'
import PracticePage from '../pages/PracticePage.vue'
import CodexPage from '../pages/CodexPage.vue'
import VulgarLibraryPage from '../pages/VulgarLibraryPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'throne', component: ThronePage },
    { path: '/campaign', name: 'campaign', component: CampaignPage },
    { path: '/lesson/:lessonId', name: 'lesson', component: LessonPage },
    { path: '/practice', name: 'practice', component: PracticePage },
    { path: '/codex', name: 'codex', component: CodexPage },
    { path: '/vulgar', name: 'vulgar', component: VulgarLibraryPage },
    { path: '/profile', name: 'profile', component: ProfilePage },
  ],
})
""")

    w("frontend/src/components/layout/ImperialShell.vue", r"""
<script setup lang="ts">
import BottomNav from './BottomNav.vue'
import TopBar from './TopBar.vue'
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
  </div>
</template>
""")

    w("frontend/src/components/layout/TopBar.vue", r"""
<template>
  <header class="top-bar">
    <div>
      <div class="eyebrow">Forge Française</div>
      <div class="top-title">Имперский мозговыбиватель</div>
    </div>

    <button class="ghost-button" type="button">RU / FR</button>
  </header>
</template>
""")

    w("frontend/src/components/layout/BottomNav.vue", r"""
<template>
  <nav class="bottom-nav">
    <RouterLink to="/">Трон</RouterLink>
    <RouterLink to="/campaign">Уроки</RouterLink>
    <RouterLink to="/practice">Дрель</RouterLink>
    <RouterLink to="/codex">Кодекс</RouterLink>
    <RouterLink to="/profile">Профиль</RouterLink>
  </nav>
</template>
""")

    w("frontend/src/components/learning/AudioButton.vue", r"""
<script setup lang="ts">
import { ref } from 'vue'
import { apiPost, publicApiUrl } from '../../lib/api'

const props = defineProps<{
  text: string
  label?: string
}>()

const loading = ref(false)

async function play() {
  loading.value = true

  try {
    const result = await apiPost<{ url: string }>('/audio/speak', {
      text: props.text,
      lang: 'fr',
      voice_id: 'mock_fr_female',
      speed: 1,
      mode: 'normal',
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

    w("frontend/src/pages/ThronePage.vue", r"""
<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import AudioButton from '../components/learning/AudioButton.vue'
import { useBootstrapStore } from '../stores/bootstrapStore'

const store = useBootstrapStore()

onMounted(() => {
  store.load()
})

const profile = computed(() => store.payload?.profile)
const firstLesson = computed(() => store.payload?.sections?.[0]?.lessons?.[0] ?? 'greetings_001')
</script>

<template>
  <section class="page throne-page">
    <div class="hero-card">
      <div class="crest-orb">♛</div>
      <div class="eyebrow">Тронный зал</div>
      <h1>Forge Française</h1>
      <p>Мобильная имперская кузница французского. Без перегруза, но с короной.</p>

      <div class="profile-strip" v-if="profile">
        <span>{{ profile.display_name }}</span>
        <strong>{{ profile.rank_id }}</strong>
      </div>

      <div class="hero-actions">
        <RouterLink class="primary-button" :to="'/lesson/' + firstLesson">Продолжить</RouterLink>
        <AudioButton text="Bonjour, monsieur." label="Слушать" />
      </div>
    </div>

    <div class="quick-grid">
      <RouterLink class="quick-card" to="/practice">
        <strong>Дрель</strong>
        <span>5 быстрых ударов по хаосу</span>
      </RouterLink>

      <RouterLink class="quick-card" to="/vulgar">
        <strong>Мат</strong>
        <span>Грубый французский под замком</span>
      </RouterLink>

      <RouterLink class="quick-card" to="/codex">
        <strong>Кодекс</strong>
        <span>Артикли, de и прочая магия</span>
      </RouterLink>
    </div>
  </section>
</template>
""")

    w("frontend/src/pages/CampaignPage.vue", r"""
<script setup lang="ts">
import { onMounted } from 'vue'
import { useBootstrapStore } from '../stores/bootstrapStore'

const store = useBootstrapStore()

onMounted(() => {
  store.load()
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Кампания</div>
      <h1>Учебные секции</h1>
    </div>

    <div class="card-list">
      <RouterLink
        v-for="section in store.payload?.sections ?? []"
        :key="section.id"
        class="lesson-tile"
        :to="section.id === 'vulgar_french' ? '/vulgar' : '/lesson/' + section.lessons[0]"
      >
        <div class="tile-icon">{{ section.icon }}</div>
        <div>
          <strong>{{ section.title.ru }}</strong>
          <span>{{ section.subtitle.ru }}</span>
        </div>
      </RouterLink>
    </div>
  </section>
</template>
""")

    w("frontend/src/pages/LessonPage.vue", r"""
<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AudioButton from '../components/learning/AudioButton.vue'
import { apiGet } from '../lib/api'

const route = useRoute()
const lesson = ref<any | null>(null)
const loading = ref(false)

async function loadLesson() {
  loading.value = true
  lesson.value = await apiGet<any>('/lessons/' + route.params.lessonId)
  loading.value = false
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
        <h1>{{ lesson.title.ru }}</h1>
      </div>

      <article v-for="card in lesson.cards" :key="JSON.stringify(card)" class="study-card">
        <template v-if="card.type === 'theory'">
          <div class="eyebrow">Теория</div>
          <h2>{{ card.title.ru }}</h2>
          <p>{{ card.body.ru }}</p>
        </template>

        <template v-else-if="card.type === 'word'">
          <div class="eyebrow">Слово</div>
          <h2>{{ card.fr }}</h2>
          <p class="transcription">{{ card.transcription }}</p>
          <p>{{ card.ru }}</p>
          <AudioButton :text="card.audio_text" />
          <details class="mini-details" v-if="card.tooltip">
            <summary>Почему?</summary>
            <p>{{ card.tooltip.ru }}</p>
          </details>
        </template>

        <template v-else-if="card.type === 'example'">
          <div class="eyebrow">Пример</div>
          <h2>{{ card.fr }}</h2>
          <p class="transcription">{{ card.transcription }}</p>
          <p>{{ card.ru }}</p>
          <AudioButton :text="card.audio_text" />
        </template>

        <template v-else-if="card.type === 'exercise'">
          <div class="eyebrow">Упражнение</div>
          <p>Упражнение подключено: {{ card.exercise_id }}</p>
          <RouterLink class="primary-button" to="/practice">Открыть дрель</RouterLink>
        </template>
      </article>
    </template>
  </section>
</template>
""")

    w("frontend/src/pages/PracticePage.vue", r"""
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AudioButton from '../components/learning/AudioButton.vue'
import { apiGet, apiPost } from '../lib/api'

const lesson = ref<any | null>(null)
const selected = ref('')
const result = ref<any | null>(null)

const exercise = computed(() => lesson.value?.exercises?.[0] ?? null)

onMounted(async () => {
  lesson.value = await apiGet<any>('/lessons/le_la_001')
})

async function answer(value: string) {
  selected.value = value
  result.value = await apiPost<any>('/practice/answer', {
    profile_id: 'local_lizard',
    lesson_id: lesson.value.id,
    exercise_id: exercise.value.id,
    answer: value,
  })
}
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Дрель</div>
      <h1>Один удар по хаосу</h1>
    </div>

    <div v-if="exercise" class="study-card">
      <h2>{{ exercise.prompt.ru }}</h2>
      <AudioButton :text="exercise.audio_text" label="Прослушать" />

      <div class="option-grid">
        <button
          v-for="option in exercise.options"
          :key="option"
          class="option-button"
          type="button"
          @click="answer(option)"
        >
          {{ option }}
        </button>
      </div>

      <div v-if="result" class="result-box" :class="{ good: result.correct, bad: !result.correct }">
        <strong>{{ result.correct ? 'Верно' : 'Мимо' }}</strong>
        <p>{{ result.explanation.ru }}</p>
      </div>
    </div>
  </section>
</template>
""")

    w("frontend/src/pages/CodexPage.vue", r"""
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiGet } from '../lib/api'

const entries = ref<any[]>([])

onMounted(async () => {
  entries.value = await apiGet<any[]>('/codex')
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Кодекс</div>
      <h1>Справочник</h1>
    </div>

    <article v-for="entry in entries" :key="entry.id" class="study-card">
      <h2>{{ entry.title.ru }}</h2>
      <p>{{ entry.summary.ru }}</p>

      <div v-for="item in entry.items" :key="item.fr" class="codex-row">
        <strong>{{ item.fr }}</strong>
        <span>{{ item.transcription }}</span>
        <span>{{ item.ru }}</span>
      </div>
    </article>
  </section>
</template>
""")

    w("frontend/src/pages/VulgarLibraryPage.vue", r"""
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AudioButton from '../components/learning/AudioButton.vue'
import { apiGet } from '../lib/api'

const items = ref<any[]>([])

onMounted(async () => {
  items.value = await apiGet<any[]>('/vulgar/items')
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Adult Codex</div>
      <h1>Французский мат</h1>
      <p>Грубые фразы с уровнем опасности, переводом и озвучкой.</p>
    </div>

    <article v-for="item in items" :key="item.id" class="study-card danger-card">
      <div class="rudeness">Грубость {{ item.rudeness_level }}/5</div>
      <h2>{{ item.fr }}</h2>
      <p class="transcription">{{ item.transcription }}</p>
      <p>{{ item.ru }}</p>
      <AudioButton :text="item.audio_text" label="Слушать" />

      <details class="mini-details">
        <summary>Контекст и мягкий вариант</summary>
        <p>{{ item.context.ru }}</p>
        <p v-if="item.softer_versions?.[0]">
          Мягче: <strong>{{ item.softer_versions[0].fr }}</strong>
          {{ item.softer_versions[0].ru }}
        </p>
      </details>
    </article>
  </section>
</template>
""")

    w("frontend/src/pages/ProfilePage.vue", r"""
<script setup lang="ts">
import { onMounted } from 'vue'
import { useBootstrapStore } from '../stores/bootstrapStore'

const store = useBootstrapStore()

onMounted(() => {
  store.load()
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Профиль</div>
      <h1>{{ store.payload?.profile?.display_name ?? 'Local Lizard' }}</h1>
    </div>

    <div class="study-card">
      <h2>Текущий ранг</h2>
      <p>{{ store.payload?.profile?.rank_id }}</p>
    </div>

    <div class="study-card">
      <h2>Голоса</h2>
      <div v-for="voice in store.payload?.voices ?? []" :key="voice.id" class="codex-row">
        <strong>{{ voice.label }}</strong>
        <span>{{ voice.engine }}</span>
      </div>
    </div>
  </section>
</template>
""")

    w("frontend/src/styles/tokens.css", r"""
:root {
  --imperial-black: #171717;
  --deep-black: #0b0d0c;
  --panel-black: rgba(14, 17, 15, 0.92);
  --sovereign-green: #255b32;
  --emerald-green: #2f7a45;
  --bone-white: #e8e2d8;
  --cloth-white: #c9c3ba;
  --antique-gold: #b08a45;
  --muted-gold: #7f6a3c;
  --danger-red: #8a2d2d;
  --text-main: #f5f0e8;
  --text-muted: #b9b2a7;
  --radius-lg: 24px;
  --radius-md: 18px;
  --shadow-soft: 0 18px 50px rgba(0, 0, 0, 0.35);
  --bottom-nav-height: 72px;
}
""")

    w("frontend/src/styles/base.css", r"""
* {
  box-sizing: border-box;
}

html,
body,
#app {
  min-height: 100%;
  margin: 0;
}

body {
  background:
    radial-gradient(circle at top, rgba(47, 122, 69, 0.22), transparent 34rem),
    linear-gradient(180deg, #0b0d0c 0%, #171717 48%, #0b0d0c 100%);
  color: var(--text-main);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

a {
  color: inherit;
  text-decoration: none;
}

button,
input,
select {
  font: inherit;
}
""")

    w("frontend/src/styles/imperial.css", r"""
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
.option-grid {
  display: grid;
  gap: 10px;
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
""")

    w("frontend/src/styles/mobile.css", r"""
.bottom-nav {
  position: fixed;
  left: 10px;
  right: 10px;
  bottom: 10px;
  z-index: 30;
  height: var(--bottom-nav-height);
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
  padding: 8px;
  border: 1px solid rgba(232, 226, 216, 0.12);
  border-radius: 24px;
  background: rgba(11, 13, 12, 0.9);
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow-soft);
}

.bottom-nav a {
  display: grid;
  place-items: center;
  border-radius: 18px;
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 800;
}

.bottom-nav a.router-link-active {
  color: #071009;
  background: var(--bone-white);
}

@media (min-width: 760px) {
  .shell-main {
    padding: 24px;
  }

  .quick-grid,
  .option-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .hero-card {
    min-height: 520px;
  }

  .bottom-nav {
    left: 50%;
    right: auto;
    width: min(620px, calc(100vw - 20px));
    transform: translateX(-50%);
  }
}
""")

    w("frontend/src/styles/animations.css", r"""
.flying-layer {
  pointer-events: none;
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  opacity: 0.18;
}

.flying-layer span {
  position: absolute;
  color: var(--antique-gold);
  font-size: clamp(2rem, 10vw, 6rem);
  animation: floatAccent 18s linear infinite;
}

.flying-layer span:nth-child(1) {
  left: 8%;
  animation-delay: 0s;
}

.flying-layer span:nth-child(2) {
  left: 36%;
  animation-delay: 4s;
}

.flying-layer span:nth-child(3) {
  left: 64%;
  animation-delay: 8s;
}

.flying-layer span:nth-child(4) {
  left: 82%;
  animation-delay: 12s;
}

@keyframes floatAccent {
  from {
    transform: translateY(110vh) rotate(0deg);
  }

  to {
    transform: translateY(-20vh) rotate(360deg);
  }
}
""")

    print("")
    print("initializing git")
    run(["git", "init"])
    run(["git", "branch", "-M", "main"])

    result = subprocess.run(
        ["git", "remote"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    remotes = result.stdout.splitlines() if result.returncode == 0 else []

    if "origin" in remotes:
        run(["git", "remote", "set-url", "origin", REMOTE_URL])
    else:
        run(["git", "remote", "add", "origin", REMOTE_URL])

    print("")
    print("running content validation")
    run([sys.executable, "scripts/validate_content.py"], cwd=ROOT / "backend")

    print("")
    print("PATCH 1 DONE")
    print("Готовность проекта: примерно 15%")
    print("")
    print("Дальше проверь:")
    print(r'cd /d "D:\PYTHON\Forge Francaise"')
    print(r"scripts\validate_content.cmd")
    print(r"scripts\dev_backend.cmd")
    print(r"scripts\dev_frontend.cmd")
    print("")
    print("Git status:")
    run(["git", "status", "--short"])

if __name__ == "__main__":
    main()