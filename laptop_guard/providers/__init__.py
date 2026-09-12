from __future__ import annotations

from .http_bot import HttpBotProvider


def build_provider(provider: str, token: str, api_base: str, proxy: str = ""):
    if provider not in {"telegram", "bale"}:
        return None
    return HttpBotProvider(token=token, api_base=api_base, proxy=proxy, provider_name=provider)
