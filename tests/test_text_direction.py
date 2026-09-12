from laptop_guard.text_direction import directional_text, text_direction


def test_persian_is_rtl():
    assert text_direction("سلام، حالت چطوره؟") == "rtl"


def test_english_is_ltr():
    assert text_direction("Hello, are you there?") == "ltr"


def test_first_strong_character_controls_mixed_text():
    assert text_direction("Laptop Guard — هشدار") == "ltr"
    assert text_direction("هشدار Laptop Guard") == "rtl"


def test_neutral_text_uses_fallback():
    assert text_direction("123 ⚠️", "rtl") == "rtl"
    assert text_direction("123 ⚠️", "ltr") == "ltr"


def test_directional_text_preserves_content():
    value, direction = directional_text("Hello", "auto")
    assert direction == "ltr"
    assert value.endswith("Hello")
