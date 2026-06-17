from pathlib import Path

from app.models.audio import AudioRequest, Voice
from app.tts.base import TTSProvider


class KokoroProvider(TTSProvider):
    def voices(self) -> list[Voice]:
        return []

    def synthesize(self, request: AudioRequest, output_path: Path) -> int:
        raise RuntimeError("KokoroProvider is reserved for the next patch.")
