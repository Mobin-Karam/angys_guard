# Issue intake and triage

AngysGuard uses focused GitHub Issue Forms so reporters provide useful, sanitized information without needing to understand the repository architecture.

## Choose the right form

| Form | Use it for | Default classification |
| --- | --- | --- |
| Bug / regression | Reproducible incorrect runtime behavior | `type:bug` |
| Installation / setup / doctor problem | Installation, first run, setup, doctor, service onboarding | `type:bug`, `area:setup` |
| Bale / Telegram / bot-control problem | Provider, pairing, command/reply/delivery behavior | `type:bug`, `area:provider` |
| Feature request | New user-facing capability or compatible improvement | `type:feature` |
| UI / UX improvement | Usability, accessibility, localization, RTL, workflow improvements | `type:feature`, `area:ux` |
| Platform / OS request | Demand for another OS, distro, desktop environment, mobile platform, device class | `type:platform-request`, `status:needs-design` |
| Architecture proposal | Cross-module boundaries, storage, provider/platform abstraction, lifecycle design | `type:architecture`, `status:needs-design` |
| Documentation problem / improvement | Missing, incorrect, outdated, confusing docs | `type:docs` |
| Release / packaging / upgrade problem | Tags, release artifacts, packaging, migration, support/release metadata | `type:release`, `area:release` |
| Question / help | Normal use/configuration help that is not clearly a defect | no forced classification |
| Security vulnerability | **Do not open a public issue**; use the private security-reporting path | private report |

## Triage workflow

1. **Protect sensitive information first.** If a report contains credentials, pairing material, OS passwords, private keys, private evidence/media, or exploit details, avoid quoting/repeating it and move the conversation to the appropriate private security path when necessary.
2. **Classify the report.** Confirm `type:*`, `area:*`, priority and milestone only after understanding the issue. A form's default labels are a starting point, not a severity decision.
3. **Use Graphify first for repository discovery.** Follow `docs/GRAPHIFY_NAVIGATION.md` to locate owning modules, callers, dependencies, tests and docs before broad source reads. Current source/tests remain authoritative.
4. **Reproduce before fixing when practical.** Follow `docs/BUG_TRIAGE_AND_FIXING.md` for defects and `docs/FEATURE_LIFECYCLE.md` for feature work.
5. **Separate current from future support.** Windows, Android, managed service and requested platforms stay Planned/Research/Requested until implementation plus target-device validation justifies a support-state change.
6. **Keep security boundaries.** No issue should become a reason to add generic remote shell execution, keylogging, stealth capture, remote OS-password collection, or authorization bypasses.
7. **Make acceptance measurable.** Convert vague requests into observable outcomes, target platforms/surfaces, validation steps and compatibility constraints.
8. **Use milestones for delivery targets.** Labels classify work; milestones group planned delivery; the GitHub Project organizes workflow state.

## Priority guidance

- **P0** — active security/release blocker, credential exposure, data-loss/security-control failure, or inability to reach a safe usable state on the supported baseline.
- **P1** — high-value next work, common serious regression, core roadmap dependency, or significant usability/reliability problem.
- **P2** — planned improvement with a workaround or lower urgency.
- **P3** — cleanup, research, opportunistic enhancement, or low-impact request.

Priority is assigned by maintainers after triage; reporters should describe impact rather than choose severity themselves.

## Duplicate and related issues

Prefer one measurable outcome per issue. Link dependencies and duplicates rather than combining unrelated failures. For a large initiative, keep a project/tracking issue with smaller implementation issues beneath it.

## Security reporting

Public issues are not suitable for vulnerability details or secrets. Follow `SECURITY.md` and the repository Security tab for private reporting. Ordinary hardening ideas that do not disclose a vulnerability may use Feature request or Architecture proposal.

## Maintaining the forms

Issue forms live under `.github/ISSUE_TEMPLATE/`.

When adding or changing a form:

- use AngysGuard product wording while keeping compatibility identifiers only where relevant;
- use labels from `.github/repository-management/labels.json`;
- avoid asking reporters for secrets or private evidence;
- keep fields focused on triage/reproduction/acceptance, not implementation trivia;
- update this guide when the chooser taxonomy changes;
- keep `config.yml` links on the canonical repository URL;
- run the normal test suite so `tests/test_issue_templates.py` can catch structural drift.
