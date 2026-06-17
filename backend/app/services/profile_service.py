from datetime import datetime, timezone
from typing import Any

from app.core.json_utils import read_json, write_json_atomic
from app.core.paths import DATA_ROOT

PROFILES_PATH = DATA_ROOT / "profiles.json"


class ProfileService:
    def ensure_profiles(self) -> None:
        if PROFILES_PATH.exists():
            return

        payload = {
            "active_profile_id": "local_lizard",
            "profiles": [
                {
                    "id": "local_lizard",
                    "display_name": "Monsieur Souveraineté",
                    "ui_language": "ru",
                    "learning_language": "fr",
                    "voice_id": "mock_fr_female",
                    "rank_id": "recrue",
                    "vulgar_library_enabled": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

        write_json_atomic(PROFILES_PATH, payload)

    def payload(self) -> dict[str, Any]:
        self.ensure_profiles()
        return read_json(PROFILES_PATH)

    def save_payload(self, payload: dict[str, Any]) -> None:
        write_json_atomic(PROFILES_PATH, payload)

    def list_profiles(self) -> list[dict[str, Any]]:
        return self.payload()["profiles"]

    def active_profile(self) -> dict[str, Any]:
        payload = self.payload()
        active_id = payload["active_profile_id"]
        return next(profile for profile in payload["profiles"] if profile["id"] == active_id)

    def update_profile(self, profile_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        payload = self.payload()
        profiles = payload["profiles"]

        for index, profile in enumerate(profiles):
            if profile["id"] == profile_id:
                merged = {**profile, **patch}
                profiles[index] = merged
                self.save_payload(payload)
                return merged

        raise KeyError(f"Profile not found: {profile_id}")


def get_profile_service() -> ProfileService:
    return ProfileService()
