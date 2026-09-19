from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ProviderError(RuntimeError):
    """Base class for token-safe provider failures."""


class ProviderAuthError(ProviderError):
    """The remote provider rejected the configured credential."""


class ProviderConnectionError(ProviderError):
    """The provider could not be reached because of network/proxy/TLS transport."""


class ProviderResponseError(ProviderError):
    """The provider returned an unexpected HTTP/API response."""


class BotProvider(ABC):
    @abstractmethod
    def get_me(self) -> dict[str, Any]: ...

    @abstractmethod
    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list[dict[str, Any]]: ...

    @abstractmethod
    def send_message(self, chat_id: int, text: str, keyboard: list[list[tuple[str, str]]] | None = None) -> dict[str, Any]: ...

    @abstractmethod
    def edit_message(self, chat_id: int, message_id: int, text: str, keyboard: list[list[tuple[str, str]]] | None = None) -> dict[str, Any]: ...

    @abstractmethod
    def send_photo(self, chat_id: int, path: Path, caption: str = "") -> dict[str, Any]: ...

    @abstractmethod
    def send_voice(self, chat_id: int, path: Path, caption: str = "") -> dict[str, Any]: ...

    @abstractmethod
    def send_video(self, chat_id: int, path: Path, caption: str = "") -> dict[str, Any]: ...

    @abstractmethod
    def download_file(self, file_id: str, destination: Path) -> Path: ...

    @abstractmethod
    def answer_callback(self, callback_id: str, text: str = "") -> None: ...
