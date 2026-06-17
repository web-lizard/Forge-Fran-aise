import hashlib
import json

from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.core.paths import AUDIO_CACHE_ROOT
from app.models.audio import AudioRequest, AudioResponse, Voice
from app.tts.mock_provider import MockProvider


class AudioService:
    def __init__(self) -> None:
        self.provider = MockProvider()

    def voices(self) -> list[Voice]:
        return self.provider.voices()

    def audio_id(self, request: AudioRequest) -> str:
        payload = request.model_dump()
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def speak(self, request: AudioRequest) -> AudioResponse:
        audio_id = self.audio_id(request)
        output_path = AUDIO_CACHE_ROOT / f"{audio_id}.wav"
        cached = output_path.exists()

        if not cached:
            duration_ms = self.provider.synthesize(request, output_path)
        else:
            duration_ms = 450

        return AudioResponse(
            audio_id=audio_id,
            url=f"/api/audio/file/{audio_id}",
            cached=cached,
            duration_ms=duration_ms,
        )

    def file_response(self, audio_id: str) -> FileResponse:
        path = AUDIO_CACHE_ROOT / f"{audio_id}.wav"

        if not path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")

        return FileResponse(path, media_type="audio/wav", filename=f"{audio_id}.wav")


def get_audio_service() -> AudioService:
    return AudioService()
