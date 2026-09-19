# Platform Identity Service

Implements the first Platform v2 identity boundary.

## Current storage

SQLite is used initially.

## Models

### users

- id
- username
- password_hash
- created_at

### users_devices

- user_id
- device_id
- os
- hostname
- permissions
- status
- last_seen

### sessions

- token
- user_id
- created_at

## Flow

```text
App install
   |
Create account
   |
Register device
   |
Receive session token
   |
Use account-scoped platform services
```

Password storage uses PBKDF2-HMAC-SHA256 with per-password salts.

Future migrations can replace SQLite without changing the identity service boundary.
