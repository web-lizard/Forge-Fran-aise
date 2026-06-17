from fastapi import APIRouter

from app.services.practice_service import get_practice_service
from app.services.progress_service import get_progress_service

router = APIRouter(tags=["review"])


@router.get("/review/{profile_id}/weak")
def weak_topics(profile_id: str):
    summary = get_progress_service().summary(profile_id)
    return {
        "profile_id": profile_id,
        "weak_topics": summary["weak_topics"],
        "tag_stats": summary["tag_stats"],
    }


@router.get("/review/{profile_id}/session")
def review_session(profile_id: str, mode: str = "quick", limit: int = 7):
    return get_practice_service().session(profile_id=profile_id, mode=mode, limit=limit)
