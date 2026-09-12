from __future__ import annotations

import asyncio
import queue
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from .audio_intercom import notify, play_audio
from .config import DATA_DIR, MEDIA_DIR

VOICE_NAMES: dict[str, str] = {
    "woman1": "شیوا",
    "woman2": "مهتاب",
    "woman3": "نگار",
    "woman4": "ریما",
    "man1": "راد",
    "man2": "پیام",
    "man3": "بهمن",
    "man4": "برنا",
    "man5": "برنا-1",
    "man6": "کیان",
    "man7": "نیما",
    "man8": "آریا",
    "boy1": "آرش",
}


@dataclass(slots=True)
class SpeechResult:
    ok: bool
    text: str
    voice: str
    path: Path | None = None
    error: str = ""


@dataclass(slots=True)
class _SpeechJob:
    text: str
    voice: str
    callback: Callable[[SpeechResult], None] | None = None


def package_available() -> bool:
    try:
        import py_persian_tts  # noqa: F401
        return True
    except Exception:
        return False


def normalize_voice(voice: str, default: str = "man2") -> str:
    value = str(voice or "").strip().lower()
    return value if value in VOICE_NAMES else default


class PersianSpeechManager:
    """Serialized Persian text-to-speech playback for owner messages.

    The third-party package is imported lazily so a missing/broken TTS package
    never prevents Laptop Guard itself from starting. Jobs are processed one at
    a time to match the package's rate-limited async API and avoid overlapping
    owner announcements on the laptop speakers.
    """

    def __init__(
        self,
        default_voice: str = "man2",
        rate_limit: float = 0.5,
        max_chars: int = 700,
        show_notification: bool = True,
        queue_size: int = 20,
    ) -> None:
        self._state_path = DATA_DIR / "tts-state.txt"
        persisted = ""
        try:
            persisted = self._state_path.read_text(encoding="utf-8").strip()
        except OSError:
            pass
        self.default_voice = normalize_voice(persisted or default_voice)
        self.rate_limit = max(0.0, min(float(rate_limit), 10.0))
        self.max_chars = max(20, min(int(max_chars), 2000))
        self.show_notification = bool(show_notification)
        self._queue: queue.Queue[_SpeechJob | None] = queue.Queue(maxsize=max(1, queue_size))
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True, name="persian-tts")
        self._thread.start()
        self._busy = threading.Event()
        self.last_error = ""

    @property
    def busy(self) -> bool:
        return self._busy.is_set()

    @property
    def queued(self) -> int:
        return self._queue.qsize()

    @property
    def available(self) -> bool:
        return package_available()

    def set_voice(self, voice: str) -> bool:
        value = str(voice or "").strip().lower()
        if value not in VOICE_NAMES:
            return False
        self.default_voice = value
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(value, encoding="utf-8")
        except OSError:
            pass
        return True

    def submit(
        self,
        text: str,
        voice: str | None = None,
        callback: Callable[[SpeechResult], None] | None = None,
    ) -> tuple[bool, str]:
        clean = " ".join(str(text or "").replace("\x00", " ").split()).strip()
        if not clean:
            return False, "متن خالی است."
        if len(clean) > self.max_chars:
            return False, f"متن بیش از حد طولانی است؛ حداکثر {self.max_chars} کاراکتر."
        if not self.available:
            return False, "py-persian-tts نصب یا قابل import نیست."
        selected = normalize_voice(voice or self.default_voice, self.default_voice)
        try:
            self._queue.put_nowait(_SpeechJob(clean, selected, callback))
        except queue.Full:
            return False, "صف تبدیل متن به صدا پر است؛ کمی بعد دوباره تلاش کنید."
        return True, f"در صف پخش با صدای {VOICE_NAMES[selected]} ({selected}) قرار گرفت."

    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                job = self._queue.get(timeout=0.25)
            except queue.Empty:
                continue
            if job is None:
                self._queue.task_done()
                break
            self._busy.set()
            try:
                result = self._run_job(job)
            except Exception as exc:  # final containment boundary
                self.last_error = str(exc)
                result = SpeechResult(False, job.text, job.voice, error=str(exc))
            finally:
                self._busy.clear()
                self._queue.task_done()
            if job.callback:
                try:
                    job.callback(result)
                except Exception:
                    pass

    def _run_job(self, job: _SpeechJob) -> SpeechResult:
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        path = MEDIA_DIR / f"persian-tts-{datetime.now():%Y%m%d-%H%M%S-%f}.wav"

        async def synthesize() -> Path:
            from py_persian_tts import PersianTTS

            tts = PersianTTS(default_voice=job.voice, rate_limit=self.rate_limit)
            try:
                generated = await tts.speak_async(job.text, voice=job.voice, filename=str(path))
                if generated:
                    candidate = Path(str(generated)).expanduser()
                    if candidate.exists():
                        return candidate
                return path
            finally:
                shutdown = getattr(tts, "shutdown", None)
                if shutdown is not None:
                    try:
                        maybe = shutdown()
                        if asyncio.iscoroutine(maybe):
                            await maybe
                    except Exception:
                        pass

        try:
            generated_path = asyncio.run(synthesize())
        except Exception as exc:
            self.last_error = str(exc)
            return SpeechResult(False, job.text, job.voice, error=f"TTS generation failed: {exc}")

        if not generated_path.exists() or generated_path.stat().st_size <= 0:
            return SpeechResult(False, job.text, job.voice, error="TTS returned no playable audio file")

        if self.show_notification:
            notify(f"پیام صوتی مالک — {VOICE_NAMES.get(job.voice, job.voice)}")
        if not play_audio(generated_path):
            return SpeechResult(False, job.text, job.voice, path=generated_path, error="Audio playback failed")
        return SpeechResult(True, job.text, job.voice, path=generated_path)

    def stop(self) -> None:
        self._stop.set()
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
