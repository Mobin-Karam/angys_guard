from __future__ import annotations

import json
import mimetypes
import time
from pathlib import Path
from typing import Any

import requests


class BaleApiError(RuntimeError):
    pass


class BaleApi:
    """Small dependency-light client for Bale's Telegram-style Bot API."""

    def __init__(self, token: str, base_url: str = "https://tapi.bale.ai") -> None:
        if not token:
            raise ValueError("BALE_BOT_TOKEN is required")
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "LaptopGuard/8.0"})

    def _url(self, method: str) -> str:
        return f"{self.base_url}/bot{self.token}/{method}"

    def _file_url(self, file_path: str) -> str:
        return f"{self.base_url}/file/bot{self.token}/{file_path.lstrip('/')}"

    def request(
        self,
        method: str,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        timeout: int = 40,
        retries: int = 3,
    ) -> Any:
        payload_data: dict[str, Any] = {}
        for key, value in (data or {}).items():
            if isinstance(value, (dict, list)):
                payload_data[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, bool):
                payload_data[key] = "true" if value else "false"
            elif value is not None:
                payload_data[key] = str(value)

        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                response = self.session.post(
                    self._url(method),
                    data=payload_data,
                    files=files,
                    timeout=timeout,
                )
                retry_after = None
                try:
                    body = response.json()
                    retry_after = (body.get("parameters") or {}).get("retry_after")
                except ValueError:
                    body = None

                if response.status_code == 429 and attempt < retries:
                    time.sleep(max(1, min(int(retry_after or 2), 15)))
                    continue
                if response.status_code >= 500 and attempt < retries:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                response.raise_for_status()
                if not isinstance(body, dict):
                    raise BaleApiError(f"{method}: invalid JSON response")
                if not body.get("ok"):
                    raise BaleApiError(body.get("description") or f"{method} failed")
                return body.get("result")
            except (requests.RequestException, BaleApiError) as exc:
                last_error = exc
                if attempt >= retries:
                    break
                time.sleep(min(2 ** attempt, 8))
        raise BaleApiError(f"{method}: {last_error}")

    def get_me(self) -> dict[str, Any]:
        return self.request("getMe")

    def get_updates(self, offset: int | None, timeout: int = 25) -> list[dict[str, Any]]:
        data: dict[str, Any] = {"timeout": timeout, "limit": 100}
        if offset is not None:
            data["offset"] = offset
        result = self.request("getUpdates", data=data, timeout=timeout + 15, retries=1)
        return result or []

    def send_message(
        self,
        chat_id: int,
        text: str,
        *,
        reply_markup: dict[str, Any] | None = None,
        reply_to_message_id: int | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            data["reply_markup"] = reply_markup
        if reply_to_message_id is not None:
            data["reply_to_message_id"] = reply_to_message_id
        return self.request("sendMessage", data=data)

    def edit_message_text(self, chat_id: int, message_id: int, text: str, *, reply_markup: dict[str, Any] | None = None) -> Any:
        data: dict[str, Any] = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if reply_markup is not None:
            data["reply_markup"] = reply_markup
        return self.request("editMessageText", data=data)

    def delete_message(self, chat_id: int, message_id: int) -> Any:
        return self.request("deleteMessage", data={"chat_id": chat_id, "message_id": message_id})

    def answer_callback(self, callback_query_id: str, text: str = "", show_alert: bool = False) -> Any:
        return self.request(
            "answerCallbackQuery",
            data={"callback_query_id": callback_query_id, "text": text, "show_alert": show_alert},
        )

    def send_chat_action(self, chat_id: int, action: str) -> Any:
        return self.request("sendChatAction", data={"chat_id": chat_id, "action": action})

    def _send_file(
        self,
        method: str,
        field: str,
        chat_id: int,
        path: Path,
        caption: str = "",
        timeout: int = 180,
    ) -> Any:
        path = Path(path)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        safe_name = path.name.encode("ascii", "ignore").decode() or f"upload{path.suffix}"
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        with path.open("rb") as handle:
            files = {field: (safe_name, handle, mime)}
            return self.request(method, data=data, files=files, timeout=timeout, retries=2)

    def send_photo(self, chat_id: int, path: Path, caption: str = "") -> Any:
        return self._send_file("sendPhoto", "photo", chat_id, path, caption)

    def send_video(self, chat_id: int, path: Path, caption: str = "") -> Any:
        return self._send_file("sendVideo", "video", chat_id, path, caption, timeout=300)

    def send_audio(self, chat_id: int, path: Path, caption: str = "") -> Any:
        return self._send_file("sendAudio", "audio", chat_id, path, caption, timeout=180)

    def send_voice(self, chat_id: int, path: Path, caption: str = "") -> Any:
        return self._send_file("sendVoice", "voice", chat_id, path, caption, timeout=180)

    def send_document(self, chat_id: int, path: Path, caption: str = "") -> Any:
        return self._send_file("sendDocument", "document", chat_id, path, caption, timeout=300)

    def get_file(self, file_id: str) -> dict[str, Any]:
        return self.request("getFile", data={"file_id": file_id})

    def download_file(self, file_id: str, destination: Path) -> Path:
        meta = self.get_file(file_id)
        file_path = str(meta.get("file_path") or "")
        if not file_path:
            raise BaleApiError("getFile returned no file_path")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with self.session.get(self._file_url(file_path), stream=True, timeout=120) as response:
            response.raise_for_status()
            with destination.open("wb") as out:
                for chunk in response.iter_content(1024 * 128):
                    if chunk:
                        out.write(chunk)
        return destination
