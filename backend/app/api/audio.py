from fastapi import APIRouter

from app.models.audio import AudioRequest
from app.services.audio_service import get_audio_service

router = APIRouter(tags=["audio"])


@router.get("/audio/voices")
def voices():
    return [voice.model_dump() for voice in get_audio_service().voices()]


@router.get("/audio/cache")
def cache_summary():
    return get_audio_service().cache_summary()


@router.delete("/audio/cache")
def clear_cache():
    return get_audio_service().clear_cache()


@router.post("/audio/speak")
def speak(request: AudioRequest):
    return get_audio_service().speak(request)


@router.get("/audio/file/{audio_id}")
def audio_file(audio_id: str):
    return get_audio_service().file_response(audio_id)
