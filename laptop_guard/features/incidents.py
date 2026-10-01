from __future__ import annotations

from .base import FeatureHost
from .manager import FeatureManager


class IncidentFeature:
    """Owner-only incident console callbacks, routed after guard authorization."""

    name = "incidents"

    def __init__(self, host: FeatureHost) -> None:
        self.host = host

    def register(self, manager: FeatureManager) -> None:
        manager.add_callback(self.name, "incident:", self._callback)

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None

    def _callback(self, chat_id: int, message_id: int | None, data: str) -> None:
        action = data.split(":", 2)
        if len(action) == 2 and action[1] in {"all", "high", "critical"}:
            self.host.feature_edit_or_reply(chat_id, message_id, *self.host.feature_incident_menu(action[1]))
            return
        if len(action) == 3 and action[1] == "ack":
            self.host.feature_edit_or_reply(chat_id, message_id, *self.host.feature_acknowledge_incident(action[2]))
            return
        if len(action) == 3 and action[1] == "evidence":
            self.host.feature_open_incident_evidence(chat_id, action[2])
            return
        self.host.feature_edit_or_reply(chat_id, message_id, *self.host.feature_incident_menu("all"))
