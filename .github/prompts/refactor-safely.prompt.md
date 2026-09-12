Refactor this code safely without changing intended external behavior: <scope/goal>

First document the current contract using existing tests/source. Identify callers, side effects, state, error semantics, and security/privacy gates.

Refactor incrementally:
- preserve public behavior and compatibility;
- avoid mixing feature changes with structural cleanup;
- reduce duplication/complexity through existing abstractions;
- keep each step testable/reviewable;
- add characterization tests before risky movement when coverage is weak.

Run focused and applicable full tests, then review the diff for accidental semantic changes.