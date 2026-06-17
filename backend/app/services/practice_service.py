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
