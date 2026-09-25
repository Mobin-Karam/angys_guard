"""Runflare-compatible root ASGI entrypoint for the managed test service.

Runflare validates that the deployed project contains ``main.py`` at its root.
The application itself remains owned by ``server.app.main`` so root and
``server/`` deployments execute the same safe API.
"""

import os

from server.app.main import app

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        proxy_headers=True,
    )
