"""Connector adapter layer for normalized dry-run connector execution."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.connectors.base import BaseConnector
from src.connectors.safe_http_connector import SafeHttpStatusConnector
from src.connectors.stub_connector import StubConnector
from src.policy.policy_engine import SHELL_TOOLS
from src.utils.safe_http import extract_safe_http_request


class ConnectorAdapter:
    """Normalize connector requests/responses and enforce dry-run behavior."""

    def __init__(
        self,
        *,
        adapter_id: str,
        connector: BaseConnector,
        supported_tools: set[str] | None = None,
    ) -> None:
        self.adapter_id = adapter_id
        self.connector = connector
        self.supported_tools = {tool.lower() for tool in (supported_tools or set())}

    def matches(self, tool: str, connector_name: str | None = None) -> bool:
        """Return whether this adapter should handle the request."""
        normalized_tool = (tool or "").strip().lower()
        normalized_connector = (connector_name or "").strip().lower()
        if normalized_connector and normalized_connector == self.connector.name.lower():
            return True
        if not self.supported_tools:
            return True
        return normalized_tool in self.supported_tools

    def normalize_request(self, request: dict[str, Any], dry_run: bool = True) -> dict[str, Any]:
        """Normalize incoming service request into a connector payload."""
        validated = self.connector.validate_request(request)
        params = validated.get("params", {})
        payload = validated.get("payload", {})
        if not isinstance(params, dict):
            params = {"raw_params": deepcopy(params)}
        if not isinstance(payload, dict):
            payload = {"raw_payload": deepcopy(payload)}

        return {
            "run_id": str(validated.get("run_id", "run-unknown")),
            "actor": str(validated.get("actor", "unknown")),
            "tool": str(validated.get("tool", "")).strip().lower(),
            "connector": str(validated.get("connector", self.connector.name)).strip().lower(),
            "command": str(validated.get("command", "")),
            "params": deepcopy(params),
            "payload": deepcopy(payload),
            "environment": str(validated.get("environment", validated.get("env", ""))),
            "target": str(validated.get("target", validated.get("target_system", ""))),
            "policy_pack": str(validated.get("policy_pack", "v1")).strip().lower() or "v1",
            "dry_run": bool(dry_run),
        }

    def execute_normalized(
        self,
        normalized_request: dict[str, Any],
        *,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Execute normalized payload through connector stub path."""
        if not dry_run:
            return {
                "adapter_id": self.adapter_id,
                "connector": self.connector.name,
                "tool": str(normalized_request.get("tool", "")),
                "dry_run": False,
                "status": "NOT_IMPLEMENTED",
                "success": False,
                "reasons": ["Connector adapters are dry_run-only in this iteration."],
                "normalized_request": deepcopy(normalized_request),
                "raw_result": {},
            }

        raw_result = self.connector.execute(deepcopy(normalized_request))
        if not isinstance(raw_result, dict):
            raw_result = {
                "connector": self.connector.name,
                "status": "INVALID_ADAPTER_RESULT",
                "success": False,
                "output": {"message": "Connector returned a non-object result."},
            }

        return {
            "adapter_id": self.adapter_id,
            "connector": self.connector.name,
            "tool": str(normalized_request.get("tool", "")),
            "dry_run": True,
            "status": "DRY_RUN_SIMULATED",
            "success": True,
            "reasons": [],
            "normalized_request": deepcopy(normalized_request),
            "raw_result": deepcopy(raw_result),
        }


class SafeHttpStatusAdapter(ConnectorAdapter):
    """Adapter for the narrow allowlisted read-only HTTP status connector."""

    def normalize_request(self, request: dict[str, Any], dry_run: bool = True) -> dict[str, Any]:
        normalized = super().normalize_request(request, dry_run=dry_run)
        safe_http = extract_safe_http_request(normalized)
        normalized["tool"] = "safe_http_status"
        normalized["command"] = f"{safe_http['method']} {safe_http['url']}".strip()
        normalized["safe_http"] = {
            "method": safe_http["method"],
            "url": safe_http["url"],
            "host": safe_http["host"],
            "path": safe_http["path"],
            "allowed": safe_http["allowed"],
            "reasons": list(safe_http["reasons"]),
        }
        return normalized

    def execute_normalized(
        self,
        normalized_request: dict[str, Any],
        *,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        safe_http = extract_safe_http_request(normalized_request)
        if not safe_http["allowed"]:
            return {
                "adapter_id": self.adapter_id,
                "connector": self.connector.name,
                "tool": str(normalized_request.get("tool", "")),
                "dry_run": bool(dry_run),
                "status": "BLOCKED",
                "success": False,
                "reasons": list(safe_http["reasons"]),
                "normalized_request": deepcopy(normalized_request),
                "raw_result": {
                    "status": "BLOCKED",
                    "success": False,
                    "output": {
                        "url": safe_http["url"],
                        "method": safe_http["method"],
                        "host": safe_http["host"],
                        "path": safe_http["path"],
                        "read_only": True,
                    },
                },
            }

        raw_result = self.connector.execute(deepcopy(normalized_request))
        return {
            "adapter_id": self.adapter_id,
            "connector": self.connector.name,
            "tool": str(normalized_request.get("tool", "")),
            "dry_run": True,
            "status": str(raw_result.get("status", "SAFE_READ_ONLY_FETCHED")),
            "success": bool(raw_result.get("success", False)),
            "reasons": [str(item) for item in raw_result.get("reasons", [])],
            "normalized_request": deepcopy(normalized_request),
            "raw_result": deepcopy(raw_result),
        }


def build_default_adapters() -> list[ConnectorAdapter]:
    """Create default deterministic adapter set for current SafeCore foundation."""
    safe_http_adapter = SafeHttpStatusAdapter(
        adapter_id="safe_http_status_adapter",
        connector=SafeHttpStatusConnector(),
        supported_tools={"safe_http_status"},
    )
    shell_adapter = ConnectorAdapter(
        adapter_id="shell_stub_adapter",
        connector=StubConnector(name="stub_shell_connector"),
        supported_tools=set(SHELL_TOOLS),
    )
    generic_adapter = ConnectorAdapter(
        adapter_id="generic_stub_adapter",
        connector=StubConnector(name="stub_generic_connector"),
        supported_tools=set(),
    )
    return [safe_http_adapter, shell_adapter, generic_adapter]
