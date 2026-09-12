# AngysGuard platform support and targets

This document is the canonical source for **which operating systems AngysGuard can be used on today, which platforms are planned, and how users can request another operating system or device class**.

AngysGuard is the future-facing product name for the project currently packaged and stored under compatibility identifiers such as `laptop-guard`, `laptop_guard`, and the `laptop_guard_v3` repository. See issue #30 for the planned compatibility-safe naming migration.

## Support-state vocabulary

| State | Meaning |
|---|---|
| **Supported** | The project intentionally targets this environment and documents installation, validation and known limitations. |
| **Best effort** | Parts may work because the environment is Linux-compatible or similar, but the project does not yet promise release-level validation. |
| **Planned** | There is an accepted roadmap target/issue, but users must not assume it works today. |
| **Research** | Feasibility is being evaluated; no delivery promise exists. |
| **Not targeted** | No active roadmap commitment. Users may submit a platform request. |

## Current operating-system support

| Platform | State | What is available now | Important limits |
|---|---|---|---|
| **Linux — Ubuntu-oriented desktop** | **Supported / primary target** | Current Python agent, guided setup, doctor, CLI, systemd user service, Bale/Telegram-style provider integration, input/camera/screen/audio/security features | Exact capabilities depend on distro, desktop environment, X11/Wayland compositor, permissions and hardware. |
| **Other Linux distributions** | **Best effort** | Core Python/runtime concepts may work | Installer packages, service behavior, desktop commands and capture backends may need distro-specific work. Do not assume official support from Ubuntu success alone. |
| **Windows** | **Planned** | No supported Windows agent/app today | Requires platform adapters and Windows-native service/security/capture implementation. Tracked by #33 and #34. |
| **Android companion app** | **Planned** | No Android app today | Planned first as a secure companion/controller for enrolled AngysGuard Linux/Windows devices. Tracked by #35. |
| **Android protected-device agent** | **Research** | Not available | Android security/privacy/API/store restrictions make this a separate feasibility question. Tracked by #36. |
| **macOS** | **Not targeted yet** | Not supported | Users may request it; a future target requires native capability/security analysis. |
| **iOS/iPadOS** | **Not targeted yet** | Not supported | Mobile OS restrictions make full-device protection different from desktop protection. Users may request a companion use case. |
| **BSD / ChromeOS / other OSes** | **Not targeted yet** | Not supported | Requests are welcome with a concrete use case/device/version. |

## Current Linux requirements

The current release baseline is Linux-first and requires:

- Python 3.11 or newer;
- a normal desktop/user session for desktop-oriented features;
- permissions/capabilities for the selected camera, microphone, input and screen backends;
- systemd user services for the documented service/autostart flow;
- a supported Bale/Telegram-style provider or local-only runtime mode when those features are selected.

The installer and docs are currently **Ubuntu-oriented**. A Linux distribution is not automatically considered officially supported just because the Python package installs there.

Run:

```bash
./run.sh setup
./run.sh doctor
```

and the target-device checks from `docs/TESTING.md` before relying on a hardware/session-dependent capability.

## X11 and Wayland

Both X11 and Wayland are part of the Linux target, but they do not expose identical capabilities.

- screen capture can depend on compositor-specific tools/portals and permission prompts;
- input monitoring backends differ and may require device permissions;
- desktop lock/session actions depend on the desktop/session stack;
- camera/microphone access depends on normal OS privacy/device permissions.

AngysGuard must not try to bypass compositor or OS privacy boundaries simply to make two sessions behave identically.

## Future desktop/mobile targets

### Linux desktop app — issue #32

The current Linux interface is primarily CLI/guided setup plus bot/chat surfaces. The planned Linux desktop app/tray should provide:

- setup/reconfiguration;
- arm/disarm/status/profiles;
- events/evidence viewer;
- provider and pairing management;
- service/autostart/doctor state;
- visible privacy/security status;
- guided errors and recovery without requiring terminal knowledge.

The existing CLI remains important for advanced, recovery and automation workflows.

### Windows desktop agent/app — issues #33 and #34

Windows is a planned first-class desktop target after platform-specific capabilities are separated behind narrow adapters. The project should use Windows-native APIs/services rather than emulate Linux commands or expose PowerShell as a remote-control shortcut.

Before Windows is declared supported, the project must define:

- supported Windows versions;
- installer/signing/update strategy;
- Windows service/startup model;
- secure credential storage;
- lock/session/notification/capture capabilities;
- real Windows target-device validation.

### Android companion app — issue #35

The initial Android target is a **companion/control app**, not a claim that the current Linux guard can simply run on Android.

The companion app is planned to support authenticated owners with:

- enrolled device list/status;
- arm/disarm/profile controls;
- event/evidence notifications and review;
- confirmation-gated safe actions;
- device pairing/revocation;
- managed/self-hosted connection status.

### Android protected-device mode — issue #36

Protecting the Android phone/tablet itself is a separate research track because Android imposes different background, capture, input, device-admin and privacy constraints. The project will not use stealth accessibility/keylogging patterns to force desktop behavior onto Android.

## Cross-platform architecture rule

Issue #33 defines the required platform-capability boundary before major ports.

The long-term model is:

```text
AngysGuard product/security policy
             |
             v
platform capability ports
      /          |          \
   Linux       Windows     future OS
 adapters      adapters     adapters
```

Platform adapters may differ, but owner authorization, security policy, bounded work, auditability and explicit feature capabilities remain consistent.

## Request support for another OS

Yes. Users can request **any operating system, Linux distribution, desktop environment, mobile platform or device class**.

Use the **Platform / OS request** GitHub issue form and include:

- OS/distribution and exact version;
- device type and architecture where relevant;
- desktop/session (for example GNOME/KDE/X11/Wayland);
- the AngysGuard capabilities you need;
- why the platform matters to your use case;
- whether you can test development builds on real hardware;
- any platform/security limitations you already know about.

A request is not an automatic support promise. New targets are prioritized by:

1. user demand and concrete security use cases;
2. feasibility without weakening AngysGuard security/privacy rules;
3. availability of native lock/service/capture/credential APIs;
4. maintainability and testing access;
5. contribution/testing capacity;
6. compatibility with the cross-platform architecture.

Issue #31 tracks the support/request process itself.

## Release rule

Every release that changes platform behavior must review this file and the root `README.md`.

A platform should not move from **Planned/Best effort** to **Supported** until:

- installation/update behavior is documented;
- required CI exists where practical;
- real target-device validation is recorded;
- security/privacy limitations are documented;
- unsupported capabilities fail clearly;
- the release manager and repository curator confirm README/support-matrix accuracy.
