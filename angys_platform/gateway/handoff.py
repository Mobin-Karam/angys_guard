"""Turn an authorized gateway route into a device-verifiable envelope."""

from __future__ import annotations

import secrets
import time

from angys_platform.protocol import CommandEnvelope

from .router import RoutedCommand


class CommandHandoff:
    """Server-side signer; transport and local execution remain separate."""

    def __init__(self, device_credentials: dict[str, tuple[int, bytes]]) -> None:
        self.device_credentials = device_credentials

    def envelope(self, routed: RoutedCommand, ttl_seconds: int = 30) -> CommandEnvelope:
        if not 1 <= ttl_seconds <= 60:
            raise ValueError("command TTL must be between one and sixty seconds")
        try:
            generation, secret = self.device_credentials[routed.device_id]
        except KeyError as error:
            raise ValueError("device is not enrolled for command delivery") from error
        now = int(time.time())
        return CommandEnvelope.issue(
            secret, routed.device_id, routed.account_id, routed.action, generation,
            secrets.token_urlsafe(24), now + ttl_seconds, now,
        )
