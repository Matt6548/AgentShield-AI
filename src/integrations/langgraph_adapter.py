"""Baseline LangGraph-style node wrappers for SafeCore."""

from __future__ import annotations

from typing import Any, Mapping

from src.integrations.base import (
    SafeCoreIntegrationBridge,
    build_safe_http_status_request,
    explain_guarded_result,
)


class SafeCoreLangGraphNode:
    """Minimal callable node that routes one state update through SafeCore."""

    def __init__(
        self,
        bridge: SafeCoreIntegrationBridge,
        *,
        state_key: str = "safecore_result",
        explanation_key: str = "safecore_explanation",
        actor: str = "langgraph-node",
        provider_id: str | None = None,
    ) -> None:
        self.bridge = bridge
        self.state_key = state_key
        self.explanation_key = explanation_key
        self.actor = actor
        self.provider_id = provider_id

    def __call__(self, state: Mapping[str, Any]) -> dict[str, Any]:
        """Transform one state mapping into a SafeCore-guarded patch."""
        if not isinstance(state, Mapping):
            raise TypeError("SafeCoreLangGraphNode expects a mapping state.")

        request = build_safe_http_status_request(
            url=str(state.get("url", "")),
            method=str(state.get("method", "GET")),
            run_id=str(state.get("run_id", "langgraph-node-run")),
            actor=str(state.get("actor", self.actor)),
            payload=dict(state.get("payload", {}) or {}),
        )
        result = self.bridge.execute(request)
        patch = {
            self.state_key: result,
            self.explanation_key: explain_guarded_result(result),
        }
        if self.provider_id:
            patch["provider_gateway"] = self.bridge.provider_snapshot(self.provider_id)
        return patch
