"""Regression coverage for providers that deploy the repository root."""


def test_root_main_exports_the_managed_asgi_application() -> None:
    from main import app

    assert app.title == "AngysGuard managed test service"
