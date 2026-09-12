# Full system audit

Audit date: 2026-09-12. Scope: current working tree of Laptop Guard 11.1. This is
a source and local-runtime audit; it is not proof of deployment, external Bale
availability, every desktop environment, or every hardware backend.

> **Architecture note:** this document records the **current implementation and
> evidence**. The canonical target architecture and dependency contract are in
> `ARCHITECTURE.md`, `architecture/`, and `adr/`. Transitional coupling described
> here should not automatically be copied into new code.

## Executive assessment

The system is a functional single-device Linux security agent with strong
owner-only command checks, constrained actions, persistent configuration,
visible capture behavior, and fail-closed exit handling. The inspected machine
passed doctor checks and 52 current tests. The highest architectural risk is
remaining coexistence of old and new warning/system/audio facades. This audit's
modularization pass added explicit runtime transport, state, feature, and event
boundaries so new work no longer needs to extend the monolithic routing chain.

The target architecture keeps those successful seams and evolves them into a
modular monolith with inward dependency direction: delivery/infrastructure at the
edges, application orchestration behind explicit ports, and infrastructure-free
security/domain decisions where extraction is valuable. See `ARCHITECTURE.md`.

## Runtime topology

```text
run.sh -> python -m laptop_guard -> cli.cmd_run
  -> ensure_runtime_configuration
  -> LaptopGuard
     -> RuntimeApi (Bale/Telegram HTTP or local no-network adapter)
     -> camera thread + pynput keyboard/mouse listeners
     -> EventLog JSONL + shared SQLite event store
     -> screen/camera/audio/chat/TTS helpers
     -> warning_sequence -> VLC/mpv/ffplay
     -> system_actions -> lock/unlock/power
     -> exit_watchdog subprocess
```

The CLI and live guard now share `RuntimeStateStore`; the live facade persists
assignments and refreshes owner-controlled fields. Guard events retain fail-safe
JSONL output and are mirrored into the shared SQLite store used by the CLI.

## Startup and configuration

`run.sh` sets `umask 077` and prefers `.venv/bin/python`. `cli.cmd_run` validates
or repairs the stored token and owner pairing before constructing the guard.
Setup and config writes use user-scoped files and atomic replacement. A service
install is refused when setup/token prerequisites are absent.

`build_runtime_api()` is the single construction boundary. Local mode now runs
without a bot token/network, fixing the previous startup crash. Remote modes
receive the configured API base and explicit proxy.

## Authorization and bot handling

All privileged update/callback handling is gated by the configured owner chat
ID. Commands map to explicit methods and fixed OS actions; there is no shell
text execution. Bale media is handled through fixed upload/download methods.
Long polling avoids a public inbound server.

The older generic `httpx` setup provider and Requests runtime client still
duplicate some transport behavior, but both now reject ambient proxy settings.

## Monitoring and intrusion flow

Camera monitoring uses OpenCV motion analysis and optional HOG person detection,
with a safe motion-only fallback. Input listeners classify activity and discard
key identities. When armed and outside grace/cooldown windows, input can capture
camera/screen evidence, notify the owner, open chat, launch the warning MP4, and
schedule lock independently of the video player. Closing the visual player does
not cancel the lock timer.

Limitations: camera, global input, screen capture, and fullscreen behavior depend
on hardware, desktop session, permissions, and Wayland/X11 capabilities. The
application does not bypass those boundaries.

## Protected stop and watchdog

The PIN store uses random salt, scrypt, constant-time digest comparison, atomic
replacement, and restrictive permissions. Ctrl+C spawns a bounded interactive
authorization worker. A successful second factor writes a one-time file/token
that the detached watchdog consumes. Other stop paths request locking.

Limitations: OS-lock helpers return only command success; they cannot verify the
screen visibly locked. The watchdog protects process lifecycle, not an attacker
with full control of the same account/environment.

## Communications and media

