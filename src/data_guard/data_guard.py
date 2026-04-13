"""Deterministic data guard foundation for SafeCore."""

from __future__ import annotations

from typing import Any

from src.policy.policy_engine import RISK_ALLOW_MAX, RISK_MAX, RISK_MIN, RISK_NEEDS_APPROVAL_MAX
from src.utils.security_patterns import detect_sensitive_findings, redact_sensitive_payload


ACTION_ALLOW = "ALLOW"
ACTION_REDACT = "REDACT"
ACTION_BLOCK = "BLOCK"
VALID_ACTIONS = {ACTION_ALLOW, ACTION_REDACT, ACTION_BLOCK}

FINDING_WEIGHTS = {
    "email": 35,
    "phone": 35,
    "secret": 50,
    "credit_card": 60,
    "suspicious_outbound": 35,
}


class DataGuard:
    """Evaluate payload sensitivity and return deterministic guard actions."""

    def inspect(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Inspect payload and return findings + risk summary."""
        if not isinstance(payload, dict):
            raise TypeError("DataGuard.inspect expects a dict payload.")

        finding_items = detect_sensitive_findings(payload)
        risk_score = self._risk_from_findings(finding_items)
        findings = [self._format_finding(item) for item in finding_items]

        return {
            "risk_score": risk_score,
            "findings": findings,
            "finding_types": sorted({item["type"] for item in finding_items}),
        }

    def redact(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Redact sensitive values from payload."""
        return redact_sensitive_payload(payload)

    def evaluate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Evaluate payload and return a stable guard decision object."""
        inspection = self.inspect(payload)
        risk_score = inspection["risk_score"]
        action = self._action_for_risk(risk_score)
        redacted_payload = payload if action == ACTION_ALLOW else self.redact(payload)

        return {
            "allowed": action != ACTION_BLOCK,
            "risk_score": risk_score,
            "findings": inspection["findings"],
            "redacted_payload": redacted_payload,
            "action": action,
        }

    def _risk_from_findings(self, finding_items: list[dict[str, str]]) -> int:
        if not finding_items:
            return 0

        finding_types = [item["type"] for item in finding_items]
        unique_types = set(finding_types)
        max_weight = max(FINDING_WEIGHTS.get(kind, 20) for kind in finding_types)

        # Baseline: strongest signal + small boost for additional categories.
        risk_score = max_weight + max(0, len(unique_types) - 1) * 10

        # Escalate when outbound transfer markers are combined with secrets/CC data.
        if "suspicious_outbound" in unique_types and (
            "secret" in unique_types or "credit_card" in unique_types
        ):
            risk_score = max(risk_score, 75)

        # Add a small count-based boost for repeated findings.
        risk_score += min(max(0, len(finding_items) - len(unique_types)) * 2, 10)

        return max(RISK_MIN, min(RISK_MAX, risk_score))

    def _action_for_risk(self, risk_score: int) -> str:
        if risk_score <= RISK_ALLOW_MAX:
            return ACTION_ALLOW
        if risk_score <= RISK_NEEDS_APPROVAL_MAX:
            return ACTION_REDACT
        return ACTION_BLOCK

    def _format_finding(self, item: dict[str, str]) -> str:
        finding_type = item["type"]
        path = item["path"]
        detail = item["detail"]
        return f"{finding_type} detected at '{path}' ({detail})"

