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
