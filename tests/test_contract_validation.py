import json
from pathlib import Path

import pytest

from src.api.service import GuardedExecutionService
from src.approval import ApprovalManager
from src.audit import AuditLogger
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.policy import PolicyEngine
from src.utils.contract_validation import (
    ContractValidationError,
    validate_audit_record,
    validate_safety_decision,
    validate_tool_call,
)
from src.utils.tool_policies import ToolGuard


class CounterIdFactory:
    def __init__(self) -> None:
        self.counter = 0

    def __call__(self) -> str:
        self.counter += 1
        return f"apr-{self.counter:04d}"


class InvalidPolicyEngine:
    def evaluate(self, input_data):  # noqa: ANN001
        return {"decision": "ALLOW", "risk_score": "not-an-int"}


class InvalidExecutionGuard:
    def execute(self, request, dry_run=True):  # noqa: ANN001
        return {"unexpected": "shape"}


def test_validate_safety_decision_success_and_failure():
    valid = {
        "decision": "ALLOW",
        "risk_score": 10,
        "reasons": ["safe"],
        "constraints": [],
        "operator_checks": [],
    }
    validate_safety_decision(valid)

    invalid = {"decision": "ALLOW", "risk_score": "10"}
    with pytest.raises(ContractValidationError):
        validate_safety_decision(invalid)


def test_validate_tool_call_success_and_failure():
    valid = {
        "tool": "shell",
        "command": "ls",
        "success": True,
        "output": {"status": "ok"},
        "timestamp": "2026-01-01T00:00:00Z",
    }
    validate_tool_call(valid)

    invalid = {
        "tool": "shell",
        "command": "ls",
        "success": "yes",
        "output": {"status": "ok"},
        "timestamp": "2026-01-01T00:00:00Z",
    }
    with pytest.raises(ContractValidationError):
        validate_tool_call(invalid)


def test_validate_audit_record_success_and_failure():
    valid = {
        "timestamp": "2026-01-01T00:00:00Z",
        "run_id": "run-1",
        "actor": "tester",
        "step": "api",
        "action": "test",
        "data": {},
        "hash": "abc123",
    }
    validate_audit_record(valid)

    invalid = {
        "timestamp": "2026-01-01T00:00:00Z",
        "run_id": "run-1",
        "actor": "tester",
        "step": "api",
        "action": "test",
        "data": {},
    }
    with pytest.raises(ContractValidationError):
        validate_audit_record(invalid)


def test_service_returns_blocked_response_when_policy_contract_is_invalid(tmp_path):
    audit_file = tmp_path / "contract_policy_failure.jsonl"
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    service = GuardedExecutionService(
        policy_engine=InvalidPolicyEngine(),  # type: ignore[arg-type]
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=ApprovalManager(audit_logger=audit_logger, id_factory=CounterIdFactory()),
    )

    response = service.execute_guarded_request(
        {
            "run_id": "validation-policy",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "payload": {"note": "ok"},
            "dry_run": True,
        }
    )

    assert response["blocked"] is True
    assert "contract_validation:policy_decision" in response["blockers"]
    assert response["execution_result"]["output"]["status"] == "BLOCKED"
    assert response["audit_record"]["action"] == "api_guarded_execute_validation_failure"

    actions = [
        json.loads(line)["action"]
        for line in audit_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert "api_guarded_execute_validation_failure" in actions


def test_service_returns_blocked_response_when_toolcall_contract_is_invalid(tmp_path):
    audit_file = tmp_path / "contract_toolcall_failure.jsonl"
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    service = GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=InvalidExecutionGuard(),  # type: ignore[arg-type]
        audit_logger=audit_logger,
        approval_manager=ApprovalManager(audit_logger=audit_logger, id_factory=CounterIdFactory()),
    )

    response = service.execute_guarded_request(
        {
            "run_id": "validation-toolcall",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "payload": {"note": "ok"},
            "dry_run": True,
        }
    )

    assert response["blocked"] is True
    assert "contract_validation:execution_result" in response["blockers"]
    assert response["audit_record"]["action"] == "api_guarded_execute_validation_failure"

