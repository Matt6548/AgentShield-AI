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


def _build_client(audit_file: Path) -> TestClient:
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    service = GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=ApprovalManager(audit_logger=audit_logger, id_factory=CounterIdFactory()),
    )
    app = create_app(service=service)
    return TestClient(app)


def test_health_endpoint(tmp_path):
    client = _build_client(tmp_path / "health_api_audit.jsonl")
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["dry_run_only"] is True


def test_guarded_execute_safe_path(tmp_path):
    client = _build_client(tmp_path / "api_safe.jsonl")
    response = client.post(
        "/v1/guarded-execute",
        json={
            "run_id": "api-safe",
            "actor": "tester",
            "action": "read_status",
            "tool": "shell",
            "command": "ls",
            "payload": {"note": "ok"},
            "dry_run": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["blocked"] is False
    assert body["execution_result"]["output"]["status"] == "DRY_RUN_SIMULATED"


def test_guarded_execute_approval_pending_approved_rejected(tmp_path):
    client = _build_client(tmp_path / "api_approval.jsonl")
    base_payload = {
        "run_id": "api-approval",
        "actor": "tester",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"flag": "alpha"},
        "dry_run": True,
    }

    pending = client.post("/v1/guarded-execute", json=base_payload)
    assert pending.status_code == 200
    pending_body = pending.json()
    assert pending_body["approval"]["status"] == "PENDING"
    assert pending_body["blocked"] is True
    request_id = pending_body["approval"]["request_id"]

    approved = client.post(
        "/v1/guarded-execute",
        json={
            **base_payload,
            "approval": {
                "request_id": request_id,
                "decision": "APPROVED",
                "approver": "security.lead",
                "reason": "ok",
            },
        },
    )
    assert approved.status_code == 200
    approved_body = approved.json()
    assert approved_body["approval"]["status"] == "APPROVED"
    assert approved_body["blocked"] is False

    pending_second = client.post(
        "/v1/guarded-execute",
        json={**base_payload, "run_id": "api-approval-2"},
    ).json()
    rejected = client.post(
        "/v1/guarded-execute",
        json={
            **base_payload,
            "run_id": "api-approval-2",
            "approval": {
                "request_id": pending_second["approval"]["request_id"],
                "decision": "REJECTED",
                "approver": "security.lead",
                "reason": "not approved",
            },
        },
    )
    rejected_body = rejected.json()
    assert rejected_body["approval"]["status"] == "REJECTED"
    assert rejected_body["blocked"] is True


def test_guarded_execute_deny_path_stays_blocked(tmp_path):
    client = _build_client(tmp_path / "api_deny.jsonl")
    response = client.post(
        "/v1/guarded-execute",
        json={
            "run_id": "api-deny",
            "actor": "tester",
            "action": "delete_everything",
            "tool": "shell",
            "command": "rm -rf /",
            "payload": {"note": "danger"},
            "dry_run": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["policy_decision"]["decision"] == "DENY"
    assert body["approval"]["status"] == "NOT_APPLICABLE_DENY"
    assert body["blocked"] is True
    assert body["execution_result"]["output"]["status"] == "BLOCKED"
