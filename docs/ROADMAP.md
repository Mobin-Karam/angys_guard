# Laptop Guard Roadmap

This roadmap turns the current Laptop Guard state into a sequence of releases aimed at one goal: **a non-technical user can install, configure, diagnose, and operate Laptop Guard without editing source files or memorizing commands.**

## Current baseline

The repository already includes:

- guided setup (`./run.sh setup`)
- runtime configuration validation
- `doctor`
- arm/disarm/status commands
- hardware/provider tests
- events and health commands
- systemd user-service management
- autostart management
- Telegram/Bale/local provider configuration

The next work should therefore focus on hardening, recovery UX, automated testing, and release quality rather than rebuilding those features.

---

# Milestone: v11.2 — Setup & Security Hardening

**Goal:** A clean machine can be brought to a safe, diagnosable Laptop Guard installation without editing configuration files manually.

## Exit criteria

- No real secrets/config files are tracked by Git.
- Installation failures give exact recovery instructions.
- `doctor` tells the user what is wrong and how to fix it.
- Setup + doctor work on the supported Ubuntu/Python baseline.

## Issues

- [ ] #1 — Remove tracked `.env` and rotate any exposed credentials — **P0**
- [ ] #2 — Make installation self-diagnosing and resilient on Ubuntu — **P0**
- [ ] #3 — Expand doctor into actionable readiness checks — **P0**

## Recommended order

1. #1 security cleanup
2. #2 installer/bootstrap
3. #3 doctor/readiness

---

# Milestone: v11.3 — Non-Technical UX

**Goal:** A normal user can operate the product by selecting actions and following prompts instead of remembering commands.

## Exit criteria

- Common actions are available through a guided menu.
- Interrupted setup resumes intelligently.
- Users can reconfigure one section without repeating setup.
- Expected failures show recovery actions instead of raw tracebacks.

## Issues

- [ ] #4 — Add a simple guided main menu for non-technical users — **P1**
- [ ] #5 — Make setup resumable by step instead of restarting the whole wizard — **P1**
- [ ] #6 — Replace raw runtime failures with guided recovery paths — **P1**

## Recommended order

1. #5 resumable/reconfigure model
2. #6 recovery/error UX
3. #4 guided main menu

---

# Milestone: v12.0 — Production-Ready Release

**Goal:** Make Laptop Guard reproducible, testable, supportable, and safe to release to other users.

## Exit criteria

- Core setup/config/security flows have automated regression coverage.
- CI runs on supported Python versions.
- Supported OS/Python/session combinations are documented.
- A clean-machine release checklist passes.
- Diagnostic/bug-report instructions do not leak credentials or captured evidence.

## Issues

- [ ] #7 — Add automated first-run and regression test coverage — **P1**
- [ ] #8 — Define supported platforms and release checklist — **P2**

## Recommended order

1. #7 automated coverage and CI
2. #8 release/support matrix
3. perform clean-machine release validation
4. tag v12.0 only after all release criteria pass

---

# Work board

## Now

- #1 Security cleanup
- #2 Installer hardening
- #3 Doctor/readiness improvements

## Next

- #5 Resumable setup + reconfigure
- #6 Guided recovery paths
- #4 Guided main menu

## Later / Release

- #7 Automated regression coverage + CI
- #8 Supported-platform matrix + release checklist

---

# Definition of done for every issue

An issue is not complete only because the happy path works. Before closing it:

- relevant automated/manual tests pass
- no tokens/secrets are logged or committed
- failure states have user-readable messages
- documentation is updated when behavior changes
- existing CLI commands remain compatible unless the change is explicitly documented
- the issue acceptance checklist is complete

---

# Product direction

Laptop Guard should remain focused on laptop security, monitoring, alerts, evidence capture, owner communication, and safe remote/local controls. Git/GitHub project management belongs in the separate `gitbr` product rather than being added to Laptop Guard.
