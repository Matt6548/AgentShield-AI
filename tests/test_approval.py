import json
from datetime import datetime, timezone

import pytest

from src.approval import (
    APPROVAL_STATUS_APPROVED,
    APPROVAL_STATUS_PENDING,
    ApprovalManager,
)
from src.audit import AuditLogger
from src.policy.policy_engine import DECISION_ALLOW, DECISION_DENY, DECISION_NEEDS_APPROVAL


def test_create_request_persists_pending_request_and_writes_audit(tmp_path):
    audit_file = tmp_path / "approval_audit.jsonl"
    manager = ApprovalManager(
        audit_logger=AuditLogger(audit_file),
        id_factory=lambda: "apr-0001",
        now_fn=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    request = manager.create_request(
        {
            "run_id": "run-1",
            "actor": "tester",
            "policy_decision": DECISION_NEEDS_APPROVAL,
            "risk_score": 60,
            "action": "change_config",
        }
    )

    assert request["request_id"] == "apr-0001"
    assert request["status"] == APPROVAL_STATUS_PENDING
    assert request["policy_decision"] == DECISION_NEEDS_APPROVAL
    assert request["risk_score"] == 60

    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    created_event = json.loads(lines[0])
    assert created_event["action"] == "approval_request_created"


def test_decide_updates_request_and_writes_decision_audit(tmp_path):
    audit_file = tmp_path / "approval_audit.jsonl"
    manager = ApprovalManager(
        audit_logger=AuditLogger(audit_file),
        id_factory=lambda: "apr-0002",
        now_fn=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    created = manager.create_request(
        {
            "run_id": "run-2",
            "actor": "tester",
            "policy_decision": DECISION_NEEDS_APPROVAL,
            "risk_score": 55,
            "action": "deploy",
        }
    )

    decided = manager.decide(created["request_id"], "approved", approver="alice", reason="ticket ok")

    assert decided["status"] == APPROVAL_STATUS_APPROVED
    assert decided["approver"] == "alice"
    assert decided["reason"] == "ticket ok"
    assert decided["decided_at"] is not None

    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    actions = [json.loads(line)["action"] for line in lines]
    assert actions == ["approval_request_created", "approval_decided"]


def test_create_request_rejects_non_needs_approval_policy_decision(tmp_path):
    manager = ApprovalManager(
        audit_logger=AuditLogger(tmp_path / "approval_audit.jsonl"),
        id_factory=lambda: "apr-0003",
    )

    with pytest.raises(ValueError, match="only be created for NEEDS_APPROVAL"):
        manager.create_request(
            {
                "run_id": "run-3",
                "actor": "tester",
                "policy_decision": DECISION_DENY,
                "risk_score": 90,
                "action": "delete",
            }
        )


def test_is_required_respects_policy_decision_and_threshold_alignment(tmp_path):
    manager = ApprovalManager(audit_logger=AuditLogger(tmp_path / "approval_audit.jsonl"))

    assert manager.is_required(50, DECISION_NEEDS_APPROVAL) is True
    assert manager.is_required(10, DECISION_ALLOW) is False
    assert manager.is_required(90, DECISION_DENY) is False
    # Defensive fallback for unknown decision values uses baseline risk thresholds.
    assert manager.is_required(50, "UNKNOWN") is True
    assert manager.is_required(10, "UNKNOWN") is False


def test_get_request_returns_none_for_missing_id(tmp_path):
    manager = ApprovalManager(audit_logger=AuditLogger(tmp_path / "approval_audit.jsonl"))
    assert manager.get_request("missing-id") is None
    _ = manager.create_request(
        {
            "run_id": "run-4",
            "actor": "tester",
            "policy_decision": DECISION_NEEDS_APPROVAL,
            "risk_score": 45,
            "action": "change",
        }
    )
    assert manager.get_request("missing-id") is None
    assert manager.get_request("apr-does-not-exist") is None
