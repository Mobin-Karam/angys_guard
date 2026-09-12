from __future__ import annotations

import math
import shutil
import subprocess
import threading
import time
from array import array
from pathlib import Path

from ..audio import AudioRecorder
from ..models import AudioConfig


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


class SoundDetectionFeature:
    """Volume-only microphone trigger; idle audio is neither stored nor transcribed."""

    name = "sound_detection"

    def __init__(self, host, config: AudioConfig) -> None:
        self.host = host
        self.config = config
        self._stop = threading.Event()
        self._paused = threading.Event()
        self._thread: threading.Thread | None = None
        self._proc: subprocess.Popen | None = None
        self._recorder = AudioRecorder(config, lambda *_: None)

    def register(self, _manager) -> None:
        return

    @property
    def available(self) -> bool:
        return bool(shutil.which("ffmpeg"))

    def pause(self) -> None:
        self._paused.set()
        self._terminate_probe()

    def resume(self) -> None:
        self._paused.clear()

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
        self.host.feature_event("sound_detected", f"rms={level:.3f}; recording={seconds}s", "high")
        path, detail = self._recorder.record_blocking(seconds)
        if path:
            kind = "voice" if Path(path).suffix.lower() == ".ogg" else "document"
            self.host.feature_send_owner_file(kind, path, f"🎙 صدای محیط پس از تشخیص صدا • {seconds} ثانیه")
        else:
            self.host.feature_event("sound_record_failed", detail, "warning")

    def _run(self) -> None:
        cooldown_until = 0.0
        required = max(1, min(int(self.config.sound_trigger_chunks), 10))
        threshold = max(0.005, min(float(self.config.sound_threshold), 1.0))
        while not self._stop.is_set():
            if self._paused.is_set() or not self.host.feature_guard_active() or time.monotonic() < cooldown_until:
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
                while not self._stop.is_set() and not self._paused.is_set() and self.host.feature_guard_active():
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
                self.host.feature_event("sound_monitor_failed", str(exc), "warning")
                self._stop.wait(2.0)
            finally:
                self._terminate_probe()
