from laptop_guard.control_api import LocalControlAPI


def test_local_api_constructs_without_shell_surface():
    api = LocalControlAPI(
        "127.0.0.1", 0, "secret",
        lambda: {"ok": True},
        lambda text: None,
        lambda text: None,
        lambda text, seconds: None,
        lambda path: None,
    )
    assert api.host == "127.0.0.1"
    assert api.token == "secret"
    assert not hasattr(api, "shell")
