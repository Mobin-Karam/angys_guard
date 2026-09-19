from __future__ import annotations

from .providers.base import ProviderError
from .providers.http_bot import HttpBotProvider


# Compatibility name retained for older internal imports. The active runtime,
# setup and Doctor construction path is providers.build_provider().
BaleApiError = ProviderError


class BaleApi(HttpBotProvider):
    """Compatibility facade over the consolidated Bale provider adapter.

    New code must use RuntimeApi/providers.build_provider rather than extending
    this class. It remains only to keep older imports working during migration.
    """

    def __init__(
        self,
        token: str,
        base_url: str = "https://tapi.bale.ai",
        proxy: str = "",
    ) -> None:
        super().__init__(
            token=token,
            api_base=base_url,
            proxy=proxy,
            provider_name="bale",
        )
        self.base_url = self.api_base

    def _url(self, method: str) -> str:
        return f"{self.root}/{method}"

    def request(
        self,
        method: str,
        data=None,
        files=None,
        timeout: int = 40,
        retries: int = 0,
    ):
        return self._call(
            method,
            data=data,
            files=files,
            timeout=timeout,
            retries=retries,
        )
