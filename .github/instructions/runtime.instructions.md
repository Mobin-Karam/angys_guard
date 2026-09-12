---
applyTo: "laptop_guard/**/*.py"
---

Follow `AGENTS.md`, `laptop_guard/AGENTS.md`, and `docs/GRAPHIFY_NAVIGATION.md`.
Before broad runtime discovery, use Graphify query/explain/path to locate the
owning symbol, callers, dependencies, tests, config/state/storage, and side-effect
boundaries. Open only the minimal current source returned by that navigation.

Preserve owner authorization/privacy boundaries, explicit feature registration,
`RuntimeApi`, shared runtime state, bounded capture/process/network behavior, and
secret handling. Prefer focused services/ports over making `LaptopGuard` larger.
Add focused success/failure/denial tests and refresh Graphify after material
relationship changes when available.
