# @angysguard/linux-agent

Linux npm installer and terminal command for AngysGuard. Installation creates an
isolated package-owned Python virtual environment, installs the bundled runtime,
and exposes `angysguard`.

```bash
npm install -g @angysguard/linux-agent
angysguard
```

Requirements: Linux, Node.js 20+, Python 3.11+ with `venv` support, and network
access to download Python dependencies. The installer never invokes `sudo` or a
shell. Optional hardware/session dependencies remain subject to `angysguard doctor`.

If installation was interrupted after resolving Python/network prerequisites:

```bash
npm rebuild @angysguard/linux-agent
```

The package is ready for publication but is not published until the AngysGuard
npm organization configures a trusted publisher and releases it. Consult the
repository's [npm package guide](../../docs/NPM_PACKAGES.md) before publishing.
