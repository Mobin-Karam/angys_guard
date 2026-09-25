import { invoke } from "@tauri-apps/api/core";
import { enable as enableAutostart } from "@tauri-apps/plugin-autostart";
import "./styles.css";

type Locale = "fa" | "en";
type Session = { access_token: string; account_id: string };
type PairCode = { pairing_code: string; expires_at: number };
const app = document.querySelector<HTMLDivElement>("#app")!;
let session: Session | null = null;
let locale: Locale = localStorage.getItem("locale") === "en" ? "en" : "fa";

const copy = {
  fa: {
    title: "انجیس‌گارد برای دسکتاپ", intro: "این دستگاه را به‌صورت امن ثبت کنید. رمز ویندوز یا لینوکس شما هرگز درخواست نمی‌شود.", language: "English", server: "نشانی سرور", email: "ایمیل", password: "رمز حساب (حداقل ۱۲ نویسه)", register: "ساخت حساب", login: "ورود", enrollTitle: "ثبت این دستگاه", enrollIntro: "برای این دستگاه نامی انتخاب کنید. اعتبار دستگاه فقط به‌صورت محلی و امن نگه‌داری می‌شود.", deviceName: "نام دستگاه", autostart: "اجرای خودکار انجیس‌گارد پس از ورود به سیستم", pair: "ثبت امن دستگاه", lock: "اجازه قفل‌کردن این نشست توسط دستور /lock ربات", botIntro: "برای پیوند گفت‌وگوی Bale یا Telegram، کد زیر را با دستور /link CODE به ربات ارسال کنید.", bot: "ساخت کد پیوند ربات", enrolled: "دستگاه ثبت شد. در لینوکس، فرمان‌های مجاز status، arm و disarm به لپ‌تاپ‌گارد محلی ارسال می‌شوند؛ برنامه را باز نگه دارید.", autostartSaved: "اجرای خودکار فعال شد.", lockSaved: "تنظیم قفل از راه دور فقط روی همین دستگاه ذخیره شد.", pairCode: "کد ثبت:", botCode: "کد پیوند ربات:", https: "برای سرور آزمایشی از HTTPS استفاده کنید.", error: "عملیات ناموفق بود.", divider: "پیوند ربات",
  },
  en: {
    title: "AngysGuard Desktop", intro: "Enroll this device securely. Your Windows or Linux password is never requested.", language: "فارسی", server: "Server URL", email: "Email", password: "Account password (12+ characters)", register: "Create account", login: "Sign in", enrollTitle: "Enroll this device", enrollIntro: "Choose a name for this device. Its credential stays in secure local storage.", deviceName: "Device name", autostart: "Start AngysGuard automatically after I sign in", pair: "Enroll this device", lock: "Allow this device to lock its session for a bot /lock command", botIntro: "To link a Bale or Telegram chat, send the generated code to your bot as /link CODE.", bot: "Create bot link code", enrolled: "Device enrolled. On Linux, allowed status, arm, and disarm actions are sent to the local Laptop Guard runtime. Keep AngysGuard running.", autostartSaved: "Autostart enabled.", lockSaved: "Remote-lock preference is saved only on this device.", pairCode: "Enrollment code:", botCode: "Bot link code:", https: "Use HTTPS for the test server.", error: "Operation failed.", divider: "Bot link",
  },
} as const;

