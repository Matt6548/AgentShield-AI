from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_why_safecore_docs_exist_and_are_linked_from_readme():
    required = [
        DOCS / "why_safecore.md",
        DOCS / "with_vs_without_safecore.md",
    ]

    for path in required:
        assert path.exists(), f"Missing doc: {path.relative_to(ROOT)}"
        assert path.read_text(encoding="utf-8").strip(), f"Empty doc: {path.relative_to(ROOT)}"

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/why_safecore.md" in readme
    assert "docs/with_vs_without_safecore.md" in readme


def test_why_safecore_docs_explain_role_and_keep_scope_honest():
    why_text = (DOCS / "why_safecore.md").read_text(encoding="utf-8").lower()
    compare_text = (DOCS / "with_vs_without_safecore.md").read_text(encoding="utf-8").lower()
    combined = "\n".join([why_text, compare_text])

    assert "control layer" in combined
    assert "agent runtime" in combined
    assert "allow" in combined
    assert "needs_approval" in combined or "needs approval" in combined
    assert "deny" in combined
    assert "approval visibility" in combined
    assert "audit" in combined
    assert "plain-language explanation" in combined or "plain-language" in combined
    assert "validated core" in combined
    assert "not a production-ready enterprise platform" in combined or "not another agent runtime" in combined

    assert "enterprise-grade guarantees" not in combined
    assert "production-ready enterprise platform" in combined
