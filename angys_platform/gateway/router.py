"""Authorize fixed provider commands before a future device-delivery adapter."""

from __future__ import annotations

from dataclasses import dataclass

from angys_platform.identity import IdentityService


class GatewayDenied(ValueError):
    """Raised when a provider message is not authorized for a fixed action."""


@dataclass(frozen=True)
class RoutedCommand:
    """An authorized command; this value deliberately has no execution behavior."""

    provider: str
    account_id: int
    device_id: str
    action: str


class GatewayRouter:
    """Server-side account/device router with no bot-token or OS-control access."""

    PROVIDERS = frozenset({"telegram", "bale"})
    ACTIONS = frozenset(
        {"status", "arm", "disarm", "lock", "suspend", "reboot", "shutdown"}
    )

    def __init__(self, identity: IdentityService) -> None:
        self.identity = identity

    @classmethod
    def _provider(cls, provider: str) -> str:
        if not isinstance(provider, str):
            raise GatewayDenied("unsupported provider account")
        normalized = provider.strip().lower()
        if normalized not in cls.PROVIDERS:
            raise GatewayDenied("unsupported provider account")
        return normalized

    def link_provider_account(
        self, provider: str, provider_user_id: str, account_id: int
    ) -> None:
        """Store a completed pairing link; pairing proof belongs to the caller."""
        provider = self._provider(provider)
        if (
            not isinstance(provider_user_id, str)
            or not provider_user_id
            or len(provider_user_id) > 256
        ):
            raise GatewayDenied("invalid provider account")
        try:
            self.identity.link_provider_account(provider, provider_user_id, account_id)
        except ValueError as error:
            raise GatewayDenied("unknown account") from error

    def route(
        self, provider: str, provider_user_id: str, device_id: str, action: str
    ) -> RoutedCommand:
        """Fail closed unless a linked provider account owns the active device."""
        provider = self._provider(provider)
        if not isinstance(provider_user_id, str) or not isinstance(action, str):
            raise GatewayDenied("unauthorized provider command")
        if action not in self.ACTIONS:
            raise GatewayDenied("unauthorized provider command")
        account_id = self.identity.linked_provider_account(provider, provider_user_id)
        if account_id is None:
            raise GatewayDenied("unauthorized provider command")
        if self.identity.device_owner(device_id) != account_id:
            raise GatewayDenied("device is not owned by provider account")
        return RoutedCommand(provider, account_id, device_id, action)
