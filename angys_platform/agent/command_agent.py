"""Verify signed commands and dispatch only the finite local action set."""

from __future__ import annotations

from typing import Callable, Protocol

from angys_platform.protocol import DeviceProtocol


class CommandTransport(Protocol):
    def poll(self, device_id: str): ...
    def acknowledge(self, device_id: str, request_id: str) -> None: ...


class DeviceCommandAgent:
    """Device-side loop; local handlers own policy/confirmation and OS effects."""

    def __init__(self, transport: CommandTransport, verifier: DeviceProtocol, handlers: dict[str, Callable[[], None]]) -> None:
        if set(handlers) - verifier.ACTIONS:
            raise ValueError("unsupported local action handler")
        self.transport = transport
        self.verifier = verifier
        self.handlers = handlers

    def run_once(self) -> bool:
        envelope = self.transport.poll(self.verifier.device_id)
        if envelope is None:
            return False
        accepted = self.verifier.accept(envelope)
        handler = self.handlers.get(accepted.action)
        if handler is None:
            raise ValueError("local policy does not allow this action")
        handler()
        self.transport.acknowledge(self.verifier.device_id, accepted.request_id)
        return True
