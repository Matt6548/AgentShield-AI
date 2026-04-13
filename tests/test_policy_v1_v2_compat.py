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
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=ApprovalManager(audit_logger=audit_logger, id_factory=CounterIdFactory()),
    )


def test_safe_read_path_remains_allow_in_v1_and_v2():
    engine = PolicyEngine(opa_binary="definitely-not-opa")
    payload = {
        "action": "read_status",
        "tool": "shell",
        "command": "ls",
        "environment": "dev",
    }

    v1 = engine.evaluate(payload, policy_pack="v1")
    v2 = engine.evaluate(payload, policy_pack="v2")

    assert v1["decision"] == "ALLOW"
    assert v2["decision"] == "ALLOW"
    assert {"decision", "risk_score", "reasons", "constraints", "operator_checks"} <= set(v1.keys())
    assert {"decision", "risk_score", "reasons", "constraints", "operator_checks"} <= set(v2.keys())


def test_service_uses_v1_by_default_and_only_switches_when_explicit(tmp_path):
    service = _build_service(tmp_path / "policy_pack_compat.jsonl")
    request = {
        "run_id": "pack-compat",
        "actor": "tester",
        "action": "deploy_service",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"feature": "beta"},
        "dry_run": True,
    }

    default_response = service.execute_guarded_request(request)
    explicit_v2_response = service.execute_guarded_request({**request, "policy_pack": "v2"})
    default_again_response = service.execute_guarded_request(request)

    assert default_response["policy_pack"] == "v1"
    assert default_response["policy_decision"]["decision"] == "NEEDS_APPROVAL"
    assert explicit_v2_response["policy_pack"] == "v2"
    assert explicit_v2_response["policy_decision"]["decision"] == "DENY"
    assert default_again_response["policy_pack"] == "v1"
    assert default_again_response["policy_decision"]["decision"] == "NEEDS_APPROVAL"


def test_service_invalid_policy_pack_returns_blocked_validation_failure(tmp_path):
    service = _build_service(tmp_path / "invalid_policy_pack.jsonl")
    response = service.execute_guarded_request(
        {
            "run_id": "invalid-pack",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "dry_run": True,
            "policy_pack": "v3",
        }
    )

    assert response["blocked"] is True
    assert "contract_validation:policy_pack_selection" in response["blockers"]
    assert response["policy_pack"] == "v1"
    assert response["audit_record"]["action"] == "api_guarded_execute_validation_failure"

