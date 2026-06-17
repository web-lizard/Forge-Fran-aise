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
