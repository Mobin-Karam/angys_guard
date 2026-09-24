"""Fixed, owner-authorized Wake-on-LAN dispatch for the always-on gateway."""

from __future__ import annotations

import ipaddress
import re
import socket
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from angys_platform.gateway import RoutedCommand


class WakeDenied(ValueError):
    """Raised when a wake request or enrolled network target is unsafe."""


_MAC = re.compile(r"^[0-9a-fA-F]{2}([:-][0-9a-fA-F]{2}){5}$")


@dataclass(frozen=True)
class WakeTarget:
    device_id: str
    account_id: int
    mac: str
    broadcast: str
    port: int


class WakeOnLanGateway:
    """Dispatch magic packets only to explicit, owner-bound enrolled targets."""

    def __init__(self, database: str | Path, socket_factory=socket.socket) -> None:
        self.database, self.socket_factory = str(database), socket_factory
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS wake_targets (
                device_id TEXT PRIMARY KEY, account_id INTEGER NOT NULL, mac TEXT NOT NULL,
                broadcast TEXT NOT NULL, port INTEGER NOT NULL, enabled INTEGER NOT NULL DEFAULT 1
            )""")

    def _connect(self):
        return sqlite3.connect(self.database)

    @staticmethod
    def _target(device_id: str, account_id: int, mac: str, broadcast: str, port: int) -> WakeTarget:
        if not isinstance(device_id, str) or not device_id or not isinstance(account_id, int):
            raise WakeDenied("invalid enrolled device")
        if not isinstance(mac, str) or not _MAC.fullmatch(mac):
            raise WakeDenied("invalid MAC address")
        try:
            address = ipaddress.IPv4Address(broadcast)
        except ipaddress.AddressValueError as error:
            raise WakeDenied("invalid broadcast address") from error
        if not address.is_multicast and not str(address).endswith(".255"):
            raise WakeDenied("broadcast address must be an explicit IPv4 broadcast")
        if not isinstance(port, int) or not 1 <= port <= 65535:
            raise WakeDenied("invalid Wake-on-LAN port")
        return WakeTarget(device_id, account_id, mac.lower().replace("-", ":"), str(address), port)

    def configure(self, device_id: str, account_id: int, mac: str, broadcast: str, port: int = 9) -> WakeTarget:
        target = self._target(device_id, account_id, mac, broadcast, port)
        with self._connect() as db:
            db.execute("""INSERT INTO wake_targets(device_id,account_id,mac,broadcast,port,enabled)
                VALUES(?,?,?,?,?,1) ON CONFLICT(device_id) DO UPDATE SET
                account_id=excluded.account_id, mac=excluded.mac, broadcast=excluded.broadcast,
                port=excluded.port, enabled=1""", (target.device_id, target.account_id, target.mac, target.broadcast, target.port))
        return target

    def revoke(self, device_id: str, account_id: int) -> None:
        with self._connect() as db:
            cur = db.execute("UPDATE wake_targets SET enabled=0 WHERE device_id=? AND account_id=? AND enabled=1", (device_id, account_id))
        if cur.rowcount != 1:
            raise WakeDenied("wake capability is unavailable")

    def wake(self, routed: RoutedCommand) -> WakeTarget:
        if routed.action != "wake":
            raise WakeDenied("not a wake action")
        with self._connect() as db:
            row = db.execute("SELECT device_id,account_id,mac,broadcast,port FROM wake_targets WHERE device_id=? AND account_id=? AND enabled=1", (routed.device_id, routed.account_id)).fetchone()
        if not row:
            raise WakeDenied("wake capability is unavailable")
        target = WakeTarget(*row)
        packet = bytes.fromhex("ff" * 6 + target.mac.replace(":", "") * 16)
        with self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as transport:
            transport.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            transport.sendto(packet, (target.broadcast, target.port))
        return target
