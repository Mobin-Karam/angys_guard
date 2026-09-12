---
applyTo: "laptop_guard/**/*.py"
---

Follow root `AGENTS.md` and `laptop_guard/AGENTS.md`.

Preserve owner authorization/privacy boundaries and existing `RuntimeApi`,
`FeatureManager`, and `GuardRuntimeState` abstractions. New bot behavior should be
a focused explicitly registered feature. Never add arbitrary remote shell/exec,
hidden capture, credential logging, or permissive secret handling. Add focused
success/failure/authorization tests for changed behavior and keep optional native
hardware dependencies lazy/degradable.
