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
