from __future__ import annotations

import json
import math
import os
import platform
import signal
import sys
import shutil
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
from pynput import keyboard, mouse

from .audio_intercom import AudioIntercom, notify, play_audio, record_audio
from .bale_api import BaleApi, BaleApiError
from .chat_surface import SecurityChatManager
from .config import MEDIA_DIR, AppConfig, load_config
from .events import EventLog
from .persian_speech import PersianSpeechManager, SpeechResult, VOICE_NAMES
from .screen_capture import ScreenCapture
from .warning_sequence import dismiss_warning, launch_warning
from .system_actions import (
    lock_screen as native_lock_screen,
    poweroff_system,
    reboot_system,
    suspend_system,
    system_snapshot,
    unlock_screen as native_unlock_screen,
)


def inline_keyboard(rows: list[list[tuple[str, str]]]) -> dict[str, Any]:
    return {
        "inline_keyboard": [
            [{"text": text, "callback_data": data} for text, data in row]
            for row in rows
        ]
    }


MAIN_MENU = inline_keyboard(
    [
        [("🛡 محافظت", "menu:security"), ("📷 دوربین", "menu:camera")],
        [("🖥 صفحه", "menu:screen"), ("🎙 صدا", "menu:audio")],
        [("💬 گفتگو", "menu:chat"), ("📜 رویدادها", "events:recent")],
        [("💻 سیستم", "menu:system"), ("⚡ برق", "menu:power")],
        [("🩺 وضعیت", "status:show")],
    ]
)


class GuardState:
    def __init__(self) -> None:
        self.armed = False
        self.grace_until = 0.0
        self.arm_ready_at = 0.0
        self.last_input_alert = 0.0
        self.last_motion_alert = 0.0
        self.last_input_kind = ""
        self.camera_ok = False

    def active(self) -> bool:
        now = time.monotonic()
        return self.armed and now >= self.arm_ready_at and now >= self.grace_until


