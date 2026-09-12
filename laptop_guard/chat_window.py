from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from .chat_surface import INBOX, OUTBOX
from .text_direction import (
    directional_text,
    paragraph_directions,
    resolve_direction,
    text_direction,
    visual_text,
)

try:
    import tkinter as tk
except ImportError:  # Main guard must not crash just because python3-tk is missing.
    tk = None  # type: ignore[assignment]

BG = "#071018"
SURFACE = "#0c1722"
SURFACE_2 = "#111f2d"
BORDER = "#223346"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
OWNER_BG = "#0b4a6f"
VISITOR_BG = "#263446"
SYSTEM_BG = "#45242b"
ACCENT = "#22d3ee"
WARNING = "#fbbf24"


class ChatWindow:
    def __init__(
        self,
        seconds: int,
        allow_reply: bool,
        session_id: str,
        direction: str = "auto",
    ) -> None:
        if tk is None:
            raise RuntimeError("Tkinter is not installed. Install python3-tk for Guard Chat.")

        self.seconds = max(15, min(int(seconds), 3600))
        self.remaining = self.seconds
        self.allow_reply = allow_reply
        self.session_id = session_id
        self.direction_mode = direction if direction in {"auto", "rtl", "ltr"} else "auto"
        self.inbox_pos = 0
        self.seen: set[str] = set()
        self.history: list[tuple[str, str, str]] = []
        self.font_size = 16
        self.composer_direction = "rtl"
        self._direction_update_pending = False

        self.root = tk.Tk()
        self.root.title("Laptop Guard — Security Conversation")
        self.root.configure(bg=BG)
        self.root.attributes("-topmost", True)
        try:
            self.root.attributes("-fullscreen", True)
        except tk.TclError:
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.protocol("WM_DELETE_WINDOW", self._deny_close)
        self.root.bind("<Escape>", self._deny_close)
        self.root.bind("<Alt-F4>", self._deny_close)
        self.root.bind("<Control-plus>", lambda _e: self._change_font(1))
        self.root.bind("<Control-equal>", lambda _e: self._change_font(1))
        self.root.bind("<Control-minus>", lambda _e: self._change_font(-1))

        self._build_ui()
        self.root.after(120, self.poll_inbox)
        self.root.after(1000, self.tick)

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=34, pady=(24, 8))

        title_box = tk.Frame(header, bg=BG)
        title_box.pack(side="right")
        tk.Label(
            title_box,
            text="🛡 Laptop Guard",
            bg=BG,
            fg=TEXT,
            font=("DejaVu Sans", 23, "bold"),
        ).pack(anchor="e")
        tk.Label(
            title_box,
            text=visual_text("گفت‌وگوی امنیتی • Security conversation", "auto"),
            bg=BG,
            fg=MUTED,
            font=("DejaVu Sans", 11),
        ).pack(anchor="e", pady=(2, 0))

        left = tk.Frame(header, bg=BG)
        left.pack(side="left")
        self.countdown = tk.Label(
            left,
            text="",
            bg="#3b1720",
            fg="#fecdd3",
            font=("DejaVu Sans", 12, "bold"),
            padx=14,
            pady=7,
        )
        self.countdown.pack(side="left")
        self.direction_badge = tk.Label(
            left,
            text="",
            bg=SURFACE_2,
            fg=ACCENT,
            font=("DejaVu Sans", 10, "bold"),
            padx=10,
            pady=7,
        )
        self.direction_badge.pack(side="left", padx=(8, 0))
        self._update_direction_badge()

        divider = tk.Frame(self.root, bg=BORDER, height=1)
        divider.pack(fill="x", padx=34, pady=(6, 8))

        body = tk.Frame(self.root, bg=BG)
        body.pack(expand=True, fill="both", padx=34, pady=4)
        self.canvas = tk.Canvas(body, bg=BG, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        self.messages = tk.Frame(self.canvas, bg=BG)
        self.messages.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self._canvas_window = self.canvas.create_window((0, 0), window=self.messages, anchor="nw")
        self.canvas.bind("<Configure>", self._resize_messages)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

        self.empty = tk.Label(
            self.messages,
            text=visual_text("در انتظار پیام مالک…\nWaiting for the owner…", "auto"),
            bg=BG,
            fg="#64748b",
            font=("DejaVu Sans", 15),
            justify="center",
        )
        self.empty.pack(pady=80)

        quick = tk.Frame(self.root, bg=BG)
        quick.pack(fill="x", padx=34, pady=(6, 5))
        for label, value in (
            ("باشه / OK", "باشه، متوجه شدم. / OK, understood."),
            ("من صاحب دستگاه هستم", "من صاحب دستگاه هستم."),
            ("Please contact me", "Please contact me."),
        ):
            tk.Button(
                quick,
                text=visual_text(label, "auto"),
                command=lambda v=value: self._quick_reply(v),
                bg=SURFACE_2,
                fg=TEXT,
                activebackground=BORDER,
                activeforeground=TEXT,
                relief="flat",
                bd=0,
                padx=12,
                pady=6,
                font=("DejaVu Sans", 10),
                state="normal" if self.allow_reply else "disabled",
            ).pack(side="right", padx=(6, 0))

        composer_card = tk.Frame(self.root, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        composer_card.pack(fill="x", padx=34, pady=(5, 16))

        toolbar = tk.Frame(composer_card, bg=SURFACE)
        toolbar.pack(fill="x", padx=12, pady=(9, 3))
        tk.Label(
            toolbar,
            text=visual_text("جهت متن / Text direction", "auto"),
            bg=SURFACE,
            fg=MUTED,
            font=("DejaVu Sans", 9),
        ).pack(side="right")
        for mode, label in (("auto", "AUTO"), ("rtl", "RTL"), ("ltr", "LTR")):
            tk.Button(
                toolbar,
                text=label,
                command=lambda m=mode: self.set_direction_mode(m),
                bg=SURFACE_2,
                fg=TEXT,
                activebackground=BORDER,
                activeforeground=ACCENT,
                relief="flat",
                bd=0,
                padx=9,
                pady=3,
                font=("DejaVu Sans", 9, "bold"),
            ).pack(side="left", padx=(0, 5))

        compose_row = tk.Frame(composer_card, bg=SURFACE)
        compose_row.pack(fill="x", padx=12, pady=(3, 11))
        self.composer = tk.Text(
            compose_row,
            height=3,
            wrap="word",
            bg="#0a131e",
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground="#155e75",
            relief="flat",
            bd=0,
            padx=13,
            pady=10,
            font=("DejaVu Sans", 14),
        )
        self.composer.pack(side="right", expand=True, fill="x", padx=(10, 0))
        self.composer.bind("<KeyRelease>", self._composer_direction_event)
        self.composer.bind("<<Modified>>", self._composer_modified)
        self.composer.bind("<<Paste>>", self._schedule_composer_direction, add="+")
        self.composer.bind("<<Cut>>", self._schedule_composer_direction, add="+")
        self.composer.bind("<Return>", self._return_pressed)
        self.composer.tag_configure("dir_rtl", justify="right", lmargin1=8, rmargin=8)
        self.composer.tag_configure("dir_ltr", justify="left", lmargin1=8, rmargin=8)
        self.composer.edit_modified(False)

        self.send_button = tk.Button(
            compose_row,
            text=visual_text("ارسال", "rtl") + "\nSend",
            command=self.send_reply,
            bg="#0891b2",
            fg="white",
            activebackground="#0e7490",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=22,
            pady=10,
            font=("DejaVu Sans", 11, "bold"),
        )
        self.send_button.pack(side="left", fill="y")
        if not self.allow_reply:
            self.composer.configure(state="disabled")
            self.send_button.configure(state="disabled")

        tk.Label(
            self.root,
            text=visual_text("📷 Security activity may be recorded • فعالیت امنیتی ممکن است ثبت شود", "auto"),
            bg=BG,
            fg="#64748b",
            font=("DejaVu Sans", 10),
        ).pack(pady=(0, 12))

    def _deny_close(self, _event=None):
        try:
            self.root.bell()
        except Exception:
            pass
        return "break"

    def _resize_messages(self, event) -> None:
        self.canvas.itemconfigure(self._canvas_window, width=max(300, event.width - 2))

    def _change_font(self, delta: int) -> None:
        self.font_size = max(11, min(24, self.font_size + delta))

    def _update_direction_badge(self) -> None:
        if self.direction_mode == "auto":
            label = "AUTO • RTL ←" if self.composer_direction == "rtl" else "AUTO • LTR →"
        else:
            label = "RTL ←" if self.direction_mode == "rtl" else "LTR →"
        self.direction_badge.configure(text=label)

    def set_direction_mode(self, mode: str) -> None:
        if mode not in {"auto", "rtl", "ltr"}:
            return
        self.direction_mode = mode
        self._update_direction_badge()
        self._apply_composer_direction()

    def _composer_direction_event(self, _event=None) -> None:
        self._schedule_composer_direction()

    def _composer_modified(self, _event=None) -> None:
        if self.composer.edit_modified():
            self.composer.edit_modified(False)
            self._schedule_composer_direction()

    def _schedule_composer_direction(self, _event=None) -> None:
        if self._direction_update_pending:
            return
        self._direction_update_pending = True
        self.root.after_idle(self._apply_composer_direction)

    def _apply_composer_direction(self) -> None:
        text = self.composer.get("1.0", "end-1c")
        directions = paragraph_directions(text, self.direction_mode, "rtl")
        self.composer.tag_remove("dir_rtl", "1.0", "end")
        self.composer.tag_remove("dir_ltr", "1.0", "end")
        for line_number, resolved in enumerate(directions, start=1):
            self.composer.tag_add(
                f"dir_{resolved}",
                f"{line_number}.0",
                f"{line_number}.end+1c",
            )

        try:
            current_line = max(1, int(self.composer.index("insert").split(".", 1)[0]))
        except (ValueError, tk.TclError):
            current_line = 1
        self.composer_direction = directions[min(current_line - 1, len(directions) - 1)]
        self._direction_update_pending = False
        self._update_direction_badge()

    def _return_pressed(self, event):
        # Shift+Enter inserts a newline; Enter sends.
        if event.state & 0x0001:
            return None
        self.send_reply()
        return "break"

    def _quick_reply(self, text: str) -> None:
        if not self.allow_reply:
            return
        self.composer.delete("1.0", "end")
        self.composer.insert("1.0", text)
        self._apply_composer_direction()
        self.composer.focus_set()

    def add_bubble(self, role: str, text: str, ts: str) -> None:
        clean = str(text).strip()
        if not clean:
            return
        if self.empty.winfo_ismapped():
            self.empty.pack_forget()

        display, resolved = directional_text(clean, self.direction_mode)
        justify = "right" if resolved == "rtl" else "left"
        anchor = "e" if resolved == "rtl" else "w"

        outer = tk.Frame(self.messages, bg=BG)
        outer.pack(fill="x", padx=20, pady=6)
        if role == "owner":
            bg, label, side = OWNER_BG, "مالک • Owner", "right"
        elif role == "visitor":
            bg, label, side = VISITOR_BG, "کاربر لپ‌تاپ • Local user", "left"
        else:
            bg, label, side = SYSTEM_BG, "سیستم • System", "center"

        bubble = tk.Frame(outer, bg=bg, padx=15, pady=10)
        bubble.pack(anchor={"right": "e", "left": "w", "center": "center"}[side])
        tk.Label(
            bubble,
            text=f"{visual_text(label, 'auto')}  •  {ts}  •  {resolved.upper()}",
            bg=bg,
            fg="#cbd5e1",
            font=("DejaVu Sans", 9, "bold"),
        ).pack(anchor=anchor)
        tk.Label(
            bubble,
            text=display,
            bg=bg,
            fg=TEXT,
            font=("DejaVu Sans", self.font_size),
            justify=justify,
            anchor=anchor,
            wraplength=max(420, min(1050, self.root.winfo_screenwidth() - 420)),
        ).pack(anchor=anchor, pady=(5, 0))

        self.history.append((ts, role, clean))
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def send_reply(self) -> None:
        if not self.allow_reply:
            return
        text = self.composer.get("1.0", "end-1c").strip()
        if not text:
            return
        self.composer.delete("1.0", "end")
        self._apply_composer_direction()
        ts = datetime.now().strftime("%H:%M:%S")
        payload = {
            "session_id": self.session_id,
            "time": ts,
            "text": text,
            "direction": resolve_direction(text, self.direction_mode, "rtl"),
        }
        OUTBOX.parent.mkdir(parents=True, exist_ok=True)
        with OUTBOX.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            fh.flush()
        self.add_bubble("visitor", text, ts)

    def poll_inbox(self) -> None:
        try:
            size = INBOX.stat().st_size
            if size < self.inbox_pos:
                self.inbox_pos = 0
            if size > self.inbox_pos:
                with INBOX.open("r", encoding="utf-8") as fh:
                    fh.seek(self.inbox_pos)
                    data = fh.read()
                    self.inbox_pos = fh.tell()
                for line in data.splitlines():
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if item.get("session_id") != self.session_id:
                        continue
                    mid = str(item.get("id") or "")
                    if mid and mid in self.seen:
                        continue
                    if mid:
                        self.seen.add(mid)
                    kind = str(item.get("kind") or "message")
                    if kind == "control":
                        if str(item.get("text")) == "close":
                            self.root.destroy()
                            return
                        continue
                    self.add_bubble(
                        str(item.get("role") or "system"),
                        str(item.get("text") or ""),
                        str(item.get("time") or ""),
                    )
                    if isinstance(item.get("seconds"), int):
                        self.remaining = max(self.remaining, int(item["seconds"]))
        except OSError:
            pass
        self.root.after(220, self.poll_inbox)

    def tick(self) -> None:
        self.countdown.configure(
            text=visual_text(f"{self.remaining}s • زمان باقی‌مانده", "auto")
        )
        if self.remaining <= 0:
            self.root.destroy()
            return
        self.remaining -= 1
        self.root.after(1000, self.tick)

    def run(self) -> None:
        self.composer.focus_set()
        self.root.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--allow-reply", choices=["0", "1"], default="1")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--direction", choices=["auto", "rtl", "ltr"], default="auto")
    args = parser.parse_args()
    if tk is None:
        print("Laptop Guard Chat requires Tkinter. Install python3-tk.")
        return 3
    ChatWindow(
        args.seconds,
        args.allow_reply == "1",
        args.session_id,
        args.direction,
    ).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
