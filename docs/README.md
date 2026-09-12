# Laptop Guard 11.1

Laptop Guard is an owner-controlled Linux security agent. It watches camera and
input activity, records local evidence, presents a five-second fullscreen
warning, can lock the desktop, and exposes a constrained Bale control surface.
It deliberately does not expose a remote shell, suppress capture indicators, or
delete user data.

## Documentation

- [System audit](SYSTEM_AUDIT.md) — architecture, flows, controls, findings, and limitations.
- [File reference](FILE_REFERENCE.md) — responsibility and status of every tracked project file.
- [Extending](EXTENDING.md) — low-context feature template and module contracts.
- [Configuration](CONFIGURATION.md) — setup, persistent files, defaults, and service preparation.
- [Security](SECURITY.md) — trust boundaries, authorization, protected stop, and privacy.
- [Testing](TESTING.md) — automated and target-device validation.
- [History](HISTORY.md) — consolidated release and migration history.

## Install and run

```bash
chmod +x install.sh run.sh doctor.sh
./install.sh
./run.sh setup
./run.sh doctor
./run.sh
```

Useful Ubuntu packages:

```bash
sudo apt install python3-venv python3-tk ffmpeg vlc gnome-screenshot libnotify-bin
```

For wlroots-based Wayland desktops, `grim` and `wf-recorder` provide additional
capture backends. Laptop Guard cannot bypass compositor permission boundaries.

## Main behavior

- Only the configured owner chat ID may issue commands.
- Configuration is stored under `~/.config/laptop-guard/`; a project `.env` is
  not required.
- Unexpected input can trigger evidence collection, owner notification, a
  bundled 1920×1080 MP4 warning, and a desktop lock.
- Ctrl+C uses local PIN plus Bale owner confirmation. Other termination paths
  fail closed through the exit-lock watchdog when enabled.
- Remote power and unlock controls are opt-in and confirmation-gated.
- Autostart and automatic arming are separate settings: the service may start
  after graphical login while remaining disarmed, or arm immediately.
- Readable Linux authentication failures generate sanitized owner alerts.
- Persian speech and automatic RTL/LTR chat rendering are supported.

## Common commands

```text
./run.sh setup
./run.sh doctor
./run.sh status
./run.sh autostart on
./run.sh autostart off
./run.sh autostart status
./run.sh profile away
./run.sh events --limit 20
./run.sh service install
./run.sh service status
```

From Bale, `/menu`, `/status`, `/arm`, `/disarm`, `/photo`, `/screen`,
`/listen`, `/chat`, `/say`, `/events`, `/lock`, `/unlock`, `/stoppin`, and the
confirmed power actions are handled by the current runtime.

The warning media is `laptop_guard/assets/warnings/countdown.mp4`: 1920×1080,
30 fps, and five seconds.
