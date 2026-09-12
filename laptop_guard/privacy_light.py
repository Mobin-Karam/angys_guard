from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LightStatus:
    available: bool
    writable: bool
    name: str = ""
    brightness: int | None = None
    max_brightness: int | None = None
    detail: str = ""


class CameraPrivacyLight:
    """Best-effort control for a *separate* camera indicator exposed via sysfs.

    Many laptop webcam LEDs are electrically tied to the image sensor and cannot
    be controlled independently. Laptop Guard intentionally never suppresses an
    active-camera privacy indicator. It can turn a separately exposed indicator
    on, and can return it to a camera-following/off state only when capture is off.
    """

    KEYWORDS = ("camera", "webcam", "video", "cam")

    def __init__(self) -> None:
        self.path = self._discover()

    def _discover(self) -> Path | None:
        root = Path("/sys/class/leds")
        if not root.exists():
            return None
        candidates: list[Path] = []
        for item in root.iterdir():
            name = item.name.lower()
            if any(k in name for k in self.KEYWORDS) and (item / "brightness").exists():
                candidates.append(item)
        return sorted(candidates, key=lambda p: p.name)[0] if candidates else None

    def status(self) -> LightStatus:
        if not self.path:
            return LightStatus(
                False,
                False,
                detail="No independently controllable camera LED was exposed by Linux; it probably follows camera hardware automatically.",
            )
        brightness_path = self.path / "brightness"
        max_path = self.path / "max_brightness"
        try:
            brightness = int(brightness_path.read_text().strip())
        except Exception:
            brightness = None
        try:
            maximum = int(max_path.read_text().strip())
        except Exception:
            maximum = 1
        return LightStatus(
            True,
            brightness_path.exists() and brightness_path.stat().st_mode is not None and __import__("os").access(brightness_path, __import__("os").W_OK),
            name=self.path.name,
            brightness=brightness,
            max_brightness=maximum,
            detail=str(self.path),
        )

    def turn_on(self) -> tuple[bool, str]:
        status = self.status()
        if not status.available:
            return False, status.detail
        if not status.writable:
            return False, f"Camera LED '{status.name}' exists but is not writable by this user."
        try:
            (self.path / "brightness").write_text(str(max(1, status.max_brightness or 1)))
            return True, f"Camera indicator '{status.name}' turned on."
        except Exception as exc:
            return False, f"Could not turn on camera indicator: {exc}"

    def turn_off(self, camera_enabled: bool) -> tuple[bool, str]:
        if camera_enabled:
            return False, "Camera is active; Laptop Guard will not suppress an active-camera privacy indicator."
        status = self.status()
        if not status.available:
            return False, status.detail
        if not status.writable:
            return False, f"Camera LED '{status.name}' is hardware/permission controlled."
        try:
            (self.path / "brightness").write_text("0")
            return True, f"Camera is off; indicator '{status.name}' turned off."
        except Exception as exc:
            return False, f"Could not turn off camera indicator: {exc}"

    def camera_follow(self, camera_enabled: bool) -> tuple[bool, str]:
        """Safe indicator policy: never force the indicator dark while capturing."""
        status = self.status()
        if not status.available:
            return False, status.detail
        if not status.writable:
            return False, f"Camera LED '{status.name}' is hardware/permission controlled."
        if camera_enabled:
            # Keeping the visible indicator on is the safe behavior during capture.
            return self.turn_on()
        try:
            (self.path / "brightness").write_text("0")
            return True, f"Camera is off; indicator '{status.name}' turned off."
        except Exception as exc:
            return False, f"Could not update camera indicator: {exc}"
