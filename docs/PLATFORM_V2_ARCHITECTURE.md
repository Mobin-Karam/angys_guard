# AngysGuard Platform v2 Architecture Foundation

Tracking issue: #62

## Goal

Transform AngysGuard from a single-machine guard application into a platform architecture supporting:

- Linux client
- Windows client
- Android companion/client
- future iOS client
- centralized accounts
- remote bot gateway
- managed configuration

## Target topology

```text
Linux / Windows / Android / iOS Apps
              |
              v
      AngysGuard Platform Server
              |
       +------+------+
       |             |
       v             v
 Bot Gateway   Configuration Service
       |
  +----+----+
  |         |
Telegram   Bale
@angysguardbot
```

## User lifecycle

1. User installs AngysGuard client.
2. User creates a platform account.
3. Server stores the account profile.
4. Client registers a device identity.
5. Server assigns configuration and permissions.
6. Client maintains an authenticated session.
7. Bot commands are routed only to authorized devices.

## Core platform boundaries

### Identity service

Owns:

- accounts
- device identities
- authentication sessions
- OS/platform permissions

Tracked by #63.

### Remote Bot Gateway

Owns:

- Telegram connection
- Bale connection
- account routing
- command delivery
- bot event ingestion

Tracked by #64.

### Unified Client Protocol

Owns:

- client/server messages
- authentication handshake
- heartbeat
- configuration sync
- command execution
- event streaming

Tracked by #65.

### Configuration Engine

Owns:

- server-managed profiles
- versioned configuration
- device overrides
- rollback support

Tracked by #66.

## Data ownership

```text
Account
 |
 +-- Devices
 |      |
 |      +-- OS identity
 |      +-- capabilities
 |      +-- heartbeat
 |
 +-- Configuration Profile
 |
 +-- Bot Routing Identity
```

## Security requirements

- Bot tokens remain server-side.
- Client devices receive scoped credentials only.
- OS passwords are never transmitted to the platform server.
- Device authorization is explicit and revocable.
- Commands are authorized against account/device permissions.

## Migration strategy

Platform v2 is introduced incrementally:

1. Add account/device identity.
2. Add remote gateway.
3. Move clients behind a common protocol.
4. Enable server-managed configuration.
5. Migrate existing local configuration gradually.

Existing local functionality remains supported during migration.
