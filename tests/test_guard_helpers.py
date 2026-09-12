from laptop_guard.guard import bounded_callback_int


def test_callback_integer_is_bounded():
    assert bounded_callback_int("camera:video:999", 8, 1, 60) == 60
    assert bounded_callback_int("camera:video:-2", 8, 1, 60) == 1


def test_malformed_callback_integer_uses_default():
    assert bounded_callback_int("camera:video:not-a-number", 8, 1, 60) == 8
    assert bounded_callback_int("missing", 8, 1, 60) == 8
