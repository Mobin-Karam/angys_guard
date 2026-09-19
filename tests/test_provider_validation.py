from __future__ import annotations

import httpx
import pytest

from laptop_guard.providers.base import (
    ProviderAuthError,
    ProviderConnectionError,
    ProviderResponseError,
)
from laptop_guard.providers.http_bot import HttpBotProvider


class _PostClient:
    def __init__(self, outcome):
        self.outcome = outcome

    def post(self, url, data=None, files=None, timeout=None):
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome

    def close(self):
        return None


def test_http_provider_classifies_transport_failure_without_exposing_token():
    token = "123456:test-only-secret-token"
    request = httpx.Request(
        "POST",
        f"https://api.telegram.org/bot{token}/getMe",
    )
    provider = HttpBotProvider(
        token,
        "https://api.telegram.org",
        provider_name="telegram",
    )
    provider.client.close()
    provider.client = _PostClient(
        httpx.ConnectError("simulated network failure", request=request)
    )

    with pytest.raises(ProviderConnectionError) as captured:
        provider.get_me()

    assert token not in str(captured.value)


def test_http_provider_classifies_default_telegram_getme_404_as_auth_rejection():
    token = "123456:test-only-rejected-token"
    request = httpx.Request(
        "POST",
        f"https://api.telegram.org/bot{token}/getMe",
    )
    response = httpx.Response(404, request=request)
    provider = HttpBotProvider(
        token,
        "https://api.telegram.org",
        provider_name="telegram",
    )
    provider.client.close()
    provider.client = _PostClient(response)

    with pytest.raises(ProviderAuthError) as captured:
        provider.get_me()

    assert token not in str(captured.value)


def test_http_provider_classifies_default_bale_getme_404_as_auth_rejection():
    token = "123456:test-only-rejected-token"
    request = httpx.Request(
        "POST",
        f"https://tapi.bale.ai/bot{token}/getMe",
    )
    response = httpx.Response(404, request=request)
    provider = HttpBotProvider(
        token,
        "https://tapi.bale.ai",
        provider_name="bale",
    )
    provider.client.close()
    provider.client = _PostClient(response)

    with pytest.raises(ProviderAuthError):
        provider.get_me()


def test_http_provider_does_not_treat_custom_api_404_as_proof_token_is_bad():
    token = "123456:test-only-candidate-token"
    request = httpx.Request(
        "POST",
        f"https://gateway.example.invalid/bot{token}/getMe",
    )
    response = httpx.Response(404, request=request)
    provider = HttpBotProvider(
        token,
        "https://gateway.example.invalid",
        provider_name="telegram",
    )
    provider.client.close()
    provider.client = _PostClient(response)

    with pytest.raises(ProviderResponseError) as captured:
        provider.get_me()

    assert token not in str(captured.value)
