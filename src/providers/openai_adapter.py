"""OpenAI and adjacent provider adapters for SafeCore integrations."""

from __future__ import annotations

from typing import Any

from src.providers.base import ProviderAdapter, ProviderCapability
from src.providers.openai_compatible_adapter import OpenAICompatibleProviderAdapter


class OpenAIProviderAdapter(OpenAICompatibleProviderAdapter):
    """OpenAI adapter with default public API base URL."""

    provider_id = "openai"
    display_name = "OpenAI"
    api_key_env = "OPENAI_API_KEY"
    base_url_env = "OPENAI_BASE_URL"
    default_base_url = "https://api.openai.com/v1"
    auth_mode = "bearer_required"
    token_optional = False

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        return (
            ProviderCapability(
                name="chat_completions_bridge",
                detail="Prepares backend request specs for OpenAI-style chat completions calls.",
            ),
            ProviderCapability(
                name="responses_ready_path",
                detail="Can be extended later for OpenAI-compatible responses-style backends without changing the gateway contract.",
            ),
            ProviderCapability(
                name="base_url_override",
                detail="Supports a backend-only base_url override for future safe self-hosted or proxy setups.",
            ),
        )


class OpenRouterProviderAdapter(OpenAICompatibleProviderAdapter):
    """OpenRouter adapter via the same OpenAI-compatible bridge pattern."""

    provider_id = "openrouter"
    display_name = "OpenRouter"
    api_key_env = "OPENROUTER_API_KEY"
    base_url_env = "OPENROUTER_BASE_URL"
    default_base_url = "https://openrouter.ai/api/v1"
    auth_mode = "bearer_required"
    token_optional = False

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        return (
            ProviderCapability(
                name="openai_compatible_bridge",
                detail="Uses the same backend bridge pattern as other OpenAI-compatible providers.",
            ),
            ProviderCapability(
                name="base_url_override",
                detail="Supports a backend-only base_url override for compatible proxy or self-hosted routes.",
            ),
        )


class AnthropicProviderAdapter(ProviderAdapter):
    """Minimal Anthropic metadata adapter for safe env-backed visibility and extension."""

    provider_id = "claude"
    display_name = "Claude"
    adapter_kind = "anthropic"
    api_key_env = "ANTHROPIC_API_KEY"
    base_url_env = "ANTHROPIC_BASE_URL"
    default_base_url = "https://api.anthropic.com"
    auth_mode = "x-api-key"

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        return (
            ProviderCapability(
                name="messages_api_metadata",
                detail="Exposes safe backend status for Anthropic-style messages integrations.",
            ),
            ProviderCapability(
                name="base_url_override",
                detail="Supports backend-only base_url override without exposing raw environment values to the shell.",
            ),
        )

    def build_request_spec(
        self,
        *,
        path: str = "/v1/messages",
        body: dict[str, Any] | None = None,
        method: str = "POST",
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured():
            raise ValueError(
                "Anthropic adapter is not configured. "
                "Set ANTHROPIC_API_KEY in the backend environment."
            )

        headers = self._build_headers(extra_headers)
        headers["x-api-key"] = str(self._api_key)
        headers.setdefault("anthropic-version", "2023-06-01")
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
