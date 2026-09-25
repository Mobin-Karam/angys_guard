"""Runflare-compatible ASGI entrypoint.

Runflare requires ``main.py`` at the deployed Python project root.  The actual
application remains in ``app.main`` so local Docker and tests use the same code.
"""

import os

from app.main import app

__all__ = ["app"]


if __name__ == "__main__":
    # Some Python PaaS providers execute ``python main.py`` while others import
    # ``main:app``. Supporting both keeps the deployment contract explicit and
    # honors the provider-assigned port instead of assuming a local one.
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        proxy_headers=True,
    )
