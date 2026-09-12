from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tkinter as tk
from pathlib import Path

DEFAULT_TEXT = "به لپ‌تاپ من دست نزن!\nمن می‌توانم تو را ببینم."
DEFAULT_STAGES = [
    "فعالیت غیرمنتظره شناسایی شد.",
    "تصویر رویداد ثبت شد.",
    "مالک دستگاه مطلع شده است.",
    "لطفاً از لپ‌تاپ فاصله بگیرید.",
    "سیستم در حال قفل شدن است.",
]


def _notify(text: str) -> None:
    if shutil.which("notify-send"):
        try:
            subprocess.Popen(
                ["notify-send", "Laptop Guard", text.replace("\n", " ")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError:
            pass


def _load_background(root: tk.Tk, image_path: str) -> tuple[object | None, int, int]:
    """Return a PhotoImage-like object fitted to the current screen.

    Pillow is optional at runtime; without it the overlay uses the normal dark
    background rather than failing the security countdown.
    """
    if not image_path:
        return None, root.winfo_screenwidth(), root.winfo_screenheight()
    path = Path(image_path)
    if not path.exists():
        return None, root.winfo_screenwidth(), root.winfo_screenheight()
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageTk

        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        image = Image.open(path).convert("RGB")
        ratio = max(sw / max(1, image.width), sh / max(1, image.height))
        new_size = (max(1, int(image.width * ratio)), max(1, int(image.height * ratio)))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        left = max(0, (image.width - sw) // 2)
        top = max(0, (image.height - sh) // 2)
        image = image.crop((left, top, left + sw, top + sh))
        image = image.filter(ImageFilter.GaussianBlur(radius=1.4))
        image = ImageEnhance.Brightness(image).enhance(0.34)
        return ImageTk.PhotoImage(image), sw, sh
    except Exception:
        return None, root.winfo_screenwidth(), root.winfo_screenheight()


def show_fullscreen(
    text: str = DEFAULT_TEXT,
    seconds: int = 5,
    title: str = "هشدار امنیتی",
    *,
    image_path: str = "",
    stages: list[str] | None = None,
    notify_each_second: bool = False,
    windowed: bool = False,
) -> int:
    seconds = max(3, min(int(seconds), 300))
    stages = [str(x).strip() for x in (stages or DEFAULT_STAGES) if str(x).strip()]
    try:
        root = tk.Tk()
        root.title("Laptop Guard Intrusion Warning")
        root.configure(background="#05070b")
        root.attributes("-topmost", True)
        root.protocol("WM_DELETE_WINDOW", lambda: root.bell())
        if windowed:
            root.geometry("1100x720")
        else:
            try:
                root.attributes("-fullscreen", True)
            except tk.TclError:
                root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

        photo, sw, sh = _load_background(root, image_path)
        if photo is not None:
            bg = tk.Label(root, image=photo, bg="#05070b")
            bg.image = photo
            bg.place(x=0, y=0, relwidth=1, relheight=1)

        veil = tk.Frame(root, bg="#090d14")
        try:
            # Tk does not support per-widget alpha; this still gives a clear
            # high-contrast card over the captured camera image.
            root.attributes("-alpha", 0.995)
        except tk.TclError:
            pass
        veil.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.78, relheight=0.72)

        top = tk.Frame(veil, bg="#090d14")
        top.pack(fill="x", padx=36, pady=(30, 10))
        tk.Label(
            top,
            text="⚠️  " + title,
            bg="#090d14",
            fg="#fbbf24",
            font=("DejaVu Sans", 25, "bold"),
            justify="right",
        ).pack(side="right")

        countdown = tk.Label(
            top,
            text="",
            bg="#3f1117",
            fg="#fecaca",
            font=("DejaVu Sans", 18, "bold"),
            padx=16,
            pady=8,
        )
        countdown.pack(side="left")

        tk.Label(
            veil,
            text="\u200f" + text,
            fg="white",
            bg="#090d14",
            justify="center",
            font=("DejaVu Sans", 34, "bold"),
            wraplength=max(700, int(sw * 0.68)),
        ).pack(expand=True, fill="both", padx=42, pady=(10, 12))

        stage_box = tk.Frame(veil, bg="#151d2a", padx=24, pady=18)
        stage_box.pack(fill="x", padx=46, pady=(0, 20))
        stage_label = tk.Label(
            stage_box,
            text="",
            bg="#151d2a",
            fg="#e2e8f0",
            font=("DejaVu Sans", 18, "bold"),
            justify="right",
            anchor="e",
        )
        stage_label.pack(fill="x")

        footer = tk.Label(
            veil,
            text="📷 رویداد ثبت می‌شود  •  مالک دستگاه مطلع شده است  •  قفل سیستم در پایان شمارش",
            fg="#94a3b8",
            bg="#090d14",
            font=("DejaVu Sans", 12),
        )
        footer.pack(pady=(0, 24))

        remaining = {"value": seconds, "last_stage": None}

        def tick() -> None:
            n = remaining["value"]
            countdown.configure(text=f"قفل در {n} ثانیه")
            elapsed = max(0, seconds - n)
            if stages:
                index = min(len(stages) - 1, int(elapsed * len(stages) / max(1, seconds)))
                message = stages[index]
                stage_label.configure(text="\u200f" + message)
                if notify_each_second and remaining["last_stage"] != (n, message):
                    _notify(f"{message} — {n}")
                    remaining["last_stage"] = (n, message)
            if n <= 0:
                try:
                    root.destroy()
                except tk.TclError:
                    pass
                return
            remaining["value"] = n - 1
            root.after(1000, tick)

        # Do not let Escape dismiss the security countdown. Lock scheduling is
        # owned by GuardApp and can only be cancelled by owner grace/disarm.
        root.bind("<Escape>", lambda _e: root.bell())
        tick()
        root.mainloop()
        return 0
    except Exception:
        _notify(text)
        return 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=5)
    parser.add_argument("--title", default="هشدار امنیتی")
    parser.add_argument("--text", default=DEFAULT_TEXT)
    parser.add_argument("--image", default="")
    parser.add_argument("--stages-json", default="[]")
    parser.add_argument("--notify-each-second", action="store_true")
    parser.add_argument("--windowed", action="store_true")
    args = parser.parse_args()
    try:
        stages = json.loads(args.stages_json)
        if not isinstance(stages, list):
            stages = DEFAULT_STAGES
    except json.JSONDecodeError:
        stages = DEFAULT_STAGES
    return show_fullscreen(
        args.text,
        args.seconds,
        args.title,
        image_path=args.image,
        stages=stages,
        notify_each_second=args.notify_each_second,
        windowed=args.windowed,
    )


if __name__ == "__main__":
    raise SystemExit(main())
