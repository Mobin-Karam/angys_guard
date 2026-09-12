# AngysGuard / Laptop Guard roadmap

This roadmap separates **current release hardening** from the longer-term **AngysGuard** product direction.

The current package/repository still use `laptop-guard` / `laptop_guard_v3` compatibility identifiers. AngysGuard — **Angel of System Guard** — is the planned public product identity; issue #30 owns the compatibility-safe migration.

The product goal is:

> A non-technical owner can install, configure, diagnose and operate AngysGuard on a supported device, choose local/self-hosted/managed control, and understand exactly which security capabilities their platform supports without editing source files or memorizing commands.

## Current baseline

The existing Linux-first product already includes:

- guided setup (`./run.sh setup`);
- runtime configuration validation;
- `doctor`;
- arm/disarm/status/profile commands;
- hardware/provider tests;
- events and health commands;
- systemd user-service/autostart management;
- Bale/Telegram/local provider configuration paths;
- camera/input/screen/audio/security features;
- event/outbox/state foundations;
- Graphify-first engineering and repository automation.

The immediate releases remain focused on hardening and production readiness before broad platform expansion.

---

# Milestone: v11.2 — Setup & Security Hardening

**Goal:** a clean supported Linux machine can reach a safe, diagnosable installation without manually editing project configuration files.

Issues:

- [ ] #1 — remove tracked `.env` / rotate exposed credentials — P0
- [ ] #2 — resilient Ubuntu installer/bootstrap — P0
- [ ] #3 — actionable doctor/readiness checks — P0

Recommended order: **#1 -> #2 -> #3**.

---

# Milestone: v11.3 — Non-Technical UX

**Goal:** normal users can operate the product through guided flows instead of memorizing commands.

Issues:

- [ ] #5 — resumable/reconfigurable setup — P1
- [ ] #6 — guided recovery instead of raw runtime failures — P1
- [ ] #4 — simple guided main menu — P1

Recommended order: **#5 -> #6 -> #4**.

---

# Milestone: v12.0 — Production-Ready Linux Release

**Goal:** make the current Linux product reproducible, testable, supportable and safe to release broadly before cross-platform expansion.

Issues:

- [ ] #7 — automated first-run/regression coverage + CI — P1
- [ ] #8 — supported-platform matrix + release checklist — P2

Release criteria include clean-machine install, supported Python/OS/session documentation, target-device validation and no unresolved P0 release blockers.

---

# Milestone: v13.0 — AngysGuard Self-Hosted UX & Linux App

**Goal:** establish the AngysGuard product identity and make the self-hosted Linux experience easy enough for non-technical users.

Issues:

- [ ] #30 — compatibility-safe public rename/migration to AngysGuard — P2
- [ ] #31 — canonical OS support matrix + user platform-request intake — P2
- [ ] #32 — guided Linux desktop/tray app — P1
- [ ] #37 — one-time-code self-hosted Bale/Telegram bot pairing — P1
- [ ] #41 — Bale/Telegram capability parity + provider-specific guidance — P2

### Exit criteria

- public AngysGuard naming is documented/migrated without breaking current installs;
- Linux desktop app covers setup/status/events/provider/service basics;
- users can create their own Bale/Telegram bot and pair without `.env` editing;
- provider differences are explicit and release-validated;
- platform requests have a structured intake and prioritization process.

Suggested order: **#31 -> #41 -> #37 -> #32**, with #30 migration timing coordinated around compatibility/release needs.

---

# Milestone: v14.0 — AngysGuard Managed Control

**Goal:** add an optional startup-operated control plane for users who do not want to maintain their own bot, while keeping self-hosted mode fully usable.

Issues:

- [ ] #38 — managed onboarding/trust model — P1
- [ ] #39 — passwordless device authorization + local privilege model — P1
- [ ] #40 — multi-device account/enrollment/revocation/dashboard — P2
- [ ] #42 — managed backend + official Bale/Telegram bots — P2

