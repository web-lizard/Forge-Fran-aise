import random
from typing import Any

from app.services.content_service import get_content_service
from app.services.progress_service import get_progress_service


def normalize(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(item).strip() for item in value).strip().lower()
    return str(value).strip().lower()


class PracticeService:
    def check_answer(self, profile_id: str, lesson_id: str, exercise_id: str, answer: Any) -> dict[str, Any]:
        exercise = get_content_service().get_exercise(lesson_id, exercise_id)

        expected = exercise.get("answer")
        correct = normalize(answer) == normalize(expected)

        progress = get_progress_service().record_answer(
            profile_id=profile_id,
            lesson_id=lesson_id,
            exercise_id=exercise_id,
            answer=answer,
            expected=expected,
            correct=correct,
            tags=exercise.get("tags", []),
            section_id=exercise.get("section_id"),
        )

        return {
            "correct": correct,
            "expected": expected,
            "explanation": exercise.get("explanation", {"ru": "", "fr": ""}),
            "score": progress.get("score", 0),
            "weak_topics": progress.get("weak_topics", []),
        }

    def session(self, profile_id: str, mode: str = "quick", limit: int = 7) -> dict[str, Any]:
        content = get_content_service()
        exercises = content.list_exercises()
        progress = get_progress_service().get_progress(profile_id)

        if mode == "weak":
            weak_topics = progress.get("weak_topics", [])
            if weak_topics:
                exercises = [
                    item for item in exercises
                    if any(tag in weak_topics for tag in item.get("tags", []))
                ] or content.list_exercises()

        elif mode == "audio":
            exercises = [item for item in exercises if item.get("audio_text")]

        elif mode == "vulgar":
            exercises = [
                item for item in exercises
                if "vulgar" in item.get("tags", []) or item.get("section_id") == "vulgar_french"
            ]

        elif mode == "articles":
            exercises = [
                item for item in exercises
                if "article" in item.get("tags", []) or item.get("section_id") in ["articles", "de_du"]
            ]

        else:
            exercises = list(exercises)

        random.seed(f"{profile_id}:{mode}:{len(exercises)}")
        random.shuffle(exercises)

        selected = exercises[: max(1, min(limit, 20))]

        return {
            "profile_id": profile_id,
            "mode": mode,
            "limit": limit,
            "count": len(selected),
            "exercises": selected,
        }


def get_practice_service() -> PracticeService:
    return PracticeService()
