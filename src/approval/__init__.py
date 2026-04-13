"""Approval module entrypoints for SafeCore."""

from src.approval.approval_manager import ApprovalManager
from src.approval.approvers import (
    APPROVAL_STATUS_APPROVED,
    APPROVAL_STATUS_PENDING,
    APPROVAL_STATUS_REJECTED,
)
from src.approval.escalation import ApprovalEscalation
from src.approval.escalation_policies import (
    ESCALATION_STATE_ESCALATED,
    ESCALATION_STATE_EXPIRED,
    ESCALATION_STATE_NONE,
    EscalationPolicy,
)

__all__ = [
    "ApprovalManager",
    "ApprovalEscalation",
    "EscalationPolicy",
    "APPROVAL_STATUS_PENDING",
    "APPROVAL_STATUS_APPROVED",
    "APPROVAL_STATUS_REJECTED",
    "ESCALATION_STATE_NONE",
    "ESCALATION_STATE_ESCALATED",
    "ESCALATION_STATE_EXPIRED",
]
