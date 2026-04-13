import json
from pathlib import Path

from src.api.service import GuardedExecutionService
from src.approval import ApprovalManager
from src.audit import AuditLogger
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.policy import PolicyEngine
from src.utils.tool_policies import ToolGuard


class CounterIdFactory:
    def __init__(self) -> None:
        self.counter = 0

    def __call__(self) -> str:
        self.counter += 1
        return f"apr-{self.counter:04d}"


def _build_service(audit_file: Path) -> GuardedExecutionService:
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    approval_manager = ApprovalManager(
        audit_logger=audit_logger,
        id_factory=CounterIdFactory(),
    )
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=approval_manager,
    )


def _read_audit_actions(audit_file: Path) -> list[str]:
    if not audit_file.exists():
        return []
    lines = [line for line in audit_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [json.loads(line)["action"] for line in lines]


def test_service_safe_path_returns_dry_run_success(tmp_path):
    audit_file = tmp_path / "api_service_safe.jsonl"
    service = _build_service(audit_file)

    response = service.execute_guarded_request(
        {
            "run_id": "svc-safe",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "payload": {"note": "ok"},
            "dry_run": True,
        }
    )

    assert response["blocked"] is False
    assert response["approval"]["status"] == "BYPASSED"
    assert response["execution_result"]["success"] is True
    assert response["execution_result"]["output"]["status"] == "DRY_RUN_SIMULATED"
    assert len(response["audit_record"]["hash"]) == 64


def test_service_approval_pending_then_approved_flow(tmp_path):
    audit_file = tmp_path / "api_service_approval.jsonl"
    service = _build_service(audit_file)
    base_request = {
        "run_id": "svc-approval",
        "actor": "tester",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"feature": "alpha"},
        "dry_run": True,
    }

    pending = service.execute_guarded_request(base_request)
    assert pending["blocked"] is True
    assert pending["approval"]["status"] == "PENDING"
    assert pending["approval"]["request_id"] is not None
    assert pending["execution_result"]["output"]["status"] == "BLOCKED"

    approved = service.execute_guarded_request(
        {
            **base_request,
            "approval": {
                "request_id": pending["approval"]["request_id"],
                "decision": "APPROVED",
                "approver": "security.lead",
                "reason": "approved for dry run",
            },
        }
    )
    assert approved["blocked"] is False
    assert approved["approval"]["status"] == "APPROVED"
    assert approved["execution_result"]["success"] is True

    actions = _read_audit_actions(audit_file)
    assert "approval_request_created" in actions
    assert "approval_decided" in actions
    assert "api_guarded_execute" in actions


def test_service_rejected_flow_remains_blocked(tmp_path):
    audit_file = tmp_path / "api_service_rejected.jsonl"
    service = _build_service(audit_file)
    base_request = {
        "run_id": "svc-rejected",
        "actor": "tester",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"feature": "beta"},
        "dry_run": True,
    }

    pending = service.execute_guarded_request(base_request)
    rejected = service.execute_guarded_request(
        {
            **base_request,
            "approval": {
                "request_id": pending["approval"]["request_id"],
                "decision": "REJECTED",
                "approver": "security.lead",
                "reason": "not enough context",
            },
        }
    )

    assert rejected["blocked"] is True
    assert rejected["approval"]["status"] == "REJECTED"
    assert rejected["execution_result"]["output"]["status"] == "BLOCKED"


def test_service_deny_path_stays_blocked_and_not_overridable(tmp_path):
    audit_file = tmp_path / "api_service_deny.jsonl"
    service = _build_service(audit_file)

    denied = service.execute_guarded_request(
        {
            "run_id": "svc-deny",
            "actor": "tester",
            "action": "delete_everything",
            "tool": "shell",
            "command": "rm -rf /",
            "payload": {"note": "danger"},
            "dry_run": True,
        }
    )

    assert denied["policy_decision"]["decision"] == "DENY"
    assert denied["approval"]["status"] == "NOT_APPLICABLE_DENY"
    assert denied["blocked"] is True
    assert denied["execution_result"]["output"]["status"] == "BLOCKED"


def test_service_outputs_are_deterministic_for_same_input_shape(tmp_path):
    audit_file = tmp_path / "api_service_deterministic.jsonl"
    service = _build_service(audit_file)
    request = {
        "run_id": "svc-det",
        "actor": "tester",
        "action": "read_status",
        "tool": "shell",
        "command": "pwd",
        "payload": {"note": "stable"},
        "dry_run": True,
    }

    first = service.execute_guarded_request(request)
    second = service.execute_guarded_request(request)

    assert first["policy_decision"] == second["policy_decision"]
    assert first["data_guard_result"] == second["data_guard_result"]
    assert first["tool_guard_result"] == second["tool_guard_result"]
    assert first["approval"]["status"] == second["approval"]["status"]
    assert first["blocked"] == second["blocked"]
    assert first["execution_result"]["output"]["status"] == second["execution_result"]["output"]["status"]


def test_service_blocked_path_still_writes_api_audit_evidence(tmp_path):
    audit_file = tmp_path / "api_service_blocked_audit.jsonl"
    service = _build_service(audit_file)

    response = service.execute_guarded_request(
        {
            "run_id": "svc-blocked",
            "actor": "tester",
            "action": "delete_everything",
            "tool": "shell",
            "command": "rm -rf /",
            "payload": {"note": "danger"},
            "dry_run": True,
        }
    )
    assert response["blocked"] is True

    lines = [line for line in audit_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines
    last = json.loads(lines[-1])
    assert last["action"] == "api_guarded_execute"
    assert last["data"]["blocked"] is True

