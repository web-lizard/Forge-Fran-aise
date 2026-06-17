from fastapi import APIRouter

from app.services.progress_service import get_progress_service

router = APIRouter(tags=["progress"])


@router.get("/progress/{profile_id}")
def get_progress(profile_id: str):
    return get_progress_service().get_progress(profile_id)
