import asyncio
from pathlib import Path

from app.models.audio import AudioRequest, Voice
from app.tts.base import TTSProvider


EDGE_VOICES = [
    {
        "id": "edge_fr_denise",
        "name": "fr-FR-DeniseNeural",
        "label": "Denise Neural, France",
        "gender": "female",
    },
    {
        "id": "edge_fr_henri",
        "name": "fr-FR-HenriNeural",
        "label": "Henri Neural, France",
        "gender": "male",
    },
    {
        "id": "edge_fr_vivienne",
        "name": "fr-FR-VivienneMultilingualNeural",
        "label": "Vivienne Multilingual, France",
        "gender": "female",
    },
    {
        "id": "edge_fr_remy",
        "name": "fr-FR-RemyMultilingualNeural",
        "label": "Rémy Multilingual, France",
        "gender": "male",
    },
    {
        "id": "edge_fr_sylvie",
        "name": "fr-CA-SylvieNeural",
        "label": "Sylvie Neural, Canada",
        "gender": "female",
    },
    {
        "id": "edge_fr_antoine",
        "name": "fr-CA-AntoineNeural",
        "label": "Antoine Neural, Canada",
        "gender": "male",
    },
]


class EdgeTTSProvider(TTSProvider):
    engine = "edge"
    extension = "mp3"

    def voices(self) -> list[Voice]:
        return [
            Voice(
                id=item["id"],
                label=item["label"],
                lang="fr",
                engine="edge",
                quality="neural-online",
                gender=item["gender"],
                description=item["name"],
            )
            for item in EDGE_VOICES
        ]

    def voice_name(self, voice_id: str) -> str:
        for item in EDGE_VOICES:
            if item["id"] == voice_id:
                return item["name"]
        return "fr-FR-DeniseNeural"

    def rate_for(self, request: AudioRequest) -> str:
        if request.mode == "slow" or request.speed < 0.9:
            return "-25%"
        if request.speed > 1.1:
            return "+15%"
        return "+0%"

    def synthesize(self, request: AudioRequest, output_path: Path) -> int:
        try:
            import edge_tts
        except Exception as exc:
            raise RuntimeError("edge-tts is not installed") from exc

        output_path.parent.mkdir(parents=True, exist_ok=True)
        voice_name = self.voice_name(request.voice_id)
        rate = self.rate_for(request)

        async def run_save() -> None:
            communicate = edge_tts.Communicate(
                text=request.text,
                voice=voice_name,
                rate=rate,
            )
            await communicate.save(str(output_path))

        asyncio.run(run_save())

        # MP3 duration is not parsed in MVP. Good enough for UI metadata.
        return max(600, min(6000, len(request.text) * 70))
