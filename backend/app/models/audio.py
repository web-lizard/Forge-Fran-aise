from pydantic import BaseModel, Field


class Voice(BaseModel):
    id: str
    label: str
    lang: str = "fr"
    engine: str
    quality: str = "mock"
    gender: str | None = None
    description: str | None = None


class AudioRequest(BaseModel):
    text: str = Field(min_length=1)
    lang: str = "fr"
    voice_id: str = "mock_fr_female"
    speed: float = 1.0
    mode: str = "normal"


class AudioResponse(BaseModel):
    audio_id: str
    url: str
    cached: bool
    duration_ms: int
    provider: str = "mock"
    format: str = "wav"
    fallback: bool = False


class AudioCacheEntry(BaseModel):
    audio_id: str
    text: str
    voice_id: str
    mode: str
    provider: str
    format: str
    path: str
    created_at: str
