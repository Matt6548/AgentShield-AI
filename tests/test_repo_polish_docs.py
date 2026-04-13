from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_readme_start_here_surfaces_value_and_adoption_docs():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/quickstart_3min.md" in readme
    assert "docs/first_run_checklist.md" in readme
    assert "docs/troubleshooting.md" in readme
    assert "docs/why_safecore.md" in readme
    assert "docs/with_vs_without_safecore.md" in readme
    assert "docs/adoption_recipes.md" in readme


def test_adoption_and_value_docs_keep_navigation_and_scope_consistent():
    adoption = (DOCS / "adoption_recipes.md").read_text(encoding="utf-8").lower()
    why = (DOCS / "why_safecore.md").read_text(encoding="utf-8").lower()
    compare = (DOCS / "with_vs_without_safecore.md").read_text(encoding="utf-8").lower()

    assert "with_vs_without_safecore.md" in adoption
    assert "why_safecore.md" in adoption
    assert "with_vs_without_safecore.md" in why

    combined = "\n".join([adoption, why, compare])
    assert "validated core" in combined
    assert "product shell" in combined
    assert "baseline integration" in combined or "baseline integrations" in combined
    assert "not a production-ready enterprise platform" in combined
    assert "not another agent runtime" in combined
