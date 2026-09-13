from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Protocol

from .bale_api import BaleApi
from .models import AppConfig


class RuntimeApi(Protocol):
    """Transport contract consumed by the guard runtime.

    Feature code depends on this small contract instead of a concrete HTTP
    library. A future provider only needs an adapter implementing these methods.
    """

    def get_me(self) -> dict[str, Any]: ...
    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list[dict[str, Any]]: ...
    def send_message(self, chat_id: int, text: str, *, reply_markup: dict | None = None) -> Any: ...
    def edit_message_text(self, chat_id: int, message_id: int, text: str, *, reply_markup: dict | None = None) -> Any: ...
    def delete_message(self, chat_id: int, message_id: int) -> Any: ...
    def answer_callback(self, callback_query_id: str, text: str = "", show_alert: bool = False) -> Any: ...
    def send_photo(self, chat_id: int, path: Path, caption: str = "") -> Any: ...
    def send_video(self, chat_id: int, path: Path, caption: str = "") -> Any: ...
    def send_audio(self, chat_id: int, path: Path, caption: str = "") -> Any: ...
    def send_voice(self, chat_id: int, path: Path, caption: str = "") -> Any: ...
    def send_document(self, chat_id: int, path: Path, caption: str = "") -> Any: ...
    def get_file(self, file_id: str) -> dict[str, Any]: ...
    def download_file(self, file_id: str, destination: Path, max_bytes: int | None = None) -> Path: ...


class LocalRuntimeApi:
    """No-network runtime adapter for local-only installations."""

    def get_me(self) -> dict[str, Any]:
        return {"id": "local", "username": "local"}

    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list[dict[str, Any]]:
        time.sleep(max(0.05, min(float(timeout), 1.0)))
        return []

    @staticmethod
    def _ok(*_args, **_kwargs) -> dict[str, bool]:
        return {"ok": True}

    send_message = _ok
    edit_message_text = _ok
    delete_message = _ok
    answer_callback = _ok
    send_photo = _ok
    send_video = _ok
    send_audio = _ok
    send_voice = _ok
    send_document = _ok

    def get_file(self, file_id: str) -> dict[str, Any]:
        return {}

    def download_file(self, file_id: str, destination: Path, max_bytes: int | None = None) -> Path:
        raise RuntimeError("Remote file download is unavailable in local mode")


def build_runtime_api(config: AppConfig, token: str) -> RuntimeApi:
    provider = str(config.bot.provider or "bale").strip().lower()
    if provider == "local":
        return LocalRuntimeApi()
    if provider not in {"bale", "telegram"}:
        raise ValueError(f"Unsupported bot provider: {provider}")
    return BaleApi(
        token,
        base_url=config.bot.api_base,
        proxy=config.bot.proxy,
    )
