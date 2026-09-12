Review this change for backward compatibility: <task or diff>

Inspect current public behavior, config/state formats, persisted data, APIs/CLI, integrations, defaults, and tests.

Check for:
- renamed/removed commands, fields, routes, files, or settings;
- changed defaults or semantics;
- config/data/schema migration needs;
- old-client/old-config behavior;
- rollback/downgrade behavior;
- changed error/exit codes or output contracts;
- package/dependency/platform compatibility.

Return concrete breakages first, then migration/compatibility recommendations and tests needed. Do not invent compatibility guarantees not present in the repo.