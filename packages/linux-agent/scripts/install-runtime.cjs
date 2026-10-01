"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

if (process.platform !== "linux") {
  console.error("@angysguard/linux-agent can only be installed on Linux.");
  process.exit(1);
}

if (process.env.ANGYSGUARD_SKIP_RUNTIME_INSTALL === "1") {
  console.log("Skipping AngysGuard Python runtime installation by explicit request.");
  process.exit(0);
}

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { stdio: "inherit", ...options });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} exited with ${result.status}.`);
  }
}

function findPython() {
  for (const candidate of ["python3", "python"]) {
    const result = spawnSync(candidate, ["-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"], {
      encoding: "utf8",
    });
    if (result.error || result.status !== 0) continue;
    const [major, minor] = result.stdout.trim().split(".").map(Number);
    if (major > 3 || (major === 3 && minor >= 11)) return candidate;
  }
  throw new Error("Python 3.11+ with venv support is required. Install it, then rerun npm rebuild @angysguard/linux-agent.");
}

try {
  const packageRoot = path.resolve(__dirname, "..");
  const source = path.join(packageRoot, "runtime-src");
  const runtimeRoot = path.join(packageRoot, "runtime");
  const target = path.join(runtimeRoot, ".venv");
  if (!fs.existsSync(source)) throw new Error("Bundled runtime source is missing; reinstall the npm package.");

  const python = findPython();
  fs.mkdirSync(runtimeRoot, { recursive: true });
  fs.rmSync(target, { recursive: true, force: true });
  run(python, ["-m", "venv", target]);
  const venvPython = path.join(target, "bin", "python");
  run(venvPython, ["-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "pip"]);
  run(venvPython, ["-m", "pip", "install", "--disable-pip-version-check", source]);
  run(venvPython, ["-m", "pip", "check"]);
  console.log("AngysGuard Linux runtime installed successfully.");
} catch (error) {
  console.error(`AngysGuard Linux runtime setup failed: ${error.message}`);
  console.error("Install Python 3.11+ with venv support and network access, then run: npm rebuild @angysguard/linux-agent");
  process.exitCode = 1;
}
