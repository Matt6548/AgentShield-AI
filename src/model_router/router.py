"""Model router foundation for SafeCore."""

from __future__ import annotations

from typing import Any

from src.model_router.profile_selector import ProfileSelector
from src.model_router.policies import choose_route, classify_action_class


class ModelRouter:
    """Deterministic model router that maps policy context to route profiles."""

    def __init__(self, profile_selector: ProfileSelector | None = None) -> None:
        self.profile_selector = profile_selector or ProfileSelector()

    def route(self, policy_decision: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Return a stable model route object."""
        if not isinstance(policy_decision, dict):
            raise TypeError("ModelRouter.route expects policy_decision to be a dict.")
        if not isinstance(context, dict):
            raise TypeError("ModelRouter.route expects context to be a dict.")

        risk_score = int(policy_decision.get("risk_score", 0))
        decision = str(policy_decision.get("decision", ""))
        action = str(context.get("action", ""))
        tool = str(context.get("tool", ""))
        command = str(context.get("command", ""))
        environment = str(context.get("environment", context.get("env", "")))

        action_class = classify_action_class(action=action, tool=tool, command=command)
        route = choose_route(
            risk_score=risk_score,
            decision=decision,
            action_class=action_class,
            environment=environment,
        )
        profile = self.profile_selector.select_profile(
            decision=decision,
            risk_score=risk_score,
            action_class=action_class,
            environment=environment,
        )
        route["action_class"] = action_class
        route["profile_id"] = profile["profile_id"]
        route["profile_name"] = profile["profile_name"]
        route["profile_reason"] = profile["selection_reason"]
        route["profile_guardrails"] = profile["guardrails"]
        return route
