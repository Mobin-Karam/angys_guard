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
| Understand Bale, Telegram, self-hosted and managed control | [Control modes](CONTROL_MODES.md) |
| Review the planned managed pairing/control contract | [Managed onboarding protocol](MANAGED_ONBOARDING_PROTOCOL.md) |
| Compare Bale vs Telegram Bot API behavior | [Provider behavior](PROVIDERS.md) |
| Request another operating system/platform | [Platform support](PLATFORM_SUPPORT.md#request-support-for-another-os) + Platform / OS request issue form |
| Install/use current Linux release | [Root README quick start](../README.md#quick-start--linux-today) |
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
