from __future__ import annotations

import shutil
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from .config import DATA_DIR, MEDIA_DIR

STOP_FLAG = DATA_DIR / "voice-intercom.stop"


def notify(text: str) -> None:
    if shutil.which("notify-send"):
        try:
            subprocess.Popen(["notify-send", "Laptop Guard", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass


def play_audio(path: Path) -> bool:
    candidates = []
    if shutil.which("ffplay"):
        candidates.append(["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", str(path)])
    if shutil.which("paplay"):
        candidates.append(["paplay", str(path)])
    if shutil.which("pw-play"):
        candidates.append(["pw-play", str(path)])
    if shutil.which("aplay"):
        candidates.append(["aplay", str(path)])
    for cmd in candidates:
        try:
            if subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90).returncode == 0:
                return True
        except Exception:
            continue
    return False


def record_audio(seconds: int, stem: str = "listen") -> tuple[Path | None, str]:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    seconds = max(1, min(int(seconds), 30))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    if shutil.which("ffmpeg"):
        ogg = MEDIA_DIR / f"{stem}-{stamp}.ogg"
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error", "-f", "pulse", "-i", "default",
            "-t", str(seconds), "-ac", "1", "-ar", "16000", "-c:a", "libopus", "-b:a", "32k", str(ogg)
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=seconds + 15)
            if result.returncode == 0 and ogg.exists() and ogg.stat().st_size:
                return ogg, "voice"
        except Exception:
            pass
    if shutil.which("arecord"):
        wav = MEDIA_DIR / f"{stem}-{stamp}.wav"
        try:
            result = subprocess.run(
                ["arecord", "-q", "-f", "S16_LE", "-r", "16000", "-c", "1", "-d", str(seconds), str(wav)],
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=seconds + 10,
            )
            if result.returncode == 0 and wav.exists() and wav.stat().st_size:
                return wav, "document"
        except Exception:
            pass
    return None, "unavailable"


class AudioIntercom:
    """Visible near-live voice intercom.

    Bale Bot API transports voice/audio messages rather than raw duplex media
    streams, so this uses short recorded chunks for a near-live session.
    """

    def __init__(self, send_chunk: Callable[[Path, str], None], chunk_seconds: int = 4) -> None:
        self.send_chunk = send_chunk
        self.chunk_seconds = max(2, min(int(chunk_seconds), 10))
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._indicator: subprocess.Popen | None = None

    @property
    def active(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self, seconds: int) -> bool:
        if self.active:
            return False
        seconds = max(10, min(int(seconds), 300))
        self._stop.clear()
        try:
            STOP_FLAG.unlink(missing_ok=True)
        except OSError:
            pass
        notify(f"مکالمه صوتی Laptop Guard برای {seconds} ثانیه فعال شد")
        try:
            self._indicator = subprocess.Popen(
                [
                    __import__("sys").executable,
                    "-m", "laptop_guard.audio_indicator",
                    "--seconds", str(seconds),
                ],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except OSError:
            self._indicator = None

        def worker() -> None:
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline and not self._stop.is_set():
                if STOP_FLAG.exists():
                    break
                remaining = max(1, int(deadline - time.monotonic()))
                chunk = min(self.chunk_seconds, remaining)
                path, kind = record_audio(chunk, "intercom")
                if not path:
                    break
                try:
                    self.send_chunk(path, kind)
                except Exception:
                    pass
            self._stop.set()
            notify("مکالمه صوتی Laptop Guard پایان یافت")
            if self._indicator and self._indicator.poll() is None:
                try:
                    self._indicator.terminate()
                except OSError:
                    pass

        self._thread = threading.Thread(target=worker, daemon=True, name="guard-audio-intercom")
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop.set()
        try:
            STOP_FLAG.write_text("stop", encoding="utf-8")
        except OSError:
            pass
        if self._indicator and self._indicator.poll() is None:
            try:
                self._indicator.terminate()
            except OSError:
                pass
