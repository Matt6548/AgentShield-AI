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
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=ApprovalManager(audit_logger=audit_logger, id_factory=CounterIdFactory()),
    )


def test_service_surfaces_broken_audit_chain(tmp_path):
    audit_file = tmp_path / "api_audit_integrity.jsonl"
    service = _build_service(audit_file)
    request = {
        "run_id": "audit-int",
        "actor": "tester",
        "action": "read_status",
        "tool": "shell",
        "command": "ls",
        "payload": {"note": "ok"},
        "dry_run": True,
    }

    first = service.execute_guarded_request(request)
    assert first["audit_integrity"]["valid"] is True
    assert first["blocked"] is False

    lines = [line for line in audit_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    tampered = json.loads(lines[0])
    tampered["actor"] = "tampered-actor"
    lines[0] = json.dumps(tampered, sort_keys=True, ensure_ascii=True)
    audit_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    second = service.execute_guarded_request({**request, "run_id": "audit-int-2"})
    assert second["audit_integrity"]["valid"] is False
    assert "audit_integrity:BROKEN_CHAIN" in second["blockers"]
    assert second["blocked"] is True
    assert second["observability"]["counters"]["audit_integrity:BROKEN"] >= 1

