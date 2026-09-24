"""RTL Persian native onboarding guide for non-technical owners."""

from __future__ import annotations

from .text_direction import visual_text

try:
    import tkinter as tk
except ImportError:
    tk = None  # type: ignore[assignment]


def onboarding_steps(provider: str = "telegram") -> list[tuple[str, str]]:
    name = "تلگرام" if provider == "telegram" else "بله"
    return [
        ("۱. انتخاب پیام‌رسان", f"پیام‌رسان {name} را در راه‌اندازی انتخاب کنید."),
        ("۲. شناسه چت", "در ربات /id را بفرستید تا شناسه چت خود را ببینید."),
        ("۳. اتصال امن", "کد یک‌بارمصرفی که برنامه نشان می‌دهد را با /pair ارسال کنید."),
        ("۴. کنترل دستگاه", "پس از اتصال، فقط فرمان‌های مجاز مانند قفل، خواب، راه‌اندازی و خاموش‌کردن در دسترس است."),
    ]


def show_onboarding(provider: str = "telegram") -> None:
    """Show a local informational screen; setup still owns all secret entry."""
    if tk is None:
        raise RuntimeError("Tkinter is required for the onboarding window.")
    root = tk.Tk()
    root.title("AngysGuard — راه‌اندازی آسان")
    root.configure(bg="#071018")
    root.geometry("680x520")
    frame = tk.Frame(root, bg="#071018", padx=34, pady=30)
    frame.pack(fill="both", expand=True)
    tk.Label(frame, text=visual_text("🛡 انگِیس‌گارد", "rtl"), bg="#071018", fg="#f8fafc", font=("DejaVu Sans", 25, "bold"), anchor="e").pack(fill="x")
    tk.Label(frame, text=visual_text("اتصال آسان و امن دستگاه به ربات", "rtl"), bg="#071018", fg="#94a3b8", font=("DejaVu Sans", 13), anchor="e").pack(fill="x", pady=(4, 24))
    for title, detail in onboarding_steps(provider):
        card = tk.Frame(frame, bg="#111f2d", padx=16, pady=12)
        card.pack(fill="x", pady=6)
        tk.Label(card, text=visual_text(title, "rtl"), bg="#111f2d", fg="#22d3ee", font=("DejaVu Sans", 13, "bold"), anchor="e").pack(fill="x")
        tk.Label(card, text=visual_text(detail, "rtl"), bg="#111f2d", fg="#f8fafc", font=("DejaVu Sans", 11), anchor="e", justify="right", wraplength=570).pack(fill="x", pady=(4, 0))
    tk.Button(frame, text=visual_text("شروع راه‌اندازی", "rtl"), command=root.destroy, bg="#0891b2", fg="white", relief="flat", padx=16, pady=10).pack(anchor="e", pady=(20, 0))
    root.mainloop()
