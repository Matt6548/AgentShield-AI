from pathlib import Path

from src.policy.rule_linter import RuleLinter
from src.policy.rule_registry import RuleRegistry


def _write_rule(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _lint(tmp_rules_dir: Path) -> dict[str, object]:
    registry = RuleRegistry(rules_path=tmp_rules_dir)
    entries = registry.load_rules()
    return RuleLinter().lint(entries)


def test_rule_linter_accepts_valid_package_safecore_rule(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    _write_rule(rules_dir / "ok.rego", "package safecore\nimport rego.v1\n")

    report = _lint(rules_dir)
    assert report["valid"] is True
    assert report["issue_count"] == 0


def test_rule_linter_rejects_missing_or_wrong_package(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    _write_rule(rules_dir / "bad_pkg.rego", "package other\n")

    report = _lint(rules_dir)
    assert report["valid"] is False
    codes = [item["code"] for item in report["issues"]]  # type: ignore[index]
    assert "PKG001" in codes


def test_rule_linter_rejects_duplicate_rule_id_metadata(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    _write_rule(
        rules_dir / "rule_a.rego",
        "# rule_id: duplicate.id\npackage safecore\n",
    )
    _write_rule(
        rules_dir / "rule_b.rego",
        "# rule_id: duplicate.id\npackage safecore\n",
    )

    report = _lint(rules_dir)
    assert report["valid"] is False
    codes = [item["code"] for item in report["issues"]]  # type: ignore[index]
    assert "META001" in codes


def test_rule_linter_rejects_ambiguous_rule_id_metadata(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    _write_rule(
        rules_dir / "ambiguous.rego",
        "# rule_id: one.id\n# rule_id: two.id\npackage safecore\n",
    )

    report = _lint(rules_dir)
    assert report["valid"] is False
    codes = [item["code"] for item in report["issues"]]  # type: ignore[index]
    assert "META003" in codes


def test_rule_linter_rejects_forbidden_unconditional_allow(tmp_path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    _write_rule(
        rules_dir / "wild_allow.rego",
        "package safecore\nallow := true\n",
    )

    report = _lint(rules_dir)
    assert report["valid"] is False
    codes = [item["code"] for item in report["issues"]]  # type: ignore[index]
    assert "ALLOW001" in codes

