from laptop_guard import desktop_onboarding
from laptop_guard.models import AppConfig


def test_managed_desktop_profile_requires_explicit_local_consent(monkeypatch):
    monkeypatch.setattr(desktop_onboarding, "setup_is_complete", lambda: False)

    try:
        desktop_onboarding.configure_managed_local_profile(device_name="Linux", consent=False)
    except desktop_onboarding.DesktopOnboardingError as error:
        assert "consent" in str(error)
    else:
        raise AssertionError("desktop profile setup must require local consent")


def test_managed_desktop_profile_disables_private_or_broad_capabilities(monkeypatch):
    cfg = AppConfig()
    saved: list[AppConfig] = []
    monkeypatch.setattr(desktop_onboarding, "setup_is_complete", lambda: False)
    monkeypatch.setattr(desktop_onboarding, "load_config", lambda: cfg)
    monkeypatch.setattr(desktop_onboarding, "save_config", lambda value: saved.append(value))
    monkeypatch.setattr(
        desktop_onboarding,
        "RuntimeStateStore",
        lambda: type("State", (), {"refresh": lambda self: type("Result", (), {"armed": False})()})(),
    )

    result = desktop_onboarding.configure_managed_local_profile(device_name="  Linux Desktop  ", consent=True)

    assert result.device_name == "Linux Desktop"
    assert cfg.setup_complete is True
    assert cfg.bot.provider == "local"
    assert cfg.camera.enabled is False
    assert cfg.audio.sound_detection_enabled is False
    assert cfg.screen.screenshots_enabled is False
    assert cfg.screen.screen_video_enabled is False
    assert cfg.security.input_snapshot is False
    assert cfg.security.input_screen_snapshot is False
    assert cfg.security.allow_remote_unlock is False
    assert cfg.security.allow_remote_power is False
    assert cfg.apps.enabled is False
    assert cfg.apps.allow_launch is False
    assert cfg.apps.allow_close is False
    assert cfg.startup.managed_desktop_consent is True
    assert saved == [cfg]


def test_managed_desktop_profile_never_overwrites_existing_provider_setup(monkeypatch):
    cfg = AppConfig(setup_complete=True)
    cfg.bot.provider = "telegram"
    monkeypatch.setattr(desktop_onboarding, "setup_is_complete", lambda: True)
    monkeypatch.setattr(desktop_onboarding, "load_config", lambda: cfg)

    try:
        desktop_onboarding.configure_managed_local_profile(device_name="Linux", consent=True)
    except desktop_onboarding.DesktopOnboardingError as error:
        assert "Bale or Telegram" in str(error)
    else:
        raise AssertionError("existing provider setup must not be overwritten")
