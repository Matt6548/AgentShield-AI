"""Baseline LangChain-style wrappers that route through SafeCore."""

from __future__ import annotations

from typing import Any, Mapping

from src.integrations.base import (
    SafeCoreIntegrationBridge,
    build_safe_http_status_request,
    explain_guarded_result,
)


def build_langchain_safe_http_request(
    tool_input: Mapping[str, Any] | str,
    *,
    actor: str = "langchain-user",
    run_id: str = "langchain-safe-http",
) -> dict[str, Any]:
    """Build one LangChain-style tool request for the safe HTTP path."""
    if isinstance(tool_input, str):
        url = tool_input
        method = "GET"
        payload: dict[str, Any] = {}
    elif isinstance(tool_input, Mapping):
        url = str(tool_input.get("url", ""))
        method = str(tool_input.get("method", "GET"))
        payload = dict(tool_input.get("payload", {}) or {})
    else:
        raise TypeError("LangChain tool input must be a string URL or mapping.")

    return build_safe_http_status_request(
        url=url,
        method=method,
        run_id=str(run_id),
        actor=str(actor),
        payload=payload,
    )


class SafeCoreLangChainToolAdapter:
    """Lightweight tool wrapper that keeps LangChain-style calls behind SafeCore."""

    def __init__(
        self,
        bridge: SafeCoreIntegrationBridge,
        *,
        name: str = "safecore_safe_http_status",
        description: str | None = None,
        actor: str = "langchain-user",
        provider_id: str | None = None,
    ) -> None:
        self.bridge = bridge
        self.name = name
        self.description = description or (
            "Route one safe read-only HTTP status request through SafeCore before connector execution."
        )
        self.actor = actor
        self.provider_id = provider_id

    def invoke(self, tool_input: Mapping[str, Any] | str) -> dict[str, Any]:
        """Invoke the wrapped tool call through SafeCore."""
        request = build_langchain_safe_http_request(
            tool_input,
            actor=self.actor,
            run_id=f"{self.name}-run",
        )
        guarded_result = self.bridge.execute(request)
        return {
            "integration": "langchain",
            "wrapper": "tool",
            "tool_name": self.name,
            "guarded_result": guarded_result,
            "explanation": explain_guarded_result(guarded_result),
            "provider_gateway": (
                self.bridge.provider_snapshot(self.provider_id) if self.provider_id else None
            ),
        }

    def as_tool_spec(self) -> dict[str, Any]:
        """Return a framework-agnostic tool spec for docs/examples."""
        return {
            "name": self.name,
            "description": self.description,
            "baseline_support": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "method": {"type": "string", "enum": ["GET", "POST"]},
                },
                "required": ["url"],
            },
        }