function t(key: keyof typeof copy.fa) { return copy[locale][key]; }
function escape(value: string) { return value.replace(/[&<>"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[character]!); }
function applyLocale() { document.documentElement.lang = locale === "fa" ? "fa" : "en"; document.documentElement.dir = locale === "fa" ? "rtl" : "ltr"; localStorage.setItem("locale", locale); }
function message(text: string, problem = false) { const target = document.querySelector("#message"); if (target) { target.textContent = text; target.className = problem ? "error" : "success"; } }
function switchLocale() { locale = locale === "fa" ? "en" : "fa"; applyLocale(); session ? enrollmentScreen() : loginScreen(); }
async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const base = (document.querySelector<HTMLInputElement>("#server")?.value || localStorage.getItem("server") || "https://api.mahakaram.ir").replace(/\/$/, "");
  if (!base.startsWith("https://") && !base.startsWith("http://localhost")) throw new Error(t("https"));
  localStorage.setItem("server", base);
  const response = await fetch(`${base}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(session ? { Authorization: `Bearer ${session.access_token}` } : {}), ...(init.headers || {}) } });
  if (!response.ok) throw new Error((await response.json().catch(() => ({ detail: response.statusText }))).detail || t("error"));
  return response.status === 204 ? undefined as T : response.json();
}
function languageButton() { return `<button id="language" class="secondary language" type="button" aria-label="${t("language")}">${t("language")}</button>`; }
function loginScreen() {
  applyLocale();
  app.innerHTML = `<section><header><h1>${t("title")}</h1>${languageButton()}</header><p>${t("intro")}</p><label>${t("server")}<input id="server" value="${escape(localStorage.getItem("server") || "https://api.mahakaram.ir")}" autocomplete="url"></label><label>${t("email")}<input id="email" type="email" autocomplete="email"></label><label>${t("password")}<input id="password" type="password" minlength="12" autocomplete="new-password"></label><div class="row"><button id="register">${t("register")}</button><button id="login" class="secondary">${t("login")}</button></div><p id="message" role="status"></p></section>`;
  const authenticate = async (path: string) => { try { session = await api<Session>(path, { method: "POST", body: JSON.stringify({ email: document.querySelector<HTMLInputElement>("#email")!.value, password: document.querySelector<HTMLInputElement>("#password")!.value }) }); enrollmentScreen(); } catch (error) { message(error instanceof Error ? error.message : t("error"), true); } };
  document.querySelector("#language")!.addEventListener("click", switchLocale);
  document.querySelector("#register")!.addEventListener("click", () => authenticate("/v1/accounts"));
  document.querySelector("#login")!.addEventListener("click", () => authenticate("/v1/sessions"));
}
function enrollmentScreen() {
  applyLocale();
  app.innerHTML = `<section><header><h1>${t("enrollTitle")}</h1>${languageButton()}</header><p>${t("enrollIntro")}</p><label>${t("deviceName")}<input id="device-name" value="${escape(navigator.userAgent.includes("Windows") ? "Windows PC" : "Linux Desktop")}" maxlength="80"></label><label class="toggle"><input id="autostart" type="checkbox" checked> ${t("autostart")}</label><button id="make-device">${t("pair")}</button><p id="pair-code" class="code"></p><label class="toggle"><input id="remote-lock" type="checkbox"> ${t("lock")}</label><hr><h2>${t("divider")}</h2><p>${t("botIntro")}</p><button id="make-bot" class="secondary">${t("bot")}</button><p id="bot-code" class="code"></p><p id="message" role="status"></p></section>`;
  document.querySelector("#language")!.addEventListener("click", switchLocale);
  document.querySelector("#make-device")!.addEventListener("click", async () => { try { const code = await api<PairCode>("/v1/devices/pairing-codes", { method: "POST", body: JSON.stringify({ device_name: document.querySelector<HTMLInputElement>("#device-name")!.value }) }); document.querySelector("#pair-code")!.textContent = `${t("pairCode")} ${code.pairing_code}`; const device = await api<{ device_id: string; device_token: string }>("/v1/devices/claim", { method: "POST", body: JSON.stringify({ pairing_code: code.pairing_code }) }); await invoke("store_device", { serverUrl: localStorage.getItem("server"), deviceId: device.device_id, deviceToken: device.device_token }); if (document.querySelector<HTMLInputElement>("#autostart")!.checked) { await enableAutostart(); message(t("autostartSaved")); } message(t("enrolled")); } catch (error) { message(error instanceof Error ? error.message : t("error"), true); } });
  document.querySelector("#remote-lock")!.addEventListener("change", async (event) => { try { await invoke("set_remote_lock_enabled", { enabled: (event.target as HTMLInputElement).checked }); message(t("lockSaved")); } catch (error) { (event.target as HTMLInputElement).checked = false; message(error instanceof Error ? error.message : t("error"), true); } });
  document.querySelector("#make-bot")!.addEventListener("click", async () => { try { const code = await api<PairCode>("/v1/bot-pairing-codes", { method: "POST" }); document.querySelector("#bot-code")!.textContent = `${t("botCode")} ${code.pairing_code}`; } catch (error) { message(error instanceof Error ? error.message : t("error"), true); } });
}
applyLocale();
loginScreen();
