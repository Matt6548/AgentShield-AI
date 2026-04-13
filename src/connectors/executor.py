"""Connector execution boundary for adapter-selected dry-run execution."""

from __future__ import annotations

from typing import Any

from src.connectors.adapters import ConnectorAdapter, build_default_adapters
from src.connectors.hardening import ConnectorHardening


class ConnectorExecutor:
    """Select connector adapters and execute normalized dry-run connector calls."""

    def __init__(
        self,
        adapters: list[ConnectorAdapter] | None = None,
        hardening: ConnectorHardening | None = None,
    ) -> None:
        self.adapters = adapters or build_default_adapters()
        self.hardening = hardening or ConnectorHardening()
        if not self.adapters:
            raise ValueError("ConnectorExecutor requires at least one adapter.")

    def select_adapter(self, tool: str, connector_name: str | None = None) -> ConnectorAdapter:
        """Select adapter by explicit connector name or tool mapping."""
        normalized_connector = (connector_name or "").strip().lower()
        if normalized_connector:
            for adapter in self.adapters:
                if adapter.connector.name.lower() == normalized_connector:
                    return adapter

        for adapter in self.adapters:
            if adapter.matches(tool=tool, connector_name=None):
                return adapter
        return self.adapters[-1]

    def execute(
        self,
        request: dict[str, Any],
        *,
        dry_run: bool = True,
        blocked_by: list[str] | None = None,
    ) -> dict[str, Any]:
        """Execute through selected adapter with explicit blocked-path behavior."""
        if not isinstance(request, dict):
            raise TypeError("ConnectorExecutor.execute expects a dict request.")

        hardening_result = self.hardening.sanitize_request(request)
        sanitized_request = hardening_result["sanitized_request"]

        tool = str(sanitized_request.get("tool", ""))
        connector_name = sanitized_request.get("connector")
        adapter = self.select_adapter(tool=tool, connector_name=str(connector_name or ""))
        normalized_request = adapter.normalize_request(sanitized_request, dry_run=dry_run)

        if not bool(hardening_result["valid"]):
            reasons = [str(reason) for reason in hardening_result["reasons"]]
            stripped_fields = [str(field) for field in hardening_result["stripped_fields"]]
            if stripped_fields:
                reasons.append(
                    "Connector request contained unsupported top-level fields: "
                    + ", ".join(sorted(stripped_fields))
                )
            invalid_result = {
                "adapter_id": adapter.adapter_id,
                "connector": adapter.connector.name,
                "tool": normalized_request["tool"],
                "dry_run": bool(dry_run),
                "status": "INVALID_INPUT",
                "success": False,
                "reasons": reasons,
                "normalized_request": normalized_request,
                "raw_result": {},
            }
            return self.hardening.sanitize_response(invalid_result)

        blockers = [str(item) for item in (blocked_by or []) if str(item).strip()]
        if blockers:
            blocked_result = {
                "adapter_id": adapter.adapter_id,
                "connector": adapter.connector.name,
                "tool": normalized_request["tool"],
                "dry_run": bool(dry_run),
                "status": "BLOCKED",
                "success": False,
                "reasons": blockers,
                "normalized_request": normalized_request,
                "raw_result": {},
            }
            return self.hardening.sanitize_response(blocked_result)

        raw_execution_result = adapter.execute_normalized(normalized_request, dry_run=dry_run)
        return self.hardening.sanitize_response(raw_execution_result)
