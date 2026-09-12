from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from .base import BotProvider, ProviderError


class HttpBotProvider(BotProvider):
    def __init__(self, token: str, api_base: str, proxy: str = "", provider_name: str = "telegram") -> None:
        self.token = token.strip()
        self.api_base = api_base.rstrip("/")
        self.provider_name = provider_name
        kwargs: dict[str, Any] = {
            "timeout": httpx.Timeout(35.0, connect=10.0),
            "trust_env": False,
            "follow_redirects": True,
        }
        if proxy.strip():
            p = proxy.strip()
            if p.startswith("socks://"):
                p = "socks5://" + p[len("socks://"):]
            kwargs["proxy"] = p
        self.client = httpx.Client(**kwargs)

    @property
    def root(self) -> str:
        return f"{self.api_base}/bot{self.token}"

    def _call(self, method: str, data: dict | None = None, files: dict | None = None) -> dict[str, Any]:
        try:
            response = self.client.post(f"{self.root}/{method}", data=data or {}, files=files)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"{self.provider_name} {method} failed: {exc}") from exc
        if not payload.get("ok", False):
            raise ProviderError(str(payload.get("description") or payload))
        return payload.get("result") or {}

    def get_me(self) -> dict[str, Any]:
        return self._call("getMe")

    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list[dict[str, Any]]:
        data = {"timeout": str(timeout)}
        if offset is not None:
            data["offset"] = str(offset)
        result = self._call("getUpdates", data=data)
        return result if isinstance(result, list) else []

    def _keyboard(self, keyboard):
        if not keyboard:
            return None
        rows = []
        for row in keyboard:
            rows.append([{"text": text, "callback_data": data} for text, data in row])
        return json.dumps({"inline_keyboard": rows}, ensure_ascii=False)

    def send_message(self, chat_id: int, text: str, keyboard=None) -> dict[str, Any]:
        data = {"chat_id": str(chat_id), "text": text}
        markup = self._keyboard(keyboard)
        if markup:
            data["reply_markup"] = markup
        return self._call("sendMessage", data=data)

    def edit_message(self, chat_id: int, message_id: int, text: str, keyboard=None) -> dict[str, Any]:
        data = {"chat_id": str(chat_id), "message_id": str(message_id), "text": text}
        markup = self._keyboard(keyboard)
        if markup:
            data["reply_markup"] = markup
        return self._call("editMessageText", data=data)

    def send_photo(self, chat_id: int, path: Path, caption: str = "") -> dict[str, Any]:
        with path.open("rb") as fh:
            return self._call(
                "sendPhoto",
                data={"chat_id": str(chat_id), "caption": caption},
                files={"photo": (path.name, fh, "image/jpeg")},
            )

    def send_voice(self, chat_id: int, path: Path, caption: str = "") -> dict[str, Any]:
        with path.open("rb") as fh:
            return self._call(
                "sendVoice",
                data={"chat_id": str(chat_id), "caption": caption},
                files={"voice": (path.name, fh, "audio/ogg")},
            )

    def send_video(self, chat_id: int, path: Path, caption: str = "") -> dict[str, Any]:
        with path.open("rb") as fh:
            return self._call(
                "sendVideo",
                data={"chat_id": str(chat_id), "caption": caption, "supports_streaming": "true"},
                files={"video": (path.name, fh, "video/mp4")},
            )


    def get_file(self, file_id: str) -> dict[str, Any]:
        result = self._call("getFile", data={"file_id": file_id})
        return result if isinstance(result, dict) else {}

    def download_file(self, file_id: str, destination: Path) -> Path:
        info = self.get_file(file_id)
        file_path = str(info.get("file_path") or "").lstrip("/")
        if not file_path:
            raise ProviderError(f"{self.provider_name} getFile returned no file_path")
        url = f"{self.api_base}/file/bot{self.token}/{file_path}"
        try:
            with self.client.stream("GET", url) as response:
                response.raise_for_status()
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("wb") as fh:
                    for chunk in response.iter_bytes():
                        fh.write(chunk)
        except httpx.HTTPError as exc:
            raise ProviderError(f"{self.provider_name} file download failed: {exc}") from exc
        return destination

    def answer_callback(self, callback_id: str, text: str = "") -> None:
        data = {"callback_query_id": callback_id}
        if text:
            data["text"] = text
        try:
            self._call("answerCallbackQuery", data=data)
        except ProviderError:
            pass
