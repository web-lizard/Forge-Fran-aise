from pydantic import BaseModel


class AppConfig(BaseModel):
    app_name: str = "Forge Francaise"
    public_title_ru: str = "Имперский мозговыбиватель французского языка"
    version: str = "0.6.0"
    backend_port: int = 8797
    frontend_port: int = 5197
    default_ui_language: str = "ru"
    learning_language: str = "fr"
    vulgar_library_enabled_by_default: bool = True
    tts_engine: str = "edge-with-mock-fallback"


config = AppConfig()
