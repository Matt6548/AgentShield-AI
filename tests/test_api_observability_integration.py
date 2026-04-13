import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
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
    approval_manager = ApprovalManager(audit_logger=audit_logger, id_factory=CounterIdFactory())
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=approval_manager,
    )


def test_service_safe_path_returns_route_connector_and_observability(tmp_path):
    audit_file = tmp_path / "obs_safe.jsonl"
    service = _build_service(audit_file)
    response = service.execute_guarded_request(
        {
            "run_id": "obs-safe",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "payload": {"note": "ok"},
            "dry_run": True,
        }
    )

    assert response["blocked"] is False
    assert response["model_route"]["route_id"] == "route_allow_fast_read"
    assert response["connector_execution"]["status"] == "DRY_RUN_SIMULATED"
    assert response["observability"]["event_count"] >= 8
    assert response["observability"]["counters"]["policy:ALLOW"] == 1
    assert response["observability"]["counters"]["audit:RECORDED"] == 1


def test_service_blocked_path_emits_observability_and_audit(tmp_path):
    audit_file = tmp_path / "obs_blocked.jsonl"
    service = _build_service(audit_file)
    response = service.execute_guarded_request(
        {
            "run_id": "obs-blocked",
            "actor": "tester",
            "action": "delete_everything",
            "tool": "shell",
            "command": "rm -rf /",
            "payload": {"note": "danger"},
            "dry_run": True,
        }
    )

    assert response["blocked"] is True
    assert response["policy_decision"]["decision"] == "DENY"
    assert response["connector_execution"]["status"] == "BLOCKED"
    assert response["observability"]["counters"]["policy:DENY"] == 1
    assert response["audit_record"]["action"] == "api_guarded_execute"

    lines = [line for line in audit_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines
    assert json.loads(lines[-1])["action"] == "api_guarded_execute"


def test_api_endpoint_includes_route_and_connector_fields(tmp_path):
    service = _build_service(tmp_path / "obs_api.jsonl")
    client = TestClient(create_app(service=service))

    response = client.post(
        "/v1/guarded-execute",
        json={
            "run_id": "obs-api",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "pwd",
            "payload": {"note": "ok"},
            "dry_run": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "model_route" in body
    assert "connector_execution" in body
    assert "observability" in body
    assert body["connector_execution"]["status"] == "DRY_RUN_SIMULATED"

