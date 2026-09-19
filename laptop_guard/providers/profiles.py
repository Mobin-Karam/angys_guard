from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ReplyMode = Literal["reply_parameters", "reply_to_message_id"]


@dataclass(frozen=True, slots=True)
class ProviderProfile:
    """Documented transport differences for a Telegram-style provider."""

    name: str
    default_api_base: str
    reply_mode: ReplyMode
    supports_streaming_video_hint: bool
    max_download_bytes: int = 20 * 1024 * 1024
    update_limit: int = 100


PROVIDER_PROFILES: dict[str, ProviderProfile] = {
    "telegram": ProviderProfile(
        name="telegram",
        default_api_base="https://api.telegram.org",
        reply_mode="reply_parameters",
        supports_streaming_video_hint=True,
    ),
    "bale": ProviderProfile(
        name="bale",
        default_api_base="https://tapi.bale.ai",
        reply_mode="reply_to_message_id",
        # Bale's current sendVideo documentation does not list Telegram's
        # supports_streaming request hint, so do not send it by assumption.
        supports_streaming_video_hint=False,
    ),
}


def get_provider_profile(provider: str) -> ProviderProfile:
    normalized = str(provider or "").strip().lower()
    try:
        return PROVIDER_PROFILES[normalized]
    except KeyError as exc:
        raise ValueError(f"Unsupported bot provider: {normalized or provider}") from exc
