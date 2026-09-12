# Laptop Guard 11.1

Laptop Guard is an owner-controlled Linux security agent. It watches camera and
input activity, records local evidence, presents a five-second fullscreen warning,
can lock the desktop, and exposes a constrained Bale control surface. It deliberately
does not expose a remote shell, suppress capture indicators, or delete user data.

The repository-level product landing page is [`../README.md`](../README.md). This
`docs/README.md` is the task-oriented documentation index for maintainers and
contributors.

## Before reading the repository broadly: use Graphify

For humans and AI agents, repository discovery is Graphify-first. Read
[Graphify navigation](GRAPHIFY_NAVIGATION.md) before trying to understand where
behavior lives or how files/symbols connect.

```text
question
  -> check Graphify freshness
  -> graphify query / explain / path
  -> identify minimal relevant files/symbols/tests/docs
  -> inspect those authoritative files
```

Useful examples:

```bash
graphify query "where is owner authorization enforced?"
graphify explain "LaptopGuard"
graphify path "InputMonitor" "EventStore"
```

Do not open the full `graphify-out/graph.json` manually for normal investigation;
query it through Graphify. `graphify-out/graph.html` is available for human visual
exploration, and `GRAPH_REPORT.md` gives a high-level overview/freshness record.

## Start here

Choose the document by what you are trying to do **after Graphify narrows the
scope**:

| Goal | Read first |
|---|---|
| Understand the product quickly | [Root repository README](../README.md) |
| Navigate/find files, symbols, callers, tests, or connections | [Graphify navigation](GRAPHIFY_NAVIGATION.md) |
| Understand the architecture contract/target design | [Architecture](ARCHITECTURE.md) |
| See current architecture evidence, risks, and limitations | [System audit](SYSTEM_AUDIT.md) |
| Review dependency rules / staged architecture evolution | [Architecture notes](architecture/) |
| Understand architecture decisions | [ADRs](adr/) |
| Use the curated file/module ownership map | [File reference](FILE_REFERENCE.md) |
| Add, change, fix, or remove a feature | [Feature lifecycle](FEATURE_LIFECYCLE.md) |
| Find the cause of a bug or fix a GitHub issue | [Bug triage and fixing](BUG_TRIAGE_AND_FIXING.md) |
| Add a new command/feature module | [Extending](EXTENDING.md) |
| Work with Codex/AI agents | [AI agent workflow](AI_AGENT_WORKFLOW.md) |
| Maintain README / GitHub About / version / repository visual | [README & repository presentation maintenance](README_MAINTENANCE.md) |
| Change setup/config/secrets | [Configuration](CONFIGURATION.md) |
| Review trust/privacy/security rules | [Security](SECURITY.md) |
| Run tests or validate hardware/session behavior | [Testing](TESTING.md) |
| See planned work | [Roadmap](ROADMAP.md) |
| Understand labels, milestones, releases, and Project views | [Project management](PROJECT_MANAGEMENT.md) |
| Prepare/maintain the repository | [Maintainer checklist](MAINTAINER_CHECKLIST.md) |
| Understand previous migrations/releases | [History](HISTORY.md) |

## Architecture at a glance

Laptop Guard is evolving as a **modular monolith with ports/adapters**, not as a
microservice system. Existing seams such as `RuntimeApi`, `FeatureManager`,
`FeatureHost`, `GuardRuntimeState`, and the event/outbox store should be strengthened
incrementally instead of replaced by a flag-day rewrite.

Use Graphify first to map the current runtime relationships, then reconcile them
with the intended architecture:

- `ARCHITECTURE.md` for the architecture contract;
- `architecture/BOUNDARIES.md` for allowed dependency direction;
- `architecture/FLOWS.md` for startup/security/delivery flows;
- `architecture/EVOLUTION_PLAN.md` for staged refactor order;
- `adr/` for accepted/proposed architecture decisions.

## Project and release management

Repository labels, milestones, issue mappings, and release notes are declared under
`.github/repository-management/` and applied by the repository-management bootstrap
workflow. `PROJECT_MANAGEMENT.md` defines the canonical GitHub Project v2 fields,
views, workflow rules, and initial issue mapping.

Repository landing-page/About metadata has its own canonical source:

- root `README.md` — product/repository landing page;
- `.github/repository-profile.json` — canonical About description/topics/social-preview source;
- `README_MAINTENANCE.md` — synchronization and update rules;
- `assets/laptop-guard-overview.svg` — high-level README product visual.

The first formal GitHub release checkpoint is `v11.1.0`. Future releases should
create a new semantic-version tag rather than moving an already-published tag.

## Maintenance workflow

For normal engineering work, use this sequence:

```text
GitHub issue / user report / feature request
                |
                v
Graphify freshness + query/path/explain
                |
                v
smallest owning files/symbols/tests/docs
                |
                v
classify the task
  architecture  -> ARCHITECTURE.md + architecture/ + ADRs
  feature work  -> FEATURE_LIFECYCLE.md
  defect        -> BUG_TRIAGE_AND_FIXING.md
                |
                v
confirm current source behavior
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
if release/version/user-visible/platform/security surface changed:
README_MAINTENANCE.md / $repository-presentation
                |
                v
refresh Graphify after material relationship changes
                |
                v
PR / release
```

If using Codex in VS Code, `AGENTS.md` is authoritative;
`docs/AI_AGENT_WORKFLOW.md` explains repo-local agents, skills, hooks, and the
Graphify-first handoff pattern. `repository_curator` / `$repository-presentation`
owns README/About/profile synchronization for release or presentation-affecting
changes.

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
- Unexpected input can trigger evidence collection, owner notification, a bundled
  1920×1080 MP4 warning, and a desktop lock.
- Ctrl+C uses local PIN plus Bale owner confirmation. Other termination paths fail
  closed through the exit-lock watchdog when enabled.
- Remote power and unlock controls are opt-in and confirmation-gated.
- Autostart and automatic arming are separate settings.
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

From Bale, `/menu`, `/status`, `/arm`, `/disarm`, `/photo`, `/screen`, `/listen`,
`/chat`, `/say`, `/events`, `/lock`, `/unlock`, `/stoppin`, and confirmed power
actions are handled by the current runtime.

The warning media is `laptop_guard/assets/warnings/countdown.mp4`: 1920×1080,
30 fps, and five seconds.
