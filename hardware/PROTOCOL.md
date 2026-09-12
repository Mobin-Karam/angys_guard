# Guard Agent Protocol (future Pi / ESP nodes)

The v4 laptop app is structured so external devices can later publish the same event model.

Recommended transport:

- Raspberry Pi: HTTPS or MQTT over TLS.
- ESP32-S3: MQTT over TLS or signed HTTPS events.
- Do **not** store Telegram/Bale bot tokens on every ESP node. Nodes should authenticate only to a Guard Hub.

Example sensor event:

```json
{
  "protocol": 1,
  "device_id": "front-door-01",
  "event": "person_detected",
  "severity": "high",
  "timestamp": "2026-09-11T21:00:00+03:30",
  "data": {
    "confidence": 0.91,
    "snapshot_available": true
  }
}
```

Suggested node endpoints/capabilities:

```text
GET  /health
GET  /snapshot
POST /record/video {"seconds": 10}
POST /record/audio {"seconds": 30}
POST /indicator {"mode": "on|off|follow"}
```

A node should have a per-device secret/certificate. The hub owns bot credentials and user authorization.