class LaptopGuard:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        self.api = BaleApi(self.config.bale.token, self.config.bale.api_base)
        self.state = GuardState()
        self.state_lock = threading.RLock()
        self.stop_event = threading.Event()
        self.events = EventLog()
        self.screen = ScreenCapture()
        self.chat = SecurityChatManager(visitor_callback=self._visitor_text)
        self.intercom = AudioIntercom(self._send_intercom_chunk, self.config.audio.intercom_chunk_seconds)
        self.tts = PersianSpeechManager(
            default_voice=self.config.tts.voice,
            rate_limit=self.config.tts.rate_limit,
            max_chars=self.config.tts.max_chars,
            show_notification=self.config.tts.show_notification,
        )
        self._awaiting_tts_text = False
        self._tts_text_mode = False
        self.last_frame = None
        self.frame_lock = threading.Lock()
        self.mouse_anchor: tuple[float, float] | None = None
        self.camera_thread: threading.Thread | None = None
        self.keyboard_listener = None
        self.mouse_listener = None
        self.warning_proc: subprocess.Popen | None = None
        self._lock_generation = 0
        self._offset: int | None = None
        self._send_lock = threading.Lock()
        self._watchdog_proc: subprocess.Popen | None = None
        self._exit_lock_requested = False

    # --------------------------- authorization / send helpers

    def _authorized(self, chat_id: int | None) -> bool:
        return self.config.bale.chat_id is not None and chat_id == self.config.bale.chat_id

    def _owner_chat(self) -> int | None:
        return self.config.bale.chat_id

    def _send(self, text: str, markup: dict | None = None) -> None:
        chat_id = self._owner_chat()
        if chat_id is None:
            return
        try:
            with self._send_lock:
                self.api.send_message(chat_id, text, reply_markup=markup)
        except Exception as exc:
            print(f"[bale] send failed: {exc}")

    def _send_async(self, text: str, markup: dict | None = None) -> None:
        threading.Thread(target=self._send, args=(text, markup), daemon=True).start()

    def _send_file_async(self, kind: str, path: Path, caption: str = "") -> None:
        chat_id = self._owner_chat()
        if chat_id is None:
            return

        def worker() -> None:
            try:
                if kind == "photo":
                    self.api.send_photo(chat_id, path, caption)
                elif kind == "video":
                    self.api.send_video(chat_id, path, caption)
                elif kind == "voice":
                    self.api.send_voice(chat_id, path, caption)
                elif kind == "audio":
                    self.api.send_audio(chat_id, path, caption)
                else:
                    self.api.send_document(chat_id, path, caption)
            except Exception as exc:
                print(f"[bale] media send failed: {exc}")

        threading.Thread(target=worker, daemon=True, name=f"send-{kind}").start()

    # --------------------------- OS actions

    @staticmethod
    def _run_first(commands: list[list[str]]) -> bool:
        for cmd in commands:
            if not shutil.which(cmd[0]) and os.path.sep not in cmd[0]:
                continue
            try:
                result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
                if result.returncode == 0:
                    return True
            except Exception:
                continue
        return False

    def lock_screen(self) -> bool:
        return native_lock_screen()

    def unlock_screen(self) -> tuple[bool, str]:
        if not self.config.security.allow_remote_unlock:
            return False, "Remote unlock is disabled. Set ALLOW_REMOTE_UNLOCK=true to opt in."
        ok, detail = native_unlock_screen()
        if ok:
            # Avoid immediately retriggering the guard while the owner resumes use.
            self.allow_for(2)
            self.events.add("unlock", "Owner requested remote session unlock", "high")
        return ok, detail

    # --------------------------- guard state

    def arm(self) -> None:
        with self.state_lock:
            self.state.armed = True
            self.state.grace_until = 0.0
            self.state.arm_ready_at = time.monotonic() + self.config.security.arm_delay
            self.mouse_anchor = None
        self.events.add("arm", "Guard armed")

    def _cancel_pending_lock(self) -> None:
        self._lock_generation += 1
        dismiss_warning(self.warning_proc)
        self.warning_proc = None

    def disarm(self) -> None:
        self._cancel_pending_lock()
        with self.state_lock:
            self.state.armed = False
            self.state.grace_until = 0.0
            self.mouse_anchor = None
        self.events.add("disarm", "Guard disarmed")

    def allow_for(self, minutes: int) -> None:
        self._cancel_pending_lock()
        minutes = max(1, min(int(minutes), 120))
        with self.state_lock:
            self.state.grace_until = time.monotonic() + minutes * 60
            self.mouse_anchor = None
        self.events.add("grace", f"Local use allowed for {minutes} minutes")

    # --------------------------- warning / input detection

    def _camera_snapshot_file(self, prefix: str = "camera") -> Path | None:
        with self.frame_lock:
            frame = None if self.last_frame is None else self.last_frame.copy()
        if frame is None:
            return None
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        path = MEDIA_DIR / f"{prefix}-{datetime.now():%Y%m%d-%H%M%S-%f}.jpg"
        if cv2.imwrite(str(path), frame, [cv2.IMWRITE_JPEG_QUALITY, 88]):
            return path
        return None

    def _capture_input_evidence(self, event_stamp: str) -> None:
        if self.config.security.camera_snapshot_on_input:
            path = self._camera_snapshot_file("intrusion")
            if path:
                self.events.add("camera_evidence", event_stamp, "high", str(path))
                self._send_file_async("photo", path, f"📷 تصویر رویداد امنیتی • {event_stamp}")
        if self.config.security.screen_snapshot_on_input:
            path, backend = self.screen.screenshot()
            if path:
                self.events.add("screen_evidence", f"{event_stamp}; {backend}", "high", str(path))
                self._send_file_async("photo", path, f"🖥 اسکرین‌شات رویداد • {event_stamp}")

    def trigger_input_alert(self, kind: str) -> None:
        now = time.monotonic()
        with self.state_lock:
            if not self.state.active():
                return
            if now - self.state.last_input_alert < self.config.security.input_cooldown:
                return
            self.state.last_input_alert = now
            self.state.last_input_kind = kind
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.events.add("input", f"{kind} at {stamp}", "high")
        self._lock_generation += 1
        generation = self._lock_generation

        self._send_async(
            f"🚨 فعالیت روی لپ‌تاپ شناسایی شد\n\nنوع: {kind}\nزمان: {stamp}\n"
            f"هشدار {self.config.security.warning_seconds} ثانیه‌ای نمایش داده می‌شود و سپس سیستم قفل خواهد شد.",
            inline_keyboard([
                [("🕐 اجازه ۵ دقیقه", "guard:allow:5"), ("🔒 قفل الآن", "guard:lock")],
                [("⛔ غیرفعال", "guard:disarm"), ("📷 عکس", "camera:photo")],
            ]),
        )
        threading.Thread(target=self._capture_input_evidence, args=(stamp,), daemon=True).start()

        if self.config.security.warning_images:
            self.warning_proc = launch_warning(self.config.security.warning_seconds)
        else:
            notify(f"هشدار امنیتی: {kind}; قفل در {self.config.security.warning_seconds} ثانیه")

        def countdown_lock() -> None:
            if self.stop_event.wait(self.config.security.warning_seconds):
                return
            if generation != self._lock_generation:
                return
            with self.state_lock:
                should_lock = self.state.active() and self.config.security.lock_after_warning
            if not should_lock:
                return
            locked = self.lock_screen()
            self.events.add("lock", f"automatic lock after {kind}; ok={locked}", "critical" if locked else "high")
            self._send_async("🔒 شمارش پایان یافت. " + ("سیستم قفل شد." if locked else "قفل سیستم ناموفق بود."))

        threading.Thread(target=countdown_lock, daemon=True, name="warning-countdown-lock").start()

    def on_key_press(self, _key) -> None:
        self.trigger_input_alert("keyboard")

    def on_mouse_click(self, _x, _y, button, pressed) -> None:
        if pressed:
            self.trigger_input_alert(f"mouse click ({button})")

    def on_mouse_scroll(self, _x, _y, _dx, _dy) -> None:
        self.trigger_input_alert("mouse scroll")

    def on_mouse_move(self, x, y) -> None:
        with self.state_lock:
            if not self.state.active():
                self.mouse_anchor = (x, y)
                return
            if self.mouse_anchor is None:
                self.mouse_anchor = (x, y)
                return
            ax, ay = self.mouse_anchor
            if math.hypot(x - ax, y - ay) < self.config.security.mouse_move_threshold:
                return
            self.mouse_anchor = (x, y)
        self.trigger_input_alert("mouse movement")

    # --------------------------- camera

    def camera_worker(self) -> None:
        cap = cv2.VideoCapture(self.config.camera.index)
        if not cap.isOpened():
            print(f"[camera] cannot open index {self.config.camera.index}")
            self._send_async(f"⚠️ دوربین {self.config.camera.index} قابل دسترسی نیست.")
            return
        with self.state_lock:
            self.state.camera_ok = True
        subtractor = cv2.createBackgroundSubtractorMOG2(history=350, varThreshold=35, detectShadows=True)
        warmup = max(12, self.config.camera.fps * 2)
        count = 0
        sleep_for = max(0.03, 1.0 / self.config.camera.fps)
        try:
            while not self.stop_event.is_set():
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.3)
                    continue
                with self.frame_lock:
                    self.last_frame = frame.copy()
                count += 1
                if count <= warmup:
                    subtractor.apply(frame)
                    time.sleep(sleep_for)
                    continue
                with self.state_lock:
                    active = self.state.active()
                if not active or not self.config.camera.motion_enabled:
                    subtractor.apply(frame, learningRate=0.01)
                    time.sleep(sleep_for)
                    continue
                h, w = frame.shape[:2]
                if w > 640:
                    scale = 640 / w
                    small = cv2.resize(frame, (640, int(h * scale)), interpolation=cv2.INTER_AREA)
                else:
                    small = frame
                fg = subtractor.apply(small)
                fg = cv2.GaussianBlur(fg, (5, 5), 0)
                _, mask = cv2.threshold(fg, 210, 255, cv2.THRESH_BINARY)
                mask = cv2.dilate(mask, None, iterations=2)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                moving = any(cv2.contourArea(c) >= self.config.camera.motion_min_area for c in contours)
                now = time.monotonic()
                if moving:
                    with self.state_lock:
                        can = now - self.state.last_motion_alert >= self.config.camera.motion_cooldown
                        if can:
                            self.state.last_motion_alert = now
                    if can:
                        path = self._camera_snapshot_file("motion")
                        if path:
                            self.events.add("motion", "Motion detected near laptop", "medium", str(path))
                            self._send_file_async("photo", path, f"📷 حرکت نزدیک لپ‌تاپ • {datetime.now():%H:%M:%S}")
                time.sleep(sleep_for)
        finally:
            cap.release()
            with self.state_lock:
                self.state.camera_ok = False

    # --------------------------- audio / chat

    def _send_intercom_chunk(self, path: Path, kind: str) -> None:
        chat_id = self._owner_chat()
        if chat_id is None:
            return
        if kind == "voice":
            self.api.send_voice(chat_id, path, "🎙 صدای زنده از Laptop Guard")
        elif kind == "audio":
            self.api.send_audio(chat_id, path, "🎙 صدای زنده از Laptop Guard")
        else:
            self.api.send_document(chat_id, path, "🎙 صدای ضبط‌شده از Laptop Guard")

    def _visitor_text(self, text: str) -> None:
        self._send_async(f"💬 پاسخ از لپ‌تاپ:\n{text}")

    def _play_owner_voice(self, file_id: str) -> None:
        def worker() -> None:
            try:
                meta = self.api.get_file(file_id)
                suffix = Path(str(meta.get("file_path") or "voice.ogg")).suffix or ".ogg"
                path = MEDIA_DIR / f"owner-voice-{datetime.now():%Y%m%d-%H%M%S-%f}{suffix}"
                # Avoid a second getFile call by downloading directly from metadata.
                file_path = str(meta.get("file_path") or "")
                if not file_path:
                    return
                with self.api.session.get(self.api._file_url(file_path), stream=True, timeout=120) as response:
                    response.raise_for_status()
                    with path.open("wb") as out:
                        for chunk in response.iter_content(131072):
                            if chunk:
                                out.write(chunk)
                notify("پیام صوتی مالک در حال پخش است")
                ok = play_audio(path)
                self.events.add("owner_voice", f"played={ok}", "info", str(path))
            except Exception as exc:
                self._send_async(f"⚠️ پخش Voice ناموفق بود: {exc}")

        threading.Thread(target=worker, daemon=True, name="owner-voice-playback").start()

    def _tts_result(self, chat_id: int, result: SpeechResult) -> None:
        if result.ok:
            self.events.add("tts", f"voice={result.voice}; chars={len(result.text)}", "info", str(result.path or ""))
            self._reply_to_chat(chat_id, f"✅ متن با صدای {VOICE_NAMES.get(result.voice, result.voice)} روی لپ‌تاپ پخش شد.")
        else:
            self.events.add("tts_error", result.error, "medium")
            self._reply_to_chat(chat_id, f"⚠️ تبدیل متن به صدا ناموفق بود: {result.error}")

    def _speak_text(self, chat_id: int, text: str, voice: str | None = None) -> None:
        if not self.config.tts.enabled:
            self._reply_to_chat(chat_id, "🗣 Persian TTS غیرفعال است. PERSIAN_TTS_ENABLED=true را در .env قرار دهید.")
            return
        clean = str(text or "").strip()
        if not clean:
            self._reply_to_chat(chat_id, "متن را بفرستید؛ مثال:\n/say سلام، لطفاً از لپ‌تاپ فاصله بگیرید.")
            return
        if self.config.tts.mirror_to_chat and self.chat.active:
            self.chat.send_owner("🔊 " + clean, self.config.chat.seconds)
        ok, detail = self.tts.submit(
            clean,
            voice=voice,
            callback=lambda result: self._tts_result(chat_id, result),
        )
        if ok:
            self._reply_to_chat(chat_id, "🗣 " + detail)
        else:
            self._reply_to_chat(chat_id, "⚠️ " + detail)

    # --------------------------- UI / commands

    def status_text(self) -> str:
        with self.state_lock:
            armed = self.state.armed
            camera_ok = self.state.camera_ok
            last = self.state.last_input_kind or "—"
            grace_s = max(0, int(self.state.grace_until - time.monotonic()))
        return (
            "🩺 وضعیت Laptop Guard\n\n"
            f"🛡 محافظت: {'فعال' if armed else 'غیرفعال'}\n"
            f"📷 دوربین: {'آماده' if camera_ok else 'غیرفعال/ناموجود'}\n"
            f"🎙 مکالمه صوتی: {'فعال' if self.intercom.active else 'خاموش'}\n"
            f"🗣 Persian TTS: {'آماده' if self.config.tts.enabled and self.tts.available else 'غیرفعال/ناموجود'} • {self.tts.default_voice}\n"
            f"💬 گفت‌وگوی محلی: {'باز' if self.chat.active else 'بسته'}\n"
            f"🕐 اجازه محلی: {grace_s // 60}:{grace_s % 60:02d}\n"
            f"⌨️ آخرین فعالیت: {last}\n"
            f"🔐 قفل هنگام خروج Guard: {'فعال' if self.config.security.lock_on_guard_exit else 'غیرفعال'}\n"
            f"🔓 Remote unlock: {'فعال' if self.config.security.allow_remote_unlock else 'غیرفعال'}\n"
            f"💻 سیستم: {platform.system()} {platform.release()}"
        )

    def security_menu(self) -> tuple[str, dict]:
        unlock_label = "🔓 Unlock" if self.config.security.allow_remote_unlock else "🔓 Unlock (OFF)"
        return (
            "🛡 کنترل محافظت\nهشدار تصویری ۵ مرحله‌ای قبل از قفل فعال است.",
            inline_keyboard([
                [("✅ فعال‌سازی", "guard:arm"), ("⛔ غیرفعال", "guard:disarm")],
                [("🕐 اجازه ۵ دقیقه", "guard:allow:5"), ("🔒 قفل الآن", "guard:lock")],
                [(unlock_label, "guard:unlock:confirm")],
                [("⬅️ منوی اصلی", "menu:main")],
            ]),
        )

    def camera_menu(self) -> tuple[str, dict]:
        return (
            "📷 دوربین\nعکس لحظه‌ای و رویدادهای Motion از این بخش در دسترس است.",
            inline_keyboard([
                [("📸 عکس الآن", "camera:photo"), ("🎥 ویدیوی ۸s", "camera:video:8")],
                [("⬅️ منوی اصلی", "menu:main")],
            ]),
        )

    def screen_menu(self) -> tuple[str, dict]:
        return (
            "🖥 صفحه‌نمایش\nScreenshot و ضبط کوتاه صفحه با ابزارهای بومی Linux انجام می‌شود.",
            inline_keyboard([
                [("📸 Screenshot", "screen:shot"), ("🎥 8s Video", "screen:video:8")],
                [("⬅️ منوی اصلی", "menu:main")],
            ]),
        )

    def audio_menu(self) -> tuple[str, dict]:
        tts_state = "آماده" if self.config.tts.enabled and self.tts.available else "غیرفعال/ناموجود"
        return (
            "🎙 صدا و گفتار\n"
            "Voice Intercom در Bale با بسته‌های صوتی کوتاه کار می‌کند؛ تماس RTP/WebRTC واقعی نیست.\n"
            f"🗣 Persian TTS: {tts_state} • صدا: {self.tts.default_voice}",
            inline_keyboard([
                [("🗣 متن → صدا", "tts:prompt"), ("🎚 انتخاب صدا", "tts:menu")],
                [("🔊 تست TTS", "tts:test"), ("🎧 شنود ۸ ثانیه", "audio:listen:8")],
                [("🗣 مکالمه ۳۰ ثانیه", "audio:intercom:30"), ("⏹ توقف", "audio:stop")],
                [("⬅️ منوی اصلی", "menu:main")],
            ]),
        )

    def tts_menu(self) -> tuple[str, dict]:
        current = self.tts.default_voice
        lines = [
            "🗣 تبدیل متن فارسی به صدا",
            f"صدای فعلی: {VOICE_NAMES.get(current, current)} ({current})",
            f"حالت متن مستقیم: {'روشن' if self._tts_text_mode else 'خاموش'}",
            "«متن → صدا» فقط پیام بعدی را پخش می‌کند؛ حالت مستقیم همه پیام‌های عادی را تا زمان خاموش‌کردن می‌خواند.",
        ]
        rows: list[list[tuple[str, str]]] = []
        choices = list(VOICE_NAMES.items())
        for i in range(0, len(choices), 3):
            row = []
            for key, name in choices[i:i+3]:
                marker = "✓ " if key == current else ""
                row.append((f"{marker}{name}", f"tts:voice:{key}"))
            rows.append(row)
        rows.append([("🗣 متن → صدا", "tts:prompt"), ("🔊 تست", "tts:test")])
        rows.append([(("⏹ خاموش‌کردن متن مستقیم" if self._tts_text_mode else "🔁 روشن‌کردن متن مستقیم"), "tts:mode:toggle")])
        rows.append([("⬅️ صدا", "menu:audio")])
        return "\n".join(lines), inline_keyboard(rows)

    def chat_menu(self) -> tuple[str, dict]:
        state = "فعال" if self.chat.active else "بسته"
        return (
            "💬 گفت‌وگوی امنیتی / Security Chat\n"
            f"وضعیت: {state}\n"
            "پیام‌های فارسی/عربی/عبری و انگلیسی به‌صورت خودکار RTL/LTR نمایش داده می‌شوند. "
            "وقتی پنجره باز است، هر متن عادی که در بله بفرستید مستقیماً به لپ‌تاپ می‌رسد.",
            inline_keyboard([
                [("💬 باز کردن گفتگو", "chat:open"), ("✖️ بستن گفتگو", "chat:close")],
                [("🔔 پیام محلی", "system:notify:prompt")],
                [("⬅️ منوی اصلی", "menu:main")],
            ]),
        )

    def system_menu(self) -> tuple[str, dict]:
        return (
            "💻 کنترل سیستم\nاطلاعات دستگاه، اعلان محلی، قفل و Unlock اختیاری از این بخش در دسترس است.",
            inline_keyboard([
                [("🩺 اطلاعات سیستم", "system:info"), ("🔒 قفل", "guard:lock")],
                [("🔓 Unlock", "guard:unlock:confirm"), ("⚠️ تست هشدار", "system:warning:test")],
                [("⬅️ منوی اصلی", "menu:main")],
            ]),
        )

    def power_menu(self) -> tuple[str, dict]:
        if not self.config.security.allow_remote_power:
            return (
                "⚡ Power controls\nRemote Suspend/Restart/Shutdown غیرفعال است. "
                "برای فعال‌سازی ALLOW_REMOTE_POWER=true را در .env قرار دهید.",
                inline_keyboard([[("⬅️ منوی اصلی", "menu:main")]]),
            )
        return (
            "⚡ Power controls\nعملیات Suspend/Restart/Shutdown نیاز به تأیید دوم دارند.",
            inline_keyboard([
                [("🌙 Suspend", "power:suspend:confirm")],
                [("🔄 Restart", "power:reboot:confirm"), ("⏻ Shutdown", "power:off:confirm")],
                [("⬅️ منوی اصلی", "menu:main")],
            ]),
        )

    def system_info_text(self) -> str:
        info = system_snapshot()
        return (
            "💻 اطلاعات سیستم / System info\n\n"
            f"Host: {info.get('hostname')}\n"
            f"OS: {info.get('os')}\n"
            f"Arch: {info.get('arch')}\n"
            f"CPU: {info.get('cpu')}\n"
            f"Memory: {info.get('memory')}\n"
            f"Disk: {info.get('disk')}\n"
            f"Battery: {info.get('battery')}\n"
            f"Uptime: {info.get('uptime')}\n"
            f"Python: {info.get('python')}"
        )

    def _reply_to_chat(self, chat_id: int, text: str, markup: dict | None = None) -> None:
        try:
            self.api.send_message(chat_id, text, reply_markup=markup)
        except Exception as exc:
            print(f"[bale] reply failed: {exc}")

    def _edit_or_reply(self, chat_id: int, message_id: int | None, text: str, markup: dict | None = None) -> None:
        if message_id is not None:
            try:
                self.api.edit_message_text(chat_id, message_id, text, reply_markup=markup)
                return
            except Exception:
                pass
        self._reply_to_chat(chat_id, text, markup)

    def _notify_local(self, text: str) -> None:
        clean = str(text).strip()[:500]
        if not clean:
            return
        notify(clean)
        self.events.add("local_notification", clean, "info")

    def _handle_text(self, chat_id: int, message: dict[str, Any]) -> None:
        text = str(message.get("text") or "").strip()
        if not text:
            return
        if text.startswith("/id"):
            self._reply_to_chat(chat_id, f"Bale Chat ID: {chat_id}\nاین مقدار را در BALE_CHAT_ID قرار دهید.")
            return
        if not self._authorized(chat_id):
            self._reply_to_chat(chat_id, "این چت مجاز نیست. برای مشاهده شناسه /id را بفرستید.")
            return

        # Persistent direct-speech mode: ordinary Bale text is synthesized and
        # played on the laptop until the owner turns the mode off.
        if not text.startswith("/") and self._tts_text_mode:
            self._speak_text(chat_id, text)
            return

        # One-shot TTS prompt from the Bale inline menu. This takes priority over
        # Guard Chat so the next plain message is spoken rather than displayed.
        if not text.startswith("/") and self._awaiting_tts_text:
            self._awaiting_tts_text = False
            self._speak_text(chat_id, text)
            return

        # When Guard Chat is already open, ordinary non-command messages become
        # live owner messages without requiring /chat on every line.
        if not text.startswith("/") and self.chat.active:
            self.chat.send_owner(text, self.config.chat.seconds)
            self._reply_to_chat(chat_id, "✓ پیام به لپ‌تاپ رسید.")
            return

        command, *rest = text.split(maxsplit=1)
        command = command.split("@", 1)[0].lower()
        arg = rest[0] if rest else ""
        if command in {"/start", "/menu"}:
            self._reply_to_chat(chat_id, "👋 به Laptop Guard خوش آمدید.\nیکی از بخش‌ها را انتخاب کنید:", MAIN_MENU)
        elif command == "/arm":
            self.arm(); self._reply_to_chat(chat_id, "🟢 محافظت فعال شد.", MAIN_MENU)
        elif command == "/disarm":
            self.disarm(); self._reply_to_chat(chat_id, "⚪ محافظت غیرفعال شد.", MAIN_MENU)
        elif command == "/allow":
            try: minutes = int(arg or "5")
            except ValueError: minutes = 5
            self.allow_for(minutes); self._reply_to_chat(chat_id, f"🕐 استفاده محلی برای {minutes} دقیقه مجاز شد.")
        elif command == "/lock":
            self._cancel_pending_lock()
            ok = self.lock_screen()
            self.events.add("lock", "manual owner lock", "high")
            self._reply_to_chat(chat_id, "🔒 سیستم قفل شد." if ok else "⚠️ قفل سیستم ناموفق بود.")
        elif command == "/unlock":
            if not self.config.security.allow_remote_unlock:
                self._reply_to_chat(
                    chat_id,
                    "🔓 Remote unlock به‌صورت پیش‌فرض خاموش است. برای فعال‌سازی ALLOW_REMOTE_UNLOCK=true را در .env قرار دهید.",
                )
            else:
                self._reply_to_chat(
                    chat_id,
                    "⚠️ Unlock نشست محلی دسترسی فیزیکی به سیستم را باز می‌کند. ادامه؟",
                    inline_keyboard([[
                        ("✅ بله، Unlock", "guard:unlock:yes"),
                        ("❌ لغو", "guard:unlock:no"),
                    ]]),
                )
        elif command == "/photo":
            self._do_camera_photo(chat_id)
        elif command == "/cameravideo":
            try: sec = int(arg or "8")
            except ValueError: sec = 8
            self._do_camera_video(chat_id, sec)
        elif command == "/screen":
            self._do_screen_shot(chat_id)
        elif command == "/screenvideo":
            try: sec = int(arg or "8")
            except ValueError: sec = 8
            self._do_screen_video(chat_id, sec)
        elif command in {"/say", "/speak", "/tts"}:
            self._speak_text(chat_id, arg)
        elif command == "/ttsvoice":
            voice = str(arg or "").strip().lower()
            if self.tts.set_voice(voice):
                self._reply_to_chat(chat_id, f"🎚 صدای TTS روی {VOICE_NAMES.get(voice, voice)} ({voice}) تنظیم شد.", self.tts_menu()[1])
            else:
                self._reply_to_chat(chat_id, "صدای نامعتبر است. یکی از این‌ها را انتخاب کنید:\n" + " ".join(VOICE_NAMES), self.tts_menu()[1])
        elif command == "/ttsvoices":
            self._reply_to_chat(chat_id, self.tts_menu()[0], self.tts_menu()[1])
        elif command == "/ttsmode":
            value = str(arg or "").strip().lower()
            if value in {"on", "1", "true", "روشن"}:
                self._tts_text_mode = True
            elif value in {"off", "0", "false", "خاموش"}:
                self._tts_text_mode = False
            else:
                self._tts_text_mode = not self._tts_text_mode
            self._awaiting_tts_text = False
            self._reply_to_chat(chat_id, f"🗣 حالت متن مستقیم {'روشن' if self._tts_text_mode else 'خاموش'} شد.", self.tts_menu()[1])
        elif command in {"/ttstest", "/saytest"}:
            self._speak_text(chat_id, "سلام. سیستم لپ‌تاپ گارد آماده است.")
        elif command == "/cancel":
            self._awaiting_tts_text = False
            self._reply_to_chat(chat_id, "لغو شد.")
        elif command == "/listen":
            try: sec = int(arg or str(self.config.audio.listen_default_seconds))
            except ValueError: sec = self.config.audio.listen_default_seconds
            self._do_listen(chat_id, sec)
        elif command == "/voicechat":
            try: sec = int(arg or "30")
            except ValueError: sec = 30
            self._start_intercom(chat_id, sec)
        elif command == "/voicechat_stop":
            self.intercom.stop(); self._reply_to_chat(chat_id, "⏹ مکالمه صوتی متوقف شد.")
        elif command == "/chat":
            msg = arg or "لطفاً از لپ‌تاپ فاصله بگیرید. / Please step away from this laptop."
            opened = self.chat.start(
                msg,
                seconds=self.config.chat.seconds,
                allow_reply=self.config.chat.allow_reply,
                direction=self.config.chat.direction,
            )
            self._reply_to_chat(chat_id, "💬 گفت‌وگو باز شد." if opened else "⚠️ پنجره گفتگو باز نشد؛ python3-tk را بررسی کنید.")
        elif command == "/chatclose":
            changed = self.chat.dismiss()
            self._reply_to_chat(chat_id, "✖️ گفت‌وگو بسته شد." if changed else "ℹ️ گفت‌وگویی باز نبود.")
        elif command == "/notify":
            if not arg:
                self._reply_to_chat(chat_id, "استفاده: /notify متن پیام")
            else:
                self._notify_local(arg)
                self._reply_to_chat(chat_id, "🔔 اعلان روی لپ‌تاپ نمایش داده شد.")
        elif command in {"/sysinfo", "/device"}:
            self._reply_to_chat(chat_id, self.system_info_text(), MAIN_MENU)
        elif command == "/suspend":
            self._reply_to_chat(chat_id, "🌙 Suspend دستگاه؟", inline_keyboard([[
                ("✅ Suspend", "power:suspend:yes"), ("❌ لغو", "power:cancel")
            ]]))
        elif command in {"/reboot", "/restart"}:
            self._reply_to_chat(chat_id, "⚠️ دستگاه Restart شود؟", inline_keyboard([[
                ("✅ Restart", "power:reboot:yes"), ("❌ لغو", "power:cancel")
            ]]))
        elif command in {"/shutdown", "/poweroff"}:
            self._reply_to_chat(chat_id, "⚠️ دستگاه خاموش شود؟", inline_keyboard([[
                ("✅ Shutdown", "power:off:yes"), ("❌ لغو", "power:cancel")
            ]]))
        elif command == "/events":
            self._send_events(chat_id)
        elif command == "/status":
            self._reply_to_chat(chat_id, self.status_text(), MAIN_MENU)
        elif command == "/help":
            self._reply_to_chat(chat_id, self.help_text())
        else:
            self._reply_to_chat(chat_id, "دستور شناخته نشد. /menu را بفرستید.", MAIN_MENU)

    def _handle_voice_or_audio(self, chat_id: int, message: dict[str, Any]) -> bool:
        if not self._authorized(chat_id):
            return False
        attachment = message.get("voice") or message.get("audio")
        if not isinstance(attachment, dict):
            return False
        file_id = str(attachment.get("file_id") or "")
        if not file_id:
            return False
        if self.config.audio.auto_play_owner_voice or self.intercom.active:
            if self.chat.active:
                self.chat.send_owner("🔊 پیام صوتی مالک در حال پخش است. / Owner voice message is playing.", self.config.chat.seconds)
            self._play_owner_voice(file_id)
            self._reply_to_chat(chat_id, "🔊 پیام صوتی روی لپ‌تاپ پخش می‌شود.")
        else:
            self._reply_to_chat(chat_id, "Voice دریافت شد؛ پخش خودکار غیرفعال است.")
        return True

    def _handle_callback(self, query: dict[str, Any]) -> None:
        qid = str(query.get("id") or "")
        data = str(query.get("data") or "")
        message = query.get("message") or {}
        chat_id = ((message.get("chat") or {}).get("id"))
        message_id_raw = message.get("message_id")
        try:
            chat_id = int(chat_id)
        except (TypeError, ValueError):
            return
        try:
            message_id = int(message_id_raw) if message_id_raw is not None else None
        except (TypeError, ValueError):
            message_id = None
        if qid:
            try:
                self.api.answer_callback(qid)
            except Exception:
                pass
        if not self._authorized(chat_id):
            return

        def menu(text: str, markup: dict | None = None) -> None:
            self._edit_or_reply(chat_id, message_id, text, markup)

        if data == "menu:main":
            menu("🏠 منوی اصلی / Main menu", MAIN_MENU)
        elif data == "menu:security":
            menu(*self.security_menu())
        elif data == "menu:camera":
            menu(*self.camera_menu())
        elif data == "menu:screen":
            menu(*self.screen_menu())
        elif data == "menu:audio":
            menu(*self.audio_menu())
        elif data == "tts:menu":
            menu(*self.tts_menu())
        elif data == "menu:chat":
            menu(*self.chat_menu())
        elif data == "menu:system":
            menu(*self.system_menu())
        elif data == "menu:power":
            menu(*self.power_menu())
        elif data == "guard:arm":
            self.arm(); menu("🟢 محافظت فعال شد.", self.security_menu()[1])
        elif data == "guard:disarm":
            self.disarm(); menu("⚪ محافظت غیرفعال شد.", self.security_menu()[1])
        elif data == "guard:allow:5":
            self.allow_for(5); menu("🕐 استفاده محلی برای ۵ دقیقه مجاز شد.", self.security_menu()[1])
        elif data == "guard:lock":
            self._cancel_pending_lock()
            ok = self.lock_screen()
            self.events.add("lock", "manual owner lock", "high")
            menu("🔒 سیستم قفل شد." if ok else "⚠️ قفل سیستم ناموفق بود.", self.security_menu()[1])
        elif data == "guard:unlock:confirm":
            if not self.config.security.allow_remote_unlock:
                menu(
                    "🔓 Remote unlock خاموش است. در صورت نیاز ALLOW_REMOTE_UNLOCK=true را در .env فعال کنید.",
                    self.system_menu()[1],
                )
            else:
                menu(
                    "⚠️ Unlock نشست محلی می‌تواند دسترسی فیزیکی را باز کند. ادامه؟",
                    inline_keyboard([[
                        ("✅ بله، Unlock", "guard:unlock:yes"),
                        ("❌ لغو", "guard:unlock:no"),
                    ]]),
                )
        elif data == "guard:unlock:yes":
            ok, detail = self.unlock_screen()
            menu(("🔓 " if ok else "⚠️ ") + detail, self.system_menu()[1])
        elif data == "guard:unlock:no":
            menu("لغو شد.", self.system_menu()[1])
        elif data == "camera:photo":
            self._do_camera_photo(chat_id)
        elif data.startswith("camera:video:"):
            self._do_camera_video(chat_id, int(data.rsplit(":", 1)[1]))
        elif data == "screen:shot":
            self._do_screen_shot(chat_id)
        elif data.startswith("screen:video:"):
            self._do_screen_video(chat_id, int(data.rsplit(":", 1)[1]))
        elif data == "tts:prompt":
            self._awaiting_tts_text = True
            menu(
                f"🗣 متن فارسی را بفرستید تا با صدای {VOICE_NAMES.get(self.tts.default_voice, self.tts.default_voice)} روی لپ‌تاپ پخش شود.\n\nبرای لغو: /cancel",
                inline_keyboard([[('❌ لغو', 'tts:cancel')], [('⬅️ انتخاب صدا', 'tts:menu')]]),
            )
        elif data == "tts:cancel":
            self._awaiting_tts_text = False
            menu("لغو شد.", self.audio_menu()[1])
        elif data == "tts:test":
            self._speak_text(chat_id, "سلام. سیستم لپ‌تاپ گارد آماده است.")
        elif data == "tts:mode:toggle":
            self._tts_text_mode = not self._tts_text_mode
            self._awaiting_tts_text = False
            menu(f"🗣 حالت متن مستقیم {'روشن' if self._tts_text_mode else 'خاموش'} شد.\n\n" + self.tts_menu()[0], self.tts_menu()[1])
        elif data.startswith("tts:voice:"):
            voice = data.rsplit(":", 1)[1]
            if self.tts.set_voice(voice):
                menu(f"🎚 صدای TTS روی {VOICE_NAMES.get(voice, voice)} تنظیم شد.\n\n" + self.tts_menu()[0], self.tts_menu()[1])
            else:
                menu("صدای انتخاب‌شده معتبر نیست.", self.tts_menu()[1])
        elif data.startswith("audio:listen:"):
            self._do_listen(chat_id, int(data.rsplit(":", 1)[1]))
        elif data.startswith("audio:intercom:"):
            self._start_intercom(chat_id, int(data.rsplit(":", 1)[1]))
        elif data == "audio:stop":
            self.intercom.stop(); menu("⏹ مکالمه متوقف شد.", self.audio_menu()[1])
        elif data == "chat:open":
            opened = self.chat.start(
                "مالک دستگاه می‌خواهد با شما گفتگو کند. / The owner wants to talk with you.",
                self.config.chat.seconds,
                self.config.chat.allow_reply,
                direction=self.config.chat.direction,
            )
            menu("💬 گفت‌وگو باز شد." if opened else "⚠️ گفت‌وگو باز نشد؛ python3-tk را بررسی کنید.", self.chat_menu()[1])
        elif data == "chat:close":
            changed = self.chat.dismiss()
            menu("✖️ گفت‌وگو بسته شد." if changed else "ℹ️ گفت‌وگویی باز نبود.", self.chat_menu()[1])
        elif data == "system:notify:prompt":
            menu("🔔 برای نمایش اعلان روی لپ‌تاپ بنویسید:\n/notify متن پیام", self.chat_menu()[1])
        elif data == "system:info":
            menu(self.system_info_text(), self.system_menu()[1])
        elif data == "system:warning:test":
            launch_warning(5)
            menu("⚠️ تست هشدار ۵ مرحله‌ای نمایش داده شد. این تست دستگاه را قفل نمی‌کند.", self.system_menu()[1])
        elif data == "power:suspend:confirm":
            if not self.config.security.allow_remote_power:
                menu("Remote power controls غیرفعال است.", self.power_menu()[1])
            else:
                menu("🌙 دستگاه Suspend شود؟", inline_keyboard([[
                    ("✅ Suspend", "power:suspend:yes"), ("❌ لغو", "power:cancel")
                ]]))
        elif data == "power:reboot:confirm":
            if not self.config.security.allow_remote_power:
                menu("Remote power controls غیرفعال است.", self.power_menu()[1])
            else:
                menu("⚠️ دستگاه Restart شود؟", inline_keyboard([[
                    ("✅ Restart", "power:reboot:yes"), ("❌ لغو", "power:cancel")
                ]]))
        elif data == "power:off:confirm":
            if not self.config.security.allow_remote_power:
                menu("Remote power controls غیرفعال است.", self.power_menu()[1])
            else:
                menu("⚠️ دستگاه خاموش شود؟", inline_keyboard([[
                    ("✅ Shutdown", "power:off:yes"), ("❌ لغو", "power:cancel")
                ]]))
        elif data == "power:cancel":
            menu(*self.power_menu())
        elif data == "power:suspend:yes":
            if not self.config.security.allow_remote_power:
                menu("Remote power controls غیرفعال است.", self.power_menu()[1]); return
            self.events.add("power", "owner suspend request", "high")
            self._reply_to_chat(chat_id, "🌙 درخواست Suspend ارسال شد.")
            suspend_system()
        elif data == "power:reboot:yes":
            if not self.config.security.allow_remote_power:
                menu("Remote power controls غیرفعال است.", self.power_menu()[1]); return
            self.events.add("power", "owner reboot request", "critical")
            self._reply_to_chat(chat_id, "🔄 دستگاه در حال Restart است.")
            reboot_system()
        elif data == "power:off:yes":
            if not self.config.security.allow_remote_power:
                menu("Remote power controls غیرفعال است.", self.power_menu()[1]); return
            self.events.add("power", "owner shutdown request", "critical")
            self._reply_to_chat(chat_id, "⏻ دستگاه در حال خاموش شدن است.")
            poweroff_system()
        elif data == "events:recent":
            self._send_events(chat_id)
        elif data == "status:show":
            menu(self.status_text(), MAIN_MENU)

    def _do_camera_photo(self, chat_id: int) -> None:
        path = self._camera_snapshot_file("manual")
        if not path:
            self._reply_to_chat(chat_id, "⚠️ تصویر دوربین آماده نیست.")
            return
        try: self.api.send_photo(chat_id, path, f"📷 {datetime.now():%Y-%m-%d %H:%M:%S}")
        except Exception as exc: self._reply_to_chat(chat_id, f"⚠️ ارسال عکس ناموفق بود: {exc}")

    def _do_camera_video(self, chat_id: int, seconds: int) -> None:
        seconds = max(2, min(seconds, 20))
        self._reply_to_chat(chat_id, f"🎥 ضبط دوربین برای {seconds} ثانیه شروع شد.")
        def worker():
            MEDIA_DIR.mkdir(parents=True, exist_ok=True)
            path = MEDIA_DIR / f"camera-{datetime.now():%Y%m%d-%H%M%S-%f}.mp4"
            fps = max(5, self.config.camera.fps)
            writer = None
            deadline = time.monotonic() + seconds
            try:
                while time.monotonic() < deadline:
                    with self.frame_lock:
                        frame = None if self.last_frame is None else self.last_frame.copy()
                    if frame is None:
                        time.sleep(0.1); continue
                    if writer is None:
                        h, w = frame.shape[:2]
                        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
                    writer.write(frame)
                    time.sleep(1.0 / fps)
            finally:
                if writer is not None:
                    writer.release()
            if not path.exists() or not path.stat().st_size:
                self._reply_to_chat(chat_id, "⚠️ ویدیوی دوربین ایجاد نشد."); return
            try: self.api.send_video(chat_id, path, "🎥 ویدیوی دوربین")
            except Exception as exc: self._reply_to_chat(chat_id, f"⚠️ ارسال ویدیوی دوربین ناموفق بود: {exc}")
        threading.Thread(target=worker, daemon=True).start()

    def _do_screen_shot(self, chat_id: int) -> None:
        try: self.api.send_chat_action(chat_id, "upload_photo")
        except Exception: pass
        self._reply_to_chat(chat_id, "🖥 در حال ثبت Screenshot...")
        def worker():
            path, backend = self.screen.screenshot()
            if not path: self._reply_to_chat(chat_id, "⚠️ Screenshot در این نشست Linux در دسترس نیست."); return
            try: self.api.send_photo(chat_id, path, f"🖥 Screenshot • {backend}")
            except Exception as exc: self._reply_to_chat(chat_id, f"⚠️ ارسال Screenshot ناموفق بود: {exc}")
        threading.Thread(target=worker, daemon=True).start()

    def _do_screen_video(self, chat_id: int, seconds: int) -> None:
        seconds = max(2, min(seconds, 30))
        self._reply_to_chat(chat_id, f"🎥 ضبط صفحه برای {seconds} ثانیه شروع شد.")
        def worker():
            path, backend = self.screen.record(seconds)
            if not path: self._reply_to_chat(chat_id, "⚠️ Screen recording در این نشست در دسترس نیست."); return
            try: self.api.send_video(chat_id, path, f"🎥 Screen recording • {backend}")
            except Exception as exc: self._reply_to_chat(chat_id, f"⚠️ ارسال ویدیو ناموفق بود: {exc}")
        threading.Thread(target=worker, daemon=True).start()

    def _do_listen(self, chat_id: int, seconds: int) -> None:
        seconds = max(2, min(seconds, 30))
        try: self.api.send_chat_action(chat_id, "record_voice")
        except Exception: pass
        notify(f"ضبط صدای محیط برای {seconds} ثانیه فعال شد")
        self._reply_to_chat(chat_id, f"🎙 ضبط صدای محیط برای {seconds} ثانیه شروع شد.")
        def worker():
            path, kind = record_audio(seconds, "listen")
            if not path: self._reply_to_chat(chat_id, "⚠️ میکروفون/ابزار ضبط در دسترس نیست."); return
            try:
                if kind == "voice": self.api.send_voice(chat_id, path, "🎙 صدای محیط")
                elif kind == "audio": self.api.send_audio(chat_id, path, "🎙 صدای محیط")
                else: self.api.send_document(chat_id, path, "🎙 فایل صدای محیط")
            except Exception as exc: self._reply_to_chat(chat_id, f"⚠️ ارسال صدا ناموفق بود: {exc}")
        threading.Thread(target=worker, daemon=True).start()

    def _start_intercom(self, chat_id: int, seconds: int) -> None:
        seconds = max(10, min(seconds, self.config.audio.intercom_max_seconds))
        if self.intercom.start(seconds):
            self._reply_to_chat(chat_id, f"🗣 Voice Intercom برای {seconds} ثانیه فعال شد. Voiceهای شما هم‌زمان روی لپ‌تاپ پخش می‌شوند.")
        else:
            self._reply_to_chat(chat_id, "ℹ️ Voice Intercom از قبل فعال است.")

    def _send_events(self, chat_id: int) -> None:
        events = self.events.recent(10)
        if not events:
            self._reply_to_chat(chat_id, "📜 هنوز رویدادی ثبت نشده است.")
            return
        lines = ["📜 آخرین رویدادها", ""]
        for e in reversed(events):
            lines.append(f"• {e.get('time')} | {e.get('type')} | {e.get('detail')}")
        self._reply_to_chat(chat_id, "\n".join(lines))

    @staticmethod
    def help_text() -> str:
        return (
            "دستورات Laptop Guard v9\n\n"
            "/menu /status /sysinfo /arm /disarm /allow 5 /lock /unlock\n"
            "/photo /cameravideo 8 /screen /screenvideo 8\n"
            "/say متن /ttsvoice man2 /ttsvoices /ttsmode on|off /ttstest\n"
            "/listen 8 /voicechat 30 /voicechat_stop\n"
            "/chat پیام /chatclose /notify پیام /events\n"
            "/suspend /reboot /shutdown /id\n\n"
            "وقتی Security Chat باز است، متن عادی بدون /chat مستقیماً به لپ‌تاپ فرستاده می‌شود."
        )

    def handle_update(self, update: dict[str, Any]) -> None:
        callback = update.get("callback_query")
        if isinstance(callback, dict):
            self._handle_callback(callback)
            return
        message = update.get("message") or update.get("edited_message")
        if not isinstance(message, dict):
            return
        chat = message.get("chat") or {}
        try:
            chat_id = int(chat.get("id"))
        except (TypeError, ValueError):
            return
        if self._handle_voice_or_audio(chat_id, message):
            return
        self._handle_text(chat_id, message)

    # --------------------------- lifecycle

    def _request_exit_lock(self, reason: str) -> None:
        if not self.config.security.lock_on_guard_exit or self._exit_lock_requested:
            return
        self._exit_lock_requested = True
        self.events.add("guard_exit_lock", reason, "critical")
        # Use a short-lived thread so signal handling itself stays lightweight.
        threading.Thread(target=self.lock_screen, daemon=True, name="guard-exit-lock").start()

    def _signal_handler(self, signum, _frame) -> None:
        self._request_exit_lock(f"signal={signum}")
        self.stop_event.set()

    def _start_exit_watchdog(self) -> None:
        if not self.config.security.lock_on_guard_exit:
            return
        cmd = [
            sys.executable,
            "-m",
            "laptop_guard.exit_watchdog",
            "--parent-pid",
            str(os.getpid()),
            "--interval",
            "0.25",
        ]
        kwargs: dict[str, Any] = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if os.name == "nt":
            flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
            kwargs["creationflags"] = flags
        else:
            kwargs["start_new_session"] = True
        try:
            self._watchdog_proc = subprocess.Popen(cmd, **kwargs)
            print(f"[security] exit-lock watchdog pid={self._watchdog_proc.pid}")
        except OSError as exc:
            self._watchdog_proc = None
            print(f"[security] could not start exit-lock watchdog: {exc}")

    def start_monitors(self) -> None:
        self.camera_thread = threading.Thread(target=self.camera_worker, daemon=True, name="camera-monitor")
        self.camera_thread.start()
        try:
            self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
            self.keyboard_listener.start()
            self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click, on_scroll=self.on_mouse_scroll)
            self.mouse_listener.start()
            print("[input] listeners started")
        except Exception as exc:
            print(f"[input] listener startup failed: {exc}")
            self._send_async(f"⚠️ Input monitoring شروع نشد: {exc}")
        if self.config.security.auto_arm:
            self.arm()

    def stop(self) -> None:
        self._request_exit_lock("guard process stopping")
        self.stop_event.set()
        self._cancel_pending_lock()
        self.intercom.stop()
        self.tts.stop()
        self.chat.stop()
        for listener in (self.keyboard_listener, self.mouse_listener):
            if listener:
                try:
                    listener.stop()
                except Exception:
                    pass

    def run(self) -> None:
        me = self.api.get_me()
        print(f"Laptop Guard Bale bot ready: @{me.get('username') or me.get('first_name') or me.get('id')}")
        if self.config.bale.chat_id is None:
            print("BALE_CHAT_ID is not set. Send /id to the bot, then set BALE_CHAT_ID and restart.")
        for sig_name in ("SIGINT", "SIGTERM", "SIGHUP"):
            sig = getattr(signal, sig_name, None)
            if sig is not None:
                try:
                    signal.signal(sig, self._signal_handler)
                except (ValueError, OSError):
                    pass
        self._start_exit_watchdog()
        self.start_monitors()
        if self._owner_chat() is not None:
            self._send_async("✅ Laptop Guard شروع شد.\n" + self.status_text(), MAIN_MENU)
        try:
            while not self.stop_event.is_set():
                try:
                    updates = self.api.get_updates(self._offset, self.config.bale.poll_timeout)
                    for update in updates:
                        uid = update.get("update_id")
                        if isinstance(uid, int):
                            self._offset = uid + 1
                        self.handle_update(update)
                except BaleApiError as exc:
                    print(f"[bale] polling error: {exc}")
                    if self.stop_event.wait(2):
                        break
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


def main() -> int:
    try:
        config = load_config()
        if not config.bale.token:
            raise SystemExit("Missing BALE_BOT_TOKEN. Copy .env.example values into your shell or service environment.")
        LaptopGuard(config).run()
        return 0
    except ValueError as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
