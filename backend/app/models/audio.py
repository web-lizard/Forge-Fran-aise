from pydantic import BaseModel, Field


class Voice(BaseModel):
    id: str
    label: str
    lang: str = "fr"
    engine: str
    quality: str = "mock"


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
