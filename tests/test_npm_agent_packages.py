"""Offline contract checks for the publishable npm terminal package sources."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("package_dir", "package_name", "platform"),
    [
        ("linux-agent", "@angysguard/linux-agent", "linux"),
        ("windows-agent", "@angysguard/windows-agent", "win32"),
    ],
)
def test_npm_agent_package_has_an_explicit_platform_and_cli(
    package_dir: str, package_name: str, platform: str
) -> None:
    manifest = json.loads((ROOT / "packages" / package_dir / "package.json").read_text())

    assert manifest["name"] == package_name
    assert manifest["version"] == "1.0.1"
    assert manifest["bin"] == {"angysguard": "bin/angysguard.cjs"}
    assert manifest["os"] == [platform]
    assert manifest["engines"]["node"] == ">=20"
    assert manifest["repository"] == "github:Mobin-Karam/angys_guard"
    assert manifest["publishConfig"] == {"access": "public", "provenance": True}


def test_linux_npm_agent_packages_its_runtime_installer() -> None:
    manifest = json.loads((ROOT / "packages" / "linux-agent" / "package.json").read_text())
    installer = (ROOT / "packages" / "linux-agent" / "scripts" / "install-runtime.cjs").read_text()
    readme = (ROOT / "packages" / "linux-agent" / "README.md").read_text()

    assert manifest["scripts"]["postinstall"] == "node scripts/install-runtime.cjs"
    assert "README.md" in manifest["files"]
    assert "npm install -g @angysguard/linux-agent" in readme
    assert "python3" in installer
    assert '"-m", "venv"' in installer
    assert '"-m", "pip", "check"' in installer
    assert ".venv.tmp-" not in installer
    assert "shell:" not in installer


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is required to parse npm launchers")
@pytest.mark.parametrize("package_dir", ["linux-agent", "windows-agent"])
def test_npm_agent_launcher_has_valid_node_syntax(package_dir: str) -> None:
    launcher = ROOT / "packages" / package_dir / "bin" / "angysguard.cjs"
    result = subprocess.run(["node", "--check", str(launcher)], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


def test_npm_agent_launchers_keep_a_narrow_local_command_boundary() -> None:
    linux = (ROOT / "packages" / "linux-agent" / "bin" / "angysguard.cjs").read_text()
    windows = (ROOT / "packages" / "windows-agent" / "bin" / "angysguard.cjs").read_text()

    assert all(fragment in linux for fragment in ("realpathSync", "runtime", ".venv", "bin", "laptop-guard"))
    assert "spawnSync(executable, runtimeArgs" in linux
    assert "angysguard-desktop" in linux
    assert "shell:" not in linux
    assert 'execFileSync("rundll32.exe", ["user32.dll,LockWorkStation"]' in windows
    assert "powershell" not in windows.lower()


def test_root_npm_release_scripts_keep_package_versions_in_lockstep() -> None:
    root_manifest = json.loads((ROOT / "package.json").read_text())
    release_script = (ROOT / "scripts" / "publish-npm-packages.cjs").read_text()

    assert root_manifest["private"] is True
    assert root_manifest["scripts"]["release:npm:check"] == "node scripts/publish-npm-packages.cjs --check"
    assert root_manifest["scripts"]["release:npm:publish"] == "node scripts/publish-npm-packages.cjs"
    assert '"linux-agent", "windows-agent"' in release_script
    assert "Linux and Windows package versions must match" in release_script
    assert '"--provenance=false"' in release_script
    assert "shell:" not in release_script
