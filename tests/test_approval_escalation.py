import json
from datetime import datetime, timedelta, timezone

from src.approval import (
    APPROVAL_STATUS_APPROVED,
    APPROVAL_STATUS_PENDING,
    ApprovalEscalation,
    ApprovalManager,
    EscalationPolicy,
)
from src.audit import AuditLogger
from src.policy.policy_engine import DECISION_NEEDS_APPROVAL


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


def test_escalation_transitions_pending_to_escalated_to_expired_with_audit(tmp_path):
    clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    audit_file = tmp_path / "escalation_audit.jsonl"
    manager = ApprovalManager(
        audit_logger=AuditLogger(audit_file),
        id_factory=CounterIdFactory(),
        now_fn=clock,
    )
    escalation = ApprovalEscalation(
        approval_manager=manager,
        policy=EscalationPolicy(
            escalate_after_seconds=10,
            expire_after_seconds=20,
            escalation_target="security-oncall",
        ),
        now_fn=clock,
    )

    created = manager.create_request(
        {
            "run_id": "escalation-run-1",
            "actor": "operator",
            "policy_decision": DECISION_NEEDS_APPROVAL,
            "risk_score": 55,
            "context": {"action": "change_config"},
        }
    )
    assert created["status"] == APPROVAL_STATUS_PENDING
    assert created["escalation_state"] == "NONE"

    clock.advance(12)
    escalated = escalation.evaluate_request(created["request_id"])
    assert escalated is not None
    assert escalated["status"] == APPROVAL_STATUS_PENDING
    assert escalated["escalation_state"] == "ESCALATED"

    clock.advance(10)
    expired = escalation.evaluate_request(created["request_id"])
    assert expired is not None
    assert expired["status"] == APPROVAL_STATUS_PENDING
    assert expired["escalation_state"] == "EXPIRED"

    actions = [
        json.loads(line)["action"]
        for line in audit_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert actions.count("approval_escalation_updated") == 2


def test_escalation_never_authorizes_execution_without_explicit_approved(tmp_path):
    clock = MutableClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    manager = ApprovalManager(
        audit_logger=AuditLogger(tmp_path / "escalation_guard.jsonl"),
        id_factory=CounterIdFactory(),
        now_fn=clock,
    )
    escalation = ApprovalEscalation(
        approval_manager=manager,
        policy=EscalationPolicy(
            escalate_after_seconds=5,
            expire_after_seconds=10,
            escalation_target="security-oncall",
        ),
        now_fn=clock,
    )

    created = manager.create_request(
        {
            "run_id": "escalation-run-2",
            "actor": "operator",
            "policy_decision": DECISION_NEEDS_APPROVAL,
            "risk_score": 55,
            "context": {"action": "change_config"},
        }
    )
    clock.advance(11)
    expired = escalation.evaluate_request(created["request_id"])
    assert expired is not None
    assert expired["escalation_state"] == "EXPIRED"
    assert expired["status"] == APPROVAL_STATUS_PENDING

    approved = manager.decide(
        created["request_id"],
        decision="APPROVED",
        approver="security.lead",
        reason="explicit approval",
    )
    assert approved["status"] == APPROVAL_STATUS_APPROVED

