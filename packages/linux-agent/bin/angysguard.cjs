#!/usr/bin/env node
"use strict";

const path = require("node:path");
const fs = require("node:fs");
const { spawnSync } = require("node:child_process");

if (process.platform !== "linux") {
  console.error("AngysGuard Linux Agent can only run on Linux.");
  process.exitCode = 2;
} else {
  const packageRoot = path.resolve(path.dirname(fs.realpathSync(__filename)), "..");
  const executable = path.join(packageRoot, "runtime", ".venv", "bin", "laptop-guard");
  const result = spawnSync(executable, process.argv.slice(2), { stdio: "inherit" });
  if (result.error && result.error.code === "ENOENT") {
    console.error("AngysGuard's bundled Python runtime is missing.");
    console.error("Repair this package with: npm rebuild @angysguard/linux-agent");
    process.exitCode = 2;
  } else {
    process.exitCode = result.status ?? 1;
  }
}
