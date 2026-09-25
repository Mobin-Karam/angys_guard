"""Register the managed-test Telegram webhook without printing its token.

Run this only on the server after its HTTPS proxy is serving api.mahakaram.ir.
The token and secret remain environment-only deployment inputs.
"""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise SystemExit(f"{name} must be set in the server environment")
    return value


def main() -> int:
    token = required("ANGYSGUARD_TELEGRAM_BOT_TOKEN")
    secret = required("ANGYSGUARD_TELEGRAM_WEBHOOK_SECRET")
    base_url = os.environ.get("ANGYSGUARD_PUBLIC_URL", "https://api.mahakaram.ir").rstrip("/")
    body = json.dumps(
        {
            "url": f"{base_url}/v1/bots/telegram/updates",
            "secret_token": secret,
            "allowed_updates": ["message"],
            "drop_pending_updates": True,
        }
    ).encode("utf-8")
    request = Request(
        f"https://api.telegram.org/bot{token}/setWebhook",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read())
    except (HTTPError, URLError, json.JSONDecodeError) as error:
        print(f"Webhook setup failed: {error}", file=sys.stderr)
        return 1
    if not payload.get("ok"):
        print("Telegram rejected webhook setup; inspect server-side configuration.", file=sys.stderr)
        return 1
    print(f"Telegram webhook registered for {base_url}/v1/bots/telegram/updates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
