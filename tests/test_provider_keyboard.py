from laptop_guard.providers.http_bot import HttpBotProvider


def test_keyboard_encoding():
    # Avoid network calls; only exercise deterministic reply-markup generation.
    provider = object.__new__(HttpBotProvider)
    encoded = provider._keyboard([[("Allow", "allow:5")]])
    assert 'allow:5' in encoded
    assert 'inline_keyboard' in encoded
