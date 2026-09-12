from laptop_guard.text_direction import directional_text, paragraph_directions, text_direction
import laptop_guard.chat_window as chat_window


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


def test_chat_composer_has_direction_detector_available():
    assert chat_window.text_direction("سلام") == "rtl"
    assert chat_window.text_direction("Hello") == "ltr"


def test_chat_paragraphs_resolve_rtl_and_ltr_independently():
    assert paragraph_directions("سلام دنیا\nHello world", "auto") == ["rtl", "ltr"]
    assert paragraph_directions("Hello\nسلام", "rtl") == ["rtl", "rtl"]
