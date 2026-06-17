from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.core.json_utils import read_json, write_json_atomic
from app.core.paths import AUDIO_CACHE_ROOT
from app.models.audio import AudioRequest, AudioResponse, Voice
from app.tts.edge_provider import EdgeTTSProvider
from app.tts.mock_provider import MockProvider


CACHE_INDEX_PATH = AUDIO_CACHE_ROOT / "index.json"


class AudioService:
    def __init__(self) -> None:
        self.mock_provider = MockProvider()
        self.edge_provider = EdgeTTSProvider()

    def providers(self):
        return {
            "mock": self.mock_provider,
            "edge": self.edge_provider,
        }

    def voices(self) -> list[Voice]:
        voices: list[Voice] = []
        voices.extend(self.edge_provider.voices())
        voices.extend(self.mock_provider.voices())
        return voices

    def provider_for_voice(self, voice_id: str):
        if voice_id.startswith("edge_"):
            return self.edge_provider
        return self.mock_provider

    def audio_id(self, request: AudioRequest, provider_engine: str) -> str:
        payload = request.model_dump()
        payload["provider_engine"] = provider_engine
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def cache_index(self) -> dict[str, Any]:
        if not CACHE_INDEX_PATH.exists():
            return {"items": []}

        try:
            return read_json(CACHE_INDEX_PATH)
        except Exception:
            return {"items": []}

    def save_cache_entry(self, entry: dict[str, Any]) -> None:
        payload = self.cache_index()
        items = payload.setdefault("items", [])
        items = [item for item in items if item.get("audio_id") != entry["audio_id"]]
        items.append(entry)
        payload["items"] = items[-1000:]
        write_json_atomic(CACHE_INDEX_PATH, payload)

    def cache_summary(self) -> dict[str, Any]:
        payload = self.cache_index()
        items = payload.get("items", [])
        files = list(AUDIO_CACHE_ROOT.glob("*.mp3")) + list(AUDIO_CACHE_ROOT.glob("*.wav"))
        total_bytes = sum(path.stat().st_size for path in files if path.exists())

        return {
            "count": len(files),
            "indexed_count": len(items),
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / 1024 / 1024, 3),
            "items": items[-50:],
        }

    def clear_cache(self) -> dict[str, Any]:
        removed = 0

        for path in list(AUDIO_CACHE_ROOT.glob("*.mp3")) + list(AUDIO_CACHE_ROOT.glob("*.wav")):
            try:
                path.unlink()
                removed += 1
            except FileNotFoundError:
                pass

        write_json_atomic(CACHE_INDEX_PATH, {"items": []})

        return {
            "removed": removed,
            "ok": True,
        }

    def speak(self, request: AudioRequest) -> AudioResponse:
        primary_provider = self.provider_for_voice(request.voice_id)
        provider = primary_provider
        fallback = False

        audio_id = self.audio_id(request, provider.engine)
        extension = provider.extension
        output_path = AUDIO_CACHE_ROOT / f"{audio_id}.{extension}"

        cached = output_path.exists()
        duration_ms = 0

        if not cached:
            try:
                duration_ms = provider.synthesize(request, output_path)
            except Exception:
                fallback = True
                provider = self.mock_provider
                audio_id = self.audio_id(request, "mock-fallback")
                extension = provider.extension
                output_path = AUDIO_CACHE_ROOT / f"{audio_id}.{extension}"
                cached = output_path.exists()

                if not cached:
                    duration_ms = provider.synthesize(request, output_path)
                else:
                    duration_ms = 450
        else:
            duration_ms = max(450, min(6000, len(request.text) * 70))

        self.save_cache_entry(
            {
                "audio_id": audio_id,
                "text": request.text,
                "voice_id": request.voice_id,
                "mode": request.mode,
                "provider": provider.engine,
                "format": extension,
                "path": str(output_path),
                "fallback": fallback,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        return AudioResponse(
            audio_id=audio_id,
            url=f"/api/audio/file/{audio_id}",
            cached=cached,
            duration_ms=duration_ms,
            provider=provider.engine,
            format=extension,
            fallback=fallback,
        )

    def file_path(self, audio_id: str) -> Path:
        for extension in ["mp3", "wav"]:
            path = AUDIO_CACHE_ROOT / f"{audio_id}.{extension}"
            if path.exists():
                return path
        raise HTTPException(status_code=404, detail="Audio file not found")

    def file_response(self, audio_id: str) -> FileResponse:
        path = self.file_path(audio_id)
        media_type = "audio/mpeg" if path.suffix == ".mp3" else "audio/wav"
        return FileResponse(path, media_type=media_type, filename=path.name)


def get_audio_service() -> AudioService:
    return AudioService()
