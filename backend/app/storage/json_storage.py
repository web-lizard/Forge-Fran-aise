from pathlib import Path
from typing import Any

from app.core.json_utils import read_json, write_json_atomic
from app.storage.base import StorageAdapter


class JsonStorage(StorageAdapter):
    def __init__(self, root: Path) -> None:
        self.root = root

    def path_for(self, key: str) -> Path:
        safe_key = key.strip().replace("\\", "/").strip("/")
        return self.root / f"{safe_key}.json"

    def read(self, key: str, default: Any = None) -> Any:
        path = self.path_for(key)
        if not path.exists():
            return default
        return read_json(path)

    def write(self, key: str, payload: Any) -> None:
        write_json_atomic(self.path_for(key), payload)

    def exists(self, key: str) -> bool:
        return self.path_for(key).exists()
