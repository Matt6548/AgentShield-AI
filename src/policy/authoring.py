"""Policy authoring helpers for rule discovery, linting, and summary preview."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.policy.policy_engine import POLICY_PACK_V1, VALID_POLICY_PACKS, PolicyEngine
from src.policy.rule_linter import RuleLinter
from src.policy.rule_registry import RuleRegistry


class PolicyAuthoringService:
    """Programmatic policy authoring utility layer."""

    def __init__(
        self,
        rules_path: str | Path | None = None,
        policy_pack: str = POLICY_PACK_V1,
        registry: RuleRegistry | None = None,
        linter: RuleLinter | None = None,
    ) -> None:
        self.registry = registry or RuleRegistry(
            rules_path=rules_path,
            default_policy_pack=policy_pack,
        )
        self.linter = linter or RuleLinter()
        self.engine = PolicyEngine(
            rules_path=self.registry.rules_root,
            opa_binary="definitely-not-opa",
            policy_pack=policy_pack,
        )

    def list_available_policy_packs(self) -> list[str]:
        """List policy packs currently available on disk."""
        return self.registry.available_policy_packs()

    def list_available_rules(self, *, policy_pack: str | None = None) -> list[dict[str, Any]]:
        """List available rule files and metadata in deterministic order."""
        entries = self.registry.load_rules(policy_pack=policy_pack)
        return [
            {
                "file_name": entry.file_name,
                "path": entry.path,
                "package": entry.package,
                "rule_id": entry.rule_id,
                "metadata": entry.metadata,
                "policy_pack": entry.policy_pack,
            }
            for entry in entries
        ]

    def lint_rules(self, *, policy_pack: str | None = None) -> dict[str, Any]:
        """Run rule lint checks and return structured report."""
        entries = self.registry.load_rules(policy_pack=policy_pack)
        report = self.linter.lint(entries)
        selected_pack = policy_pack or self.registry.default_policy_pack
        report["rules_path"] = str(self.registry.get_rules_path(selected_pack))
        report["policy_pack"] = selected_pack
        report["available_policy_packs"] = self.registry.available_policy_packs()
        report["rule_count"] = len(entries)
        return report

    def validate_rules_or_raise(self, *, policy_pack: str | None = None) -> None:
        """Raise ValueError if lint report contains errors."""
        report = self.lint_rules(policy_pack=policy_pack)
        if report["valid"]:
            return

        issues = report.get("issues", [])
        rendered = "; ".join(
            f"{issue['code']}[{issue['file_name']}]: {issue['message']}" for issue in issues
        )
        raise ValueError(f"Policy rule lint failed: {rendered}")

    def preview_fallback_summary(self, *, policy_pack: str | None = None) -> dict[str, Any]:
        """Preview fallback evaluator summary based on current policy constants."""
        return self.engine.fallback_rule_summary(policy_pack=policy_pack)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SafeCore policy authoring helper")
    parser.add_argument(
        "command",
        choices=("list", "lint", "summary"),
        help="Action to execute.",
    )
    parser.add_argument(
        "--rules-path",
        default=None,
        help="Optional custom path to .rego policy rules.",
    )
    parser.add_argument(
        "--policy-pack",
        default=POLICY_PACK_V1,
        choices=sorted(VALID_POLICY_PACKS),
        help="Policy pack version to target.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for policy authoring helper."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    service = PolicyAuthoringService(rules_path=args.rules_path, policy_pack=args.policy_pack)

    if args.command == "list":
        payload = {
            "policy_pack": args.policy_pack,
            "available_policy_packs": service.list_available_policy_packs(),
            "rules": service.list_available_rules(policy_pack=args.policy_pack),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.command == "summary":
        print(
            json.dumps(
                service.preview_fallback_summary(policy_pack=args.policy_pack),
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    try:
        report = service.lint_rules(policy_pack=args.policy_pack)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["valid"] else 1
    except Exception as exc:  # noqa: BLE001
        print(f"Policy lint failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
