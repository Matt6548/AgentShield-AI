"""Deterministic routing policies for SafeCore model routing."""

from __future__ import annotations

from typing import Any

from src.policy.policy_engine import (
    DECISION_DENY,
    DECISION_NEEDS_APPROVAL,
    RISK_MAX,
    RISK_MIN,
    RISK_ALLOW_MAX,
    RISK_NEEDS_APPROVAL_MAX,
)


ACTION_CLASS_READ_ONLY = "READ_ONLY"
ACTION_CLASS_CHANGE = "CHANGE"
ACTION_CLASS_DESTRUCTIVE = "DESTRUCTIVE"
ACTION_CLASS_GENERAL = "GENERAL"

READ_ONLY_HINTS = ("read", "list", "get", "fetch", "describe", "inspect", "view", "query")
CHANGE_HINTS = ("change", "update", "modify", "deploy", "restart", "write", "configure")
DESTRUCTIVE_HINTS = ("delete", "destroy", "drop", "truncate", "wipe", "shutdown", "reboot")


def classify_action_class(action: str, tool: str, command: str) -> str:
    """Classify action class from plain-text action/tool/command context."""
    combined = " ".join([action, tool, command]).lower()
    if any(hint in combined for hint in DESTRUCTIVE_HINTS):
        return ACTION_CLASS_DESTRUCTIVE
    if any(hint in combined for hint in CHANGE_HINTS):
        return ACTION_CLASS_CHANGE
    if any(hint in combined for hint in READ_ONLY_HINTS):
        return ACTION_CLASS_READ_ONLY
    return ACTION_CLASS_GENERAL


def choose_route(
    *,
    risk_score: int,
    decision: str,
    action_class: str,
    environment: str,
) -> dict[str, Any]:
    """Choose a deterministic model route based on policy context."""
    bounded_risk = max(RISK_MIN, min(RISK_MAX, int(risk_score)))
    env = (environment or "").lower()
    decision_upper = (decision or "").upper()

    if decision_upper == DECISION_DENY or bounded_risk > RISK_NEEDS_APPROVAL_MAX:
        return {
            "route_id": "route_deny_guard",
            "model_profile": "deny_guard",
            "reason": "High-risk or denied action routed to strict deny profile.",
            "constraints": [
                "Do not execute external side effects.",
                "Require manual policy review before retry.",
            ],
        }

    if decision_upper == DECISION_NEEDS_APPROVAL or bounded_risk > RISK_ALLOW_MAX:
        if action_class == ACTION_CLASS_CHANGE and env in {"prod", "production"}:
            return {
                "route_id": "route_approval_prod_change",
                "model_profile": "review_strict",
                "reason": "Production change requires strict review routing.",
                "constraints": [
                    "Block execution until explicit approval.",
                    "Require operator rollback validation.",
                ],
            }
        return {
            "route_id": "route_approval_general",
            "model_profile": "review_standard",
            "reason": "Medium-risk path routed for approval-oriented review.",
            "constraints": [
                "Require approval before execution.",
            ],
        }

    if action_class == ACTION_CLASS_READ_ONLY:
        return {
            "route_id": "route_allow_fast_read",
            "model_profile": "safe_fast_read",
            "reason": "Low-risk read-only path routed to fast safe profile.",
            "constraints": ["Read-only operations only."],
        }

    return {
        "route_id": "route_allow_standard",
        "model_profile": "safe_standard",
        "reason": "Low-risk general path routed to standard safe profile.",
        "constraints": ["Keep dry_run-first posture."],
    }
