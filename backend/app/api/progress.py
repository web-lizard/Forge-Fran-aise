from fastapi import APIRouter

from app.services.progress_service import get_progress_service

router = APIRouter(tags=["progress"])


@router.get("/progress/{profile_id}")
def get_progress(profile_id: str):
    return get_progress_service().get_progress(profile_id)


@router.get("/progress/{profile_id}/summary")
def progress_summary(profile_id: str):
    return get_progress_service().summary(profile_id)


@router.post("/progress/{profile_id}/lessons/{lesson_id}/complete")
def complete_lesson(profile_id: str, lesson_id: str):
    return get_progress_service().complete_lesson(profile_id, lesson_id)
