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
