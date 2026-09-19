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

The v12.0 Linux support promise is **configured-feature based**: an environment is
release-ready only when `./run.sh doctor` reports `READY` for the features
enabled on that machine and the relevant target-device checks pass.

| Platform | Project state | v12.0 release position | Important limits |
|---|---|---|---|
| **Ubuntu Desktop 24.04 LTS — amd64** | **Primary qualification target** | Intended Supported environment for v12.0 after the [release checklist](RELEASE_CHECKLIST.md) is recorded | GNOME X11 and GNOME Wayland are both qualified separately; not every screen/input backend is available in both sessions. |
| **Ubuntu Desktop 26.04 LTS — amd64** | **Best effort / candidate** | Not v12.0 release-qualified yet | Ubuntu 26.04 uses Python 3.14 by default, while the current release CI/support matrix is Python 3.11–3.13. Qualification requires an explicitly supported Python/toolchain and the full target-device checklist. |
| **Ubuntu Desktop 22.04 LTS — amd64** | **Best effort** | Not v12.0 release-qualified | Its default Python 3.10 is below AngysGuard's Python 3.11 minimum; a separately installed supported Python does not by itself make the OS release-qualified. |
| **Other Linux distributions / Ubuntu flavors** | **Best effort** | Not automatically supported | Installer packages, service behavior, desktop commands and capture backends may differ. Ubuntu success does not transfer automatically to another distro/flavor. |
| **Windows** | **Planned** | No supported release today | Requires platform adapters and Windows-native service/security/capture implementation. Tracked by #33 and #34. |
| **Android companion app** | **Planned** | No app today | Planned first as a secure companion/controller for enrolled AngysGuard Linux/Windows devices. Tracked by #35. |
| **Android protected-device agent** | **Research** | Not available | Android security/privacy/API/store restrictions make this a separate feasibility question. Tracked by #36. |
| **macOS / iOS / iPadOS / BSD / ChromeOS / other OSes** | **Not targeted yet** | Not supported | Users may request support with a concrete use case/device/version. |

Ubuntu 24.04, 26.04 and 22.04 are maintained LTS releases according to Canonical's
[Ubuntu release cycle](https://ubuntu.com/about/release-cycle). AngysGuard's own
support state is narrower: Canonical support for Ubuntu does not imply AngysGuard
release qualification.

## Current Linux requirements

The current release baseline is Linux-first. For v12.0 release qualification:

- **Python 3.11, 3.12 and 3.13** are the supported Python versions because all
  three run in the required CI matrix. The installer/package metadata may accept a
  newer Python, but newer versions are best effort until added to CI and target
  validation.
- **amd64 / x86_64** is the v12.0 target-device architecture. Other architectures
  are not release-qualified merely because upstream dependencies publish wheels.
- a normal graphical desktop/user session is required for desktop-oriented features;
- permissions/capabilities are required for each enabled camera, microphone, input
  and screen backend;
- systemd user services are required for the documented service/autostart path;
- Bale/Telegram-style provider access requires network connectivity, while
  local-only mode must remain usable without a provider.

The installer and docs are currently **Ubuntu-oriented**. A Linux distribution is
not automatically considered officially supported just because the Python package
installs there. The complete clean-machine qualification procedure is
[RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

Run:

```bash
./run.sh setup
./run.sh doctor
```

and the target-device checks from `docs/TESTING.md` before relying on a hardware/session-dependent capability.

## GNOME X11 and Wayland support

Both **GNOME X11** and **GNOME Wayland** are v12.0 session qualification targets,
but capability support is not identical.

| Capability | GNOME X11 | GNOME Wayland |
|---|---|---|
| Guard runtime / setup / doctor | Targeted | Targeted |
| Camera / microphone | Normal Linux device/privacy permissions | Normal Linux device/privacy permissions |
| Global input activity | evdev preferred; pynput may also work | **evdev preferred/expected**; pynput/global compositor hooks must not be assumed |
| Screenshot | `gnome-screenshot` or ImageMagick backend when available | `gnome-screenshot` when the session permits it; other compositor-specific tools may differ |
| Screen recording | Current supported path is `ffmpeg` + `x11grab` | Only supported when the compositor works with current `wf-recorder` path; this is **not a generic GNOME Wayland guarantee** |
| Desktop lock | Requires a working supported session lock backend | Requires a working supported session lock backend |
| systemd user service | Starts after graphical login | Starts after graphical login |

Input monitoring intentionally records activity classes rather than key identities.
The runtime prefers readable **evdev** devices because that path is more reliable
under Wayland; evdev requires appropriate device permissions. If evdev is
unavailable, **pynput** is only a fallback where the actual session supports it.

For screen capture, a successful `wf-recorder` test on a compatible Wayland
compositor must not be generalized to GNOME or every Wayland compositor. If the
configured screen-video feature has no supported backend, disable it through
reconfiguration and require Doctor to return `READY` for the remaining claimed
feature set.

AngysGuard must not bypass compositor or OS privacy boundaries simply to make X11
and Wayland appear identical. Record both session results separately using the
[release checklist](RELEASE_CHECKLIST.md).

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

Every release must follow [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md). Every
release that changes platform behavior must also review this file and the root
`README.md`.

A platform should not move from **Planned/Best effort** to **Supported** until:

- installation/update behavior is documented;
- required CI exists where practical;
- real target-device validation is recorded;
- security/privacy limitations are documented;
- unsupported capabilities fail clearly;
- the release manager and repository curator confirm README/support-matrix accuracy.
