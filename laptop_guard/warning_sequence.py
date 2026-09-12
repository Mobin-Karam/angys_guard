from __future__ import annotations

import argparse
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

try:
    import tkinter as tk
except ImportError:
    tk = None  # type: ignore[assignment]

ASSET_DIR = Path(__file__).resolve().parent / "assets" / "warnings"


def _notify(text: str) -> None:
    if shutil.which("notify-send"):
        try:
            subprocess.Popen(
                ["notify-send", "Laptop Guard", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError:
            pass


class WarningSequence:
    def __init__(self, seconds: int = 5, asset_dir: Path = ASSET_DIR) -> None:
        if tk is None:
            raise RuntimeError("Tkinter is not installed")
        self.seconds = max(3, min(int(seconds), 15))
        self.asset_dir = asset_dir
        self.root = tk.Tk()
        self.root.title("Laptop Guard Warning")
        self.root.configure(bg="black")
        self.root.attributes("-topmost", True)
        try:
            self.root.attributes("-fullscreen", True)
        except tk.TclError:
            self.root.geometry(
                f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0"
            )
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.bell())
        self.root.bind("<Escape>", lambda _e: self.root.bell())
        self.root.bind("<Alt-F4>", lambda _e: self.root.bell())
        self.label = tk.Label(self.root, bg="black")
        self.label.pack(expand=True, fill="both")
        self.remaining = self.seconds
        self._photo = None

    def _load(self, number: int):
        path = self.asset_dir / f"{number}.png"
        if not path.exists():
            return None
        try:
            from PIL import Image, ImageTk

            image = Image.open(path).convert("RGB")
            sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            scale = max(sw / image.width, sh / image.height)
            image = image.resize(
                (int(image.width * scale), int(image.height * scale)),
                Image.Resampling.LANCZOS,
            )
            left = max(0, (image.width - sw) // 2)
            top = max(0, (image.height - sh) // 2)
            image = image.crop((left, top, left + sw, top + sh))
            return ImageTk.PhotoImage(image)
        except Exception:
            return None

    def tick(self) -> None:
        # Assets are numbered 5..1. For warning lengths >5 the first image is
        # held until the final five seconds, then the sequence advances each second.
        number = max(1, min(5, self.remaining))
        photo = self._load(number)
        if photo is not None:
            self._photo = photo
            self.label.configure(image=photo, text="")
        else:
            self.label.configure(
                image="",
                text=(
                    "⚠ SECURITY WARNING / هشدار امنیتی\n\n"
                    "به لپ‌تاپ من دست نزن! / Do not touch this laptop.\n\n"
                    f"Lock in {self.remaining}s / قفل در {self.remaining} ثانیه"
                ),
                fg="#ff3344",
                bg="#050505",
                font=("DejaVu Sans", 30, "bold"),
                justify="center",
            )
        _notify(f"قفل در {self.remaining} ثانیه • Lock in {self.remaining}s")
        if self.remaining <= 1:
            self.root.after(1000, self.root.destroy)
            return
        self.remaining -= 1
        self.root.after(1000, self.tick)

    def run(self) -> None:
        self.tick()
        self.root.mainloop()


def _notification_fallback(seconds: int) -> int:
    seconds = max(3, min(int(seconds), 15))
    for remaining in range(seconds, 0, -1):
        _notify(
            f"⚠ به لپ‌تاپ من دست نزن! • Do not touch this laptop. • "
            f"قفل در {remaining} ثانیه / Lock in {remaining}s"
        )
        time.sleep(1)
    return 0


def launch_warning(seconds: int = 5) -> subprocess.Popen | None:
    try:
        return subprocess.Popen(
            [sys.executable, "-m", "laptop_guard.warning_sequence", "--seconds", str(seconds)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return None


def dismiss_warning(proc: subprocess.Popen | None) -> None:
    if not proc or proc.poll() is not None:
        return
    try:
        proc.send_signal(signal.SIGTERM)
    except OSError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=5)
    args = parser.parse_args()
    if tk is None:
        return _notification_fallback(args.seconds)
    WarningSequence(args.seconds).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
