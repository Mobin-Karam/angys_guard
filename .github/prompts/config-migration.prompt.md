Change configuration or persisted state safely: <change>

Inspect current schema/defaults/load/save paths, migrations, secret handling, file/database permissions, tests, and rollback behavior before editing.

Requirements:
- new installs get safe defaults;
- existing installs migrate deterministically;
- missing/invalid/old values fail safely or recover predictably;
- secrets stay separate/redacted as designed;
- writes remain atomic/transactional where applicable;
- repeated migration is safe;
- downgrade/rollback impact is documented if relevant.

Add migration and round-trip tests using temporary/fake data, then run applicable checks.