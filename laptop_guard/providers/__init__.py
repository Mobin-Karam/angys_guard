from __future__ import annotations

from .http_bot import HttpBotProvider
from .profiles import get_provider_profile


def build_provider(
    provider: str,
    token: str,
    api_base: str = "",
    proxy: str = "",
):
    if provider not in {"telegram", "bale"}:
        return None
    profile = get_provider_profile(provider)
    return HttpBotProvider(
        token=token,
        api_base=api_base or profile.default_api_base,
        proxy=proxy,
        provider_name=provider,
    )
