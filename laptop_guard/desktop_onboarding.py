"""Safe non-interactive setup used only by the AngysGuard desktop client.

The desktop client is a managed-control companion, not a shortcut around the
interactive setup wizard. Its first-run profile deliberately enables no
camera, microphone, screen capture, app control, remote unlock, or remote
power. A user can later opt in through the local guided setup flow.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import load_config, save_config, setup_is_complete
from .state import RuntimeStateStore


class DesktopOnboardingError(ValueError):
    """The desktop app attempted an unsafe or incompatible local transition."""


@dataclass(frozen=True)
class DesktopOnboardingStatus:
    configured: bool
    managed_local_profile: bool
    consent_recorded: bool
    armed: bool
    device_name: str


def configure_managed_local_profile(*, device_name: str, consent: bool) -> DesktopOnboardingStatus:
    """Create the minimal consented profile used by the managed desktop app.

    Existing non-local setups are never rewritten: they may contain owner
    configured provider and capability choices which only local setup may alter.
    Re-running this operation for the same local profile is idempotent.
    """

    normalized_name = device_name.strip()
    if not consent:
        raise DesktopOnboardingError("local protection consent is required")
    if not normalized_name or len(normalized_name) > 80:
        raise DesktopOnboardingError("device name must contain 1 to 80 characters")

    existing_complete = setup_is_complete()
    cfg = load_config()
    if existing_complete and cfg.bot.provider != "local":
        raise DesktopOnboardingError(
            "this device already uses a local Bale or Telegram setup; use local reconfiguration instead"
        )

    if not existing_complete:
        cfg.device_name = normalized_name
        cfg.setup_complete = True
        cfg.bot.provider = "local"
        cfg.bot.chat_id = None
        cfg.bot.proxy = ""

        # The managed server/bot is only a fixed-action delivery path. Every
        # potentially private capture or broad local app action remains off
        # until the owner explicitly configures it on the protected device.
        cfg.camera.enabled = False
        cfg.audio.sound_detection_enabled = False
        cfg.screen.screenshots_enabled = False
        cfg.screen.screen_video_enabled = False
        cfg.security.input_snapshot = False
        cfg.security.input_screen_snapshot = False
        cfg.security.input_screen_video_seconds = 0
        cfg.security.intrusion_photo_background = False
        cfg.security.warning_video = False
        cfg.security.allow_remote_unlock = False
        cfg.security.allow_remote_power = False
        cfg.apps.enabled = False
        cfg.apps.allow_launch = False
        cfg.apps.allow_close = False

    cfg.startup.managed_desktop_consent = True
    save_config(cfg)
    return desktop_onboarding_status()


def desktop_onboarding_status() -> DesktopOnboardingStatus:
    """Return a small non-secret status payload suitable for the desktop UI."""

    cfg = load_config()
    state = RuntimeStateStore().refresh()
    return DesktopOnboardingStatus(
        configured=setup_is_complete(),
        managed_local_profile=cfg.bot.provider == "local",
        consent_recorded=bool(cfg.startup.managed_desktop_consent),
        armed=bool(state.armed),
        device_name=cfg.device_name,
    )
