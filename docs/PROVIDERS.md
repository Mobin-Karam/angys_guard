# Bale and Telegram provider behavior

Research baseline: **2026-09-19**.

Canonical external references:

- Telegram Bot API: https://core.telegram.org/bots/api
- Bale Bot API: https://docs.bale.ai/

Bale explicitly documents that its Bot API is based on Telegram's Bot API with
small changes. AngysGuard therefore shares one HTTP adapter for the common
contract while keeping provider differences explicit rather than assuming every
field/method is interchangeable.

## Active transport architecture

The active construction path is:

```text
setup / doctor / runtime
        |
        v
providers.build_provider()
        |
        v
HttpBotProvider + ProviderProfile
        |
        +-- Telegram profile
        +-- Bale profile
```

`RuntimeApi` remains the application-owned port consumed by the Guard.
`laptop_guard/bale_api.py` is now a **compatibility-only facade** over the same
adapter. New code must not add behavior there.

## Shared documented contract

Both providers currently document:

- HTTPS Bot API requests with the token in the URL path;
- GET/POST support;
- URL-encoded, JSON, and multipart request forms;
- JSON responses with `ok`, `result`, and error description/code fields;
- `getMe` for credential validation;
- long-poll `getUpdates` with `offset`, `limit`, and `timeout`;
- inline keyboards/callback queries;
- `sendMessage`, edit/delete message methods;
- photo/video/audio/voice/document upload methods;
- `getFile` plus provider-hosted file download URLs;
- a documented 20 MiB bot file-download ceiling.

AngysGuard uses the common parts through `HttpBotProvider`.

## Provider differences AngysGuard implements

| Behavior | Telegram | Bale | AngysGuard behavior |
|---|---|---|---|
| Default Bot API | `https://api.telegram.org` | `https://tapi.bale.ai` | Provider profile owns the default host. |
| Reply-to field | Current API uses `reply_parameters={"message_id": ...}` | Current docs use `reply_to_message_id` | Adapter encodes replies per provider. |
| Video streaming hint | `supports_streaming` is documented | Not documented in current Bale `sendVideo` parameter table | Sent only to Telegram. |
| `getUpdates` offset | Increasing ID; after a week of no updates Telegram may choose the next ID randomly | Bale documents IDs starting at zero and increasing | Guard treats IDs as opaque increasing values and always advances from received `update_id`. |
| Update retention | Updates are kept no longer than 24 hours | Last 2000 messages are kept for 24 hours | Guard does not assume old updates remain available. |
| Webhook ports | 443, 80, 88, 8443 | 443, 88 | AngysGuard currently uses long polling, so this is documented but not configured by runtime. |
| Media caption limits | Current Telegram media methods use 1024-character captions | Bale documents larger limits for several media methods (for example audio/document/video/voice) | Current AngysGuard captions are intentionally short; no provider-specific truncation is required today. |
| Voice formats | Telegram explicitly supports OGG/OPUS, MP3 and M4A for uploaded voice messages | Bale documents `sendVoice` and notes stricter URL behavior for OGG voice files | AngysGuard uploads local bounded recordings using multipart; generated voice paths remain provider-tested separately. |

Absence of a Bale parameter in the current documentation is **not** interpreted as
proof that Bale rejects it. The adapter simply avoids sending Telegram-only
optional hints that AngysGuard does not need for Bale.

## Retry and timeout policy

One adapter owns the policy:

- long-poll `getUpdates`, `getMe`, and `getFile` may retry a bounded transient
  network/429/5xx failure;
- retry delay is bounded; a returned `parameters.retry_after` is honored when
  present;
- side-effecting sends/uploads are **not blindly retried** after transport
  uncertainty because the provider may already have accepted the request;
- long-poll request timeout is the configured poll timeout plus a bounded grace
  window;
- ambient environment proxies are ignored; only the explicit owner-configured
  proxy is used.

## File downloads

The provider profile owns the documented 20 MiB download ceiling. A stricter
application-requested limit is respected. Partial downloads are deleted on
failure or limit overflow.

Download URLs remain provider-specific through the selected API base:

```text
Telegram: https://api.telegram.org/file/bot<token>/<file_path>
Bale:     https://tapi.bale.ai/file/bot<token>/<file_path>
```

Tokens must never be printed, logged, or placed in diagnostics.

## Capability confidence

| Capability | Telegram | Bale |
|---|---|---|
| Credential validation / `getMe` | CI contract-tested; live validation required for release claim | CI contract-tested; live validation required for release claim |
| Long polling / offset handling | CI contract-tested; live validation required | CI contract-tested; live validation required |
| Text + inline keyboard + callback | CI contract-tested; live validation required | CI contract-tested; live validation required |
| Photo/video/audio/voice/document multipart upload | CI contract-tested request shape; live media validation required | CI contract-tested request shape; live media validation required |
| File metadata/download | CI contract-tested URL/limit policy; live validation required | CI contract-tested URL/limit policy; live validation required |
| Proxy behavior | CI tested | CI tested |
| Webhooks | Not used by AngysGuard runtime | Not used by AngysGuard runtime |

CI tests prove AngysGuard's request construction and adapter boundaries. They do
not prove that a live Bale/Telegram service accepted a request on a particular
release day. Release claims still require the live-provider checklist from
`docs/RELEASE_CHECKLIST.md`.
