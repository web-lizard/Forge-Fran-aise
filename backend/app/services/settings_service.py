from app.core.config import config


class SettingsService:
    def app_settings(self) -> dict:
        return config.model_dump()


def get_settings_service() -> SettingsService:
    return SettingsService()
