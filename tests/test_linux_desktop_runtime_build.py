import importlib.util
from pathlib import Path


def _build_script_module():
    path = Path(__file__).parents[1] / "scripts" / "build_linux_desktop_runtime.py"
    spec = importlib.util.spec_from_file_location("build_linux_desktop_runtime", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_windows_packaging_prebuild_is_a_safe_noop(monkeypatch):
    module = _build_script_module()
    monkeypatch.setattr(module.platform, "system", lambda: "Windows")

    assert module.main() == 0
