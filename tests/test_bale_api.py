from __future__ import annotations

import json

import httpx

from laptop_guard.bale_api import BaleApi, BaleApiError
from laptop_guard.providers.base import ProviderError
from laptop_guard.providers.http_bot import HttpBotProvider


class CaptureClient:
    def __init__(self):
        self.calls = []

    def post(self, url, data=None, files=None, timeout=None):
        self.calls.append((url, dict(data or {}), files, timeout))
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            request=request,
            json={"ok": True, "result": {"message_id": 1}},
        )

    def close(self):
        return None


def test_bale_api_is_compatibility_facade_over_active_adapter():
    api = BaleApi("123:secret")
    assert isinstance(api, HttpBotProvider)
    assert api.provider_name == "bale"
    assert api.base_url == "https://tapi.bale.ai"
    assert BaleApiError is ProviderError
    api.client.close()


def test_compatibility_send_message_uses_bale_payload():
    api = BaleApi("123:secret")
    fake = CaptureClient()
    api.client.close()
    api.client = fake

    markup = {
        "inline_keyboard": [
            [{"text": "Lock", "callback_data": "guard:lock"}],
        ]
    }
    api.send_message(42, "hello", reply_markup=markup, reply_to_message_id=7)

    url, data, _, _ = fake.calls[-1]
    assert url.endswith("/bot123:secret/sendMessage")
    assert data["reply_to_message_id"] == "7"
    assert json.loads(data["reply_markup"]) == markup


def test_file_download_url_keeps_bale_host():
    api = BaleApi("123:secret")
    assert (
        api._file_url("voice/file.ogg")
        == "https://tapi.bale.ai/file/bot123:secret/voice/file.ogg"
    )
    api.client.close()
