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
