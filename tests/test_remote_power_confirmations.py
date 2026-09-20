from __future__ import annotations

from types import SimpleNamespace

from laptop_guard.guard import LaptopGuard, POWER_CONFIRMATION_TTL_SECONDS
from laptop_guard.models import AppConfig, BotConfig, SecurityConfig


class FakeApi:
    def __init__(self) -> None:
        self.messages: list[tuple[int, str, dict | None]] = []

    def send_message(self, chat_id: int, text: str, reply_markup: dict | None = None) -> None:
        self.messages.append((chat_id, text, reply_markup))

    def answer_callback(self, _query_id: str) -> None:
        pass

    def edit_message_text(self, chat_id: int, _message_id: int, text: str, reply_markup: dict | None = None) -> None:
        self.messages.append((chat_id, text, reply_markup))


def make_guard(*, power_enabled: bool) -> tuple[LaptopGuard, FakeApi]:
    guard = object.__new__(LaptopGuard)
    guard.config = AppConfig(
        bot=BotConfig(provider="local", chat_id=77),
        security=SecurityConfig(allow_remote_power=power_enabled),
    )
    guard.api = api = FakeApi()
    guard.features = SimpleNamespace(dispatch_command=lambda *_args: False, dispatch_callback=lambda *_args: False)
    guard.events = SimpleNamespace(add=lambda *_args: None)
    guard._pending_power_confirmation = None
    return guard, api


def callback(data: str) -> dict:
    return {"id": "callback-id", "data": data, "message": {"chat": {"id": 77}, "message_id": 1}}


def confirmation_token(api: FakeApi) -> str:
    markup = api.messages[-1][2]
    assert markup is not None
    value = markup["inline_keyboard"][0][0]["callback_data"]
    return value.rsplit(":", 1)[1]


def test_disabled_power_command_does_not_offer_executable_confirmation() -> None:
    guard, api = make_guard(power_enabled=False)

    guard._handle_text(77, {"text": "/shutdown"})

    assert "غیرفعال" in api.messages[-1][1]
    assert api.messages[-1][2]["inline_keyboard"] == [[{"text": "⬅️ منوی اصلی", "callback_data": "menu:main"}]]
    assert guard._pending_power_confirmation is None


def test_power_confirmation_is_action_bound_single_use_and_runs_requested_action(monkeypatch) -> None:
    guard, api = make_guard(power_enabled=True)
    calls: list[str] = []
    monkeypatch.setattr("laptop_guard.guard.reboot_system", lambda: calls.append("reboot") or True)

    guard._handle_text(77, {"text": "/restart"})
    token = confirmation_token(api)
    guard._handle_callback(callback(f"power:off:yes:{token}"))
    assert calls == []

    guard._handle_text(77, {"text": "/restart"})
    token = confirmation_token(api)
    guard._handle_callback(callback(f"power:reboot:yes:{token}"))
    guard._handle_callback(callback(f"power:reboot:yes:{token}"))

    assert calls == ["reboot"]
    assert guard._pending_power_confirmation is None


def test_expired_power_confirmation_is_rejected(monkeypatch) -> None:
    guard, api = make_guard(power_enabled=True)
    calls: list[str] = []
    monkeypatch.setattr("laptop_guard.guard.suspend_system", lambda: calls.append("suspend") or True)
    guard._handle_text(77, {"text": "/suspend"})
    token = confirmation_token(api)
    action, pending_token, expires_at = guard._pending_power_confirmation
    guard._pending_power_confirmation = (action, pending_token, expires_at - POWER_CONFIRMATION_TTL_SECONDS - 1)

    guard._handle_callback(callback(f"power:suspend:yes:{token}"))

    assert calls == []
    assert "منقضی" in api.messages[-1][1]