Security chat uses append-only JSON lines plus an atomic transcript mirror and
direction-aware Tk UI. Persian speech jobs are bounded/serialized and the
external library is lazy-loaded. Audio/screen/camera commands use fixed native
tool argument arrays rather than a shell. Capture/playback errors degrade to
messages instead of crashing the core loop.

## Persistence

JSONL remains a fail-safe human-readable log while SQLite provides CLI event
visibility and the offline outbox. New guard events are written to both. Runtime
state is now shared between CLI and the live guard. The outbound send path still
does not enqueue every failed v11 send into the durable outbox.

No automatic event/media retention or storage quota is implemented. Long-lived
installations need operational cleanup policy.

## Local API and app control

The optional local API uses bearer comparison and loopback defaults, caps JSON
and media sizes, and exposes fixed status/chat/speech/warning/capture callbacks.
App management discovers `.desktop` files and filters through an allowlist.
Neither component exposes arbitrary shell execution.

## Packaging and operations

The project declares Python 3.11+, runtime dependencies, a pytest extra, console
entry point, and explicit warning media package data. Installer behavior still
depends on package network access and native OS packages. A clean wheel build
and wheel-install doctor smoke test remains open because build tooling could not
be installed in the audit environment.

The systemd user service passes desktop/audio environment variables and restarts
automatically. Actual operation depends on the graphical user session and user
service environment.

## Findings and priorities

| Priority | Finding | Recommended action |
|---|---|---|
| Resolved | Live guard and CLI state/events drifted | Added shared persistent state and SQLite event mirroring |
| Resolved | Local mode crashed and runtime ignored provider construction boundary | Added `RuntimeApi`, local adapter, and centralized factory |
| Resolved | Malformed numeric callback payloads could raise from the polling path | Added bounded, defaulting callback parsing |
| Resolved | CLI lock command returned success when every lock backend failed | Return exit code 2 on failure |
| Resolved | Service commands always returned success even when systemctl failed | Propagate native command results through the CLI |
| Resolved | Main runtime bypassed the faster evdev-capable input monitor | Use `InputMonitor`, 100ms evdev polling, and lower movement threshold |
| Resolved | Warning launch followed network/evidence scheduling | Launch video first; keep delivery and evidence asynchronous |
| Added | Automatic startup needed an explicit switch | Persist `autostart on/off/status`, separate from automatic arming |
| Added | Failed login attempts were not visible remotely | Capability-detected journal monitoring and sanitized Bale alerts |
| P1 | No retention/quota for evidence and event data | Add configurable age/size cleanup with safe defaults |
| P2 | Setup and runtime still have two HTTP transport implementations | Consolidate retries, uploads, and errors behind one adapter |
| P2 | Three warning layers and two system-action facades coexist | Mark compatibility facades and reduce to one active implementation |
| P2 | Wheel installation not smoke-tested in this environment | Build/install in a clean Python 3.11–3.14 matrix |
| P2 | Hardware/security flows lack end-to-end automation | Add disposable integration tests plus target-laptop checklist evidence |
| Resolved | Historical legacy tests duplicated current tests | Removed the uncollected copies; current migration tests remain |
| P3 | Some modules are formatting-dense and broadly catch exceptions | Gradually improve typing, structured logging, and narrow exception handling |

The architecture evolution sequence for these findings is maintained in
`architecture/EVOLUTION_PLAN.md`; architecture decisions are recorded in `adr/`.

## Evidence boundary

Confirmed locally: source compilation/imports, current test logic, shell syntax,
dependency consistency, current doctor result, MP4 metadata, CLI help/status,
configuration parsing, and source-level authorization/action boundaries.

Not confirmed: clean network install, isolated wheel contents, live Bale command
round trips, actual armed intrusion on hardware, webcam/microphone fidelity,
Wayland/X11 coverage, fullscreen focus, OS lock/unlock effect, abrupt-kill
watchdog behavior, TTS network synthesis, systemd restart after login/reboot, or
long-duration retention behavior.
