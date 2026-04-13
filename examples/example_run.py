"""SafeCore example run for guarded dry-run workflow snapshots."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.api.service import GuardedExecutionService
from src.approval import ApprovalManager
from src.audit import AuditLogger
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.policy import PolicyEngine
from src.utils.tool_policies import ToolGuard


def _build_service(audit_file: Path) -> GuardedExecutionService:
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    approval_manager = ApprovalManager(audit_logger=audit_logger)
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=approval_manager,
    )


def run_flow(
    service: GuardedExecutionService,
    *,
    name: str,
    request: dict[str, Any],
    approval_decision: str | None = None,
) -> dict[str, Any]:
    """Run one guarded flow and return a compact summary."""
    first = service.execute_guarded_request(request)
    final = first

    approval = first.get("approval", {})
    request_id = approval.get("request_id")
    if approval_decision and isinstance(request_id, str) and request_id:
        final = service.execute_guarded_request(
            {
                **request,
                "approval": {
                    "request_id": request_id,
                    "decision": approval_decision,
                    "approver": "example.approver",
                    "reason": f"{name} flow decision",
                },
            }
        )

    model_route = final.get("model_route", {})
    execution_result = final.get("execution_result", {})
    execution_output = execution_result.get("output", {}) if isinstance(execution_result, dict) else {}
    connector_execution = final.get("connector_execution", {})
    audit_integrity = final.get("audit_integrity", {})

    return {
        "flow": name,
        "run_id": final.get("run_id"),
        "blocked": bool(final.get("blocked", True)),
        "blockers": list(final.get("blockers", [])),
        "policy_decision": final.get("policy_decision", {}),
        "approval_status": final.get("approval", {}).get("status"),
        "model_route": {
            "route_id": model_route.get("route_id"),
            "model_profile": model_route.get("model_profile"),
            "profile_id": model_route.get("profile_id"),
            "profile_name": model_route.get("profile_name"),
        },
        "execution_status": execution_output.get("status"),
        "connector_status": connector_execution.get("status"),
        "audit_integrity": {
            "valid": bool(audit_integrity.get("valid", False)),
            "broken_indices": list(audit_integrity.get("broken_indices", [])),
        },
        "audit_hash": final.get("audit_record", {}).get("hash"),
    }


def build_flow_summaries(audit_file: Path | None = None) -> list[dict[str, Any]]:
    """Build the three canonical example flows."""
    resolved_audit_file = audit_file or (Path(__file__).resolve().parent / "example_audit.log.jsonl")
    if resolved_audit_file.exists():
        resolved_audit_file.unlink()

    service = _build_service(resolved_audit_file)

    safe_request = {
        "run_id": "example-safe",
        "actor": "demo-user",
        "action": "read_status",
        "tool": "shell",
        "command": "ls",
        "payload": {"note": "safe"},
        "dry_run": True,
    }
    approval_required_request = {
        "run_id": "example-approval",
        "actor": "demo-user",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"config": "feature_flag"},
        "dry_run": True,
    }
    rejected_request = {
        "run_id": "example-rejected",
        "actor": "demo-user",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"config": "critical_flag"},
        "dry_run": True,
    }

    return [
        run_flow(service, name="safe_path", request=safe_request),
        run_flow(
            service,
            name="approval_required_path",
            request=approval_required_request,
            approval_decision="APPROVED",
        ),
        run_flow(
            service,
            name="rejected_path",
            request=rejected_request,
            approval_decision="REJECTED",
        ),
    ]


def main() -> None:
    summaries = build_flow_summaries()
    for summary in summaries:
        print("=" * 80)
        print(f"Flow: {summary['flow']}")
        print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

