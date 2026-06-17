from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
CONTENT_ROOT = PROJECT_ROOT / "content"
DATA_ROOT = BACKEND_ROOT / "data"
AUDIO_CACHE_ROOT = DATA_ROOT / "audio_cache"
