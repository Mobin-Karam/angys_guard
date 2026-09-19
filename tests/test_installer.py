from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.sh"


def _write_executable(path: Path, body: str) -> None:
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8")
    path.chmod(0o755)


def _prepare_install_tree(tmp_path: Path) -> tuple[Path, Path, dict[str, str]]:
    work = tmp_path / "repo"
    fake_bin = tmp_path / "bin"
    work.mkdir()
    fake_bin.mkdir()
    (work / "install.sh").write_text(INSTALLER.read_text(encoding="utf-8"), encoding="utf-8")
    (work / "requirements.txt").write_text("requests>=2.32,<3\n", encoding="utf-8")
    os_release = tmp_path / "os-release"
    os_release.write_text('ID=ubuntu\nPRETTY_NAME="Ubuntu Test"\nVERSION_CODENAME=noble\n', encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:/usr/bin:/bin"
    env["ANGYSGUARD_OS_RELEASE_FILE"] = str(os_release)
    return work, fake_bin, env


def _run(work: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "install.sh"],
        cwd=work,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=10,
    )


def _write_working_venv_python(path: Path, version: str = "3.12") -> None:
    _write_executable(
        path,
        f"""
if [[ "$1" == "-c" && "$2" == *'sys.version_info[0]'* ]]; then echo {version}; exit 0; fi
if [[ "$1" == "-m" && "$2" == "pip" ]]; then exit 0; fi
exit 99
""",
    )


def test_fresh_supported_install_ends_with_setup_and_doctor(tmp_path: Path) -> None:
    work, fake_bin, env = _prepare_install_tree(tmp_path)
    _write_executable(
        fake_bin / "python3",
        """
if [[ "$1" == "-c" && "$2" == *'sys.version_info[:3]'* ]]; then echo 3.12.4; exit 0; fi
if [[ "$1" == "-c" && "$2" == *'ensurepip, venv'* ]]; then exit 0; fi
if [[ "$1" == "-m" && "$2" == "venv" ]]; then
  mkdir -p "$3/bin"
  cat > "$3/bin/python" <<'PYEOF'
#!/usr/bin/env bash
if [[ "$1" == "-c" && "$2" == *'sys.version_info[0]'* ]]; then echo 3.12; exit 0; fi
if [[ "$1" == "-m" && "$2" == "pip" ]]; then exit 0; fi
exit 99
PYEOF
  chmod +x "$3/bin/python"
  exit 0
fi
exit 99
""",
    )
    _write_executable(fake_bin / "dpkg-query", "echo 'install ok installed'\n")

    result = _run(work, env)

    assert result.returncode == 0
    assert (work / ".venv" / "bin" / "python").exists()
    assert "Installation summary: PASS" in result.stdout
    assert "Next command:\n  ./run.sh setup" in result.stdout
    assert "Then verify with:\n  ./run.sh doctor" in result.stdout


def test_missing_venv_reports_exact_ubuntu_package_and_mirror_help(tmp_path: Path) -> None:
    work, fake_bin, env = _prepare_install_tree(tmp_path)
    _write_executable(
        fake_bin / "python3",
        """
if [[ "$1" == "-c" && "$2" == *'sys.version_info[:3]'* ]]; then echo 3.12.4; exit 0; fi
if [[ "$1" == "-c" && "$2" == *'ensurepip, venv'* ]]; then exit 1; fi
exit 99
""",
    )
    _write_executable(fake_bin / "apt-cache", "exit 1\n")
    _write_executable(
        fake_bin / "apt-get",
        "echo 'W: Failed to fetch http://bad.example/ubuntu/dists/noble/InRelease  404 Not Found'\nexit 0\n",
    )
    _write_executable(fake_bin / "timeout", 'shift\nexec "$@"\n')
    _write_executable(fake_bin / "dpkg-query", "exit 1\n")

    result = _run(work, env)

    assert result.returncode == 1
    assert "sudo apt install python3.12-venv" in result.stdout
    assert "mirror/release metadata looks broken or obsolete" in result.stdout
    assert "Installation summary: FAILED" in result.stdout
    assert "Traceback" not in result.stdout
    assert "Next command:" not in result.stdout


