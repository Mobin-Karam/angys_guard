# @angysguard/linux-agent

Linux npm installer and terminal command for AngysGuard. Installation creates an
isolated package-owned Python virtual environment, installs the bundled runtime,
and exposes `angysguard` from any terminal for that Linux account.

```bash
npm install -g @angysguard/linux-agent
angysguard
```

If the optional AngysGuard Linux dashboard (`.deb`) is installed too, the first
interactive launch offers **Open dashboard** or **Continue in terminal**. You
can choose explicitly with `angysguard app` or `angysguard terminal`. The npm
package does not download or install the desktop application itself.

Requirements: Linux, Node.js 20+, Python 3.11+ with `venv` support, and network
access to download Python dependencies. The installer never invokes `sudo` or a
shell. Optional hardware/session dependencies remain subject to `angysguard doctor`.

If installation was interrupted after resolving Python/network prerequisites:

```bash
npm rebuild @angysguard/linux-agent
```

This is an experimental Linux launcher, not a separate security product or a
claim of a supported desktop/Windows release. Consult the repository's
[npm package guide](../../docs/NPM_PACKAGES.md) for release verification and
maintainer publishing guidance.
