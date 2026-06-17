from pydantic import BaseModel


class AppSettings(BaseModel):
    app_name: str
    public_title_ru: str
    version: str
    backend_port: int
    frontend_port: int
    default_ui_language: str
    learning_language: str
    vulgar_library_enabled_by_default: bool
    tts_engine: str
