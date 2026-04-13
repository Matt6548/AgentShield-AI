from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_product_shell_docs_exist_and_are_linked_from_readme():
    required = [
        ROOT / "README.md",
        DOCS / "productization_pack_a.md",
        DOCS / "product_shell_user_guide.md",
    ]
    for path in required:
        assert path.exists(), f"Missing file: {path.relative_to(ROOT)}"
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"

    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    assert "product shell features" in readme
    assert "docs/productization_pack_a.md" in readme
    assert "docs/product_shell_user_guide.md" in readme


def test_product_shell_docs_preserve_honest_scope():
    pack_doc = (DOCS / "productization_pack_a.md").read_text(encoding="utf-8").lower()
    guide_doc = (DOCS / "product_shell_user_guide.md").read_text(encoding="utf-8").lower()

    assert "not a production-ready platform" in pack_doc
    assert "local json history store" in pack_doc
    assert "dry-run-first" in pack_doc

    assert "approval queue" in guide_doc
    assert "audit viewer" in guide_doc
    assert "pending does not mean approved" in guide_doc
    assert "not a production-ready platform" in guide_doc
