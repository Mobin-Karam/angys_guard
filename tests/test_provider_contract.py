from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from laptop_guard.providers import build_provider
from laptop_guard.providers.http_bot import HttpBotProvider
from laptop_guard.providers.profiles import get_provider_profile


class CaptureClient:
    def __init__(self, responses=None):
        self.calls = []
        self.responses = list(responses or [])

    def post(self, url, data=None, files=None, timeout=None):
        self.calls.append(
            {
                "url": url,
                "data": dict(data or {}),
                "files": files,
                "timeout": timeout,
            }
        )
        if self.responses:
            outcome = self.responses.pop(0)
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            request=request,
            json={"ok": True, "result": {"message_id": 1}},
        )

    def close(self):
        return None


@pytest.mark.parametrize(
    ("provider", "base"),
    [
        ("telegram", "https://api.telegram.org"),
        ("bale", "https://tapi.bale.ai"),
    ],
)
def test_provider_factory_uses_documented_default_base(provider, base):
    adapter = build_provider(provider, "123:test", "")
    assert isinstance(adapter, HttpBotProvider)
    assert adapter.provider_name == provider
    assert adapter.api_base == base
    adapter.client.close()


def test_telegram_reply_uses_reply_parameters():
    adapter = HttpBotProvider(
        "123:test",
        "https://api.telegram.org",
        provider_name="telegram",
    )
    fake = CaptureClient()
    adapter.client.close()
    adapter.client = fake

    adapter.send_message(42, "hello", reply_to_message_id=7)

    data = fake.calls[-1]["data"]
    assert "reply_to_message_id" not in data
    assert json.loads(data["reply_parameters"]) == {"message_id": 7}


def test_bale_reply_uses_reply_to_message_id():
    adapter = HttpBotProvider(
        "123:test",
        "https://tapi.bale.ai",
        provider_name="bale",
    )
    fake = CaptureClient()
    adapter.client.close()
    adapter.client = fake

    adapter.send_message(42, "hello", reply_to_message_id=7)

    data = fake.calls[-1]["data"]
    assert data["reply_to_message_id"] == "7"
    assert "reply_parameters" not in data


def test_inline_keyboard_is_shared_contract():
    markup = {
        "inline_keyboard": [
            [{"text": "Lock", "callback_data": "guard:lock"}],
        ]
    }
    for provider in ("telegram", "bale"):
        adapter = HttpBotProvider(
            "123:test",
            get_provider_profile(provider).default_api_base,
            provider_name=provider,
        )
        fake = CaptureClient()
        adapter.client.close()
        adapter.client = fake

        adapter.send_message(42, "hello", reply_markup=markup)

        assert json.loads(fake.calls[-1]["data"]["reply_markup"]) == markup


def test_video_streaming_hint_is_telegram_only(tmp_path: Path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"test-video")

    captured = {}
    for provider in ("telegram", "bale"):
        adapter = HttpBotProvider(
            "123:test",
            get_provider_profile(provider).default_api_base,
            provider_name=provider,
        )
        fake = CaptureClient()
        adapter.client.close()
        adapter.client = fake

        adapter.send_video(42, video, "clip")
        captured[provider] = fake.calls[-1]["data"]

    assert captured["telegram"]["supports_streaming"] == "true"
    assert "supports_streaming" not in captured["bale"]


def test_get_updates_has_bounded_long_poll_contract():
    request = httpx.Request(
        "POST",
        "https://tapi.bale.ai/bot123:test/getUpdates",
    )
    response = httpx.Response(
        200,
        request=request,
        json={"ok": True, "result": [{"update_id": 0}]},
    )
    adapter = HttpBotProvider(
        "123:test",
        "https://tapi.bale.ai",
        provider_name="bale",
    )
    fake = CaptureClient([response])
    adapter.client.close()
    adapter.client = fake

    updates = adapter.get_updates(offset=0, timeout=25)

    assert updates == [{"update_id": 0}]
    assert fake.calls[-1]["data"] == {
        "timeout": "25",
        "limit": "100",
        "offset": "0",
    }
    assert fake.calls[-1]["timeout"] == 40


def test_side_effecting_send_does_not_retry_after_transport_uncertainty():
    token = "123:test-only-secret"
    request = httpx.Request(
        "POST",
        f"https://api.telegram.org/bot{token}/sendMessage",
    )
    adapter = HttpBotProvider(
        token,
        "https://api.telegram.org",
        provider_name="telegram",
    )
    fake = CaptureClient(
        [httpx.ConnectError("simulated", request=request)]
    )
    adapter.client.close()
    adapter.client = fake

    with pytest.raises(Exception):
        adapter.send_message(42, "hello")

    assert len(fake.calls) == 1
