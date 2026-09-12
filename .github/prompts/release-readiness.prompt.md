Assess whether the current version/commit is ready for release.

Use repository release policy, roadmap/issues, changelog/version metadata, CI/status checks, security findings, dependency state, migrations, docs, packaging/install flow, and required manual target-environment checks.

Return three sections:
- READY: evidence-backed completed gates;
- BLOCKED: specific release blockers and exact next action;
- MANUAL VALIDATION: checks automation cannot prove.

Do not create tags/releases/publish/deploy unless explicitly requested. Do not mark ready while known critical security/data-loss blockers or required failing checks remain.