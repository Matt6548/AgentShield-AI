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


def _file_names(root: Path) -> set[str]:
    return {str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()}


def test_dry_run_safe_path_has_no_side_effects_beyond_audit_log(tmp_path):
    audit_file = tmp_path / "dry_run_safe_audit.jsonl"
    service = _build_service(audit_file)
    before_files = _file_names(tmp_path)

    response = service.execute_guarded_request(
        {
            "run_id": "dry-safe",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "payload": {"note": "safe"},
            "dry_run": True,
        }
    )

    after_files = _file_names(tmp_path)
    assert response["blocked"] is False
    assert response["execution_result"]["output"]["dry_run"] is True
    assert response["execution_result"]["output"]["status"] == "DRY_RUN_SIMULATED"
    assert response["connector_execution"]["dry_run"] is True
    assert after_files - before_files == {audit_file.name}


def test_dry_run_blocked_path_has_no_side_effects_beyond_audit_log(tmp_path):
    audit_file = tmp_path / "dry_run_blocked_audit.jsonl"
    service = _build_service(audit_file)
    before_files = _file_names(tmp_path)

    response = service.execute_guarded_request(
        {
            "run_id": "dry-blocked",
            "actor": "tester",
            "action": "delete_everything",
            "tool": "shell",
            "command": "rm -rf /",
            "payload": {"note": "danger"},
            "dry_run": True,
        }
    )

    after_files = _file_names(tmp_path)
    assert response["blocked"] is True
    assert response["execution_result"]["output"]["dry_run"] is True
    assert response["execution_result"]["output"]["status"] == "BLOCKED"
    assert response["connector_execution"]["status"] == "BLOCKED"
    assert after_files - before_files == {audit_file.name}

