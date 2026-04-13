"""Profile selector abstraction for model-router policy profiles."""

from __future__ import annotations

from typing import Any

from src.model_router.profiles import (
    PROFILE_GUARDED_STANDARD,
    PROFILE_HIGH_RISK_REVIEW,
    PROFILE_RESTRICTED_NO_EXECUTE,
    PROFILE_SAFE_LOW_RISK,
    get_profile_definition,
)
from src.policy.policy_engine import DECISION_DENY, DECISION_NEEDS_APPROVAL, RISK_ALLOW_MAX, RISK_NEEDS_APPROVAL_MAX


class ProfileSelector:
    """Deterministic selector for model-router policy profiles."""

    def select_profile(
        self,
        *,
        decision: str,
        risk_score: int,
        action_class: str,
        environment: str,
    ) -> dict[str, Any]:
        """Select one profile from current context and return profile metadata."""
        try:
            bounded_risk = int(risk_score)
        except (TypeError, ValueError):
            bounded_risk = 0
        decision_upper = str(decision or "").upper()
        action = str(action_class or "").upper()
        env = str(environment or "").lower()

        profile_id = PROFILE_GUARDED_STANDARD
        reason = "Default guarded profile selected."

        if decision_upper == DECISION_DENY or bounded_risk > RISK_NEEDS_APPROVAL_MAX:
            profile_id = PROFILE_RESTRICTED_NO_EXECUTE
            reason = "Denied/high-risk path mapped to restricted no-execute profile."
        elif decision_upper == DECISION_NEEDS_APPROVAL or bounded_risk > RISK_ALLOW_MAX:
            if action == "CHANGE" and env in {"prod", "production"}:
                profile_id = PROFILE_HIGH_RISK_REVIEW
                reason = "Production change approval path mapped to high-risk review profile."
            else:
                profile_id = PROFILE_GUARDED_STANDARD
                reason = "Approval-level path mapped to guarded standard profile."
        elif action == "READ_ONLY":
            profile_id = PROFILE_SAFE_LOW_RISK
            reason = "Low-risk read-only path mapped to safe low-risk profile."
        else:
            profile_id = PROFILE_GUARDED_STANDARD
            reason = "Low-risk non-read path mapped to guarded standard profile."

        profile = get_profile_definition(profile_id)
        profile["selection_reason"] = reason
        return profile
