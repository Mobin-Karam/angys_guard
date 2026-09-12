from __future__ import annotations

import argparse
import tkinter as tk

from .audio_intercom import STOP_FLAG


class Indicator:
    def __init__(self, seconds: int) -> None:
        self.remaining = seconds
        self.root = tk.Tk()
        self.root.title("Laptop Guard Voice")
        self.root.configure(bg="#111827")
        self.root.attributes("-topmost", True)
        self.root.geometry("460x190+40+40")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        tk.Label(
            self.root, text="🎙 مکالمه صوتی فعال است", bg="#111827", fg="#f8fafc",
            font=("DejaVu Sans", 18, "bold")
        ).pack(pady=(22, 8))
        tk.Label(
            self.root, text="صدا در قالب بخش‌های کوتاه برای مالک ارسال می‌شود.",
            bg="#111827", fg="#94a3b8", font=("DejaVu Sans", 11)
        ).pack()
        self.clock = tk.Label(self.root, text="", bg="#111827", fg="#38bdf8", font=("DejaVu Sans", 13, "bold"))
        self.clock.pack(pady=8)
        tk.Button(self.root, text="توقف مکالمه", command=self.stop, bg="#991b1b", fg="white", relief="flat", padx=18, pady=6).pack()
        self.root.after(1000, self.tick)

    def stop(self) -> None:
        try:
            STOP_FLAG.parent.mkdir(parents=True, exist_ok=True)
            STOP_FLAG.write_text("stop", encoding="utf-8")
        except OSError:
            pass
        self.root.destroy()

    def tick(self) -> None:
        self.clock.configure(text=f"زمان باقی‌مانده: {self.remaining} ثانیه")
        self.remaining -= 1
        if self.remaining < 0:
            self.root.destroy()
            return
        self.root.after(1000, self.tick)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seconds", type=int, default=30)
    args = p.parse_args()
    Indicator(max(1, args.seconds)).root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
