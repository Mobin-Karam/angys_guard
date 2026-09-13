from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_tracked_secrets.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_tracked_secrets", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_secret_filename_policy() -> None:
    checker = _load_checker()
    blocked = (
        ".env",
        "deploy/.env.production",
        "secrets.json",
        "config/stop-pin.json",
        "credentials.json",
        "keys/id_rsa",
        "keys/id_dsa",
        "keys/id_ecdsa",
        "keys/id_ed25519",
        "keys/device.key",
        "keys/device.pem",
        "keys/device.ppk",
        "keys/device.p12",
        "keys/device.pfx",
        "keys/device.jks",
        ".netrc",
        ".npmrc",
        ".pypirc",
        "private.secret",
    )
    assert all(checker.is_blocked_path(path) for path in blocked)
    assert checker.is_blocked_path(".env.example") is False
    assert checker.is_blocked_path("docs/CONFIGURATION.md") is False


def test_current_git_index_contains_no_blocked_secret_paths() -> None:
    checker = _load_checker()
    assert [path for path in checker.tracked_paths() if checker.is_blocked_path(path)] == []


def test_checker_command_rejects_blocked_tracked_file(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".env.example").write_text("SAFE_EXAMPLE=\n", encoding="utf-8")
    subprocess.run(["git", "add", ".env.example"], cwd=tmp_path, check=True)
    allowed = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)], cwd=tmp_path, capture_output=True, text=True
    )
    assert allowed.returncode == 0

    key_path = tmp_path / "device.p12"
    key_path.write_bytes(b"test fixture, not a credential")
    subprocess.run(["git", "add", "-f", "device.p12"], cwd=tmp_path, check=True)
    blocked = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)], cwd=tmp_path, capture_output=True, text=True
    )
    assert blocked.returncode == 1
    assert "device.p12" in blocked.stdout


def test_workflow_invokes_checker_with_python3() -> None:
    workflow = (ROOT / ".github" / "workflows" / "repository-safety.yml").read_text(
        encoding="utf-8"
    )
    assert "python3 scripts/check_tracked_secrets.py" in workflow
