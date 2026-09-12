from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path
from typing import Sequence


DEFAULT_STAGES = [
    "فعالیت غیرمنتظره شناسایی شد.",
    "تصویر رویداد ثبت شد.",
    "مالک دستگاه مطلع شده است.",
    "لطفاً از لپ‌تاپ فاصله بگیرید.",
    "سیستم در حال قفل شدن است.",
]


class WarningScreenManager:
    """Launch and control the visible intrusion countdown surface.

    The child process is deliberately only a visual deterrence surface. The
    actual desktop lock is scheduled by GuardApp so killing the window cannot
    cancel the security action.
    """

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    @property
    def visible(self) -> bool:
        with self._lock:
            return self._proc is not None and self._proc.poll() is None

    def show(
        self,
        text: str,
        seconds: int,
        title: str = "هشدار امنیتی",
        *,
        image_path: Path | str | None = None,
        stages: Sequence[str] | None = None,
        notify_each_second: bool = True,
    ) -> bool:
        seconds = max(3, min(int(seconds), 300))
        stage_items = [str(x).strip() for x in (stages or DEFAULT_STAGES) if str(x).strip()]
        with self._lock:
            if self._proc is not None and self._proc.poll() is None:
                # Replace an older warning with the newest evidence/countdown.
                try:
                    self._proc.terminate()
                except OSError:
                    pass
                self._proc = None
            try:
                cmd = [
                    sys.executable,
                    "-m",
                    "laptop_guard.warning_screen",
                    "--seconds",
                    str(seconds),
                    "--title",
                    title,
                    "--text",
                    text,
                    "--stages-json",
                    json.dumps(stage_items, ensure_ascii=False),
                ]
                if image_path:
                    cmd.extend(["--image", str(image_path)])
                if notify_each_second:
                    cmd.append("--notify-each-second")
                self._proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except (OSError, subprocess.SubprocessError):
                self._proc = None
                return False

    def dismiss(self) -> bool:
        with self._lock:
            proc = self._proc
            self._proc = None
        if not proc or proc.poll() is not None:
            return False
        try:
            proc.terminate()
            return True
        except OSError:
            return False
