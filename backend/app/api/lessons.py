from fastapi import APIRouter, HTTPException

from app.services.content_service import get_content_service

router = APIRouter(tags=["lessons"])


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: str):
    try:
        return get_content_service().get_lesson(lesson_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
