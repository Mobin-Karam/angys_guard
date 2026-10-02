#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const root = path.resolve(__dirname, "..");
const packages = ["linux-agent", "windows-agent"].map((directory) => {
  const cwd = path.join(root, "packages", directory);
  const manifest = JSON.parse(fs.readFileSync(path.join(cwd, "package.json"), "utf8"));
  return { cwd, manifest };
});

function run(command, args, cwd = root) {
  const result = spawnSync(command, args, { cwd, stdio: "inherit" });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}

function fail(message) {
  console.error(`Release check failed: ${message}`);
  process.exit(1);
}

const [first, ...rest] = packages;
const version = first.manifest.version;
if (!/^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(version)) fail(`invalid semver version: ${version}`);
if (rest.some(({ manifest }) => manifest.version !== version)) fail("Linux and Windows package versions must match.");
if (packages.some(({ manifest }) => manifest.publishConfig?.access !== "public")) fail("both packages must be public scoped packages.");

console.log(`Checking AngysGuard npm packages at version ${version}.`);
for (const { cwd, manifest } of packages) {
  console.log(`\nPacking ${manifest.name}@${version}…`);
  run("npm", ["pack", "--dry-run", "--json"], cwd);
}

if (process.argv.includes("--check")) {
  console.log("\nPackage release check passed. No registry changes were made.");
  process.exit(0);
}

console.log("\nPublishing public packages. npm may open a browser for 2FA approval.");
for (const { cwd, manifest } of packages) {
  console.log(`\nPublishing ${manifest.name}@${version}…`);
  run("npm", ["publish", "--access", "public", "--provenance=false"], cwd);
}

console.log(`\nPublished both AngysGuard npm packages at ${version}.`);
console.log("Verify with: npm view @angysguard/linux-agent version dist-tags --json");
