from laptop_guard.models import AppConfig


def test_chat_defaults_to_two_minutes_and_allows_visitor_reply():
    cfg = AppConfig()

    assert cfg.communication.chat_seconds == 120
    assert cfg.chat.seconds == 120
    assert cfg.chat.allow_reply is True
    assert cfg.chat.direction == "auto"
