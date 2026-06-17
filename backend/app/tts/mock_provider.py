from pathlib import Path
import wave

from app.models.audio import AudioRequest, Voice
from app.tts.base import TTSProvider


class MockProvider(TTSProvider):
    engine = "mock"
    extension = "wav"

    def voices(self) -> list[Voice]:
        return [
            Voice(
                id="mock_fr_female",
                label="Voix impériale féminine, mock",
                engine="mock",
                quality="dev",
                gender="female",
                description="Fallback silence generator for offline development.",
            ),
            Voice(
                id="mock_fr_male",
                label="Voix impériale masculine, mock",
                engine="mock",
                quality="dev",
                gender="male",
                description="Fallback silence generator for offline development.",
            ),
        ]

    def synthesize(self, request: AudioRequest, output_path: Path) -> int:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        sample_rate = 16000
        duration_seconds = 0.45 if request.mode == "normal" else 0.75
        frame_count = int(sample_rate * duration_seconds)
        silence = b"\x00\x00" * frame_count

        with wave.open(str(output_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(silence)

        return int(duration_seconds * 1000)
