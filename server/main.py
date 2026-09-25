"""Runflare-compatible ASGI entrypoint.

Runflare requires ``main.py`` at the deployed Python project root.  The actual
application remains in ``app.main`` so local Docker and tests use the same code.
"""

from app.main import app

__all__ = ["app"]
