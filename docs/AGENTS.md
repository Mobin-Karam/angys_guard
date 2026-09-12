# Documentation instructions

These rules apply under `docs/` in addition to the root `AGENTS.md`.

- Document current behavior, not planned behavior, unless the section is clearly
  labeled roadmap/proposal.
- Keep commands copy-pasteable and prefer safe, non-destructive examples.
- Never include real credentials, chat IDs, private IPs, captured media, or
  secret-store contents in examples.
- Keep security/privacy limitations explicit, especially for camera, microphone,
  screen/input monitoring, remote unlock/control, and network providers.
- When code changes user-visible setup, CLI commands, dependencies, architecture,
  target-device requirements, or release behavior, update the relevant doc in
  the same change.
- Avoid duplicating long canonical instructions: link to the source-of-truth doc
  instead.
- Keep `ROADMAP.md` focused on planned work and `CHANGELOG.md` focused on shipped
  changes.
