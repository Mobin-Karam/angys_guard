from __future__ import annotations

import re
import unicodedata
from typing import Literal

Direction = Literal["rtl", "ltr"]
DirectionMode = Literal["auto", "rtl", "ltr"]

# Persian/Arabic ranges, including presentation/extended characters.
_RTL_RE = re.compile(
    r"[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF\U0001EE00-\U0001EEFF]"
)

try:
    import arabic_reshaper  # type: ignore
except ImportError:  # Optional, but recommended for older Tk builds.
    arabic_reshaper = None  # type: ignore[assignment]

try:
    from bidi.algorithm import get_display as _bidi_get_display  # type: ignore
except ImportError:  # Optional, but recommended for correct Tk RTL rendering.
    _bidi_get_display = None


def text_direction(text: object, default: Direction = "ltr") -> Direction:
    """Return the direction of the first strong Unicode character.

    Numbers, punctuation, whitespace, emoji, and neutral characters do not decide
    the direction. This makes mixed Persian/English messages behave naturally.
    """
    value = str(text or "")
    fallback: Direction = default if default in {"rtl", "ltr"} else "ltr"

    for ch in value:
        bidi = unicodedata.bidirectional(ch)
        if bidi in {"R", "AL"}:
            return "rtl"
        if bidi == "L":
            return "ltr"

    return fallback


def contains_rtl(text: object) -> bool:
    return bool(_RTL_RE.search(str(text or "")))


def resolve_direction(text: object, mode: DirectionMode = "auto", default: Direction = "rtl") -> Direction:
    if mode == "rtl":
        return "rtl"
    if mode == "ltr":
        return "ltr"
    return text_direction(text, default)


def paragraph_directions(
    text: object,
    mode: DirectionMode = "auto",
    default: Direction = "rtl",
) -> list[Direction]:
    """Resolve every input paragraph independently for editable text widgets."""
    value = str(text or "")
    lines = value.split("\n")
    return [resolve_direction(line, mode, default) for line in lines]


def _reshape_arabic(text: str) -> str:
    if not text or not contains_rtl(text) or arabic_reshaper is None:
        return text
    try:
        return arabic_reshaper.reshape(text)
    except Exception:
        # Display helpers must never make the security window unusable.
        return text


def _visual_line(line: str, direction: Direction) -> str:
    if not line:
        return line

    # python-bidi converts logical Unicode order into visual order for widgets
    # (such as older Tk labels) that do not implement the BiDi algorithm well.
    if _bidi_get_display is not None:
        try:
            shaped = _reshape_arabic(line)
            return _bidi_get_display(shaped, base_dir="R" if direction == "rtl" else "L")
        except Exception:
            pass

    # Graceful fallback: keep valid logical Unicode. Modern Tk builds may render
    # this correctly by themselves; importantly, we never reverse strings by hand.
    return line


def visual_text(
    text: object,
    mode: DirectionMode = "auto",
    default: Direction = "rtl",
) -> str:
    """Return text prepared only for visual rendering in Tkinter.

    Never save the returned value to JSON, logs, clipboard history, or network
    payloads. Store/transmit the original logical Unicode text instead.
    """
    value = str(text or "")
    resolved = resolve_direction(value, mode, default)
    return "\n".join(_visual_line(line, resolved) for line in value.split("\n"))


def directional_text(
    text: object,
    mode: DirectionMode = "auto",
    default: Direction = "rtl",
) -> tuple[str, Direction]:
    """Return ``(visual_text, resolved_direction)`` for display widgets."""
    value = str(text or "")
    resolved = resolve_direction(value, mode, default)
    return visual_text(value, resolved, default), resolved


def direction_mark(direction: Direction) -> str:
    """Unicode mark useful in plain-text metadata without changing the content."""
    return "\u200f" if direction == "rtl" else "\u200e"
