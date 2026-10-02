# NPM terminal packages (experimental)

AngysGuard's primary runtime is Python and its current release path is
Linux-first. The source tree includes two small npm packages so users can have a
consistent terminal command. Npm installs the bundled Python runtime into the
Linux package's own virtual environment; it is **not** used to silently gain
privileged native capabilities.

## Linux launcher

`packages/linux-agent` provides `@angysguard/linux-agent`. Its `postinstall`
creates a package-owned virtual environment, then installs the bundled
`laptop-guard` Python source using argument-list process execution without a
shell:

```bash
npm install -g @angysguard/linux-agent
angysguard
```

It requires Linux, Node.js 20+, Python 3.11+ with `venv`, and access to PyPI for
Python dependencies. It never calls `sudo`; optional Linux packages and
hardware/session readiness are reported by `angysguard doctor`.

When the optional AngysGuard dashboard `.deb` is already installed, an
interactive `angysguard` launch offers **Open dashboard** or **Continue in
terminal**. `angysguard app` opens the installed dashboard explicitly and
`angysguard terminal` always uses the terminal flow. The npm package does not
bundle the desktop application and does not silently install a system package.

## Windows foundation

`packages/windows-agent` provides a deliberately narrow terminal foundation:
local `status`, `doctor`, and a fixed local `lock` operation. It is not a Windows
protection agent or a supported Windows release. See
[PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md) for the current support boundary.

## Publishing gate

The Linux and Windows wrappers are released together using the same npm version.
From the repository root, run the deterministic package check first, then the
interactive npm release command:

```bash
npm run release:npm:check
npm run release:npm:publish
```

`release:npm:publish` uses `npm publish --access public --provenance=false` for
a maintainer's local 2FA session. It never reads an npm token from the project.
The GitHub `npm-publish.yml` workflow remains the preferred trusted-publishing
path when its npm environment is configured.

Before publishing either package to npm, maintainers must:

1. validate the package tarball and Node compatibility;
2. use an organization-owned npm account with MFA and provenance enabled;
3. verify the exact package name and version are available/owned;
4. perform target-device tests on the relevant operating system;
5. update the changelog, support matrix, and release notes truthfully.

The repository includes npm packaging/install CI for Linux and Windows, plus a
protected `npm-production` GitHub Actions environment. The one-time bootstrap
release must be published manually by an organization owner using npm 2FA. Then
configure npm trusted publishing for each package with GitHub repository
`Mobin-Karam/angys_guard`, workflow `npm-publish.yml`, and environment
`npm-production`; later version tags publish with OIDC provenance and no stored
npm token. Until the bootstrap release is made, the scoped package names are not
available from the public npm registry.
