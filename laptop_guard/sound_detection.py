from __future__ import annotations

import math
import shutil
import subprocess
import threading
import time
from array import array
from pathlib import Path
from typing import Callable

from .audio import AudioRecorder
from .models import AudioConfig


def pcm_rms(data: bytes) -> float:
    """Return normalized RMS for little-endian signed 16-bit mono PCM."""
    usable = len(data) - (len(data) % 2)
    if usable <= 0:
        return 0.0
    samples = array("h")
    samples.frombytes(data[:usable])
    if not samples:
        return 0.0
    mean_square = sum(float(sample) ** 2 for sample in samples) / len(samples)
    return min(1.0, math.sqrt(mean_square) / 32768.0)


class SoundDetectionMonitor:
    """Bounded volume-triggered capture adapter; idle PCM is never retained."""

    def __init__(
        self,
        config: AudioConfig,
        is_active: Callable[[], bool],
        owner_available: Callable[[], bool],
        on_event: Callable[[str, str, str], None],
        on_clip: Callable[[str, Path, str], None],
    ) -> None:
        self.config = config
        self.is_active = is_active
        self.owner_available = owner_available
        self.on_event = on_event
        self.on_clip = on_clip
        self._stop = threading.Event()
        self._paused = threading.Event()
        self._pause_lock = threading.Lock()
        self._pause_depth = 0
        self._thread: threading.Thread | None = None
        self._proc: subprocess.Popen | None = None
        self._recorder = AudioRecorder(config, lambda *_: None)

    @property
    def available(self) -> bool:
        return bool(shutil.which("ffmpeg"))

    def pause(self) -> None:
        with self._pause_lock:
            self._pause_depth += 1
            self._paused.set()
        self._terminate_probe()
        self._recorder.cancel()

    def resume(self) -> None:
        with self._pause_lock:
            self._pause_depth = max(0, self._pause_depth - 1)
            if self._pause_depth == 0:
                self._paused.clear()

    def cancel_capture(self) -> None:
        """Cancel an in-flight probe/clip without changing pause ownership."""
        self._terminate_probe()
        self._recorder.cancel()

    def start(self) -> None:
        if not self.config.sound_detection_enabled or not self.available:
            return
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="sound-detection")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._terminate_probe()
        self._recorder.cancel()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _input_args(self) -> list[str]:
        backend = self.config.backend
        if backend == "auto":
            backend = "pulse" if shutil.which("pactl") else "alsa"
        return ["-f", backend, "-i", self.config.input or "default"]

    def _probe_command(self) -> list[str]:
        return [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            *self._input_args(), "-ac", "1", "-ar", "16000",
            "-f", "s16le", "pipe:1",
        ]

    def _terminate_probe(self) -> None:
        proc = self._proc
        self._proc = None
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                proc.kill()
            except OSError:
                pass

    def _capture_and_send(self, level: float) -> None:
        seconds = max(2, min(int(self.config.sound_record_seconds), 30))
        self.on_event("sound_detected", f"rms={level:.3f}; recording={seconds}s", "high")
        path, detail = self._recorder.record_blocking(seconds)
        if path:
            if not self._eligible():
                Path(path).unlink(missing_ok=True)
                self.on_event("sound_record_cancelled", "guard inactive before delivery", "info")
                return
            kind = "voice" if Path(path).suffix.lower() == ".ogg" else "document"
            self.on_clip(kind, path, f"🎙 صدای محیط پس از تشخیص صدا • {seconds} ثانیه")
        else:
            self.on_event("sound_record_failed", detail, "warning")

    def _eligible(self) -> bool:
        return not self._stop.is_set() and not self._paused.is_set() and self.is_active() and self.owner_available()

    def _run(self) -> None:
        cooldown_until = 0.0
        required = max(1, min(int(self.config.sound_trigger_chunks), 10))
        threshold = max(0.005, min(float(self.config.sound_threshold), 1.0))
        while not self._stop.is_set():
            if not self._eligible() or time.monotonic() < cooldown_until:
                self._stop.wait(0.25)
                continue
            loud_chunks = 0
            try:
                self._proc = subprocess.Popen(
                    self._probe_command(),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
                assert self._proc.stdout is not None
                while not self._stop.is_set() and self._eligible():
                    chunk = self._proc.stdout.read(3200)
                    if not chunk:
                        break
                    level = pcm_rms(chunk)
                    loud_chunks = loud_chunks + 1 if level >= threshold else 0
                    if loud_chunks >= required:
                        self._terminate_probe()
                        self._capture_and_send(level)
                        cooldown_until = time.monotonic() + max(5, int(self.config.sound_cooldown))
                        break
            except (OSError, subprocess.SubprocessError) as exc:
                self.on_event("sound_monitor_failed", str(exc), "warning")
                self._stop.wait(2.0)
            finally:
                self._terminate_probe()
