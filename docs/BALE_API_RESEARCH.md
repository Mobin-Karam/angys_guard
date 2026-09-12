# Bale Bot API research for Laptop Guard v9

Research date: 2026-09-12

The official Bale Bot API uses HTTPS requests at `https://tapi.bale.ai/bot<token>/METHOD_NAME` and supports both long polling (`getUpdates`) and webhooks. Laptop Guard keeps long polling so the local laptop does not need a public inbound HTTP endpoint.

Capabilities used by v8:

- `getUpdates`: receive owner text, voice/audio, and callback interactions.
- `sendMessage`: status, alerts and command results.
- `InlineKeyboardMarkup` + `answerCallbackQuery`: owner-only dashboard controls.
- `editMessageText`: update an existing menu message to reduce chat clutter.
- `sendPhoto`: camera and screenshot evidence.
- `sendVideo`: camera and screen recordings.
- `sendVoice` / `sendAudio`: short intercom chunks and audio files.
- `getFile`: retrieve an owner voice/audio message for local playback.
- `sendChatAction`: show upload/record states during longer operations.
- Bale also documents media groups, location/contact messages, message deletion/editing and chat administration methods; v8 deliberately exposes only controls that make sense for a local guard agent.

## Audio limitation

The Bot API transfers voice/audio messages as files; it is not a raw WebRTC/RTP call transport. Laptop Guard therefore implements a **visible near-live intercom**:

1. laptop records a short OGG/Opus chunk;
2. chunk is sent with `sendVoice`;
3. owner voice messages are received through `getUpdates`;
4. file metadata is retrieved with `getFile`;
5. the file is played through the laptop speaker.

A future low-latency full-duplex call should use a dedicated media protocol such as WebRTC and keep Bale only for signaling/control.

## Deliberately excluded

Laptop Guard does not expose arbitrary shell commands through Bale. Bot controls map to a fixed allowlist such as lock, optional unlock, camera, screen capture, audio, chat, system information and confirmed power actions.
