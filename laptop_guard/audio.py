from __future__ import annotations

import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable

from .config import MEDIA_DIR
from .models import AudioConfig
from .system import desktop_notify


class AudioRecorder:
    def __init__(self, config: AudioConfig, on_done: Callable[[Path | None, str], None]) -> None:
        self.config = config
        self.on_done = on_done
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    @property
    def busy(self) -> bool:
        with self._lock:
            return self._proc is not None and self._proc.poll() is None

    def cancel(self) -> bool:
        with self._lock:
            proc = self._proc
        if not proc or proc.poll() is not None:
            return False
        proc.terminate()
        return True

    def record_async(self, seconds: int) -> bool:
        if self.busy:
            return False
        seconds = max(1, min(seconds, self.config.max_seconds))
        threading.Thread(target=self._record, args=(seconds,), daemon=True, name="audio-recorder").start()
        return True

    def _command(self, seconds: int, output: Path) -> list[str]:
        backend = self.config.backend
        source = self.config.input or "default"
        if backend == "auto":
            backend = "pulse" if shutil.which("pactl") else "alsa"
        if backend == "pulse":
            return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "pulse", "-i", source, "-t", str(seconds), "-c:a", "libopus", "-b:a", "32k", "-y", str(output)]
        return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "alsa", "-i", source, "-t", str(seconds), "-c:a", "libopus", "-b:a", "32k", "-y", str(output)]

    def record_blocking(self, seconds: int) -> tuple[Path | None, str]:
        """Record a short clip synchronously for the localhost control API."""
        if self.busy:
            return None, "audio recorder is busy"
        if not shutil.which("ffmpeg"):
            return None, "ffmpeg is not installed"
        seconds = max(1, min(int(seconds), self.config.max_seconds))
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        path = MEDIA_DIR / f"audio-api-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.ogg"
        if self.config.local_notification:
            desktop_notify("Laptop Guard", f"Microphone recording started for {seconds} seconds")
        try:
            with self._lock:
                self._proc = subprocess.Popen(self._command(seconds, path), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                proc = self._proc
            _, stderr = proc.communicate(timeout=seconds + 20)
            if proc.returncode == 0 and path.exists() and path.stat().st_size > 0:
                return path, "ok"
            return None, (stderr or b"").decode(errors="ignore").strip()[-500:] or f"ffmpeg exited with {proc.returncode}"
        except Exception as exc:
            return None, str(exc)
        finally:
            with self._lock:
                self._proc = None

    def _record(self, seconds: int) -> None:
        if not shutil.which("ffmpeg"):
            self.on_done(None, "ffmpeg is not installed")
            return
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        path = MEDIA_DIR / f"audio-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.ogg"
        if self.config.local_notification:
            desktop_notify("Laptop Guard", f"Microphone recording started for {seconds} seconds")
        try:
            with self._lock:
                self._proc = subprocess.Popen(self._command(seconds, path), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                proc = self._proc
            _, stderr = proc.communicate()
            if proc.returncode == 0 and path.exists() and path.stat().st_size > 0:
                self.on_done(path, "ok")
            elif proc.returncode in {-15, 143}:
                self.on_done(None, "cancelled")
            else:
                msg = (stderr or b"").decode(errors="ignore").strip()[-500:]
                self.on_done(None, msg or f"ffmpeg exited with {proc.returncode}")
        except Exception as exc:
            self.on_done(None, str(exc))
        finally:
            with self._lock:
                self._proc = None


class RemoteAudioPlayer:
    def __init__(self, config: AudioConfig) -> None:
        self.config = config
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    @property
    def busy(self) -> bool:
        with self._lock:
            return self._proc is not None and self._proc.poll() is None

    def stop(self) -> bool:
        with self._lock:
            proc = self._proc
        if not proc or proc.poll() is not None:
            return False
        try:
            proc.terminate()
            return True
        except Exception:
            return False

    def _player_command(self, path: Path) -> list[str] | None:
        if shutil.which("ffplay"):
            return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", str(path)]
        if shutil.which("mpv"):
            return ["mpv", "--no-video", "--really-quiet", str(path)]
        if shutil.which("paplay"):
            return ["paplay", str(path)]
        return None

    def play_async(self, path: Path, on_done: Callable[[bool, str], None] | None = None) -> bool:
        if self.busy:
            return False
        cmd = self._player_command(path)
        if not cmd:
            if on_done:
                on_done(False, "No audio player found. Install ffmpeg (ffplay) or mpv.")
            return False

        def worker() -> None:
            try:
                with self._lock:
                    self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    proc = self._proc
                _, stderr = proc.communicate()
                ok = proc.returncode == 0
                detail = "played" if ok else (stderr or b"").decode(errors="ignore").strip()[-300:]
                if on_done:
                    on_done(ok, detail or f"player exited with {proc.returncode}")
            except Exception as exc:
                if on_done:
                    on_done(False, str(exc))
            finally:
                with self._lock:
                    self._proc = None

        threading.Thread(target=worker, daemon=True, name="remote-audio-player").start()
        return True


class TextToSpeechPlayer:
    """Local TTS for short owner messages. No cloud service is used."""

    def __init__(self, config: AudioConfig) -> None:
        self.config = config
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    @property
    def available(self) -> bool:
        return bool(shutil.which("espeak-ng") or shutil.which("espeak") or shutil.which("spd-say"))

    def stop(self) -> bool:
        with self._lock:
            proc = self._proc
        if not proc or proc.poll() is not None:
            return False
        try:
            proc.terminate()
            return True
        except Exception:
            return False

    def speak_async(self, text: str, on_done: Callable[[bool, str], None] | None = None) -> bool:
        if not self.config.tts_enabled or not self.available:
            return False
        clean = " ".join(text.split())[: max(1, self.config.max_tts_chars)]
        if not clean:
            return False
        if shutil.which("espeak-ng"):
            cmd = ["espeak-ng", "-v", "fa", clean]
        elif shutil.which("espeak"):
            cmd = ["espeak", "-v", "fa", clean]
        else:
            cmd = ["spd-say", "-l", "fa", "-w", clean]

        def worker() -> None:
            try:
                with self._lock:
                    self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    proc = self._proc
                _, stderr = proc.communicate(timeout=120)
                ok = proc.returncode == 0
                detail = "spoken" if ok else (stderr or b"").decode(errors="ignore")[-300:]
                if on_done:
                    on_done(ok, detail)
            except Exception as exc:
                if on_done:
                    on_done(False, str(exc))
            finally:
                with self._lock:
                    self._proc = None

        threading.Thread(target=worker, daemon=True, name="tts-player").start()
        return True
