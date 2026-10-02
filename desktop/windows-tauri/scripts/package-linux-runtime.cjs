#!/usr/bin/env node
"use strict";

const { existsSync } = require("node:fs");
const { resolve } = require("node:path");
const { spawnSync } = require("node:child_process");

// The bundled Python sidecar is Linux-only. Windows packages must not require
// Python or PyInstaller while building their native managed-test client.
if (process.platform !== "linux") {
  process.exit(0);
}

const desktopRoot = resolve(__dirname, "..");
const repositoryRoot = resolve(desktopRoot, "..", "..");
const runtimeBuilder = resolve(repositoryRoot, "scripts", "build_linux_desktop_runtime.py");
const configuredPython = process.env.ANGYSGUARD_BUILD_PYTHON;
const projectPython = resolve(repositoryRoot, ".venv", "bin", "python");
const python = configuredPython || (existsSync(projectPython) ? projectPython : "python3");

function run(args, options = {}) {
  const result = spawnSync(python, args, {
    cwd: repositoryRoot,
    stdio: options.stdio || "inherit",
  });

  if (result.error) {
    console.error(`Could not start Python (${python}): ${result.error.message}`);
    process.exit(1);
  }
  if (result.status !== 0) {
    process.exit(result.status || 1);
  }
}

// Build tooling stays in the local build environment. The installed desktop
// app receives the completed sidecar and never installs Python packages.
const pyInstallerCheck = spawnSync(python, ["-c", "import PyInstaller"], {
  cwd: repositoryRoot,
  stdio: "ignore",
});

if (pyInstallerCheck.error) {
  console.error(`Could not start Python (${python}): ${pyInstallerCheck.error.message}`);
  process.exit(1);
}

if (pyInstallerCheck.status !== 0) {
  console.log("Preparing the Linux desktop build environment (PyInstaller)…");
  run([
    "-m",
    "pip",
    "install",
    "--disable-pip-version-check",
    "-e",
    repositoryRoot,
    "pyinstaller>=6,<7",
  ]);
}

run([runtimeBuilder]);
