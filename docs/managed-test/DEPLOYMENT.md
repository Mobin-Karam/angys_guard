# Managed test deployment — `api.mahakaram.ir`

This is the controlled **10-user test** deployment for the Tauri v2 desktop
agent. The same source builds Windows installers and a Linux `.deb`/AppImage
desktop client. Both interfaces are Persian-first RTL with an English toggle.
This is not a production support claim and must remain behind HTTPS.

On Linux, the desktop client delegates its three existing protection actions
only to the fixed local commands `laptop-guard status`, `laptop-guard arm`, and
`laptop-guard disarm`. The Linux package workflow builds that Python runtime as
an audited sidecar and bundles it into the `.deb`/AppImage; the installed user
service records the sidecar's stable installed path. A single-install Linux
release remains a release gate until the resulting artifacts are signed and
validated on clean target devices.

## What is deployed

`docker-compose.managed-test.yml` starts a small account/enrollment/action-queue
service on loopback port `8080`. Put it behind the existing TLS reverse proxy for
`https://api.mahakaram.ir`; proxy only that hostname to `127.0.0.1:8080`.

The service stores:

- salted, high-work-factor AngysGuard account-password verifiers;
- revocable **hashes** of device credentials;
- short-lived, one-use device and bot link codes;
- linked bot chat IDs and bounded command audit results.

It never requests, stores, or transmits a protected Windows password.
Account creation and sign-in are bounded to ten attempts per source address every
15 minutes for this single-process test deployment; keep reverse-proxy rate
limiting enabled as a separate protection.

## Server setup

1. Copy `.env.managed-test.example` to an untracked `.env.managed-test` beside
   `docker-compose.managed-test.yml`.
2. Set a unique random `ANGYSGUARD_SERVER_SECRET` (at least 32 characters) using
   your server secret manager. Do not send it in chat or commit it.
3. Configure TLS for `api.mahakaram.ir` and force HTTP-to-HTTPS redirect at the
   proxy. Install [the Nginx rate-limit zone](nginx-http-rate-limit.conf) once
   in the `http` context, then add [the location policy](nginx-api.mahakaram.ir.conf)
   to the hostname's HTTPS server block. The Docker port intentionally binds to
   loopback only.
4. Run `docker compose -f docker-compose.managed-test.yml up -d --build`.
5. Confirm `https://api.mahakaram.ir/healthz` returns `{"status":"ok"}`.

Back up the named Docker volume before making server changes. A backup contains
account/password verifier data and device metadata; treat it as confidential.

### Runflare Python PaaS

Deploy from the repository root with `runflare deploy`. The root
[main.py](../../main.py) is the provider entrypoint and exposes the same ASGI
application as [server/main.py](../../server/main.py), so Runflare can either
import `main:app` or execute `python main.py`. Root
[requirements.txt](../../requirements.txt) includes the API runtime
dependencies. In the Runflare environment-variable dashboard, copy the
variable names from [server/.env.example](../../server/.env.example) and set
their values there; do not upload a populated `.env` file. Let Runflare set
`PORT` if it provides one.

The server is the control plane, not the protected-device runtime. Do **not**
install `laptop-guard` in Runflare: Laptop Guard must run locally in each
user's Linux desktop session, where it owns monitoring, visible warnings,
device state, and local OS policy. The desktop app links that local runtime to
the user's account and bot with the fixed action queue.

### Linux desktop local-protection flow

The shared Tauri desktop source includes a **managed-test** Linux flow after a
user enrolls the device: they explicitly accept the local privacy notice, press
**Start local protection**, and the app invokes only fixed local commands to
create a `bot.provider = "local"` Laptop Guard profile and start its systemd
user service. That first-run profile deliberately leaves camera, microphone
sound detection, screenshots/screen recording, application control, remote
unlock and remote power disabled. Those capabilities can only be enabled later
through local Laptop Guard configuration and its existing consent/Doctor flow.

The Tauri app continues to poll the managed fixed-action queue while it is
running; the Laptop Guard user service keeps local protection running after
desktop login. Development builds may fall back to a locally installed
`laptop-guard` executable, but packaged Linux builds resolve the bundled
sidecar. This is not yet a claim that an artifact is release-qualified: the
actual `.deb`/AppImage must pass clean-device installation, reboot/recovery,
X11/Wayland and provider checks before being distributed to testers.

`ANGYSGUARD_SERVER_SECRET` is required and must be a new random value of at
least 32 characters. `ANGYSGUARD_DATABASE_PATH` must point to a Runflare
**persistent** directory/volume. If Runflare does not provide persistent disk
storage for the selected plan, this SQLite test service is not suitable: every
restart would lose accounts, pairings, and revocations.

After the provider reports the deployment as running, confirm:

```bash
curl --fail-with-body https://api.mahakaram.ir/healthz
curl --fail-with-body https://api.mahakaram.ir/readyz
```

They must return `{"status":"ok"}` and `{"status":"ready"}` before
registering a webhook or enrolling a device. A provider `503 Loading` page means
the application has not started or the domain is not attached to the running
service yet. If `/healthz` returns `{"status":"degraded"}`, the process is
running but `ANGYSGUARD_SERVER_SECRET` is missing/too short or the configured
database directory is not writable.

## Bot webhooks

For each enabled provider, set a distinct high-entropy webhook secret in the
server secret manager, plus that provider's bot token. Never put tokens in the
desktop installer, desktop app, repository, or user instructions.

Configure the provider to POST updates to one of:

```text
https://api.mahakaram.ir/v1/bots/telegram/updates
https://api.mahakaram.ir/v1/bots/bale/updates
```

Telegram must use its `secret_token` webhook feature so it sends the configured
value in `X-Telegram-Bot-Api-Secret-Token`. Bale must be configured to send the
same provider-specific secret in `X-AngysGuard-Bot-Secret`, or an equivalent
gateway must translate and authenticate its webhook before forwarding it.

After the HTTPS health check works, register Telegram from the server environment:

```bash
python server/scripts/configure_telegram_webhook.py
```

Create the Telegram bot with BotFather and the Bale bot through Bale's official
bot-management flow first. This repository intentionally cannot create provider
accounts or invent provider tokens. The supplied registration helper never prints
the token.

The current test bot accepts only `/link CODE`, `/devices`, `/use DEVICE-ID`,
`/status`, `/arm`, `/disarm`, `/lock`, and `/revoke`. One chat is tied to one
account. With multiple devices, `/devices` lists the account's short IDs and
`/use DEVICE-ID` selects one; no action is queued until that selection is made.
`/revoke` requires a separate, single-use `/confirm-revoke CODE` reply within
30 seconds. After the device completes a fixed action, the server sends its
bounded result back to the same linked chat.

## Operator release gate

Do not create a `windows-v*` tag until all of these pass:

- real install/uninstall and upgrade on Windows 10 and Windows 11;
- real install/uninstall and desktop-session lock testing on supported Ubuntu
  X11 and Wayland sessions;
- enrollment and credential storage/revocation on each OS;
- a live Telegram and Bale webhook/link/command test;
- remote lock is visibly locally enabled and locks only the enrolled session;
- independent review of reverse-proxy TLS, backups, logs, rate limits, and
  provider token handling.

The `windows-v*` tag starts GitHub Actions, which packages NSIS `.exe` and MSI
installers and attaches them as a **prerelease**. Configure Windows code signing
in GitHub Actions before presenting the download to test users.
