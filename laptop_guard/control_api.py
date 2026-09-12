from __future__ import annotations

import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from .config import MEDIA_DIR


class LocalControlAPI:
    """Small authenticated local API.

    Default bind is 127.0.0.1. It intentionally exposes a narrow action set and
    never provides shell-command execution.
    """

    def __init__(
        self,
        host: str,
        port: int,
        token: str,
        status_cb: Callable[[], dict],
        chat_cb: Callable[[str], None],
        say_cb: Callable[[str], None],
        warning_cb: Callable[[str, int], None],
        play_audio_cb: Callable[[Path], None],
        max_upload_mb: int = 20,
        screen_snapshot_cb: Callable[[], tuple[Path | None, str]] | None = None,
        record_voice_cb: Callable[[int], tuple[Path | None, str]] | None = None,
    ) -> None:
        self.host = host
        self.port = int(port)
        self.token = token
        self.status_cb = status_cb
        self.chat_cb = chat_cb
        self.say_cb = say_cb
        self.warning_cb = warning_cb
        self.play_audio_cb = play_audio_cb
        self.max_upload = max(1, int(max_upload_mb)) * 1024 * 1024
        self.screen_snapshot_cb = screen_snapshot_cb
        self.record_voice_cb = record_voice_cb
        self.server: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "LaptopGuardAPI/1"
            def log_message(self, fmt, *args):
                return
            def _auth(self) -> bool:
                auth = self.headers.get("Authorization", "")
                return secrets.compare_digest(auth, f"Bearer {outer.token}")
            def _json(self, code: int, payload: dict):
                data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            def _binary(self, code: int, data: bytes, content_type: str):
                self.send_response(code); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            def _body_json(self):
                length = min(int(self.headers.get("Content-Length", "0") or 0), 1_000_000)
                return json.loads(self.rfile.read(length) or b"{}")
            def do_GET(self):
                if not self._auth(): self._json(401, {"ok": False, "error": "unauthorized"}); return
                if self.path == "/v1/status": self._json(200, {"ok": True, "result": outer.status_cb()}); return
                if self.path == "/v1/screen/snapshot" and outer.screen_snapshot_cb:
                    path, detail = outer.screen_snapshot_cb()
                    if path and path.exists(): self._binary(200, path.read_bytes(), "image/png")
                    else: self._json(503, {"ok": False, "error": detail})
                    return
                self._json(404, {"ok": False, "error": "not_found"})
            def do_POST(self):
                if not self._auth(): self._json(401, {"ok": False, "error": "unauthorized"}); return
                try:
                    if self.path == "/v1/chat":
                        body = self._body_json(); outer.chat_cb(str(body.get("text") or "")); self._json(200, {"ok": True}); return
                    if self.path == "/v1/say":
                        body = self._body_json(); outer.say_cb(str(body.get("text") or "")); self._json(200, {"ok": True}); return
                    if self.path == "/v1/warning":
                        body = self._body_json(); outer.warning_cb(str(body.get("text") or ""), int(body.get("seconds") or 30)); self._json(200, {"ok": True}); return
                    if self.path == "/v1/voice/record" and outer.record_voice_cb:
                        body = self._body_json(); seconds = max(1, min(int(body.get("seconds") or 10), 300))
                        path, detail = outer.record_voice_cb(seconds)
                        if path and path.exists(): self._binary(200, path.read_bytes(), "audio/ogg")
                        else: self._json(503, {"ok": False, "error": detail})
                        return
                    if self.path == "/v1/voice/play":
                        length = int(self.headers.get("Content-Length", "0") or 0)
                        if length <= 0 or length > outer.max_upload:
                            self._json(413, {"ok": False, "error": "invalid_size"}); return
                        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
                        path = MEDIA_DIR / "api-voice-upload.ogg"
                        path.write_bytes(self.rfile.read(length))
                        outer.play_audio_cb(path); self._json(200, {"ok": True}); return
                    self._json(404, {"ok": False, "error": "not_found"})
                except Exception as exc:
                    self._json(400, {"ok": False, "error": str(exc)})

        self.server = ThreadingHTTPServer((self.host, self.port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True, name="local-control-api")
        self.thread.start()

    def stop(self) -> None:
        if self.server:
            self.server.shutdown(); self.server.server_close(); self.server = None
