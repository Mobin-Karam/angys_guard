Safely remove this feature: <feature>

Do not start by deleting its main file. First build a dependency/removal map from current source and docs:
- registrations/routes/entry points;
- callers/imports/exports;
- config/defaults/migrations/secrets;
- state/storage/events/data;
- setup/doctor/service/CLI/UI references;
- tests/fixtures/assets;
- docs/examples/changelog/dependencies;
- security/privacy assumptions that depended on it.

Then remove the feature in the smallest safe sequence, preserving migration/compatibility behavior where required. Delete dead code only after proving it is no longer referenced. Add/update tests so absence is intentional and old config/data fails or migrates safely. Run full applicable checks and document any breaking change.