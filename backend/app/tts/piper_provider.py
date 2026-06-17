from pathlib import Path

from app.models.audio import AudioRequest, Voice
from app.tts.base import TTSProvider


class PiperProvider(TTSProvider):
    def voices(self) -> list[Voice]:
        return []

    def synthesize(self, request: AudioRequest, output_path: Path) -> int:
        raise RuntimeError("PiperProvider is reserved for the next patch.")
