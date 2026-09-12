from laptop_guard.screen_capture import ScreenCaptureManager


def test_parse_gnome_dbus_path():
    out = "(true, '/home/test/Videos/screen.webm')\n"
    assert ScreenCaptureManager._parse_gdbus_path(out) == "/home/test/Videos/screen.webm"


def test_parse_gnome_dbus_failure_is_empty():
    assert ScreenCaptureManager._parse_gdbus_path("(false, '')") == ""
