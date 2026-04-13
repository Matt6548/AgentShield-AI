"""Approval escalation evaluator for pending NEEDS_APPROVAL requests."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from src.approval.approval_manager import ApprovalManager
from src.approval.approvers import APPROVAL_STATUS_PENDING
from src.approval.escalation_policies import (
    ESCALATION_STATE_ESCALATED,
    ESCALATION_STATE_EXPIRED,
    ESCALATION_STATE_NONE,
    EscalationPolicy,
)
from src.policy.policy_engine import DECISION_NEEDS_APPROVAL


class ApprovalEscalation:
    """Apply deterministic escalation transitions for pending approvals."""

    def __init__(
        self,
        approval_manager: ApprovalManager,
        policy: EscalationPolicy | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.approval_manager = approval_manager
        self.policy = policy or EscalationPolicy()
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))

    def evaluate_request(self, request_id: str) -> dict | None:
        """Evaluate escalation state for a single approval request."""
        request = self.approval_manager.get_request(request_id)
        if request is None:
            return None

        if request.get("status") != APPROVAL_STATUS_PENDING:
            return request
        if str(request.get("policy_decision", "")).upper() != DECISION_NEEDS_APPROVAL:
            return request

        elapsed_seconds = self._pending_elapsed_seconds(request)
        desired_state = self.policy.classify(elapsed_seconds)
        current_state = str(request.get("escalation_state", ESCALATION_STATE_NONE)).upper()

        if desired_state == current_state:
            return request

        reason = self._reason_for_transition(desired_state, elapsed_seconds)
        return self.approval_manager.set_escalation_state(
            request_id=request_id,
            escalation_state=desired_state,
            escalation_target=self.policy.escalation_target,
            reason=reason,
            elapsed_seconds=elapsed_seconds,
        )

    def _pending_elapsed_seconds(self, request: dict) -> int:
        created_at = str(request.get("created_at", ""))
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            created_dt = self._now_fn().astimezone(timezone.utc)

        now = self._now_fn().astimezone(timezone.utc)
        elapsed = int((now - created_dt).total_seconds())
        return max(0, elapsed)

    def _reason_for_transition(self, state: str, elapsed_seconds: int) -> str:
        if state == ESCALATION_STATE_ESCALATED:
            return (
                "Pending approval exceeded "
                f"{self.policy.escalate_after_seconds}s escalation threshold."
            )
        if state == ESCALATION_STATE_EXPIRED:
            return (
                "Pending approval exceeded "
                f"{self.policy.expire_after_seconds}s expiration threshold."
            )
        return f"Escalation reset at {elapsed_seconds}s pending time."
