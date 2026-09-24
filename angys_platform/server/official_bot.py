"""Server-only polling loop for the official Telegram/Bale bot."""

from __future__ import annotations

from typing import Any

from angys_platform.gateway import GatewayDenied, ProviderUpdateAdapter

from .command_server import CommandServer


class OfficialBotService:
    """Consumes provider updates and queues only authorized device commands."""

    def __init__(self, provider_name: str, provider: Any, adapter: ProviderUpdateAdapter, commands: CommandServer) -> None:
        self.provider_name = provider_name
        self.provider = provider
        self.adapter = adapter
        self.commands = commands
        self.offset: int | None = None

    def run_once(self) -> int:
        handled = 0
        for update in self.provider.get_updates(offset=self.offset):
            update_id = update.get("update_id") if isinstance(update, dict) else None
            if isinstance(update_id, int):
                self.offset = update_id + 1
            try:
                routed = self.adapter.receive(self.provider_name, update)
                text = ((update.get("message") or {}).get("text") or "").strip()
                chat_id = ((update.get("message") or {}).get("chat") or {}).get("id")
                if text.startswith("/pair "):
                    reply = "Device paired successfully."
                else:
                    self.commands.queue(routed)
                    reply = "Command queued for the enrolled device."
                if isinstance(chat_id, int):
                    self.provider.send_message(chat_id, reply)
                handled += 1
            except GatewayDenied:
                continue
        for request_id, chat_id, result in self.commands.completed_replies(self.provider_name):
            try:
                self.provider.send_message(int(chat_id), f"Device result: {result} ({request_id})")
            except Exception:
                self.commands.record_reply_failure(self.provider_name, request_id)
                continue
            self.commands.mark_reply_delivered(self.provider_name, request_id)
        return handled
