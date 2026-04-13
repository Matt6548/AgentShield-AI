from datetime import datetime, timedelta, timezone
from pathlib import Path

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
        self.counter = 0

    def __call__(self) -> str:
        self.counter += 1
        return f"apr-{self.counter:04d}"


def _build_service(audit_file: Path, clock: MutableClock | None = None) -> GuardedExecutionService:
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    now_fn = clock if clock is not None else None
    approval_manager = ApprovalManager(
        audit_logger=audit_logger,
        id_factory=CounterIdFactory(),
        now_fn=now_fn,
    )
    escalation = ApprovalEscalation(
        approval_manager=approval_manager,
        policy=EscalationPolicy(
            escalate_after_seconds=5,
            expire_after_seconds=10,
            escalation_target="security-oncall",
        ),
        now_fn=now_fn,
    )
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=approval_manager,
        approval_escalation=escalation,
    )


def test_deny_never_executes_even_if_approval_payload_is_present(tmp_path):
    service = _build_service(tmp_path / "deny_never_executes.jsonl")
    response = service.execute_guarded_request(
        {
            "run_id": "sec-deny",
            "actor": "tester",
            "action": "delete_everything",
            "tool": "shell",
            "command": "rm -rf /",
            "payload": {"note": "danger"},
            "dry_run": True,
            "approval": {
                "request_id": "apr-irrelevant",
                "decision": "APPROVED",
                "approver": "security.lead",
                "reason": "should be ignored for DENY",
            },
        }
    )

    assert response["blocked"] is True
    assert response["policy_decision"]["decision"] == "DENY"
    assert response["approval"]["status"] == "NOT_APPLICABLE_DENY"
    assert response["execution_result"]["output"]["status"] == "BLOCKED"


def test_needs_approval_never_executes_without_explicit_approved(tmp_path):
    clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    service = _build_service(tmp_path / "needs_approval_invariant.jsonl", clock=clock)

    base_request = {
        "run_id": "sec-approval",
        "actor": "operator",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"feature": "alpha"},
        "dry_run": True,
    }
    pending = service.execute_guarded_request(base_request)
    request_id = pending["approval"]["request_id"]
    assert pending["approval"]["status"] == "PENDING"
    assert pending["blocked"] is True

    clock.advance(11)
    expired = service.execute_guarded_request(
        {
            **base_request,
            "approval": {"request_id": request_id},
        }
    )
    assert expired["approval"]["status"] == "PENDING"
    assert expired["approval"]["escalation"]["state"] == "EXPIRED"
    assert expired["blocked"] is True
    assert expired["execution_result"]["output"]["status"] == "BLOCKED"


def test_only_explicit_approved_can_unblock_when_other_guards_allow(tmp_path):
    clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    service = _build_service(tmp_path / "explicit_approved_unblocks.jsonl", clock=clock)

    base_request = {
        "run_id": "sec-approved",
        "actor": "operator",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"feature": "beta"},
        "dry_run": True,
    }
    pending = service.execute_guarded_request(base_request)
    request_id = pending["approval"]["request_id"]
    assert pending["blocked"] is True

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
    assert approved["approval"]["status"] == "APPROVED"
    assert approved["blocked"] is False
    assert approved["execution_result"]["output"]["status"] == "DRY_RUN_SIMULATED"

