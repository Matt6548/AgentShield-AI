"""Tool guard policy helpers and ToolGuard baseline implementation."""

from __future__ import annotations

from typing import Any

from src.policy.policy_engine import (
    DECISION_ALLOW,
    DECISION_DENY,
    DECISION_NEEDS_APPROVAL,
    RISK_ALLOW_MAX,
    RISK_MAX,
    RISK_MIN,
    RISK_NEEDS_APPROVAL_MAX,
    SAFE_SHELL_COMMAND_PREFIXES,
    SHELL_TOOLS,
)
from src.utils.safe_http import SAFE_HTTP_TOOL, extract_safe_http_request, is_safe_http_tool


DEFAULT_ALLOWED_TOOLS = {
    "shell",
    "filesystem_read",
    "config_reader",
    "inventory",
    "echo",
    "noop",
    SAFE_HTTP_TOOL,
}

DANGEROUS_COMMAND_PATTERNS = (
    "rm -rf",
    "mkfs",
    "dd if=",
    "shutdown",
    "reboot",
    "chmod 777",
    "chown root",
    "sudo ",
    " su ",
    ":(){:|:&};:",
)

SUSPICIOUS_TRANSFER_PATTERNS = (
    "curl ",
    "wget ",
    "scp ",
    "ftp://",
    "http://",
    "https://",
    "s3://",
    "upload",
    "exfil",
)

SHELL_CONTROL_OPERATORS = ("&&", "||", ";", "|", "`", "$(", ">", "<")


class ToolGuard:
    """Baseline deterministic tool guard."""

    def __init__(
        self,
        allowed_tools: set[str] | None = None,
        safe_shell_commands: set[str] | None = None,
    ) -> None:
        self.allowed_tools = set(allowed_tools or DEFAULT_ALLOWED_TOOLS)
        self.safe_shell_commands = set(safe_shell_commands or SAFE_SHELL_COMMAND_PREFIXES)

    def evaluate(self, request: dict[str, Any]) -> dict[str, Any]:
        """Evaluate whether a tool request is safe enough to execute."""
        if not isinstance(request, dict):
            raise TypeError("ToolGuard.evaluate expects a dict request.")

        tool = str(request.get("tool", "")).strip().lower()
        command = str(request.get("command", "")).strip()
        reasons: list[str] = []
        risk_score = 10

        if not tool:
            risk_score = 90
            reasons.append("Missing tool identifier.")
        elif tool not in self.allowed_tools:
            risk_score = 90
            reasons.append(f"Tool '{tool}' is not in the allowlist.")
        elif tool in SHELL_TOOLS:
            risk_score, reasons = self._evaluate_shell_command(command)
        elif is_safe_http_tool(tool):
            risk_score, reasons = self._evaluate_safe_http_request(request)
        else:
            lowered_command = command.lower()
            if lowered_command and self._contains_any(lowered_command, DANGEROUS_COMMAND_PATTERNS):
                risk_score = 90
                reasons.append("Tool command matched a dangerous pattern.")
            else:
                risk_score = 20
                reasons.append(f"Tool '{tool}' is allowlisted.")

        decision = self._decision_for_risk(risk_score)
        allowed = decision == DECISION_ALLOW
        if decision == DECISION_NEEDS_APPROVAL:
            allowed = False
            reasons.append("Approval flow is deferred in this iteration; treating as blocked.")

        return {
            "allowed": allowed,
            "decision": decision,
            "risk_score": max(RISK_MIN, min(RISK_MAX, risk_score)),
            "reasons": reasons,
            "tool": tool,
            "command": command,
        }

    def _evaluate_shell_command(self, command: str) -> tuple[int, list[str]]:
        reasons: list[str] = []
        normalized = command.strip().lower()
        if not normalized:
            return 80, ["Shell tool requires a non-empty command."]

        if self._contains_any(normalized, DANGEROUS_COMMAND_PATTERNS):
            return 95, ["Shell command matched a known dangerous pattern."]

        if self._contains_any(normalized, SUSPICIOUS_TRANSFER_PATTERNS):
            return 90, ["Shell command includes suspicious outbound transfer markers."]

        if self._contains_any(normalized, SHELL_CONTROL_OPERATORS):
            return 60, ["Shell command includes control operators requiring approval."]

        prefix = normalized.split()[0]
        if prefix not in self.safe_shell_commands:
            return 85, [f"Shell command prefix '{prefix}' is not in the safe allowlist."]

        reasons.append(f"Shell command prefix '{prefix}' is allowlisted.")
        return 15, reasons

    def _evaluate_safe_http_request(self, request: dict[str, Any]) -> tuple[int, list[str]]:
        safe_http = extract_safe_http_request(request)
        if not safe_http["allowed"]:
            return 95, list(safe_http["reasons"])

        return 20, [
            (
                "Safe HTTP status fetch is allowlisted for explicit local GET "
                "health/status/metadata endpoints."
            )
        ]

    def _decision_for_risk(self, risk_score: int) -> str:
        if risk_score <= RISK_ALLOW_MAX:
            return DECISION_ALLOW
        if risk_score <= RISK_NEEDS_APPROVAL_MAX:
            return DECISION_NEEDS_APPROVAL
        return DECISION_DENY

    def _contains_any(self, text: str, patterns: tuple[str, ...]) -> bool:
        return any(pattern in text for pattern in patterns)
