from fastapi import APIRouter

from app.services.audio_service import get_audio_service
from app.services.content_service import get_content_service
from app.services.profile_service import get_profile_service
from app.services.progress_service import get_progress_service

router = APIRouter(tags=["bootstrap"])


@router.get("/app/bootstrap")
def bootstrap():
    profile = get_profile_service().active_profile()

    return {
        "profile": profile,
        "progress": get_progress_service().get_progress(profile["id"]),
        "sections": get_content_service().list_sections(),
        "ranks": get_content_service().list_ranks(),
        "voices": [voice.model_dump() for voice in get_audio_service().voices()],
    }
