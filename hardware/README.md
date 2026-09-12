# Hardware targets

## Current target: Linux laptop

The complete v4 application runs on Linux and uses the laptop camera, microphone, input devices, speaker, power state and bot connection.

## Recommended next target: Raspberry Pi

A Pi Zero 2 W / Pi 4 / Pi 5 can run a trimmed Python agent with the same event schema. The Pi is suitable when you need camera + microphone + local storage + network + richer vision processing.

## ESP32-S3 target

Use ESP32-S3 as a sensor node rather than trying to run the Linux Python project directly. Typical node capabilities:

- camera snapshot / simple local inference
- microphone sampling
- PIR/door/accelerometer sensors
- device health and tamper events
- MQTT/HTTPS communication to a trusted hub

Bot credentials should remain at the hub; each ESP node should receive only its own device credential.

See `PROTOCOL.md`.
