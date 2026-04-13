"""Rule linting helpers for SafeCore policy authoring."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.policy.rule_registry import RuleEntry


FORBIDDEN_ALLOW_PATTERNS = (
    re.compile(r"(?mi)^\s*allow\s*:=\s*true\s*$"),
    re.compile(r"(?mi)^\s*allow\s*=\s*true\s*$"),
    re.compile(r"(?mi)^\s*allow\s+if\s+true\s*$"),
)
RULE_ID_PATTERN = re.compile(r"(?mi)^\s*#\s*rule_id\s*:\s*(.+?)\s*$")


@dataclass(frozen=True)
class LintIssue:
    """One lint issue emitted by the rule linter."""

    code: str
    message: str
    file_name: str


class RuleLinter:
    """Lint Rego policy rules with small deterministic checks."""

    def lint(self, entries: list[RuleEntry]) -> dict[str, object]:
        """Lint entries and return structured issue report."""
        issues: list[LintIssue] = []
        issues.extend(self._check_required_package(entries))
        issues.extend(self._check_duplicate_rule_ids(entries))
        issues.extend(self._check_forbidden_allow_patterns(entries))

        return {
            "valid": len(issues) == 0,
            "issue_count": len(issues),
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "file_name": issue.file_name,
                }
                for issue in issues
            ],
        }

    def _check_required_package(self, entries: list[RuleEntry]) -> list[LintIssue]:
        issues: list[LintIssue] = []
        for entry in entries:
            if entry.package != "safecore":
                issues.append(
                    LintIssue(
                        code="PKG001",
                        message=(
                            "Rule must declare `package safecore` "
                            f"(pack={entry.policy_pack})."
                        ),
                        file_name=entry.file_name,
                    )
                )
        return issues

    def _check_duplicate_rule_ids(self, entries: list[RuleEntry]) -> list[LintIssue]:
        issues: list[LintIssue] = []
        seen: dict[tuple[str, str], str] = {}
        for entry in entries:
            declared_rule_ids = [item.strip() for item in RULE_ID_PATTERN.findall(entry.content)]
            if not declared_rule_ids:
                continue

            unique_rule_ids = sorted({item for item in declared_rule_ids if item})
            if len(unique_rule_ids) > 1:
                issues.append(
                    LintIssue(
                        code="META003",
                        message=(
                            "Ambiguous rule_id metadata detected; file defines "
                            f"multiple rule_ids {unique_rule_ids}."
                        ),
                        file_name=entry.file_name,
                    )
                )
                continue

            rule_id = unique_rule_ids[0] if unique_rule_ids else ""
            if not rule_id:
                issues.append(
                    LintIssue(
                        code="META002",
                        message=(
                            "Metadata rule_id is empty or ambiguous "
                            f"(pack={entry.policy_pack})."
                        ),
                        file_name=entry.file_name,
                    )
                )
                continue

            key = (entry.policy_pack, rule_id)
            if key in seen:
                previous = seen[key]
                issues.append(
                    LintIssue(
                        code="META001",
                        message=(
                            f"Duplicate rule_id '{rule_id}' also used by '{previous}' "
                            f"(pack={entry.policy_pack})."
                        ),
                        file_name=entry.file_name,
                    )
                )
            else:
                seen[key] = entry.file_name
        return issues

    def _check_forbidden_allow_patterns(self, entries: list[RuleEntry]) -> list[LintIssue]:
        issues: list[LintIssue] = []
        for entry in entries:
            for pattern in FORBIDDEN_ALLOW_PATTERNS:
                if pattern.search(entry.content):
                    issues.append(
                        LintIssue(
                            code="ALLOW001",
                            message=(
                                "Forbidden wildcard allow pattern detected "
                                "(e.g., unconditional allow)."
                            ),
                            file_name=entry.file_name,
                        )
                    )
                    break
        return issues
