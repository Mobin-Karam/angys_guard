# Platform capability contract

Issue #33 accepts the capability-first boundary required before Windows or
Android product work. Linux is the reference implementation. A platform is not
supported merely because one adapter has code; every claimed capability needs
target-device validation.

## Application-owned ports

| Port | Purpose | Unsafe fallback prohibited |
| --- | --- | --- |
| `SystemActions` | lock, suspend, reboot, shutdown | shell/PowerShell text from a bot message |
| `ServiceLifecycle` | install, start, stop, autostart | broad administrator command runner |
| `CredentialStore` | device credentials and local secrets | plain configuration/environment storage |
| `OwnerNotification` | user-visible local status/errors | silent failure for security-critical actions |
| `InputActivity` | privacy-preserving activity signals | key identity/keylogging |
| `Capture` | opted-in camera/screen/audio | hidden/unbounded collection |
| `SessionCapabilities` | detect safe available features | pretend unsupported actions succeeded |

Policy/use cases choose *whether* an action is permitted. An adapter chooses
*how* its platform performs it and returns a stable unsupported/denied/error
result. No port accepts a command line, script, path or opaque provider payload.

## Initial platform matrix

| Capability | Linux reference | Windows 10/11 target | Android companion |
| --- | --- | --- | --- |
| Fixed lock/suspend/reboot/shutdown | Existing native command adapters; target validation required | Existing fixed Windows calls need native-service/session validation | No protected-device promise |
| Service/autostart | systemd user service | Windows service/task model required | App lifecycle only |
| Credential store | current protected local files; keyring migration planned | DPAPI/Credential Manager required | OS keystore required |
| Notifications | desktop/provider paths | Windows notification API required | companion notifications only |
| Input/capture | capability dependent, explicit privacy rules | separate native design required | research only for protected device |

## Migration order

1. Introduce typed capability protocols and stable result types around current
   Linux adapters without changing behavior.
2. Select adapters only in a composition root; do not add scattered platform
   conditionals to policy or bot handlers.
3. Implement Windows adapters with Windows-native APIs, installer/signing and
   target-device tests before stating support.
4. Keep Android as a companion target until a separate protected-device design
   meets privacy and lifecycle gates.

## Validation gates

- Unit tests cover unsupported/denied capability results.
- Linux, Windows, and Android capability claims each have real-device evidence.
- Security review covers privileged actions and credential lifecycle.
- UI/doctor exposes unavailable capabilities instead of hiding them.
