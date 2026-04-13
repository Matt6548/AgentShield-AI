"""Policy rule registry utilities for deterministic rule discovery."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.policy.policy_engine import POLICY_PACK_V1, POLICY_PACK_V2, VALID_POLICY_PACKS


PACKAGE_PATTERN = re.compile(r"^\s*package\s+([a-zA-Z0-9_.-]+)\s*$", re.MULTILINE)
METADATA_PATTERN = re.compile(r"^\s*#\s*([a-zA-Z0-9_.-]+)\s*:\s*(.+?)\s*$")


@dataclass(frozen=True)
class RuleEntry:
    """Structured policy rule file entry."""

    file_name: str
    path: str
    package: str | None
    metadata: dict[str, str]
    rule_id: str
    content: str
    policy_pack: str


class RuleRegistry:
    """Discover and load Rego policy rules in deterministic order."""

    def __init__(
        self,
        rules_path: str | Path | None = None,
        default_policy_pack: str = POLICY_PACK_V1,
    ) -> None:
        default_rules_path = Path(__file__).resolve().parent / "rules"
        self.rules_root = Path(rules_path) if rules_path else default_rules_path
        self.default_policy_pack = self._normalize_policy_pack(default_policy_pack)

    def available_policy_packs(self) -> list[str]:
        """Return policy packs currently available in the registry root."""
        packs: list[str] = []
        for pack in sorted(VALID_POLICY_PACKS):
            path = self._resolve_rules_path(pack)
            if path.exists() and path.is_dir():
                packs.append(pack)
        return packs

    def list_rule_files(self, policy_pack: str | None = None) -> list[Path]:
        """Return sorted rule file paths for the selected policy pack."""
        selected_pack = self._effective_pack(policy_pack)
        selected_path = self.get_rules_path(selected_pack)
        if not selected_path.exists() or not selected_path.is_dir():
            return []
        return sorted(selected_path.glob("*.rego"), key=lambda path: path.name)

    def load_rules(self, policy_pack: str | None = None) -> list[RuleEntry]:
        """Load rule entries with parsed package and metadata."""
        selected_pack = self._effective_pack(policy_pack)
        entries: list[RuleEntry] = []
        for rule_path in self.list_rule_files(policy_pack=selected_pack):
            content = rule_path.read_text(encoding="utf-8")
            metadata = self._parse_metadata(content)
            package = self._extract_package(content)
            rule_id = metadata.get("rule_id", rule_path.stem)
            entries.append(
                RuleEntry(
                    file_name=rule_path.name,
                    path=str(rule_path),
                    package=package,
                    metadata=metadata,
                    rule_id=rule_id,
                    content=content,
                    policy_pack=selected_pack,
                )
            )
        return entries

    def summary(self, policy_pack: str | None = None) -> dict[str, Any]:
        """Return deterministic summary of currently available rules."""
        selected_pack = self._effective_pack(policy_pack)
        entries = self.load_rules(policy_pack=selected_pack)
        return {
            "rules_root": str(self.rules_root),
            "policy_pack": selected_pack,
            "available_policy_packs": self.available_policy_packs(),
            "count": len(entries),
            "rule_files": [entry.file_name for entry in entries],
            "rule_ids": [entry.rule_id for entry in entries],
        }

    def get_rules_path(self, policy_pack: str | None = None) -> Path:
        """Return filesystem path for the selected policy pack."""
        selected_pack = self._effective_pack(policy_pack)
        return self._resolve_rules_path(selected_pack)

    def _effective_pack(self, policy_pack: str | None) -> str:
        if policy_pack is None:
            return self.default_policy_pack
        return self._normalize_policy_pack(policy_pack)

    def _resolve_rules_path(self, policy_pack: str) -> Path:
        if policy_pack == POLICY_PACK_V2:
            return self.rules_root / "v2"
        return self.rules_root

    def _normalize_policy_pack(self, policy_pack: str) -> str:
        normalized = str(policy_pack).strip().lower()
        if normalized not in VALID_POLICY_PACKS:
            raise ValueError(
                f"Unsupported policy_pack '{policy_pack}'. Supported values: {sorted(VALID_POLICY_PACKS)}"
            )
        return normalized

    def _extract_package(self, content: str) -> str | None:
        match = PACKAGE_PATTERN.search(content)
        if not match:
            return None
        return match.group(1).strip()

    def _parse_metadata(self, content: str) -> dict[str, str]:
        metadata: dict[str, str] = {}
        for line in content.splitlines():
            match = METADATA_PATTERN.match(line)
            if not match:
                continue
            key = match.group(1).strip().lower()
            value = match.group(2).strip()
            metadata[key] = value
        return metadata
