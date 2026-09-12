Simplify this code while preserving behavior: <scope>

Inspect callers/tests/contracts first. Prefer deleting unnecessary indirection, duplication, branches, and state over introducing new abstractions.

Do not optimize for fewer lines at the cost of readability, testability, security, or error handling. Avoid broad rewrites.

Return the simplest safe patch, explain what complexity was removed, and run tests proving behavior remained stable.