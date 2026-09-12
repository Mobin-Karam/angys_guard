from pathlib import Path

import laptop_guard.config as config_module


def test_old_lock_config_migrates_to_visible_countdown_lock(tmp_path, monkeypatch):
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
[camera]
index = 0
[audio]
backend = "auto"
input = "default"
[security]
lock_on_input = true
allow_remote_unlock = false
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(config_module, "CONFIG_PATH", cfg_path)
    cfg = config_module.load_config()
    assert cfg.security.input_action == "warning_lock"
    assert cfg.security.lock_on_input is False
