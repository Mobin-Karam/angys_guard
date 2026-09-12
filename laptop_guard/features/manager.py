from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Feature

CommandHandler = Callable[[int, str], None]
CallbackHandler = Callable[[int, int | None, str], None]


class FeatureConflictError(ValueError):
    pass


@dataclass(frozen=True)
class RouteInfo:
    feature: str
    route: str


class FeatureManager:
    """Owns deterministic command/callback routes and feature lifecycle."""

    def __init__(self) -> None:
        self._commands: dict[str, tuple[str, CommandHandler]] = {}
        self._callbacks: dict[str, tuple[str, CallbackHandler]] = {}
        self._features: list[Feature] = []

    @staticmethod
    def normalize_command(command: str) -> str:
        value = str(command or "").strip().split("@", 1)[0].lower()
        if value and not value.startswith("/"):
            value = "/" + value
        return value

    def add_command(self, feature: str, names: Iterable[str], handler: CommandHandler) -> None:
        for raw in names:
            name = self.normalize_command(raw)
            if not name:
                raise ValueError("Command name cannot be empty")
            if name in self._commands:
                owner = self._commands[name][0]
                raise FeatureConflictError(f"Command {name} already belongs to {owner}")
            self._commands[name] = (feature, handler)

    def add_callback(self, feature: str, prefix: str, handler: CallbackHandler) -> None:
        prefix = str(prefix or "").strip()
        if not prefix:
            raise ValueError("Callback prefix cannot be empty")
        for existing, (owner, _) in self._callbacks.items():
            if prefix.startswith(existing) or existing.startswith(prefix):
                raise FeatureConflictError(
                    f"Callback prefix {prefix} overlaps {existing} owned by {owner}"
                )
        self._callbacks[prefix] = (feature, handler)

    def install(self, feature: Feature) -> None:
        if any(item.name == feature.name for item in self._features):
            raise FeatureConflictError(f"Feature {feature.name} is already installed")
        commands_before = dict(self._commands)
        callbacks_before = dict(self._callbacks)
        try:
            feature.register(self)
        except Exception:
            self._commands = commands_before
            self._callbacks = callbacks_before
            raise
        self._features.append(feature)

    def dispatch_command(self, command: str, chat_id: int, argument: str = "") -> bool:
        route = self._commands.get(self.normalize_command(command))
        if route is None:
            return False
        route[1](chat_id, argument)
        return True

    def dispatch_callback(self, data: str, chat_id: int, message_id: int | None) -> bool:
        matches = [item for prefix, item in self._callbacks.items() if data.startswith(prefix)]
        if not matches:
            return False
        if len(matches) > 1:
            raise FeatureConflictError(f"Ambiguous callback route: {data}")
        matches[0][1](chat_id, message_id, data)
        return True

    def start(self) -> None:
        for feature in self._features:
            feature.start()

    def stop(self) -> None:
        for feature in reversed(self._features):
            feature.stop()

    def routes(self) -> tuple[RouteInfo, ...]:
        commands = [RouteInfo(owner, route) for route, (owner, _) in self._commands.items()]
        callbacks = [RouteInfo(owner, prefix + "*") for prefix, (owner, _) in self._callbacks.items()]
        return tuple(sorted(commands + callbacks, key=lambda item: (item.feature, item.route)))
