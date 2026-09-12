from __future__ import annotations

from .models import AppConfig, ProfileName

PROFILE_LABELS = {
    "away": "🚪 بیرون / Away",
    "home": "🏠 خانه / Home",
    "night": "🌙 شب / Night",
    "testing": "🧪 تست / Testing",
    "custom": "⚙️ سفارشی / Custom",
}


def apply_profile(cfg: AppConfig, profile: ProfileName) -> AppConfig:
    """Apply safe, reversible-ish defaults for a named operating profile.

    Profiles never enable remote unlock. Away/Night use the visible five-second
    warning countdown followed by the normal desktop lock; Home remains warning-only.
    """
    cfg.profile = profile
    if profile == "away":
        cfg.camera.enabled = True
        cfg.camera.mode = "motion_person"
        cfg.camera.motion_min_area = 2200
        cfg.camera.event_clip_seconds = max(10, cfg.camera.event_clip_seconds)
        cfg.camera.pre_event_seconds = max(5, cfg.camera.pre_event_seconds)
        cfg.camera.tamper_enabled = True
        cfg.security.input_action = "warning_lock"
        cfg.security.warning_seconds = 5
        cfg.security.lock_after_countdown = True
        cfg.security.input_snapshot = True
        cfg.security.lock_on_input = False
        cfg.monitors.usb_events = True
        cfg.monitors.power_events = True
    elif profile == "home":
        cfg.camera.enabled = True
        cfg.camera.mode = "motion"
        cfg.camera.motion_min_area = 4200
        cfg.camera.event_clip_seconds = min(max(cfg.camera.event_clip_seconds, 5), 10)
        cfg.camera.pre_event_seconds = min(max(cfg.camera.pre_event_seconds, 2), 5)
        cfg.security.input_action = "warning"
        cfg.security.input_snapshot = True
        cfg.security.lock_on_input = False
    elif profile == "night":
        cfg.camera.enabled = True
        cfg.camera.mode = "motion_person"
        cfg.camera.motion_min_area = 1700
        cfg.camera.event_clip_seconds = max(15, cfg.camera.event_clip_seconds)
        cfg.camera.pre_event_seconds = max(5, cfg.camera.pre_event_seconds)
        cfg.security.input_action = "warning_lock"
        cfg.security.warning_seconds = 5
        cfg.security.lock_after_countdown = True
        cfg.security.input_snapshot = True
        cfg.security.lock_on_input = False
        cfg.camera.tamper_enabled = True
    elif profile == "testing":
        cfg.camera.enabled = True
        cfg.camera.mode = "motion"
        cfg.camera.motion_min_area = 5000
        cfg.camera.event_clip_seconds = 0
        cfg.camera.pre_event_seconds = 0
        cfg.camera.tamper_enabled = False
        cfg.security.input_action = "notify"
        cfg.security.input_snapshot = False
        cfg.security.lock_on_input = False
        cfg.monitors.usb_events = False
        cfg.monitors.power_events = False
    return cfg
