"""Baseline SafeCore integration helpers for external agent stacks."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from src.api.service import GuardedExecutionService
from src.providers import ProviderGateway, build_default_provider_gateway
from src.utils.safe_http import SAFE_HTTP_TOOL


def build_safe_http_status_request(
    *,
    url: str,
    method: str = "GET",
    run_id: str,
    actor: str,
    action: str = "fetch_status",
    timeout_seconds: int = 2,
    payload: Mapping[str, Any] | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Build the narrow safe HTTP request shape used by current SafeCore integrations."""
    normalized_method = str(method or "GET").strip().upper() or "GET"
    safe_payload = dict(payload or {})
    return {
        "run_id": str(run_id),
        "actor": str(actor),
        "action": str(action),
        "tool": SAFE_HTTP_TOOL,
        "command": normalized_method,
        "params": {
            "method": normalized_method,
            "url": str(url),
            "timeout_seconds": int(timeout_seconds),
        },
        "target": str(url),
        "payload": safe_payload,
        "dry_run": bool(dry_run),
    }


def build_safe_http_example_request(name: str, *, url: str | None = None) -> dict[str, Any]:
    """Build the three existing safe HTTP example scenarios by name."""
    example_name = str(name).strip()
    default_url = url or "http://127.0.0.1:8000/health"
    if example_name == "allowlisted_get":
        return build_safe_http_status_request(
            url=default_url,
            method="GET",
            run_id="safe-http-allowlisted_get",
            actor="demo-user",
        )
    if example_name == "blocked_host":
        return build_safe_http_status_request(
            url="http://example.com/health",
            method="GET",
            run_id="safe-http-blocked_host",
            actor="demo-user",
        )
    if example_name == "blocked_method":
        return build_safe_http_status_request(
            url=default_url,
            method="POST",
            run_id="safe-http-blocked_method",
            actor="demo-user",
        )
    raise KeyError(f"Unknown safe HTTP example: {name}")


def explain_guarded_result(result: Mapping[str, Any]) -> str:
    """Return a short human-readable explanation for one guarded result."""
    decision = str(result.get("policy_decision", {}).get("decision", "")).upper()
    blocked = bool(result.get("blocked", True))
    approval_status = str(result.get("approval", {}).get("status", ""))
    connector_status = str(result.get("connector_execution", {}).get("status", ""))
    if decision == "ALLOW" and not blocked:
        return (
            "SafeCore allowed the request inside the current safe boundary. "
            f"Connector status: {connector_status or 'SAFE'}."
        )
    if decision == "NEEDS_APPROVAL":
        return (
            "SafeCore kept the request blocked until explicit approval exists. "
            f"Approval status: {approval_status or 'PENDING'}."
        )
    return (
        "SafeCore blocked the request before it could widen beyond the current safe boundary. "
        f"Connector status: {connector_status or 'BLOCKED'}."
    )


class SafeCoreIntegrationBridge:
    """Thin bridge that routes external integration requests through SafeCore."""

    def __init__(
        self,
        *,
        service: GuardedExecutionService | None = None,
        executor: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        provider_gateway: ProviderGateway | None = None,
    ) -> None:
        self.service = service or GuardedExecutionService()
        self._executor = executor or self.service.execute_guarded_request
        self.provider_gateway = provider_gateway or build_default_provider_gateway()

    def execute(self, request: Mapping[str, Any]) -> dict[str, Any]:
        """Route one request through the current SafeCore guarded flow."""
        if not isinstance(request, Mapping):
            raise TypeError("SafeCoreIntegrationBridge.execute expects a mapping request.")
        return self._executor(dict(request))

    def provider_snapshot(self, provider_id: str) -> dict[str, Any]:
        """Return one safe provider snapshot from the gateway."""
        return self.provider_gateway.get_adapter(provider_id).safe_snapshot().as_public_dict()

    def provider_catalog(self) -> dict[str, Any]:
        """Return safe provider gateway metadata."""
        return self.provider_gateway.safe_status_catalog()
