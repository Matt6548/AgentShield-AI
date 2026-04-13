"""OpenAI-compatible backend adapter for safe opt-in integrations."""

from __future__ import annotations

from typing import Any

from src.providers.base import ProviderAdapter, ProviderCapability, ProviderHealth


class OpenAICompatibleProviderAdapter(ProviderAdapter):
    """Backend-only adapter for OpenAI-compatible HTTP APIs."""

    provider_id = "openai_compatible"
    display_name = "OpenAI-compatible"
    adapter_kind = "openai_compatible"
    api_key_env = "SAFECORE_OPENAI_COMPATIBLE_API_KEY"
    base_url_env = "SAFECORE_OPENAI_COMPATIBLE_BASE_URL"
    auth_mode = "bearer_optional"
    token_optional = True

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        return (
            ProviderCapability(
                name="chat_completions_bridge",
                detail="Can prepare backend request specs for chat-completions-compatible APIs.",
            ),
            ProviderCapability(
                name="base_url_override",
                detail="Supports configurable base_url for local, self-hosted, or future compatible providers.",
            ),
            ProviderCapability(
                name="token_optional",
                detail="Can operate with or without a bearer token, depending on the target endpoint.",
            ),
        )

    def health(self) -> ProviderHealth:
        if self.is_configured():
            return ProviderHealth(
                status="READY",
                ok=True,
                summary="Base URL is configured for the OpenAI-compatible bridge.",
            )
        return ProviderHealth(
            status="NOT_CONFIGURED",
            ok=False,
            summary="Set a compatible base URL to enable this opt-in bridge.",
        )

    def build_request_spec(
        self,
        *,
        path: str = "/chat/completions",
        body: dict[str, Any] | None = None,
        method: str = "POST",
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured():
            raise ValueError(
                "OpenAI-compatible adapter is not configured. "
                "Set SAFECORE_OPENAI_COMPATIBLE_BASE_URL in the backend environment."
            )

        headers = self._build_headers(extra_headers)
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        return {
            "provider_id": self.provider_id,
            "adapter_kind": self.adapter_kind,
            "method": method.upper(),
            "url": self._join_url(path),
            "headers": headers,
            "json": body or {},
            "timeout_seconds": 30,
            "auth_mode": self.auth_mode,
        }
