from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_root_runflare_requirements_exclude_protected_device_dependencies() -> None:
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for dependency in ("fastapi", "uvicorn", "httpx", "email-validator"):
        assert dependency in requirements
    for dependency in ("opencv", "evdev", "pynput", "pyudev", "py-persian-tts"):
        assert dependency not in requirements


def test_local_runtime_requirements_keep_protected_device_dependencies() -> None:
    requirements = (ROOT / "requirements.local.txt").read_text(encoding="utf-8")
    for dependency in ("opencv", "evdev", "pynput", "pyudev", "py-persian-tts"):
        assert dependency in requirements
