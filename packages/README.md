# AngysGuard terminal packages

These packages make a familiar npm terminal entry point available without
turning npm into a hidden installer for security-sensitive native components.

| Package | Platform | Current purpose | Support state |
| --- | --- | --- | --- |
| `@angysguard/linux-agent` | Linux | Starts the installed Python `laptop-guard` runtime | Experimental launcher; Linux runtime remains Linux-first |
| `@angysguard/windows-agent` | Windows | Fixed local `status`, `doctor`, and `lock` commands | Experimental foundation; no supported Windows protection release |

The packages have a shared `1.0.2` wrapper release line. The Linux package
installs the bundled Linux runtime and can open the separately installed local
dashboard; the Windows wrapper remains experimental even when its npm package
version is `1.0.2`.

Maintainers can validate and publish both package directories together from the
repository root:

```bash
npm run release:npm:check
npm run release:npm:publish
```

The publish command uses npm's interactive 2FA flow and deliberately does not
store an npm token in the repository. Before publication, target-device checks
and the release checklist still apply.

The wrappers deliberately do not add remote shell execution, secret handling,
hidden capture, generic command dispatch, or arbitrary filesystem access.
