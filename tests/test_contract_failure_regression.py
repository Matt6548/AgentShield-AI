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


class InvalidPolicyEngine:
    def evaluate(self, input_data):  # noqa: ANN001
        return {"decision": "ALLOW", "risk_score": "invalid"}


class InvalidExecutionGuard:
    def execute(self, request, dry_run=True):  # noqa: ANN001
        return {"unexpected": "shape"}


def _build_service(audit_file: Path) -> GuardedExecutionService:
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=ApprovalManager(audit_logger=audit_logger, id_factory=CounterIdFactory()),
    )


def test_policy_contract_failure_returns_blocked_safe_with_evidence(tmp_path):
    audit_file = tmp_path / "policy_contract_failure.jsonl"
    service = _build_service(audit_file)
    service.policy_engine = InvalidPolicyEngine()  # type: ignore[assignment]

    response = service.execute_guarded_request(
        {
            "run_id": "reg-contract-policy",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "payload": {"note": "safe"},
            "dry_run": True,
        }
    )

    assert response["blocked"] is True
    assert "contract_validation:policy_decision" in response["blockers"]
    assert response["audit_record"]["action"] == "api_guarded_execute_validation_failure"
    assert "contract_validation:FAILED" in response["observability"]["counters"]
    assert "execution:BLOCKED" in response["observability"]["counters"]


def test_execution_contract_failure_returns_blocked_safe_with_evidence(tmp_path):
    audit_file = tmp_path / "execution_contract_failure.jsonl"
    service = _build_service(audit_file)
    service.execution_guard = InvalidExecutionGuard()  # type: ignore[assignment]

    response = service.execute_guarded_request(
        {
            "run_id": "reg-contract-exec",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "payload": {"note": "safe"},
            "dry_run": True,
        }
    )

    assert response["blocked"] is True
    assert "contract_validation:execution_result" in response["blockers"]
    assert response["audit_record"]["action"] == "api_guarded_execute_validation_failure"
    assert "contract_validation:FAILED" in response["observability"]["counters"]
    assert "execution:BLOCKED" in response["observability"]["counters"]

