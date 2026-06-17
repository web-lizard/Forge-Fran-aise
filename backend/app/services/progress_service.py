from collections import Counter, defaultdict
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

    def default_progress(self, profile_id: str) -> dict[str, Any]:
        return {
            "profile_id": profile_id,
            "current_level": "A0",
            "score": 0,
            "completed_lessons": [],
            "lesson_progress": {},
            "weak_topics": [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_progress(self, profile_id: str) -> dict[str, Any]:
        path = self.progress_path(profile_id)

        if not path.exists():
            payload = self.default_progress(profile_id)
            write_json_atomic(path, payload)

        payload = read_json(path)

        changed = False
        for key, value in self.default_progress(profile_id).items():
            if key not in payload:
                payload[key] = value
                changed = True

        if changed:
            write_json_atomic(path, payload)

        return payload

    def save_progress(self, profile_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload["profile_id"] = profile_id
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        write_json_atomic(self.progress_path(profile_id), payload)
        return payload

    def append_event(self, profile_id: str, event: dict[str, Any]) -> None:
        EVENTS_ROOT.mkdir(parents=True, exist_ok=True)
        event["ts"] = datetime.now(timezone.utc).isoformat()

        with self.events_path(profile_id).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def read_events(self, profile_id: str, limit: int | None = None) -> list[dict[str, Any]]:
        path = self.events_path(profile_id)

        if not path.exists():
            return []

        rows: list[dict[str, Any]] = []

        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        if limit is not None:
            return rows[-limit:]

        return rows

    def record_answer(
        self,
        profile_id: str,
        lesson_id: str,
        exercise_id: str,
        answer: Any,
        expected: Any,
        correct: bool,
        tags: list[str],
        section_id: str | None = None,
    ) -> dict[str, Any]:
        progress = self.get_progress(profile_id)

        delta = 10 if correct else 1
        if tags and "vulgar" in tags and correct:
            delta += 2

        progress["score"] = int(progress.get("score", 0)) + delta

        lesson_progress = progress.setdefault("lesson_progress", {})
        lesson_state = lesson_progress.setdefault(
            lesson_id,
            {
                "status": "in_progress",
                "score": 0,
                "attempts": 0,
                "correct": 0,
                "wrong": 0,
                "last_opened_at": None,
                "last_answered_at": None,
            },
        )

        lesson_state["attempts"] = int(lesson_state.get("attempts", 0)) + 1
        lesson_state["score"] = int(lesson_state.get("score", 0)) + delta
        lesson_state["last_answered_at"] = datetime.now(timezone.utc).isoformat()

        if correct:
            lesson_state["correct"] = int(lesson_state.get("correct", 0)) + 1
        else:
            lesson_state["wrong"] = int(lesson_state.get("wrong", 0)) + 1

        attempts = max(1, int(lesson_state.get("attempts", 0)))
        correct_count = int(lesson_state.get("correct", 0))
        lesson_state["accuracy"] = round(correct_count / attempts * 100)

        if attempts >= 3 and lesson_state["accuracy"] >= 70:
            lesson_state["status"] = "ready_to_complete"

        self.append_event(
            profile_id,
            {
                "event": "exercise_answered",
                "lesson_id": lesson_id,
                "section_id": section_id,
                "exercise_id": exercise_id,
                "answer": answer,
                "expected": expected,
                "correct": correct,
                "score_delta": delta,
                "tags": tags,
            },
        )

        self.recalculate_weak_topics(profile_id, progress)
        return self.save_progress(profile_id, progress)

    def complete_lesson(self, profile_id: str, lesson_id: str) -> dict[str, Any]:
        progress = self.get_progress(profile_id)
        completed = progress.setdefault("completed_lessons", [])

        if lesson_id not in completed:
            completed.append(lesson_id)
            progress["score"] = int(progress.get("score", 0)) + 25

        lesson_progress = progress.setdefault("lesson_progress", {})
        lesson_state = lesson_progress.setdefault(lesson_id, {})
        lesson_state["status"] = "completed"
        lesson_state["completed_at"] = datetime.now(timezone.utc).isoformat()

        self.append_event(
            profile_id,
            {
                "event": "lesson_completed",
                "lesson_id": lesson_id,
                "score_delta": 25,
                "tags": ["lesson"],
            },
        )

        return self.save_progress(profile_id, progress)

    def recalculate_weak_topics(self, profile_id: str, progress: dict[str, Any] | None = None) -> list[str]:
        events = self.read_events(profile_id)
        wrong_by_tag: Counter[str] = Counter()

        for event in events:
            if event.get("event") != "exercise_answered":
                continue
            if event.get("correct") is True:
                continue
            for tag in event.get("tags", []):
                wrong_by_tag[tag] += 1

        weak = [tag for tag, _count in wrong_by_tag.most_common(8)]

        if progress is not None:
            progress["weak_topics"] = weak

        return weak

    def summary(self, profile_id: str) -> dict[str, Any]:
        progress = self.get_progress(profile_id)
        events = self.read_events(profile_id)

        answered = [event for event in events if event.get("event") == "exercise_answered"]
        total = len(answered)
        correct = sum(1 for event in answered if event.get("correct") is True)
        wrong = total - correct
        accuracy = round(correct / total * 100) if total else 0

        by_tag: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0, "wrong": 0})

        for event in answered:
            tags = event.get("tags", []) or ["untagged"]
            for tag in tags:
                by_tag[tag]["total"] += 1
                if event.get("correct") is True:
                    by_tag[tag]["correct"] += 1
                else:
                    by_tag[tag]["wrong"] += 1

        tag_stats = []
        for tag, stat in by_tag.items():
            total_tag = max(1, stat["total"])
            tag_stats.append({
                "tag": tag,
                "total": stat["total"],
                "correct": stat["correct"],
                "wrong": stat["wrong"],
                "accuracy": round(stat["correct"] / total_tag * 100),
            })

        tag_stats.sort(key=lambda item: (-item["wrong"], item["accuracy"], item["tag"]))

        return {
            "profile_id": profile_id,
            "score": int(progress.get("score", 0)),
            "current_level": progress.get("current_level", "A0"),
            "completed_lessons": progress.get("completed_lessons", []),
            "completed_count": len(progress.get("completed_lessons", [])),
            "total_answers": total,
            "correct_answers": correct,
            "wrong_answers": wrong,
            "accuracy": accuracy,
            "weak_topics": progress.get("weak_topics", []),
            "tag_stats": tag_stats[:12],
            "recent_events": events[-12:],
        }


def get_progress_service() -> ProgressService:
    return ProgressService()
