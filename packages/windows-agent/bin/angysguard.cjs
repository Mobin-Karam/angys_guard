#!/usr/bin/env node
"use strict";

const { execFileSync } = require("node:child_process");

const command = process.argv[2] || "help";
const copy = {
  fa: {
    title: "AngysGuard Windows Agent — آزمایشی",
    unsupported: "این agent هنوز Windows support تأییدشده نیست. دوربین و input monitor در این CLI فعال نیستند.",
    status: "وضعیت محلی: CLI آماده است؛ سرویس حفاظت Windows هنوز پیاده‌سازی/اعتبارسنجی نشده است.",
    lock: "درخواست قفل Windows ارسال شد.",
  },
  en: {
    title: "AngysGuard Windows Agent — experimental",
    unsupported: "This agent is not validated Windows support yet. Camera and input monitoring are unavailable in this CLI.",
    status: "Local status: CLI is ready; the Windows protection service is not implemented/validated yet.",
    lock: "Windows lock request sent.",
  },
};
const lang = process.env.ANGYSGUARD_LANG === "en" ? "en" : "fa";
const text = copy[lang];
function help() {
  console.log(`${text.title}\n\n${text.unsupported}\n\nCommands:\n  angysguard status\n  angysguard lock\n  angysguard doctor\n  angysguard help`);
}
if (process.platform !== "win32") {
  console.error("AngysGuard Windows Agent can only run on Windows.");
  process.exitCode = 2;
} else if (command === "help" || command === "--help" || command === "-h") {
  help();
} else if (command === "status" || command === "doctor") {
  console.log(`${text.title}\n${text.status}\n${text.unsupported}`);
} else if (command === "lock") {
  try {
    execFileSync("rundll32.exe", ["user32.dll,LockWorkStation"], { stdio: "ignore", timeout: 5000 });
    console.log(text.lock);
  } catch {
    console.error("Windows refused the fixed lock request.");
    process.exitCode = 2;
  }
} else {
  console.error(`Unknown command: ${command}`);
  help();
  process.exitCode = 2;
}
