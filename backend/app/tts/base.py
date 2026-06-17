from abc import ABC, abstractmethod
from pathlib import Path

from app.models.audio import AudioRequest, Voice


class TTSProvider(ABC):
    @abstractmethod
    def voices(self) -> list[Voice]:
        raise NotImplementedError

    @abstractmethod
    def synthesize(self, request: AudioRequest, output_path: Path) -> int:
        raise NotImplementedError
