"""Build the Linux runtime sidecar bundled by the AngysGuard Tauri client.

This is intentionally a build-time tool. The installed app never downloads or
installs Python packages on a protected device; it executes the audited sidecar
that was built in CI for the matching Linux architecture.
"""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "scripts" / "desktop_runtime_entry.py"
BINARIES = ROOT / "desktop" / "windows-tauri" / "src-tauri" / "binaries"
RUNTIME_NAME = "laptop-guard-runtime"


def main() -> int:
    # Windows builds intentionally retain the empty resource directory because
    # their native agent is a separate planned implementation. Tauri invokes
    # this pre-build hook for every bundle target.
    if platform.system() != "Linux":
        return 0
    if platform.machine() not in {"x86_64", "amd64"}:
        raise SystemExit("The bundled pilot runtime is built only on Linux x86_64.")
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name",
        RUNTIME_NAME,
        "--distpath",
        str(BINARIES),
        "--workpath",
        str(ROOT / ".build" / "pyinstaller-work"),
        "--specpath",
        str(ROOT / ".build" / "pyinstaller-spec"),
        "--paths",
        str(ROOT),
        "--collect-submodules",
        "laptop_guard",
        str(ENTRYPOINT),
    ]
    try:
        subprocess.run(command, check=True, cwd=ROOT)
    except subprocess.CalledProcessError as error:
        raise SystemExit(
            "Could not build the bundled runtime. For a Linux release build, "
            "install the project and PyInstaller in the build Python environment."
        ) from error
    executable = BINARIES / RUNTIME_NAME / RUNTIME_NAME
    if not executable.is_file():
        raise SystemExit("PyInstaller did not produce the expected Linux runtime executable.")
    executable.chmod(executable.stat().st_mode | 0o111)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
