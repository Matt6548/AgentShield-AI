from pathlib import Path

import pytest

from src.policy.authoring import PolicyAuthoringService, main


def _write_rule(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_policy_authoring_lists_rules_in_deterministic_order(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    _write_rule(rules_dir / "z.rego", "package safecore\n")
    _write_rule(rules_dir / "a.rego", "package safecore\n")

    service = PolicyAuthoringService(rules_path=rules_dir)
    listed = service.list_available_rules()

    assert [item["file_name"] for item in listed] == ["a.rego", "z.rego"]


def test_policy_authoring_preview_exposes_fallback_thresholds(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    _write_rule(rules_dir / "base.rego", "package safecore\n")

    service = PolicyAuthoringService(rules_path=rules_dir)
    summary = service.preview_fallback_summary()

    assert summary["risk_thresholds"]["allow_max"] == 33
    assert summary["risk_thresholds"]["needs_approval_max"] == 66
    assert "ls" in summary["safe_shell_command_prefixes"]


def test_policy_authoring_validation_raises_and_cli_returns_non_zero(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    _write_rule(rules_dir / "invalid.rego", "package wrongpkg\n")

    service = PolicyAuthoringService(rules_path=rules_dir)
    with pytest.raises(ValueError, match="Policy rule lint failed"):
        service.validate_rules_or_raise()

    exit_code = main(["lint", "--rules-path", str(rules_dir)])
    assert exit_code == 1