### Hard security exit criteria

- **no protected computer OS password is sent to Bale/Telegram or the managed backend**;
- account/device credentials are scoped, revocable and rotatable;
- pairing codes are single-use, short-lived and rate-limited;
- backend compromise does not expose a generic device shell;
- self-hosted mode still works without the managed service;
- retention/deletion/audit/incident policies are documented;
- security review is complete before broad release.

Recommended order: **#39 + #38 -> #40 -> #42**.

---

# Planning milestone: Future Platform Expansion — Windows & Android

This is a long-horizon planning target, **not a claim of current support**.

Issues:

- [ ] #33 — cross-platform capability adapters — P1
- [ ] #34 — native Windows desktop agent/app — P1
- [ ] #35 — Android companion app — P2
- [ ] #36 — Android protected-device feasibility research — P3

Recommended sequence:

```text
#33 platform capability contract
      |
      +--> #34 Windows native agent/app
      |
      +--> #35 Android companion app
              |
              +--> #36 protected-device feasibility decision
```

Linux remains the reference platform while this work proceeds.

Users may request macOS, iOS/iPadOS, ChromeOS, BSD, another Linux distribution, another desktop environment, or any other device class through the Platform / OS request form. Requests inform prioritization; they do not create an automatic support commitment.

---

# Architecture evolution track

Architecture evolution remains separate from release marketing. The existing issues #19-#24 incrementally move the system toward the documented modular-monolith / ports-and-adapters design.

Cross-platform issue #33 should build on that architecture rather than introduce a second framework.

Relevant docs:

- `docs/ARCHITECTURE.md`;
- `docs/architecture/EVOLUTION_PLAN.md`;
- `docs/adr/0008-cross-platform-capability-adapters.md`;
- `docs/adr/0007-passwordless-device-pairing.md`.

---

# Product/control-mode direction

The target product supports three owner-control choices:

```text
Local-only / desktop app
        |
Self-hosted Bale/Telegram bot
        |
Optional managed AngysGuard bot/app service
```

Self-hosted mode remains a first-class choice even after managed mode exists.

See `docs/CONTROL_MODES.md`.

---

# Platform direction

| Platform | Direction |
|---|---|
| Linux | Current primary platform; future desktop app/tray |
| Windows | Planned native agent/app after capability abstraction |
| Android | Planned companion app; protected-device agent under research |
| Other OSes | Request-driven future candidates |

See `docs/PLATFORM_SUPPORT.md`.

---

# Work board

## Now

- #1 security cleanup
- #2 installer hardening
- #3 doctor/readiness

## Next

- #5 resumable setup
- #6 guided recovery
- #4 guided main menu

## Production release

- #7 regression coverage
- #8 support/release checklist

## AngysGuard self-hosted UX

- #31 platform support/request process
- #41 provider parity
- #37 self-hosted pairing
- #32 Linux desktop app
- #30 branding migration

## Managed control

- #39 security/auth model
- #38 managed onboarding
- #40 multi-device
- #42 managed service/official bots

## Cross-platform

- #33 capability adapters
- #34 Windows
- #35 Android companion
- #36 Android protected-device research

---

# Definition of done for every issue

An issue is not complete just because the happy path works. Before closing it:

- relevant automated/manual tests pass;
- no tokens/secrets/passwords/private evidence are logged or committed;
- failure states have user-readable recovery;
- documentation/README/platform/control-mode claims are updated when behavior changes;
- existing compatibility paths remain safe unless migration is explicit;
- platform capability/support claims have real validation;
- security review is included for pairing, credentials, managed service, remote control, capture and privileged OS actions;
- Graphify is refreshed after material repository-relationship changes when available;
- issue acceptance criteria are complete.

# Product direction guardrail

AngysGuard remains focused on device security, monitoring, evidence, alerts, owner communication and **safe fixed local/remote controls**. It must not become spyware, a credential collection service, or a generic remote-administration shell.
