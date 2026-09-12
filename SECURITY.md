# Security Policy

Laptop Guard handles security events, device controls, bot credentials, screenshots, recordings, and other potentially sensitive data. Security reports must be handled carefully.

## Supported code

Security fixes are prioritized for the current release line and the current `main` branch. Older versions may not receive fixes unless explicitly stated in release notes.

## Reporting a vulnerability

**Do not open a normal GitHub issue for a vulnerability.** Do not paste bot tokens, API tokens, chat IDs, private screenshots, recordings, logs containing personal data, or exploit details into public/shared issue threads.

Use GitHub's **private vulnerability reporting / Security Advisory** flow for this repository when it is available.

If private vulnerability reporting is unavailable, contact the repository owner through a private channel already established with the maintainer. Share only the minimum information needed to establish contact first; send sensitive reproduction details only through that private channel.

## What to include

- A short description of the vulnerability.
- Affected Laptop Guard version or commit.
- Affected platform/session (for example Ubuntu, X11, Wayland).
- Reproduction steps using dummy credentials and non-sensitive data where possible.
- Security impact and realistic attack conditions.
- Any proposed mitigation or patch, if available.

## Secrets and evidence

Assume a credential is compromised if it was committed to Git, pasted into an issue, included in logs shared with others, or otherwise exposed outside its intended secret store. Rotate exposed credentials instead of relying only on deletion from the latest commit.

Laptop Guard should never require real secrets in tests, examples, CI configuration, or bug reports.

## Scope priorities

Reports involving these areas are particularly important:

- Authentication/authorization of Telegram or Bale owner commands.
- Remote lock/unlock and stop authorization.
- Local control API authentication.
- Secret storage and file permissions.
- Command execution or application-launch boundaries.
- Screen/camera/audio capture privacy controls.
- Bypass of armed-state or intrusion protections.
- Leakage of private evidence, credentials, or device information.
