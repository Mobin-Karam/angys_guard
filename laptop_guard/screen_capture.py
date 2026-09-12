from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path

from .config import MEDIA_DIR


class ScreenCapture:
    def __init__(self) -> None:
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    def screenshot(self) -> tuple[Path | None, str]:
        path = MEDIA_DIR / f"screen-{datetime.now():%Y%m%d-%H%M%S}.png"
        candidates: list[tuple[str, list[str]]] = []
        if shutil.which("gnome-screenshot"):
            candidates.append(("gnome-screenshot", ["gnome-screenshot", "-f", str(path)]))
        if shutil.which("grim"):
            candidates.append(("grim", ["grim", str(path)]))
        if shutil.which("spectacle"):
            candidates.append(("spectacle", ["spectacle", "-b", "-n", "-o", str(path)]))
        if os.environ.get("DISPLAY") and shutil.which("import"):
            candidates.append(("imagemagick", ["import", "-window", "root", str(path)]))
        for name, cmd in candidates:
            try:
                result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=20)
                if result.returncode == 0 and path.exists() and path.stat().st_size:
                    return path, name
            except Exception:
                continue
        return None, "unavailable"

    def record(self, seconds: int = 8) -> tuple[Path | None, str]:
        seconds = max(2, min(int(seconds), 30))
        path = MEDIA_DIR / f"screen-{datetime.now():%Y%m%d-%H%M%S}.mp4"
        if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wf-recorder"):
            try:
                proc = subprocess.Popen(["wf-recorder", "-f", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(seconds)
                proc.send_signal(signal.SIGINT)
                proc.wait(timeout=10)
                if path.exists() and path.stat().st_size:
                    return path, "wf-recorder"
            except Exception:
                pass
        if os.environ.get("DISPLAY") and shutil.which("ffmpeg"):
            size = "1920x1080"
            if shutil.which("xdpyinfo"):
                try:
                    out = subprocess.check_output(["xdpyinfo"], text=True, timeout=3)
                    for line in out.splitlines():
                        if "dimensions:" in line:
                            size = line.split("dimensions:", 1)[1].strip().split()[0]
                            break
                except Exception:
                    pass
            try:
                result = subprocess.run(
                    ["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-video_size", size,
                     "-framerate", "15", "-i", os.environ.get("DISPLAY", ":0"), "-t", str(seconds),
                     "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(path)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=seconds + 20,
                )
                if result.returncode == 0 and path.exists() and path.stat().st_size:
                    return path, "ffmpeg-x11grab"
            except Exception:
                pass
        return None, "unavailable"


class ScreenCaptureManager(ScreenCapture):
    """Backward-compatible facade for older diagnostics/tests."""

    def __init__(self, notify_local: bool = True) -> None:
        super().__init__()
        self.notify_local = notify_local

    @property
    def screenshot_backend(self) -> str:
        if shutil.which("gnome-screenshot"):
            return "gnome-screenshot"
        if shutil.which("grim"):
            return "grim"
        if shutil.which("spectacle"):
            return "spectacle"
        if os.environ.get("DISPLAY") and shutil.which("import"):
            return "imagemagick"
        return "unavailable"

    @property
    def video_backend(self) -> str:
        if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wf-recorder"):
            return "wf-recorder"
        if os.environ.get("DISPLAY") and shutil.which("ffmpeg"):
            return "ffmpeg-x11grab"
        return "unavailable"

    @staticmethod
    def _parse_gdbus_path(output: str) -> str:
        import re
        match = re.search(r"\(\s*true\s*,\s*['\"]([^'\"]+)['\"]", str(output), re.I)
        return match.group(1) if match else ""
