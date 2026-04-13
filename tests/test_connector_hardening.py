from pathlib import Path

from src.api.service import GuardedExecutionService
from src.approval import ApprovalManager
from src.audit import AuditLogger
from src.connectors import ConnectorExecutor
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


def test_connector_executor_rejects_invalid_request_shape():
    executor = ConnectorExecutor()

    response = executor.execute(
        {
            "run_id": "conn-invalid",
            "actor": "tester",
            "tool": "shell",
            "command": "ls",
            "params": {"api_key": "secret", "depth": 1},
            "payload": {"note": "safe"},
        },
        dry_run=True,
    )

    assert response["status"] == "INVALID_INPUT"
    assert response["success"] is False
    assert response["raw_result"] == {}


def test_invalid_connector_input_blocks_execution_and_emits_evidence(tmp_path):
    audit_file = tmp_path / "connector_invalid_input.jsonl"
    service = _build_service(audit_file)
    response = service.execute_guarded_request(
        {
            "run_id": "svc-connector-invalid",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "params": {"api_key": "secret"},
            "payload": {"note": "safe"},
            "dry_run": True,
        }
    )

    assert response["blocked"] is True
    assert "connector:INVALID_INPUT" in response["blockers"]
    assert response["connector_execution"]["status"] == "INVALID_INPUT"
    assert response["execution_result"]["output"]["status"] == "BLOCKED"
    assert response["audit_record"]["data"]["connector_status"] == "INVALID_INPUT"
    assert response["observability"]["counters"]["connector_execution:INVALID_INPUT"] == 1
    assert response["observability"]["counters"]["audit:RECORDED"] == 1
