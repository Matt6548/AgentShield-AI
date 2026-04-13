import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.service import GuardedExecutionService
from src.approval import ApprovalEscalation, ApprovalManager, EscalationPolicy
from src.audit import AuditLogger
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.policy import PolicyEngine
from src.utils.tool_policies import ToolGuard


class MutableClock:
    def __init__(self, start: datetime) -> None:
        self.current = start

    def __call__(self) -> datetime:
        return self.current

    def advance(self, seconds: int) -> None:
        self.current = self.current + timedelta(seconds=seconds)


class CounterIdFactory:
    def __init__(self) -> None:
        self.value = 0

    def __call__(self) -> str:
        self.value += 1
        return f"apr-{self.value:04d}"


def _build_service(audit_file: Path, clock: MutableClock) -> GuardedExecutionService:
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    approval_manager = ApprovalManager(
        audit_logger=audit_logger,
        id_factory=CounterIdFactory(),
        now_fn=clock,
    )
    approval_escalation = ApprovalEscalation(
        approval_manager=approval_manager,
        policy=EscalationPolicy(
            escalate_after_seconds=5,
            expire_after_seconds=10,
            escalation_target="security-oncall",
        ),
        now_fn=clock,
    )
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=approval_manager,
        approval_escalation=approval_escalation,
    )


def test_service_escalation_path_remains_blocked_until_explicit_approved(tmp_path):
    clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    audit_file = tmp_path / "api_escalation_service.jsonl"
    service = _build_service(audit_file, clock)
    base_request = {
        "run_id": "api-escalation-1",
        "actor": "operator",
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
    assert pending["approval"]["escalation"]["state"] == "NONE"
    request_id = pending["approval"]["request_id"]
    assert request_id is not None

    clock.advance(6)
    escalated = service.execute_guarded_request(
        {
            **base_request,
            "approval": {"request_id": request_id},
        }
    )
    assert escalated["blocked"] is True
    assert escalated["approval"]["status"] == "PENDING"
    assert escalated["approval"]["escalation"]["state"] == "ESCALATED"
    assert escalated["execution_result"]["output"]["status"] == "BLOCKED"
    assert "approval:PENDING" in escalated["blockers"]

    clock.advance(6)
    expired = service.execute_guarded_request(
        {
            **base_request,
            "approval": {"request_id": request_id},
        }
    )
    assert expired["blocked"] is True
    assert expired["approval"]["status"] == "PENDING"
    assert expired["approval"]["escalation"]["state"] == "EXPIRED"
    assert expired["execution_result"]["output"]["status"] == "BLOCKED"
    assert expired["observability"]["counters"]["escalation:EXPIRED"] == 1

    approved = service.execute_guarded_request(
        {
            **base_request,
            "approval": {
                "request_id": request_id,
                "decision": "APPROVED",
                "approver": "security.lead",
                "reason": "explicit approval",
            },
        }
    )
    assert approved["blocked"] is False
    assert approved["approval"]["status"] == "APPROVED"
    assert approved["execution_result"]["success"] is True
    assert approved["approval"]["escalation"]["state"] == "NONE"

    actions = [
        json.loads(line)["action"]
        for line in audit_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert "approval_escalation_updated" in actions
    assert "approval_decided" in actions


def test_api_endpoint_supports_pending_escalation_check_without_decision(tmp_path):
    clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    service = _build_service(tmp_path / "api_escalation_endpoint.jsonl", clock)
    client = TestClient(create_app(service=service))

    base_payload = {
        "run_id": "api-escalation-2",
        "actor": "operator",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"feature": "beta"},
        "dry_run": True,
    }

    pending = client.post("/v1/guarded-execute", json=base_payload).json()
    request_id = pending["approval"]["request_id"]
    assert pending["approval"]["status"] == "PENDING"
    assert pending["blocked"] is True

    clock.advance(6)
    escalated = client.post(
        "/v1/guarded-execute",
        json={
            **base_payload,
            "approval": {"request_id": request_id},
        },
    ).json()

    assert escalated["approval"]["status"] == "PENDING"
    assert escalated["approval"]["escalation"]["state"] == "ESCALATED"
    assert escalated["blocked"] is True

