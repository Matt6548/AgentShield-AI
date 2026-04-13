"""Approval manager foundation for SafeCore."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from src.audit import AuditLogger
from src.approval.escalation_policies import (
    ESCALATION_STATE_NONE,
    VALID_ESCALATION_STATES,
)
from src.approval.approvers import (
    APPROVAL_STATUS_APPROVED,
    APPROVAL_STATUS_PENDING,
    APPROVAL_STATUS_REJECTED,
    normalize_approval_status,
)
from src.policy.policy_engine import (
    DECISION_ALLOW,
    DECISION_DENY,
    DECISION_NEEDS_APPROVAL,
    RISK_ALLOW_MAX,
    RISK_NEEDS_APPROVAL_MAX,
)


class ApprovalManager:
    """Manage in-memory approval requests and decisions."""

    def __init__(
        self,
        audit_logger: AuditLogger | None = None,
        id_factory: Callable[[], str] | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.audit_logger = audit_logger or AuditLogger()
        self._id_factory = id_factory or self._default_id_factory
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._requests: dict[str, dict[str, Any]] = {}

    def create_request(self, context: dict[str, Any]) -> dict[str, Any]:
        """Create a pending approval request from policy context."""
        if not isinstance(context, dict):
            raise TypeError("ApprovalManager.create_request expects a dict context.")

        request_id = self._id_factory()
        created_at = self._now_iso()
        policy_decision = str(context.get("policy_decision", "")).upper()
        risk_score = self._to_int(context.get("risk_score", 0))
        if policy_decision != DECISION_NEEDS_APPROVAL:
            raise ValueError("Approval requests can only be created for NEEDS_APPROVAL decisions.")

        request = {
            "request_id": request_id,
            "created_at": created_at,
            "status": APPROVAL_STATUS_PENDING,
            "policy_decision": policy_decision,
            "risk_score": risk_score,
            "context": copy.deepcopy(context),
            "approver": None,
            "reason": "",
            "decided_at": None,
            "escalation_state": ESCALATION_STATE_NONE,
            "escalation_target": None,
            "escalation_reason": "",
            "escalation_updated_at": None,
            "escalation_elapsed_seconds": 0,
        }
        self._requests[request_id] = request

        self._write_audit(
            action="approval_request_created",
            context=context,
            data={
                "request_id": request_id,
                "status": APPROVAL_STATUS_PENDING,
                "policy_decision": policy_decision,
                "risk_score": risk_score,
            },
        )
        return copy.deepcopy(request)

    def decide(
        self,
        request_id: str,
        decision: str,
        approver: str,
        reason: str = "",
    ) -> dict[str, Any]:
        """Apply an APPROVED/REJECTED decision to a pending approval request."""
        request = self._requests.get(request_id)
        if request is None:
            raise KeyError(f"Approval request '{request_id}' was not found.")

        normalized_decision = normalize_approval_status(decision)
        if normalized_decision == APPROVAL_STATUS_PENDING:
            raise ValueError("Cannot set decision to PENDING via decide().")
        if request["status"] != APPROVAL_STATUS_PENDING:
            raise ValueError("Only pending approval requests can be decided.")

        policy_decision = str(request["policy_decision"]).upper()
        if policy_decision == DECISION_ALLOW:
            raise ValueError("ALLOW decisions bypass approval and cannot be manually decided.")
        if policy_decision == DECISION_DENY and normalized_decision == APPROVAL_STATUS_APPROVED:
            raise ValueError("DENY decisions are not overridable in this iteration.")

        request["status"] = normalized_decision
        request["approver"] = str(approver)
        request["reason"] = str(reason)
        request["decided_at"] = self._now_iso()
        request["escalation_state"] = ESCALATION_STATE_NONE
        request["escalation_target"] = None
        request["escalation_reason"] = "Approval decision finalized."
        request["escalation_updated_at"] = request["decided_at"]
        request["escalation_elapsed_seconds"] = int(request.get("escalation_elapsed_seconds", 0))

        self._write_audit(
            action="approval_decided",
            context=request["context"],
            data={
                "request_id": request_id,
                "status": normalized_decision,
                "approver": request["approver"],
                "reason": request["reason"],
                "policy_decision": policy_decision,
            },
        )
        return copy.deepcopy(request)

    def get_request(self, request_id: str) -> dict[str, Any] | None:
        """Return an approval request by ID if it exists."""
        request = self._requests.get(request_id)
        return copy.deepcopy(request) if request else None

    def is_required(self, risk_score: int, policy_decision: str) -> bool:
        """Return whether explicit approval is required."""
        normalized_decision = str(policy_decision).upper()
        if normalized_decision == DECISION_NEEDS_APPROVAL:
            return True
        if normalized_decision in {DECISION_ALLOW, DECISION_DENY}:
            return False

        # Defensive fallback: align to policy threshold constants.
        score = self._to_int(risk_score)
        return RISK_ALLOW_MAX < score <= RISK_NEEDS_APPROVAL_MAX

    def set_escalation_state(
        self,
        request_id: str,
        escalation_state: str,
        escalation_target: str | None,
        reason: str = "",
        elapsed_seconds: int = 0,
    ) -> dict[str, Any]:
        """Update escalation metadata for a pending NEEDS_APPROVAL request."""
        request = self._requests.get(request_id)
        if request is None:
            raise KeyError(f"Approval request '{request_id}' was not found.")

        if request["status"] != APPROVAL_STATUS_PENDING:
            raise ValueError("Escalation can only be applied to pending approval requests.")
        if str(request["policy_decision"]).upper() != DECISION_NEEDS_APPROVAL:
            raise ValueError("Escalation applies only to NEEDS_APPROVAL requests.")

        normalized_state = str(escalation_state).upper()
        if normalized_state not in VALID_ESCALATION_STATES:
            raise ValueError(
                f"Unsupported escalation_state '{escalation_state}'. "
                f"Expected one of {sorted(VALID_ESCALATION_STATES)}."
            )

        previous_state = str(request.get("escalation_state", ESCALATION_STATE_NONE)).upper()
        if (
            previous_state == normalized_state
            and request.get("escalation_target") == escalation_target
            and str(request.get("escalation_reason", "")) == str(reason)
            and int(request.get("escalation_elapsed_seconds", 0)) == int(elapsed_seconds)
        ):
            return copy.deepcopy(request)

        request["escalation_state"] = normalized_state
        request["escalation_target"] = str(escalation_target) if escalation_target else None
        request["escalation_reason"] = str(reason)
        request["escalation_updated_at"] = self._now_iso()
        request["escalation_elapsed_seconds"] = max(0, self._to_int(elapsed_seconds))

        self._write_audit(
            action="approval_escalation_updated",
            context=request["context"],
            data={
                "request_id": request_id,
                "status": request["status"],
                "previous_escalation_state": previous_state,
                "escalation_state": normalized_state,
                "escalation_target": request["escalation_target"],
                "reason": request["escalation_reason"],
                "elapsed_seconds": request["escalation_elapsed_seconds"],
            },
        )
        return copy.deepcopy(request)

    def _write_audit(self, action: str, context: dict[str, Any], data: dict[str, Any]) -> None:
        run_id = str(context.get("run_id", "approval-run"))
        actor = str(context.get("actor", "approval-system"))
        self.audit_logger.append_record(
            {
                "run_id": run_id,
                "actor": actor,
                "step": "approval",
                "action": action,
                "data": data,
            }
        )

    def _now_iso(self) -> str:
        return self._now_fn().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def _to_int(self, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _default_id_factory(self) -> str:
        return f"apr-{uuid4().hex[:12]}"
