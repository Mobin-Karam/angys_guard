# Laptop Guard 11.1

Laptop Guard is an owner-controlled Linux security agent. It watches camera and
input activity, records local evidence, presents a five-second fullscreen
warning, can lock the desktop, and exposes a constrained Bale control surface.
It deliberately does not expose a remote shell, suppress capture indicators, or
delete user data.

## Start here

Choose the document by what you are trying to do:

| Goal | Read first |
|---|---|
| Understand the architecture contract/target design | [Architecture](ARCHITECTURE.md) |
| See current architecture evidence, risks, and limitations | [System audit](SYSTEM_AUDIT.md) |
| Review dependency rules / staged architecture evolution | [Architecture notes](architecture/) |
| Understand architecture decisions | [ADRs](adr/) |
| Find the file/module responsible for behavior | [File reference](FILE_REFERENCE.md) |
| Add, change, fix, or remove a feature | [Feature lifecycle](FEATURE_LIFECYCLE.md) |
| Find the cause of a bug or fix a GitHub issue | [Bug triage and fixing](BUG_TRIAGE_AND_FIXING.md) |
| Add a new command/feature module | [Extending](EXTENDING.md) |
| Work with Codex/AI agents | [AI agent workflow](AI_AGENT_WORKFLOW.md) |
| Change setup/config/secrets | [Configuration](CONFIGURATION.md) |
| Review trust/privacy/security rules | [Security](SECURITY.md) |
| Run tests or validate hardware/session behavior | [Testing](TESTING.md) |
| See planned work | [Roadmap](ROADMAP.md) |
| Prepare/maintain the repository | [Maintainer checklist](MAINTAINER_CHECKLIST.md) |
| Understand previous migrations/releases | [History](HISTORY.md) |

## Architecture at a glance

Laptop Guard is evolving as a **modular monolith with ports/adapters**, not as a
microservice system. Existing seams such as `RuntimeApi`, `FeatureManager`,
`FeatureHost`, `GuardRuntimeState`, and the event/outbox store should be strengthened
incrementally instead of replaced by a flag-day rewrite.

For new architecture work, start with `ARCHITECTURE.md`, then use:

- `architecture/BOUNDARIES.md` for allowed dependency direction;
- `architecture/FLOWS.md` for startup/security/delivery flows;
- `architecture/EVOLUTION_PLAN.md` for staged refactor order;
- `adr/` for accepted/proposed architecture decisions.

## Maintenance workflow

For normal engineering work, use this sequence:

```text
GitHub issue / user report / feature request
                |
                v
classify the task
  architecture  -> ARCHITECTURE.md + architecture/ + ADRs
  feature work  -> FEATURE_LIFECYCLE.md
  defect        -> BUG_TRIAGE_AND_FIXING.md
                |
                v
find owner/path with FILE_REFERENCE.md + SYSTEM_AUDIT.md
                |
                v
implement smallest safe change
                |
                v
focused regression tests
                |
                v
TESTING.md + reviewer/security review when needed
                |
                v
PR / release
```

If using Codex in VS Code, `AGENTS.md` is the authoritative instruction file and
`docs/AI_AGENT_WORKFLOW.md` explains the repo-local agents, skills, and hooks.

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
