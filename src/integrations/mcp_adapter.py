"""Minimal MCP-style proxy boundary for SafeCore tool mediation."""

from __future__ import annotations

from typing import Any, Mapping

from src.integrations.base import (
    SafeCoreIntegrationBridge,
    build_safe_http_status_request,
    explain_guarded_result,
)


class SafeCoreMcpBoundary:
    """Small MCP-style proxy surface that keeps tool calls behind SafeCore."""

    supported_tools = {"safe_http_status"}

    def __init__(
        self,
        bridge: SafeCoreIntegrationBridge,
        *,
        actor: str = "mcp-client",
        provider_id: str | None = None,
    ) -> None:
        self.bridge = bridge
        self.actor = actor
        self.provider_id = provider_id

    def describe_boundary(self) -> dict[str, Any]:
        """Return one safe description of the boundary surface."""
        return {
            "adapter": "mcp_boundary",
            "baseline_support": True,
            "supported_tools": sorted(self.supported_tools),
            "notes": (
                "This is a minimal proxy boundary, not a full MCP server. "
                "It routes a supported tool call through SafeCore first."
            ),
        }

    def handle_tool_call(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
        *,
        run_id: str = "mcp-boundary-run",
        actor: str | None = None,
    ) -> dict[str, Any]:
        """Route one supported MCP-style tool call through SafeCore."""
        normalized_tool = str(tool_name or "").strip()
        if normalized_tool not in self.supported_tools:
            raise ValueError(f"Unsupported MCP-style tool: {tool_name}")
        if not isinstance(arguments, Mapping):
            raise TypeError("MCP-style arguments must be a mapping.")

        request = build_safe_http_status_request(
            url=str(arguments.get("url", "")),
            method=str(arguments.get("method", "GET")),
            run_id=str(run_id),
            actor=str(actor or self.actor),
            payload=dict(arguments.get("payload", {}) or {}),
        )
        result = self.bridge.execute(request)
        payload = {
            "tool_name": normalized_tool,
            "guarded_result": result,
            "explanation": explain_guarded_result(result),
        }
        if self.provider_id:
            payload["provider_gateway"] = self.bridge.provider_snapshot(self.provider_id)
        return payload
