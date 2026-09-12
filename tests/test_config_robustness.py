from laptop_guard import config as config_module


def test_string_false_is_not_coerced_to_true():
    assert config_module._coerce_like(True, "false") is False
    assert config_module._coerce_like(False, "true") is True
    assert config_module._coerce_like(True, "not-a-bool") is True


def test_malformed_legacy_warning_seconds_does_not_crash(tmp_path, monkeypatch):
    path = tmp_path / "config.toml"
    path.write_text('[security]\ninput_action = "warning"\nwarning_seconds = "invalid"\n')
    monkeypatch.setattr(config_module, "CONFIG_PATH", path)
    cfg = config_module.load_config()
    assert cfg.security.warning_seconds == 5
