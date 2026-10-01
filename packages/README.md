# AngysGuard terminal packages

These packages make a familiar npm terminal entry point available without
turning npm into a hidden installer for security-sensitive native components.

| Package | Platform | Current purpose | Support state |
| --- | --- | --- | --- |
| `@angysguard/linux-agent` | Linux | Starts the installed Python `laptop-guard` runtime | Experimental launcher; Linux runtime remains Linux-first |
| `@angysguard/windows-agent` | Windows | Fixed local `status`, `doctor`, and `lock` commands | Experimental foundation; no supported Windows protection release |

Neither package has been published to npm yet. The package names, versioning,
provenance/signing, npm publishing workflow, and platform target-device checks
must be completed before users should install by package name.

The wrappers deliberately do not add remote shell execution, secret handling,
hidden capture, generic command dispatch, or arbitrary filesystem access.
