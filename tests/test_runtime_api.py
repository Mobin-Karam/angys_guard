from laptop_guard.models import AppConfig
from laptop_guard.providers.http_bot import HttpBotProvider
from laptop_guard.runtime_api import LocalRuntimeApi, build_runtime_api


def test_local_runtime_does_not_require_bot_token():
    cfg = AppConfig()
    cfg.bot.provider = "local"
    api = build_runtime_api(cfg, "")
    assert isinstance(api, LocalRuntimeApi)
    assert api.get_me()["id"] == "local"
    assert api.get_updates(timeout=0) == []


def test_remote_runtime_uses_shared_provider_factory(monkeypatch):
    import laptop_guard.runtime_api as runtime_api

    captured = {}

    class FakeApi:
        pass

    def build(provider, token, api_base, proxy):
        captured.update(
            provider=provider,
            token=token,
            api_base=api_base,
            proxy=proxy,
        )
        return FakeApi()

    monkeypatch.setattr(runtime_api, "build_provider", build)
    cfg = AppConfig()
    cfg.bot.provider = "telegram"
    cfg.bot.api_base = "https://api.telegram.org"
    cfg.bot.proxy = "socks5://127.0.0.1:9050"

    result = build_runtime_api(cfg, "secret")

    assert isinstance(result, FakeApi)
    assert captured == {
        "provider": "telegram",
        "token": "secret",
        "api_base": "https://api.telegram.org",
        "proxy": cfg.bot.proxy,
    }


def test_real_remote_runtime_builds_same_http_adapter_as_setup():
    for provider, base in (
        ("telegram", "https://api.telegram.org"),
        ("bale", "https://tapi.bale.ai"),
    ):
        cfg = AppConfig()
        cfg.bot.provider = provider
        cfg.bot.api_base = base
        api = build_runtime_api(cfg, "123:test")
        assert isinstance(api, HttpBotProvider)
        assert api.provider_name == provider
        api.client.close()
