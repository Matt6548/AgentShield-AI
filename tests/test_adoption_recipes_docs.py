from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_adoption_recipe_docs_exist_and_are_linked_from_readme():
    required = [
        DOCS / "adoption_recipes.md",
        DOCS / "recipe_langchain.md",
        DOCS / "recipe_langgraph.md",
        DOCS / "recipe_openai_compatible_local.md",
    ]

    for path in required:
        assert path.exists(), f"Missing doc: {path.relative_to(ROOT)}"
        assert path.read_text(encoding="utf-8").strip(), f"Empty doc: {path.relative_to(ROOT)}"

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/adoption_recipes.md" in readme
    assert "docs/recipe_langchain.md" in readme
    assert "docs/recipe_langgraph.md" in readme
    assert "docs/recipe_openai_compatible_local.md" in readme


def test_adoption_recipes_describe_safecore_role_and_honest_scope():
    combined = "\n".join(
        [
            (DOCS / "adoption_recipes.md").read_text(encoding="utf-8").lower(),
            (DOCS / "recipe_langchain.md").read_text(encoding="utf-8").lower(),
            (DOCS / "recipe_langgraph.md").read_text(encoding="utf-8").lower(),
            (DOCS / "recipe_openai_compatible_local.md").read_text(encoding="utf-8").lower(),
        ]
    )

    assert "baseline support" in combined or "baseline integration" in combined
    assert "starter recipe" in combined or "starting point" in combined
    assert "app or agent -> safecore" in combined or "safecore sits" in combined
    assert "validated core" in combined
    assert "not a production-ready platform" in combined or "production guarantees" in combined
    assert "dry-run-first" in combined or "dry-run" in combined
    assert "does not mean" in combined
    assert "enterprise-grade support" in combined

    assert "full framework coverage" in combined or "does not cover" in combined
