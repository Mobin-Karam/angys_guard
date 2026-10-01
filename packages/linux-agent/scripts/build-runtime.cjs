"use strict";

const fs = require("node:fs");
const path = require("node:path");

const packageRoot = path.resolve(__dirname, "..");
const repositoryRoot = path.resolve(packageRoot, "..", "..");
const runtimeSource = path.join(packageRoot, "runtime-src");

function copyRequired(source, destination) {
  if (!fs.existsSync(source)) {
    throw new Error(`Required runtime source is missing: ${source}`);
  }
  fs.cpSync(source, destination, {
    recursive: true,
    filter: (candidate) =>
      !candidate.includes("__pycache__") &&
      !candidate.endsWith(".pyc") &&
      path.basename(candidate) !== "AGENTS.md",
  });
}

fs.rmSync(runtimeSource, { recursive: true, force: true });
fs.mkdirSync(runtimeSource, { recursive: true });
copyRequired(path.join(repositoryRoot, "pyproject.toml"), path.join(runtimeSource, "pyproject.toml"));
copyRequired(path.join(repositoryRoot, "README.md"), path.join(runtimeSource, "README.md"));
copyRequired(path.join(repositoryRoot, "laptop_guard"), path.join(runtimeSource, "laptop_guard"));

console.log("Prepared bundled AngysGuard Python runtime source.");
