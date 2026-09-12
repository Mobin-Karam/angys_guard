Perform a security review of: <change/component>

Use the repository's threat/security model plus current source. Do not read or print real secrets/private data.

Inspect relevant boundaries:
- identity/authentication/authorization;
- privilege and remote-control actions;
- input validation/injection/path handling;
- secrets/config/logging;
- network/API exposure;
- filesystem/database permissions;
- subprocess/process/OS actions;
- capture/privacy/data retention;
- replay/race/concurrency/resource abuse;
- dependency/supply-chain impact.

Return vulnerabilities first, ranked by severity and exploitability, with concrete trigger/impact/remediation/test. Then list optional hardening. If no blocking issue is found, state which boundaries were checked.