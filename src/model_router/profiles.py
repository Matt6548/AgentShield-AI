"""Model-router profile definitions for deterministic routing behavior."""

from __future__ import annotations

from typing import Any


PROFILE_SAFE_LOW_RISK = "safe_low_risk"
PROFILE_GUARDED_STANDARD = "guarded_standard"
PROFILE_HIGH_RISK_REVIEW = "high_risk_review"
PROFILE_RESTRICTED_NO_EXECUTE = "restricted_no_execute"


PROFILE_DEFINITIONS: dict[str, dict[str, Any]] = {
    PROFILE_SAFE_LOW_RISK: {
        "profile_id": PROFILE_SAFE_LOW_RISK,
        "profile_name": "Safe Low Risk",
        "guardrails": [
            "Read-only operations only.",
            "Maintain dry_run-first posture.",
        ],
    },
    PROFILE_GUARDED_STANDARD: {
        "profile_id": PROFILE_GUARDED_STANDARD,
        "profile_name": "Guarded Standard",
        "guardrails": [
            "Require approval before execution.",
            "Record audit evidence for each guarded step.",
        ],
    },
    PROFILE_HIGH_RISK_REVIEW: {
        "profile_id": PROFILE_HIGH_RISK_REVIEW,
        "profile_name": "High Risk Review",
        "guardrails": [
            "Block execution until explicit approval.",
            "Require rollback and change-context validation.",
        ],
    },
    PROFILE_RESTRICTED_NO_EXECUTE: {
        "profile_id": PROFILE_RESTRICTED_NO_EXECUTE,
        "profile_name": "Restricted No Execute",
        "guardrails": [
            "Do not execute external side effects.",
            "Require manual policy review before retry.",
        ],
    },
}


def get_profile_definition(profile_id: str) -> dict[str, Any]:
    """Return copy-safe profile metadata for a known profile id."""
    if profile_id not in PROFILE_DEFINITIONS:
        raise ValueError(
            f"Unknown model-router profile_id '{profile_id}'. Supported: {sorted(PROFILE_DEFINITIONS)}"
        )
    profile = PROFILE_DEFINITIONS[profile_id]
    return {
        "profile_id": str(profile["profile_id"]),
        "profile_name": str(profile["profile_name"]),
        "guardrails": [str(item) for item in profile["guardrails"]],
    }
