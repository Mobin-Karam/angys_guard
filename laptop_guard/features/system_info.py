from __future__ import annotations

from .base import FeatureHost
from .manager import FeatureManager


class SystemInfoFeature:
    name = "system-info"

    def __init__(self, host: FeatureHost) -> None:
        self.host = host

    def register(self, manager: FeatureManager) -> None:
        manager.add_command(self.name, ("/status",), self._status)
        manager.add_command(self.name, ("/sysinfo", "/device"), self._system_info)
        manager.add_command(self.name, ("/help",), self._help)

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None

    def _status(self, chat_id: int, _argument: str) -> None:
        self.host.feature_reply(chat_id, self.host.feature_status(), self.host.feature_main_menu())

    def _system_info(self, chat_id: int, _argument: str) -> None:
        self.host.feature_reply(chat_id, self.host.feature_system_info(), self.host.feature_main_menu())

    def _help(self, chat_id: int, _argument: str) -> None:
        self.host.feature_reply(chat_id, self.host.feature_help())
