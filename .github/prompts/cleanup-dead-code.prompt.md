Identify and safely remove dead code in: <scope>

Prove code is unused before deleting it by checking imports/callers/registrations/config/migrations/tests/docs/assets/build/release/runtime discovery and reflection/plugin mechanisms.

Distinguish truly dead code from compatibility, optional-platform, migration, fallback, or dynamically referenced code.

Remove only proven-dead paths, update references/docs/tests, and run applicable checks. Report any uncertain candidates separately instead of deleting them.