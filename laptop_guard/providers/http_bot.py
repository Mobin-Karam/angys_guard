from __future__ import annotations

import json
import mimetypes
import time
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
from .profiles import ProviderProfile, get_provider_profile


class HttpBotProvider(BotProvider):
    """Single active HTTP adapter for Bale and Telegram Bot APIs.

    ProviderProfile contains the documented request differences. Shared HTTP,
    proxy, timeout, upload, file-download, and error policy lives here so setup
    validation and the running Guard cannot drift into separate transports.
    """

    def __init__(
        self,
        token: str,
        api_base: str = "",
        proxy: str = "",
        provider_name: str = "telegram",
    ) -> None:
        clean_token = str(token or "").strip()
        if not clean_token:
            raise ValueError("Bot token is required. Run ./run.sh setup to configure it.")

        self.profile: ProviderProfile = get_provider_profile(provider_name)
        self.provider_name = self.profile.name
        self.token = clean_token
        self.api_base = (
            str(api_base or "").strip().rstrip("/")
            or self.profile.default_api_base
        )
        self._request_timeout = httpx.Timeout(35.0, connect=10.0)

        kwargs: dict[str, Any] = {
            "timeout": self._request_timeout,
            "trust_env": False,
            "follow_redirects": True,
            "headers": {"User-Agent": "LaptopGuard/11.0"},
        }
        if str(proxy or "").strip():
            configured_proxy = str(proxy).strip()
            if configured_proxy.startswith("socks://"):
                configured_proxy = "socks5://" + configured_proxy[len("socks://"):]
            kwargs["proxy"] = configured_proxy
        try:
            self.client = httpx.Client(**kwargs)
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderConnectionError(
                f"{self.provider_name} client configuration could not be initialized."
            ) from exc

    @property
    def root(self) -> str:
        return f"{self.api_base}/bot{self.token}"

    def _file_url(self, file_path: str) -> str:
        return f"{self.api_base}/file/bot{self.token}/{str(file_path).lstrip('/')}"

    def _credential_rejected(self, method: str, status_code: int | None) -> bool:
        if status_code in {401, 403}:
            return True
        return bool(
            method == "getMe"
            and status_code == 404
            and self.api_base == self.profile.default_api_base
        )

    @staticmethod
    def _serialize_data(data: dict[str, Any] | None) -> dict[str, str]:
        payload: dict[str, str] = {}
        for key, value in (data or {}).items():
            if value is None:
                continue
            if isinstance(value, (dict, list)):
                payload[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, bool):
                payload[key] = "true" if value else "false"
            else:
                payload[key] = str(value)
        return payload

    @staticmethod
    def _retry_after(payload: Any) -> int:
        if not isinstance(payload, dict):
            return 2
        params = payload.get("parameters")
        if not isinstance(params, dict):
            return 2
        try:
            return max(1, min(int(params.get("retry_after") or 2), 15))
        except (TypeError, ValueError):
            return 2

    def _call(
        self,
        method: str,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        *,
        timeout: float | httpx.Timeout | None = None,
        retries: int = 0,
    ) -> Any:
        payload_data = self._serialize_data(data)
        attempts = max(0, int(retries)) + 1

        for attempt in range(attempts):
            try:
                response = self.client.post(
                    f"{self.root}/{method}",
                    data=payload_data,
                    files=files,
                    timeout=timeout or self._request_timeout,
                )
            except httpx.RequestError as exc:
                if attempt + 1 < attempts:
                    time.sleep(min(2 ** attempt, 4))
                    continue
                raise ProviderConnectionError(
                    f"{self.provider_name} {method} could not reach the provider service."
                ) from exc

            payload: Any = None
            try:
                payload = response.json()
            except ValueError:
                payload = None

            if response.status_code == 429 and attempt + 1 < attempts:
                time.sleep(self._retry_after(payload))
                continue
            if response.status_code >= 500 and attempt + 1 < attempts:
                time.sleep(min(2 ** attempt, 4))
                continue

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

            if not isinstance(payload, dict):
                raise ProviderResponseError(
                    f"{self.provider_name} {method} returned an invalid API response."
                )

            if not payload.get("ok", False):
                raw_code = payload.get("error_code")
                try:
                    status_code = int(raw_code) if raw_code is not None else None
                except (TypeError, ValueError):
                    status_code = None

                if status_code == 429 and attempt + 1 < attempts:
                    time.sleep(self._retry_after(payload))
                    continue
                if self._credential_rejected(method, status_code):
                    raise ProviderAuthError(
                        f"{self.provider_name} rejected the bot credential."
                    )
                raise ProviderResponseError(
                    f"{self.provider_name} {method} returned an unsuccessful API response."
                )

            return payload.get("result")

        raise ProviderResponseError(
            f"{self.provider_name} {method} exhausted its bounded retry policy."
        )

    def get_me(self) -> dict[str, Any]:
        result = self._call("getMe", retries=1)
        return result if isinstance(result, dict) else {}

    def get_updates(
        self,
        offset: int | None = None,
        timeout: int = 25,
    ) -> list[dict[str, Any]]:
        bounded_timeout = max(0, min(int(timeout), 120))
        data: dict[str, Any] = {
            "timeout": bounded_timeout,
            "limit": self.profile.update_limit,
        }
        if offset is not None:
            data["offset"] = int(offset)
        result = self._call(
            "getUpdates",
            data=data,
            timeout=max(15, bounded_timeout + 15),
            retries=1,
        )
        return result if isinstance(result, list) else []

    @staticmethod
    def _keyboard(keyboard):
        """Encode the legacy tuple keyboard surface as Bot API JSON."""
        if not keyboard:
            return None
        rows = [
            [{"text": text, "callback_data": data} for text, data in row]
            for row in keyboard
        ]
        return json.dumps({"inline_keyboard": rows}, ensure_ascii=False)

    def _reply_data(self, reply_to_message_id: int | None) -> dict[str, Any]:
        if reply_to_message_id is None:
            return {}
        if self.profile.reply_mode == "reply_parameters":
            return {"reply_parameters": {"message_id": int(reply_to_message_id)}}
        return {"reply_to_message_id": int(reply_to_message_id)}

    def send_message(
        self,
        chat_id: int,
        text: str,
        keyboard=None,
        *,
        reply_markup: dict[str, Any] | None = None,
        reply_to_message_id: int | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {"chat_id": int(chat_id), "text": str(text)}
        if reply_markup is None:
            reply_markup = self._keyboard(keyboard)
        if reply_markup is not None:
            data["reply_markup"] = reply_markup
        data.update(self._reply_data(reply_to_message_id))
        result = self._call("sendMessage", data=data)
        return result if isinstance(result, dict) else {}

    def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        *,
        reply_markup: dict[str, Any] | None = None,
    ) -> Any:
        data: dict[str, Any] = {
            "chat_id": int(chat_id),
            "message_id": int(message_id),
            "text": str(text),
        }
        if reply_markup is not None:
            data["reply_markup"] = reply_markup
        return self._call("editMessageText", data=data)

    def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        keyboard=None,
    ) -> Any:
        """Compatibility alias for the pre-RuntimeApi provider surface."""
        return self.edit_message_text(
            chat_id,
            message_id,
            text,
            reply_markup=self._keyboard(keyboard),
        )

    def delete_message(self, chat_id: int, message_id: int) -> Any:
        return self._call(
            "deleteMessage",
            data={"chat_id": int(chat_id), "message_id": int(message_id)},
        )

    def answer_callback(
        self,
        callback_query_id: str,
        text: str = "",
        show_alert: bool = False,
    ) -> Any:
        data: dict[str, Any] = {
            "callback_query_id": str(callback_query_id),
            "show_alert": bool(show_alert),
        }
        if text:
            data["text"] = str(text)
        try:
            return self._call("answerCallbackQuery", data=data)
        except ProviderError:
            # Callback acknowledgements are best effort and must not take down
            # the guard's polling loop.
            return None

    def send_chat_action(self, chat_id: int, action: str) -> Any:
        return self._call(
            "sendChatAction",
            data={"chat_id": int(chat_id), "action": str(action)},
        )

    def _send_file(
        self,
        method: str,
        field: str,
        chat_id: int,
        path: Path,
        caption: str = "",
        *,
        timeout: int = 180,
        extra_data: dict[str, Any] | None = None,
    ) -> Any:
        path = Path(path)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        safe_name = path.name.encode("ascii", "ignore").decode() or f"upload{path.suffix}"
        data: dict[str, Any] = {"chat_id": int(chat_id)}
        if caption:
            data["caption"] = str(caption)
        if extra_data:
            data.update(extra_data)

        with path.open("rb") as handle:
            files = {field: (safe_name, handle, mime)}
            # Do not automatically retry side-effecting media sends: after a
            # transport failure the server may already have accepted the upload.
            return self._call(
                method,
                data=data,
                files=files,
                timeout=timeout,
                retries=0,
            )

    def send_photo(self, chat_id: int, path: Path, caption: str = "") -> Any:
        return self._send_file("sendPhoto", "photo", chat_id, path, caption)

    def send_video(self, chat_id: int, path: Path, caption: str = "") -> Any:
        extra: dict[str, Any] = {}
        if self.profile.supports_streaming_video_hint:
            extra["supports_streaming"] = True
        return self._send_file(
            "sendVideo",
            "video",
            chat_id,
            path,
            caption,
            timeout=300,
            extra_data=extra,
        )

    def send_audio(self, chat_id: int, path: Path, caption: str = "") -> Any:
        return self._send_file(
            "sendAudio",
            "audio",
            chat_id,
            path,
            caption,
            timeout=180,
        )

    def send_voice(self, chat_id: int, path: Path, caption: str = "") -> Any:
        return self._send_file(
            "sendVoice",
            "voice",
            chat_id,
            path,
            caption,
            timeout=180,
        )

    def send_document(self, chat_id: int, path: Path, caption: str = "") -> Any:
        return self._send_file(
            "sendDocument",
            "document",
            chat_id,
            path,
            caption,
            timeout=300,
        )

    def get_file(self, file_id: str) -> dict[str, Any]:
        result = self._call(
            "getFile",
            data={"file_id": str(file_id)},
            retries=1,
        )
        return result if isinstance(result, dict) else {}

    def download_file(
        self,
        file_id: str,
        destination: Path,
        max_bytes: int | None = None,
    ) -> Path:
        info = self.get_file(file_id)
        file_path = str(info.get("file_path") or "").lstrip("/")
        if not file_path:
            raise ProviderResponseError(
                f"{self.provider_name} getFile returned no file_path."
            )

        provider_limit = self.profile.max_download_bytes
        requested_limit = (
            max(1, int(max_bytes))
            if max_bytes is not None
            else provider_limit
        )
        effective_limit = min(provider_limit, requested_limit)
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        total = 0

        try:
            with self.client.stream(
                "GET",
                self._file_url(file_path),
                timeout=120,
            ) as response:
                response.raise_for_status()
                try:
                    declared = int(response.headers.get("Content-Length") or 0)
                except (TypeError, ValueError):
                    declared = 0
                if declared > effective_limit:
                    raise ProviderResponseError(
                        f"{self.provider_name} file exceeds the allowed download limit."
                    )

                with destination.open("wb") as handle:
                    for chunk in response.iter_bytes(1024 * 128):
                        if not chunk:
                            continue
                        total += len(chunk)
                        if total > effective_limit:
                            raise ProviderResponseError(
                                f"{self.provider_name} file exceeds the allowed download limit."
                            )
                        handle.write(chunk)
        except httpx.RequestError as exc:
            destination.unlink(missing_ok=True)
            raise ProviderConnectionError(
                f"{self.provider_name} file download could not reach the provider service."
            ) from exc
        except httpx.HTTPStatusError as exc:
            destination.unlink(missing_ok=True)
            raise ProviderResponseError(
                f"{self.provider_name} file download returned HTTP {exc.response.status_code}."
            ) from exc
        except Exception:
            destination.unlink(missing_ok=True)
            raise

        return destination
