# AngysGuard / Laptop Guard documentation

The repository-level landing page is [`../README.md`](../README.md). This file is the task-oriented documentation index for users, maintainers and contributors.

**AngysGuard — Angel of System Guard** is the planned public product identity. Current package/repository compatibility identifiers remain `laptop-guard`, `laptop_guard` and `laptop_guard_v3` until issue #30 executes a safe migration.

## Start here by goal

| Goal | Read first |
|---|---|
| Understand AngysGuard quickly | [Root README](../README.md) |
| Understand Platform v2 multi-client architecture | [Platform v2 architecture foundation](PLATFORM_V2_ARCHITECTURE.md) |
| See product direction and future apps | [AngysGuard product vision](ANGYSGUARD_PRODUCT_VISION.md) |
| Know which OSes work today / are planned | [Platform support](PLATFORM_SUPPORT.md) |
| Review the cross-platform capability contract | [Platform capabilities](PLATFORM_CAPABILITIES.md) |
| Understand Bale, Telegram, self-hosted and managed control | [Control modes](CONTROL_MODES.md) |
| Review the planned managed pairing/control contract | [Managed onboarding protocol](MANAGED_ONBOARDING_PROTOCOL.md) |
| Review the implemented gateway authorization boundary and remaining work | [Platform gateway boundary](PLATFORM_GATEWAY.md) |
| Review the implemented client command-verification boundary | [Platform client protocol](PLATFORM_CLIENT_PROTOCOL.md) |
| Compare Bale vs Telegram Bot API behavior | [Provider behavior](PROVIDERS.md) |
| Request another operating system/platform | [Platform support](PLATFORM_SUPPORT.md#request-support-for-another-os) + Platform / OS request issue form |
| Install/use current Linux release | [Root README quick start](../README.md#quick-start--linux-today) |
| Deploy the limited Windows managed test | [Managed test deployment](managed-test/DEPLOYMENT.md) |
| Navigate files/symbols/callers/tests with minimal context | [Graphify navigation](GRAPHIFY_NAVIGATION.md) |
| Understand architecture | [Architecture](ARCHITECTURE.md) |
| See current source-level architecture evidence | [System audit](SYSTEM_AUDIT.md) |
| Review architecture boundaries/evolution | [Architecture notes](architecture/) |
| Read architecture decisions | [ADRs](adr/) |
| Add/change/remove a feature | [Feature lifecycle](FEATURE_LIFECYCLE.md) |
| Add a feature module | [Extending](EXTENDING.md) |
| Find/fix a bug | [Bug triage and fixing](BUG_TRIAGE_AND_FIXING.md) |
| Configuration/secrets/setup | [Configuration](CONFIGURATION.md) |
| Security/trust/privacy rules | [Product security](SECURITY.md) |
| Testing/manual platform validation | [Testing](TESTING.md) |
| Qualify a production release | [Release checklist](RELEASE_CHECKLIST.md) |
| Use AI agents/skills/prompts | [AI agent workflow](AI_AGENT_WORKFLOW.md) |
| See file ownership | [File reference](FILE_REFERENCE.md) |
| See current + future roadmap | [Roadmap](ROADMAP.md) |
| Understand milestones/labels/Project views | [Project management](PROJECT_MANAGEMENT.md) |
| Maintain root README/About/version/support claims | [README maintenance](README_MAINTENANCE.md) |
| Run repository/release maintenance | [Maintainer checklist](MAINTAINER_CHECKLIST.md) |
| Configure GitHub repository settings | [GitHub setup](GITHUB_SETUP.md) |
| Review release/migration history | [History](HISTORY.md) |

## Platform v2 tracking

Issue #62 is the architecture foundation milestone. Implementation is split into:

- #63 Platform Accounts + Device Identity Service
- #64 Remote Bot Gateway Service
- #65 Unified Client Protocol
- #66 Server Managed Configuration Profiles

Each item has its own implementation PR and preserves compatibility with the current local Guard runtime during migration.

## Current vs future

Use `PLATFORM_SUPPORT.md` before assuming a distro/session/provider is release-supported.

### Future product

The long-term AngysGuard roadmap adds:

- public AngysGuard identity (#30);
- user platform-request intake (#31);
- Linux desktop app/tray (#32);
- cross-platform capability adapters (#33);
- Windows native agent/app (#34);
- Android companion app (#35);
- Android protected-device feasibility research (#36);
- simpler self-hosted Bale/Telegram pairing (#37);
- optional managed AngysGuard service (#38/#42);
- passwordless device-scoped authorization/local privilege (#39);
- multi-device account/dashboard (#40);
- provider parity/capability guidance (#41).

The repository now contains an **unqualified Windows managed-test implementation**
under `desktop/windows-tauri/` plus `server/`. It remains a test-only source
implementation until its Windows installer, real Windows 10/11 behavior, reverse
proxy, and live Bale/Telegram flow are validated. See the deployment guide above.

Future items are **not current support claims**.

## Control-mode summary

```text
Current / always-important
├── local CLI + guided setup
├── Bale bot/provider surface
└── Telegram-style provider surface

Planned
├── Linux desktop app
├── self-hosted bot + one-time device pairing
├── optional managed AngysGuard bot/service
├── Android companion app
└── Windows desktop app
```

The managed-service design must never require the protected computer's OS password to be sent through Bale/Telegram or stored in the AngysGuard backend. Read `CONTROL_MODES.md` and ADR 0007.

## Platform summary

| Platform | Status |
|---|---|
| Ubuntu Desktop 24.04 LTS amd64 | v12.0 primary qualification target |
| Ubuntu 22.04 / 26.04 LTS | Best effort / candidate until separately qualified |
| Other Linux distros | Best effort until validated |
| Windows | Planned |
| Android companion | Planned |
| Android protected-device mode | Research |
| Other platforms | Request-driven candidates |

## Graphify-first repository discovery

Before broad repository reads/searches:

```bash
graphify query "where is owner authorization enforced?"
graphify explain "LaptopGuard"
graphify path "InputMonitor" "EventStore"
```

Use Graphify to select the smallest relevant source/tests/docs, then confirm important facts against current source. Do not load all of `graphify-out/graph.json` into normal chat context. See `GRAPHIFY_NAVIGATION.md`.

## Architecture decisions relevant to future platforms

- `adr/0007-passwordless-device-pairing.md` — Proposed: remote pairing/device credentials do not transmit OS passwords; local privilege stays local/platform-native.
- `adr/0008-cross-platform-capability-adapters.md` — Proposed: cross-platform ports/adapters before Windows/Android expansion.
- existing ADRs remain authoritative for feature registration, RuntimeApi, shared state and modular-monolith evolution.

## Project and release management

Repository labels, milestones and issue mappings are declared under `.github/repository-management/` and applied by the repository-management bootstrap workflow.

Current future milestones:

```text
v11.2 -> v11.3 -> v12.0
                    |
                    +-> v13.0 AngysGuard Self-Hosted UX & Linux App
                    +-> v14.0 AngysGuard Managed Control
                    +-> Future Platform Expansion — Windows & Android
```

The native GitHub Project v2 board requires separate user/organization Projects write permission; `PROJECT_MANAGEMENT.md` remains the canonical board specification.

## Repository presentation maintenance

When a release/change affects current features, OS/platform support, Bale/Telegram behavior, managed/self-hosted control, installation, security boundaries or roadmap commitments, update the smallest relevant set of:

- root `README.md`;
- `PLATFORM_SUPPORT.md`;
- `CONTROL_MODES.md`;
- `ANGYSGUARD_PRODUCT_VISION.md`;
- `ROADMAP.md` / `PROJECT_MANAGEMENT.md`;
- `.github/repository-profile.json`;
- release/changelog docs.

Use the repository-curator/product-planning workflows rather than letting marketing/support claims drift from source and issue state.
