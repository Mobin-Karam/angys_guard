from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from .base import (
    BotProvider,
    ProviderAuthError,
    ProviderConnectionError,
    ProviderError,
    ProviderResponseError,
)


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
        try:
            self.client = httpx.Client(**kwargs)
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderConnectionError(
                f"{self.provider_name} client configuration could not be initialized."
            ) from exc

    @property
    def root(self) -> str:
        return f"{self.api_base}/bot{self.token}"

    def _credential_rejected(self, method: str, status_code: int | None) -> bool:
        if status_code in {401, 403}:
            return True
        default_bases = {
            "telegram": "https://api.telegram.org",
            "bale": "https://tapi.bale.ai",
        }
        return bool(
            method == "getMe"
            and status_code == 404
            and self.api_base == default_bases.get(self.provider_name)
        )

    def _call(self, method: str, data: dict | None = None, files: dict | None = None) -> dict[str, Any]:
        try:
            response = self.client.post(
                f"{self.root}/{method}",
                data=data or {},
                files=files,
            )
        except httpx.RequestError as exc:
            raise ProviderConnectionError(
                f"{self.provider_name} {method} could not reach the provider service."
            ) from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if self._credential_rejected(method, status_code):
                raise ProviderAuthError(
                    f"{self.provider_name} rejected the bot credential."
                ) from exc
            raise ProviderResponseError(
                f"{self.provider_name} {method} returned HTTP {status_code}."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise ProviderResponseError(
                f"{self.provider_name} {method} returned an invalid API response."
            ) from exc

        if not payload.get("ok", False):
            raw_code = payload.get("error_code")
            try:
                status_code = int(raw_code) if raw_code is not None else None
            except (TypeError, ValueError):
                status_code = None
            if self._credential_rejected(method, status_code):
                raise ProviderAuthError(
                    f"{self.provider_name} rejected the bot credential."
                )
            raise ProviderResponseError(
                f"{self.provider_name} {method} returned an unsuccessful API response."
            )
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
        except httpx.RequestError as exc:
            raise ProviderConnectionError(
                f"{self.provider_name} file download could not reach the provider service."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderResponseError(
                f"{self.provider_name} file download returned HTTP {exc.response.status_code}."
            ) from exc
        return destination

    def answer_callback(self, callback_id: str, text: str = "") -> None:
        data = {"callback_query_id": callback_id}
        if text:
            data["text"] = text
        try:
            self._call("answerCallbackQuery", data=data)
        except ProviderError:
            pass
