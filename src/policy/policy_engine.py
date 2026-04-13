"""SafeCore Policy Engine skeleton.

This module provides a deterministic local policy evaluator and an optional
OPA subprocess hook. The local evaluator is the default/fallback path.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from src.utils.safe_http import (
    SAFE_HTTP_ALLOWED_HOSTS,
    SAFE_HTTP_ALLOWED_METHODS,
    SAFE_HTTP_ALLOWED_PATH_PREFIXES,
    SAFE_HTTP_TOOL,
    extract_safe_http_request,
    is_safe_http_tool,
)


DECISION_ALLOW = "ALLOW"
DECISION_DENY = "DENY"
DECISION_NEEDS_APPROVAL = "NEEDS_APPROVAL"
VALID_DECISIONS = {DECISION_ALLOW, DECISION_DENY, DECISION_NEEDS_APPROVAL}

RISK_ALLOW_MAX = 33
RISK_NEEDS_APPROVAL_MAX = 66
RISK_MIN = 0
RISK_MAX = 100

POLICY_PACK_V1 = "v1"
POLICY_PACK_V2 = "v2"
VALID_POLICY_PACKS = {POLICY_PACK_V1, POLICY_PACK_V2}

SHELL_TOOLS = {"shell", "bash", "sh", "cmd", "powershell", "terminal"}
SAFE_SHELL_COMMAND_PREFIXES = {
    "ls",
    "cat",
    "echo",
    "pwd",
    "whoami",
    "id",
    "date",
    "head",
    "tail",
    "grep",
    "find",
}
SHELL_CHAINING_TOKENS = ("&&", "||", ";", "|", ">", "<", "$(", "`")

DESTRUCTIVE_ACTION_HINTS = (
    "delete",
    "destroy",
    "drop",
    "truncate",
    "shutdown",
    "wipe",
    "privileged",
    "admin",
    "root",
)
DESTRUCTIVE_COMMAND_HINTS = (
    "rm -rf",
    "mkfs",
    "dd if=",
    "format",
    "del /f",
)
PROD_CHANGE_HINTS = ("change", "update", "modify", "deploy", "restart", "write", "delete")
PRODUCTION_ENV_HINTS = {"prod", "production"}
READ_ONLY_HINTS = ("read", "list", "get", "fetch", "describe", "inspect", "view", "query")
EXFIL_ACTION_HINTS = ("export", "upload", "transfer", "sync", "send", "share", "exfil")
EXFIL_TECH_HINTS = (
    "http://",
    "https://",
    "ftp://",
    "s3://",
    "scp",
    "curl",
    "wget",
    "nc ",
    "netcat",
    "dropbox",
    "pastebin",
    "drive.google",
)

CHANGE_TICKET_KEYS = ("change_ticket", "ticket", "approval_id")


class PolicyEngine:
    """Policy decision engine with optional OPA integration and local fallback."""

    def __init__(
        self,
        rules_path: str | Path | None = None,
        opa_binary: str = "opa",
        policy_pack: str = POLICY_PACK_V1,
    ) -> None:
        default_rules_root = Path(__file__).resolve().parent / "rules"
        self.rules_root = Path(rules_path) if rules_path else default_rules_root
        self._explicit_rules_path = rules_path is not None
        self.policy_pack = self._normalize_policy_pack(policy_pack)
        self.rules_path = self._resolve_rules_path(self.policy_pack)
        self.opa_binary = opa_binary
        self._opa_available = shutil.which(self.opa_binary) is not None

    @property
    def opa_available(self) -> bool:
        """Return whether the OPA binary is currently available."""
        return self._opa_available

    def available_policy_packs(self) -> list[str]:
        """Return policy packs currently available on disk."""
        available: list[str] = []
        for pack in sorted(VALID_POLICY_PACKS):
            if self._resolve_rules_path(pack).exists():
                available.append(pack)
        return available

    def load_rules(self, policy_pack: str | None = None) -> list[Path]:
        """Load .rego files from the selected rules path."""
        selected_pack = self._resolve_evaluation_pack(policy_pack=policy_pack, input_data=None)
        selected_path = self._resolve_rules_path(selected_pack)
        if not selected_path.exists() or not selected_path.is_dir():
            return []
        return sorted(selected_path.glob("*.rego"))

    def evaluate(
        self,
        input_data: dict[str, Any],
        *,
        policy_pack: str | None = None,
    ) -> dict[str, Any]:
        """Evaluate input data and return a SafetyDecision-compatible object."""
        if not isinstance(input_data, dict):
            raise TypeError("PolicyEngine.evaluate expects input_data to be a dict.")

        selected_pack = self._resolve_evaluation_pack(policy_pack=policy_pack, input_data=input_data)
        opa_error: str | None = None
        if self.opa_available:
            try:
                opa_result = self._evaluate_with_opa(input_data, policy_pack=selected_pack)
                return self._normalize_decision(opa_result)
            except Exception as exc:  # noqa: BLE001
                opa_error = str(exc)

        fallback_result = self._evaluate_locally(input_data, policy_pack=selected_pack)
        if opa_error:
            fallback_result["reasons"].append(
                (
                    f"OPA evaluation failed ({opa_error}). "
                    f"Local fallback policy used ({selected_pack})."
                )
            )
        else:
            fallback_result["reasons"].append(
                f"OPA unavailable. Local fallback policy used ({selected_pack})."
            )
        return self._normalize_decision(fallback_result)

    def fallback_rule_summary(self, *, policy_pack: str | None = None) -> dict[str, Any]:
        """Return deterministic summary of the local fallback evaluator model."""
        selected_pack = self._resolve_evaluation_pack(policy_pack=policy_pack, input_data=None)
        summary = {
            "policy_pack": selected_pack,
            "risk_thresholds": {
                "min": RISK_MIN,
                "allow_max": RISK_ALLOW_MAX,
                "needs_approval_max": RISK_NEEDS_APPROVAL_MAX,
                "max": RISK_MAX,
            },
            "safe_shell_command_prefixes": sorted(SAFE_SHELL_COMMAND_PREFIXES),
            "destructive_action_hints": list(DESTRUCTIVE_ACTION_HINTS),
            "destructive_command_hints": list(DESTRUCTIVE_COMMAND_HINTS),
            "production_change_hints": list(PROD_CHANGE_HINTS),
            "production_env_hints": sorted(PRODUCTION_ENV_HINTS),
            "read_only_hints": list(READ_ONLY_HINTS),
            "exfil_action_hints": list(EXFIL_ACTION_HINTS),
            "exfil_tech_hints": list(EXFIL_TECH_HINTS),
            "safe_http_example": {
                "tool": SAFE_HTTP_TOOL,
                "allowed_methods": sorted(SAFE_HTTP_ALLOWED_METHODS),
                "allowed_hosts": sorted(SAFE_HTTP_ALLOWED_HOSTS),
                "allowed_path_prefixes": list(SAFE_HTTP_ALLOWED_PATH_PREFIXES),
            },
        }
        if selected_pack == POLICY_PACK_V2:
            summary["shell_chaining_tokens"] = list(SHELL_CHAINING_TOKENS)
            summary["change_ticket_keys"] = list(CHANGE_TICKET_KEYS)
        return summary

    def _evaluate_with_opa(
        self,
        input_data: dict[str, Any],
        *,
        policy_pack: str,
    ) -> dict[str, Any]:
        """Evaluate policies via OPA and return a candidate decision object."""
        rules = self.load_rules(policy_pack=policy_pack)
        if not rules:
            raise RuntimeError(
                f"No policy rules found for pack '{policy_pack}' in {self._resolve_rules_path(policy_pack)}."
            )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8", delete=False
        ) as f:
            json.dump(input_data, f)
            input_path = Path(f.name)

        try:
            command = [
                self.opa_binary,
                "eval",
                "--format",
                "json",
                "--input",
                str(input_path),
            ]
            for rule_file in rules:
                command.extend(["--data", str(rule_file)])
            command.append("data.safecore.decision")

            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if completed.returncode != 0:
                error_text = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
                raise RuntimeError(f"OPA exited with code {completed.returncode}: {error_text}")

            payload = json.loads(completed.stdout)
            return self._extract_opa_result(payload)
        finally:
            input_path.unlink(missing_ok=True)

    def _extract_opa_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Extract a decision-like object from OPA eval JSON output."""
        result = payload.get("result")
        if not isinstance(result, list) or not result:
            raise RuntimeError("OPA output did not contain a result list.")

        first = result[0]
        expressions = first.get("expressions")
        if not isinstance(expressions, list) or not expressions:
            raise RuntimeError("OPA output did not contain expressions.")

        value = expressions[0].get("value")
        if not isinstance(value, dict):
            raise RuntimeError("OPA expression value was not an object.")

        return value

    def _evaluate_locally(
        self,
        input_data: dict[str, Any],
        *,
        policy_pack: str,
    ) -> dict[str, Any]:
        """Deterministic baseline evaluator used when OPA is not available."""
        if policy_pack == POLICY_PACK_V2:
            return self._evaluate_locally_v2(input_data)
        return self._evaluate_locally_v1(input_data)

    def _evaluate_locally_v1(self, input_data: dict[str, Any]) -> dict[str, Any]:
        risk_score = 10
        reasons: list[str] = []
        constraints: list[str] = []
        operator_checks: list[str] = []

        action = self._as_lower_text(input_data.get("action"))
        tool = self._as_lower_text(input_data.get("tool"))
        command = self._as_lower_text(input_data.get("command"))
        params = self._as_lower_text(input_data.get("params"))
        user = self._as_lower_text(input_data.get("user"))
        environment = self._as_lower_text(
            input_data.get("environment", input_data.get("env", ""))
        )
        target = self._as_lower_text(
            input_data.get("target", input_data.get("target_system", ""))
        )

        safe_http_allowed = False
        if is_safe_http_tool(tool):
            safe_http = extract_safe_http_request(input_data)
            safe_http_allowed = bool(safe_http["allowed"])
            if safe_http_allowed:
                risk_score = max(risk_score, 20)
                reasons.append("Allowlisted local safe HTTP status fetch detected.")
                constraints.append("Limit HTTP integration to explicit local GET health/status endpoints.")
            else:
                risk_score = max(risk_score, 90)
                reasons.extend(list(safe_http["reasons"]))
                constraints.append("Block any non-allowlisted or non-GET HTTP connector request.")
                operator_checks.append("Review destination allowlist and method restrictions before retry.")

        if self._contains_any(action, DESTRUCTIVE_ACTION_HINTS) or self._contains_any(
            command, DESTRUCTIVE_COMMAND_HINTS
        ):
            risk_score = max(risk_score, 75)
            reasons.append("Privileged or destructive operation pattern detected.")
            constraints.append("Block privileged/destructive operations by default policy.")
            operator_checks.append("Require explicit operator sign-off and rollback readiness.")

        if environment in PRODUCTION_ENV_HINTS and self._contains_any(action, PROD_CHANGE_HINTS):
            risk_score = max(risk_score, 55)
            reasons.append("Production change pattern detected.")
            constraints.append("Require human approval for production changes.")
            operator_checks.append("Confirm rollback plan and change ticket.")

        if tool in SHELL_TOOLS:
            if not command.strip():
                risk_score = max(risk_score, 75)
                reasons.append("Shell execution requested with an empty command.")
                constraints.append("Reject empty shell command payloads.")
            elif not self._is_safe_shell_command(command):
                risk_score = max(risk_score, 90)
                reasons.append("Shell command is outside the safe allowlist.")
                constraints.append("Only allow approved read-only shell commands.")
                operator_checks.append("Review shell command intent and scope.")
            else:
                risk_score = max(risk_score, 15)
                reasons.append("Shell command matches safe allowlist.")

        exfil_signals = " ".join([action, command, params, target])
        if not safe_http_allowed and (
            self._contains_any(exfil_signals, EXFIL_TECH_HINTS)
            or (
            self._contains_any(action, EXFIL_ACTION_HINTS)
            and self._contains_any(target, ("http://", "https://", "ftp://", "s3://"))
            )
        ):
            risk_score = max(risk_score, 75)
            reasons.append("Potential external network egress or exfiltration signal detected.")
            constraints.append("Block outbound transfer until destination is approved.")
            operator_checks.append("Validate destination ownership and data classification.")

        if user in {"admin", "root"} and risk_score < 67:
            risk_score = max(risk_score, 45)
            reasons.append("Privileged user context detected.")
            operator_checks.append("Verify least-privilege requirement for this action.")

        if self._contains_any(action, READ_ONLY_HINTS) and risk_score <= RISK_ALLOW_MAX:
            risk_score = min(risk_score, 20)
            reasons.append("Read-only action pattern detected.")

        if not reasons:
            reasons.append("No specific policy risks detected under baseline evaluator.")

        return {
            "decision": self._decision_for_risk(risk_score),
            "risk_score": risk_score,
            "reasons": self._deduplicate(reasons),
            "constraints": self._deduplicate(constraints),
            "operator_checks": self._deduplicate(operator_checks),
        }

    def _evaluate_locally_v2(self, input_data: dict[str, Any]) -> dict[str, Any]:
        risk_score = 10
        reasons: list[str] = []
        constraints: list[str] = []
        operator_checks: list[str] = []

        action = self._as_lower_text(input_data.get("action"))
        tool = self._as_lower_text(input_data.get("tool"))
        command = self._as_lower_text(input_data.get("command"))
        params = self._as_lower_text(input_data.get("params"))
        payload = self._as_lower_text(input_data.get("payload"))
        user = self._as_lower_text(input_data.get("user", input_data.get("actor", "")))
        environment = self._as_lower_text(
            input_data.get("environment", input_data.get("env", ""))
        )
        target = self._as_lower_text(
            input_data.get("target", input_data.get("target_system", ""))
        )

        safe_http_allowed = False
        if is_safe_http_tool(tool):
            safe_http = extract_safe_http_request(input_data)
            safe_http_allowed = bool(safe_http["allowed"])
            if safe_http_allowed:
                risk_score = max(risk_score, 18)
                reasons.append("Allowlisted local safe HTTP status fetch detected under policy pack v2.")
                constraints.append("Limit HTTP integration to explicit local GET health/status endpoints.")
            else:
                risk_score = max(risk_score, 95)
                reasons.extend(list(safe_http["reasons"]))
                constraints.append("Block any non-allowlisted or non-GET HTTP connector request.")
                operator_checks.append("Review destination allowlist and method restrictions before retry.")

        if not action.strip() or not tool.strip():
            risk_score = max(risk_score, 45)
            reasons.append("Insufficient action/tool context under policy pack v2.")
            constraints.append("Require explicit action and tool identifiers.")
            operator_checks.append("Add missing context fields before re-evaluation.")

        if self._contains_any(action, DESTRUCTIVE_ACTION_HINTS) or self._contains_any(
            command, DESTRUCTIVE_COMMAND_HINTS
        ):
            risk_score = max(risk_score, 82)
            reasons.append("Privileged or destructive operation pattern detected.")
            constraints.append("Block privileged/destructive operations by default policy.")
            operator_checks.append("Require explicit operator sign-off and rollback readiness.")

        if environment in PRODUCTION_ENV_HINTS and self._contains_any(action, PROD_CHANGE_HINTS):
            if self._has_change_ticket(input_data):
                risk_score = max(risk_score, 55)
                reasons.append("Production change pattern detected with change ticket metadata.")
                constraints.append("Require human approval before production changes.")
                operator_checks.append("Confirm rollback plan and linked change ticket.")
            else:
                risk_score = max(risk_score, 70)
                reasons.append("Production change pattern detected without change ticket metadata.")
                constraints.append("Block production mutation until change ticket is provided.")
                operator_checks.append("Provide approved change ticket before retry.")

        if tool in SHELL_TOOLS:
            if not command.strip():
                risk_score = max(risk_score, 95)
                reasons.append("Shell execution requested with an empty command.")
                constraints.append("Reject empty shell command payloads.")
            elif self._contains_shell_chaining(command):
                risk_score = max(risk_score, 95)
                reasons.append("Shell command chaining/redirection detected under v2 policy.")
                constraints.append("Block shell chaining and redirection constructs.")
                operator_checks.append("Split command into audited read-only steps.")
            elif not self._is_safe_shell_command(command):
                risk_score = max(risk_score, 92)
                reasons.append("Shell command is outside the safe allowlist.")
                constraints.append("Only allow approved read-only shell commands.")
                operator_checks.append("Review shell command intent and scope.")
            else:
                risk_score = max(risk_score, 15)
                reasons.append("Shell command matches safe allowlist.")

        exfil_signals = " ".join([action, command, params, target, payload])
        if not safe_http_allowed and (
            self._contains_any(exfil_signals, EXFIL_TECH_HINTS)
            or self._contains_any(action, EXFIL_ACTION_HINTS)
        ):
            risk_score = max(risk_score, 85)
            reasons.append("Potential external network egress or exfiltration signal detected.")
            constraints.append("Block outbound transfer until destination is approved.")
            operator_checks.append("Validate destination ownership and data classification.")

        if user in {"admin", "root"} and risk_score < 67:
            risk_score = max(risk_score, 60)
            reasons.append("Privileged user context detected.")
            operator_checks.append("Verify least-privilege requirement for this action.")

        if self._contains_any(action, READ_ONLY_HINTS) and risk_score <= RISK_ALLOW_MAX:
            risk_score = min(risk_score, 20)
            reasons.append("Read-only action pattern detected.")

        if not reasons:
            reasons.append("No specific policy risks detected under policy pack v2.")

        return {
            "decision": self._decision_for_risk(risk_score),
            "risk_score": risk_score,
            "reasons": self._deduplicate(reasons),
            "constraints": self._deduplicate(constraints),
            "operator_checks": self._deduplicate(operator_checks),
        }

    def _normalize_decision(self, result: dict[str, Any]) -> dict[str, Any]:
        """Normalize any candidate object into SafetyDecision contract shape."""
        risk_score = self._clamp_risk(result.get("risk_score"))
        raw_decision = str(result.get("decision", "")).upper()
        decision = raw_decision if raw_decision in VALID_DECISIONS else self._decision_for_risk(risk_score)

        reasons = self._to_string_list(result.get("reasons"))
        constraints = self._to_string_list(result.get("constraints"))
        operator_checks = self._to_string_list(result.get("operator_checks"))

        if not reasons:
            reasons = ["No policy reason provided."]

        return {
            "decision": decision,
            "risk_score": risk_score,
            "reasons": reasons,
            "constraints": constraints,
            "operator_checks": operator_checks,
        }

    def _resolve_evaluation_pack(
        self,
        *,
        policy_pack: str | None,
        input_data: dict[str, Any] | None,
    ) -> str:
        if policy_pack is not None:
            return self._normalize_policy_pack(policy_pack)

        if isinstance(input_data, dict):
            raw = input_data.get("policy_pack")
            if raw is not None and str(raw).strip():
                return self._normalize_policy_pack(str(raw))
        return self.policy_pack

    def _normalize_policy_pack(self, policy_pack: str) -> str:
        normalized = str(policy_pack).strip().lower()
        if normalized not in VALID_POLICY_PACKS:
            raise ValueError(
                f"Unsupported policy_pack '{policy_pack}'. Supported values: {sorted(VALID_POLICY_PACKS)}"
            )
        return normalized

    def _resolve_rules_path(self, policy_pack: str) -> Path:
        if policy_pack == POLICY_PACK_V2:
            return self.rules_root / "v2"
        return self.rules_root

    def _decision_for_risk(self, risk_score: int) -> str:
        if risk_score <= RISK_ALLOW_MAX:
            return DECISION_ALLOW
        if risk_score <= RISK_NEEDS_APPROVAL_MAX:
            return DECISION_NEEDS_APPROVAL
        return DECISION_DENY

    def _clamp_risk(self, value: Any) -> int:
        try:
            risk_score = int(value)
        except (TypeError, ValueError):
            risk_score = RISK_MIN
        return max(RISK_MIN, min(RISK_MAX, risk_score))

    def _is_safe_shell_command(self, command: str) -> bool:
        normalized = command.strip().lower()
        if not normalized:
            return False
        prefix = normalized.split()[0]
        return prefix in SAFE_SHELL_COMMAND_PREFIXES

    def _contains_shell_chaining(self, command: str) -> bool:
        normalized = command.strip().lower()
        return any(token in normalized for token in SHELL_CHAINING_TOKENS)

    def _contains_any(self, text: str, patterns: tuple[str, ...] | set[str]) -> bool:
        return any(pattern in text for pattern in patterns)

    def _as_lower_text(self, value: Any) -> str:
        if isinstance(value, str):
            return value.lower()
        if isinstance(value, dict) or isinstance(value, list):
            return json.dumps(value, sort_keys=True).lower()
        return str(value).lower()

    def _has_change_ticket(self, input_data: dict[str, Any]) -> bool:
        params = input_data.get("params", {})
        if isinstance(params, dict):
            for key in CHANGE_TICKET_KEYS:
                value = params.get(key)
                if value is not None and str(value).strip():
                    return True

        payload = input_data.get("payload", {})
        if isinstance(payload, dict):
            approved_change = payload.get("approved_change")
            if isinstance(approved_change, bool) and approved_change:
                return True
            for key in CHANGE_TICKET_KEYS:
                value = payload.get(key)
                if value is not None and str(value).strip():
                    return True
        return False

    def _to_string_list(self, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]

    def _deduplicate(self, items: list[str]) -> list[str]:
        # Keep first occurrence order to preserve deterministic explanations.
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered
