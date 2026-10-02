#!/usr/bin/env node
"use strict";

const path = require("node:path");
const fs = require("node:fs");
const { spawn, spawnSync } = require("node:child_process");

function desktopExecutable() {
  for (const candidate of ["/usr/bin/angysguard-desktop", "/usr/local/bin/angysguard-desktop"]) {
    if (fs.existsSync(candidate)) return candidate;
  }
  const found = spawnSync("which", ["angysguard-desktop"], { encoding: "utf8" });
  return found.status === 0 ? found.stdout.trim() : null;
}

function openDesktop() {
  const executable = desktopExecutable();
  if (!executable) {
    console.error("The optional AngysGuard desktop dashboard is not installed.");
    console.error("Continue in the terminal, or install the Linux .deb dashboard release.");
    process.exitCode = 2;
    return;
  }
  const child = spawn(executable, [], { detached: true, stdio: "ignore" });
  child.once("error", () => {
    console.error("Could not start the AngysGuard desktop dashboard.");
    process.exitCode = 2;
  });
  child.unref();
}

function chooseInterface() {
  const dashboard = desktopExecutable();
  if (!dashboard || !process.stdin.isTTY || !process.stdout.isTTY) return false;

  process.stdout.write("\nAngysGuard\n1. Open dashboard\n2. Continue in terminal\nChoose [1]: ");
  const answer = fs.readFileSync(0, "utf8").trim();
  if (!answer || answer === "1") {
    openDesktop();
    return true;
  }
  return false;
}

if (process.platform !== "linux") {
  console.error("AngysGuard Linux Agent can only run on Linux.");
  process.exitCode = 2;
} else {
  const packageRoot = path.resolve(path.dirname(fs.realpathSync(__filename)), "..");
  const executable = path.join(packageRoot, "runtime", ".venv", "bin", "laptop-guard");
  const args = process.argv.slice(2);
  if (args[0] === "app" || args[0] === "dashboard") {
    openDesktop();
  } else {
    const runtimeArgs = args[0] === "terminal" ? args.slice(1) : args;
    if (!runtimeArgs.length && chooseInterface()) process.exit(0);
    const result = spawnSync(executable, runtimeArgs, { stdio: "inherit" });
  if (result.error && result.error.code === "ENOENT") {
    console.error("AngysGuard's bundled Python runtime is missing.");
    console.error("Repair this package with: npm rebuild @angysguard/linux-agent");
    process.exitCode = 2;
  } else {
    process.exitCode = result.status ?? 1;
  }
  }
}
