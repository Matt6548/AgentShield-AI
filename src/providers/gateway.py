"""Safe provider gateway registry for external SafeCore integrations."""

from __future__ import annotations

from typing import Any

from src.providers.base import LocalDemoProviderAdapter, ProviderAdapter
from src.providers.openai_adapter import (
    AnthropicProviderAdapter,
    OpenAIProviderAdapter,
    OpenRouterProviderAdapter,
)
from src.providers.openai_compatible_adapter import OpenAICompatibleProviderAdapter


class ProviderGateway:
    """Registry and metadata surface for SafeCore provider adapters."""

    def __init__(self, adapters: list[ProviderAdapter] | None = None) -> None:
        resolved = adapters or build_default_provider_adapters()
        self._adapters = {adapter.provider_id: adapter for adapter in resolved}
        if not self._adapters:
            raise ValueError("ProviderGateway requires at least one adapter.")

    def list_adapters(self) -> list[ProviderAdapter]:
        """Return adapters in deterministic id order."""
        return [self._adapters[key] for key in sorted(self._adapters)]

    def get_adapter(self, provider_id: str) -> ProviderAdapter:
        """Return one adapter by id."""
        try:
            return self._adapters[str(provider_id)]
        except KeyError as exc:
            raise KeyError(f"Unknown provider adapter: {provider_id}") from exc

    def safe_status_catalog(self) -> dict[str, Any]:
        """Return safe public metadata for UI, docs, or operator visibility."""
        snapshots = [adapter.safe_snapshot().as_public_dict() for adapter in self.list_adapters()]
        return {
            "providers": snapshots,
            "summary": {
                "provider_count": len(snapshots),
                "current_shell_enabled_ids": [
                    snapshot["id"] for snapshot in snapshots if snapshot["enabled"]
                ],
                "opt_in_gateway_ids": [
                    snapshot["id"] for snapshot in snapshots if not snapshot["enabled"]
                ],
                "openai_compatible_bridge_ids": [
                    snapshot["id"]
                    for snapshot in snapshots
                    if snapshot["adapter_kind"] == "openai_compatible"
                ],
                "framework_adapter_ids": ["langchain", "langgraph", "mcp_boundary"],
            },
        }

    def build_request_spec(
        self,
        provider_id: str,
        *,
        path: str,
        body: dict[str, Any] | None = None,
        method: str = "POST",
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Delegate provider-specific backend request spec generation."""
        adapter = self.get_adapter(provider_id)
        return adapter.build_request_spec(
            path=path,
            body=body,
            method=method,
            extra_headers=extra_headers,
        )


def build_default_provider_adapters() -> list[ProviderAdapter]:
    """Return the default provider adapter set for the current SafeCore repo."""
    return [
        AnthropicProviderAdapter(),
        LocalDemoProviderAdapter(),
        OpenAICompatibleProviderAdapter(),
        OpenAIProviderAdapter(),
        OpenRouterProviderAdapter(),
    ]


def build_default_provider_gateway() -> ProviderGateway:
    """Return the default SafeCore provider gateway."""
    return ProviderGateway(build_default_provider_adapters())
