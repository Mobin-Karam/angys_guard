Verify this change comprehensively: <change/diff>

Read repository testing instructions and infer the smallest relevant test set from changed behavior. Run focused checks first, then broader required checks.

Validate:
- acceptance criteria;
- regression tests;
- compile/type/lint/static checks used by the repo;
- config/migration behavior;
- security/privacy-sensitive paths;
- docs/link/build/package checks when affected;
- target-device/manual checks that automation cannot prove.

Do not claim hardware/provider/platform behavior passed unless it was actually exercised. Return passed, failed, skipped/manual, and next action.