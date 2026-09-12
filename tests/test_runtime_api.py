from laptop_guard.models import AppConfig
from laptop_guard.runtime_api import LocalRuntimeApi, build_runtime_api


def test_local_runtime_does_not_require_bot_token():
    cfg = AppConfig()
    cfg.bot.provider = "local"
    api = build_runtime_api(cfg, "")
    assert isinstance(api, LocalRuntimeApi)
    assert api.get_me()["id"] == "local"
    assert api.get_updates(timeout=0) == []


def test_remote_runtime_receives_configured_proxy(monkeypatch):
    import laptop_guard.runtime_api as runtime_api

    captured = {}

    class FakeApi:
        def __init__(self, token, base_url, proxy):
            captured.update(token=token, base_url=base_url, proxy=proxy)

    monkeypatch.setattr(runtime_api, "BaleApi", FakeApi)
    cfg = AppConfig()
    cfg.bot.proxy = "socks5://127.0.0.1:9050"
    build_runtime_api(cfg, "secret")
    assert captured["proxy"] == cfg.bot.proxy
