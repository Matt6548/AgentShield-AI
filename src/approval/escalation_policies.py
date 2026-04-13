"""Escalation policy primitives for unresolved approval requests."""

from __future__ import annotations

from dataclasses import dataclass


ESCALATION_STATE_NONE = "NONE"
ESCALATION_STATE_ESCALATED = "ESCALATED"
ESCALATION_STATE_EXPIRED = "EXPIRED"
VALID_ESCALATION_STATES = {
    ESCALATION_STATE_NONE,
    ESCALATION_STATE_ESCALATED,
    ESCALATION_STATE_EXPIRED,
}


@dataclass(frozen=True)
class EscalationPolicy:
    """Deterministic timeout policy for pending approvals."""

    escalate_after_seconds: int = 300
    expire_after_seconds: int = 900
    escalation_target: str = "security-oncall"

    def __post_init__(self) -> None:
        if self.escalate_after_seconds < 0:
            raise ValueError("escalate_after_seconds must be >= 0")
        if self.expire_after_seconds < self.escalate_after_seconds:
            raise ValueError(
                "expire_after_seconds must be >= escalate_after_seconds"
            )

    def classify(self, elapsed_seconds: int) -> str:
        """Classify escalation state from elapsed pending time."""
        elapsed = max(0, int(elapsed_seconds))
        if elapsed >= self.expire_after_seconds:
            return ESCALATION_STATE_EXPIRED
        if elapsed >= self.escalate_after_seconds:
            return ESCALATION_STATE_ESCALATED
        return ESCALATION_STATE_NONE