def test_installer_is_safe_to_run_twice_with_existing_matching_venv(tmp_path: Path) -> None:
    work, fake_bin, env = _prepare_install_tree(tmp_path)
    venv_bin = work / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    venv_called = tmp_path / "venv-called"
    _write_executable(
        fake_bin / "python3",
        f"""
if [[ "$1" == "-c" && "$2" == *'sys.version_info[:3]'* ]]; then echo 3.12.4; exit 0; fi
if [[ "$1" == "-c" && "$2" == *'ensurepip, venv'* ]]; then exit 0; fi
if [[ "$1" == "-m" && "$2" == "venv" ]]; then echo called >> {venv_called!s}; exit 99; fi
exit 99
""",
    )
    _write_working_venv_python(venv_bin / "python")
    _write_executable(fake_bin / "dpkg-query", "echo 'install ok installed'\n")

    first = _run(work, env)
    second = _run(work, env)

    assert first.returncode == 0
    assert second.returncode == 0
    assert "Reusing existing .venv" in first.stdout
    assert "Installation summary: PASS" in second.stdout
    assert not venv_called.exists()


def test_pip_failure_preserves_fresh_venv_and_hides_success_instructions(tmp_path: Path) -> None:
    work, fake_bin, env = _prepare_install_tree(tmp_path)
    _write_executable(
        fake_bin / "python3",
        """
if [[ "$1" == "-c" && "$2" == *'sys.version_info[:3]'* ]]; then echo 3.12.4; exit 0; fi
if [[ "$1" == "-c" && "$2" == *'ensurepip, venv'* ]]; then exit 0; fi
if [[ "$1" == "-m" && "$2" == "venv" ]]; then
  mkdir -p "$3/bin"
  cat > "$3/bin/python" <<'PYEOF'
#!/usr/bin/env bash
if [[ "$1" == "-c" && "$2" == *'sys.version_info[0]'* ]]; then echo 3.12; exit 0; fi
if [[ "$1" == "-m" && "$2" == "pip" && "$3" == "--version" ]]; then exit 0; fi
if [[ "$1" == "-m" && "$2" == "pip" && "$3" == "install" && "$4" == "--upgrade" ]]; then exit 0; fi
if [[ "$1" == "-m" && "$2" == "pip" && "$3" == "install" && "$4" == "-r" ]]; then
  echo 'ERROR: Could not find a version that satisfies the requirement requests>=2.32'
  exit 1
fi
exit 99
PYEOF
  chmod +x "$3/bin/python"
  exit 0
fi
exit 99
""",
    )
    _write_executable(fake_bin / "dpkg-query", "echo 'install ok installed'\n")

    result = _run(work, env)

    assert result.returncode == 1
    assert (work / ".venv" / "bin" / "python").exists()
    assert "virtual environment is recoverable" in result.stdout
    assert "Installation summary: FAILED" in result.stdout
    assert "Installation summary: PASS" not in result.stdout
    assert "Next command:" not in result.stdout


def test_failed_replacement_restores_previous_venv(tmp_path: Path) -> None:
    work, fake_bin, env = _prepare_install_tree(tmp_path)
    old_python = work / ".venv" / "bin" / "python"
    old_python.parent.mkdir(parents=True)
    _write_executable(
        old_python,
        """
if [[ "$1" == "-c" && "$2" == *'sys.version_info[0]'* ]]; then echo 3.11; exit 0; fi
if [[ "$1" == "-m" && "$2" == "pip" ]]; then exit 0; fi
exit 99
""",
    )
    marker = work / ".venv" / "old-environment"
    marker.write_text("keep me", encoding="utf-8")

    _write_executable(
        fake_bin / "python3",
        """
if [[ "$1" == "-c" && "$2" == *'sys.version_info[:3]'* ]]; then echo 3.12.4; exit 0; fi
if [[ "$1" == "-c" && "$2" == *'ensurepip, venv'* ]]; then exit 0; fi
if [[ "$1" == "-m" && "$2" == "venv" ]]; then
  mkdir -p "$3/bin"
  cat > "$3/bin/python" <<'PYEOF'
#!/usr/bin/env bash
if [[ "$1" == "-c" && "$2" == *'sys.version_info[0]'* ]]; then echo 3.12; exit 0; fi
if [[ "$1" == "-m" && "$2" == "pip" && "$3" == "--version" ]]; then exit 0; fi
if [[ "$1" == "-m" && "$2" == "pip" && "$3" == "install" && "$4" == "--upgrade" ]]; then exit 0; fi
if [[ "$1" == "-m" && "$2" == "pip" && "$3" == "install" && "$4" == "-r" ]]; then exit 1; fi
exit 99
PYEOF
  chmod +x "$3/bin/python"
  exit 0
fi
exit 99
""",
    )
    _write_executable(fake_bin / "dpkg-query", "echo 'install ok installed'\n")

    result = _run(work, env)

    assert result.returncode == 1
    assert marker.read_text(encoding="utf-8") == "keep me"
    assert "Restoring the previous .venv" in result.stdout
    assert "Next command:" not in result.stdout
