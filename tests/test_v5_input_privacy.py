from laptop_guard.input_monitor import InputMonitor


def test_input_monitor_has_backend_and_no_key_buffer():
    m = InputMonitor(35, lambda _: None, backend="auto")
    assert m.backend_name == "none"
    # Regression guard: activity monitor must not grow a typed-key history.
    assert not hasattr(m, "keys")
    assert not hasattr(m, "key_buffer")
