from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_API = ROOT / "laptop_guard" / "runtime_api.py"
BALE_API = ROOT / "laptop_guard" / "bale_api.py"
ARCHITECTURE = ROOT / "docs" / "ARCHITECTURE.md"
PROVIDERS = ROOT / "docs" / "PROVIDERS.md"


def test_runtime_api_constructs_provider_through_one_factory():
    text = RUNTIME_API.read_text(encoding="utf-8")

    assert "from .providers import build_provider" in text
    assert "BaleApi" not in text
    assert "requests" not in text
    assert "httpx" not in text


def test_bale_api_is_explicit_compatibility_only_surface():
    text = BALE_API.read_text(encoding="utf-8")

    assert "Compatibility facade" in text
    assert "providers.build_provider" in text
    assert "requests" not in text


def test_architecture_documents_one_active_transport_strategy():
    text = ARCHITECTURE.read_text(encoding="utf-8")
    providers = PROVIDERS.read_text(encoding="utf-8")

    assert "HttpBotProvider" in text
    assert "compatibility-only" in text
    assert "Telegram" in providers
    assert "Bale" in providers
    assert "reply_parameters" in providers
    assert "reply_to_message_id" in providers
    assert "https://core.telegram.org/bots/api" in providers
    assert "https://docs.bale.ai/" in providers
