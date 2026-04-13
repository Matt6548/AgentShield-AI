"""Execution guard skeleton for safe dry-run execution paths."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.utils.tool_policies import ToolGuard


class ExecutionGuard:
    """Validate and execute guarded requests in dry-run mode."""

    def __init__(self, tool_guard: ToolGuard | None = None) -> None:
        self.tool_guard = tool_guard or ToolGuard()

    def validate_execution(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate request safety before execution."""
        if not isinstance(request, dict):
            raise TypeError("ExecutionGuard.validate_execution expects a dict request.")

        blocked_by = request.get("blocked_by", [])
        blocked_reasons = [str(item) for item in blocked_by] if isinstance(blocked_by, list) else []
        if blocked_reasons:
            return {
                "allowed": False,
                "status": "BLOCKED",
                "risk_score": 67,
                "reasons": blocked_reasons,
                "tool_decision": None,
            }

        tool_decision = self.tool_guard.evaluate(request)
        allowed = bool(tool_decision["allowed"])
        return {
            "allowed": allowed,
            "status": "READY" if allowed else "BLOCKED",
            "risk_score": int(tool_decision["risk_score"]),
            "reasons": list(tool_decision["reasons"]),
            "tool_decision": tool_decision,
        }

    def execute(self, request: dict[str, Any], dry_run: bool = True) -> dict[str, Any]:
        """Execute guarded request with explicit dry-run behavior."""
        validation = self.validate_execution(request)
        tool = str(request.get("tool", ""))
        command = str(request.get("command", ""))
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        if not validation["allowed"]:
            return {
                "tool": tool,
                "command": command,
                "success": False,
                "output": {
                    "status": "BLOCKED",
                    "dry_run": dry_run,
                    "reasons": validation["reasons"],
                    "validation": validation,
                },
                "timestamp": timestamp,
            }

        if dry_run:
            return {
                "tool": tool,
                "command": command,
                "success": True,
                "output": {
                    "status": "DRY_RUN_SIMULATED",
                    "dry_run": True,
                    "message": "Execution skipped in dry_run mode.",
                    "validation": validation,
                },
                "timestamp": timestamp,
            }

        return {
            "tool": tool,
            "command": command,
            "success": False,
            "output": {
                "status": "NOT_IMPLEMENTED",
                "dry_run": False,
                "message": "Real execution is deferred to a later iteration.",
                "validation": validation,
            },
            "timestamp": timestamp,
        }

