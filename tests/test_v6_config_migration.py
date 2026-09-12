from pathlib import Path

import laptop_guard.config as config_module


def test_external_text_editor_migrates_to_live_notepad(tmp_path, monkeypatch):
    cfg_path = tmp_path / "config.toml"
    cfg_path.write_text(
        """
[app]
setup_complete = true
[bot]
provider = "local"
api_base = ""
proxy = ""
poll_timeout = 25
[communication]
surface = "text_editor"
open_text_editor_mirror = true
[security]
input_action = "warning"
warning_seconds = 20
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(config_module, "CONFIG_PATH", cfg_path)
    cfg = config_module.load_config()
    assert cfg.communication.surface == "live_notepad"
    assert cfg.communication.open_text_editor_mirror is False
    assert cfg.security.input_action == "warning_lock"
    assert cfg.security.warning_seconds == 5


def test_v6_default_input_evidence_settings():
    cfg = config_module.AppConfig()
    assert cfg.security.input_action == "warning_lock"
    assert cfg.security.input_screen_snapshot is True
    assert cfg.security.input_screen_video_seconds == 5
    assert cfg.security.intrusion_photo_background is True
