from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_productization_pack_m1_docs_exist_and_are_linked():
    required = [
        ROOT / "README.md",
        DOCS / "productization_pack_m1.md",
        DOCS / "provider_setup_guide.md",
    ]
    for path in required:
        assert path.exists(), f"Missing file: {path.relative_to(ROOT)}"
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"

    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    assert "product shell onboarding" in readme
    assert "docs/productization_pack_m1.md" in readme
    assert "provider status / configuration" in readme


def test_productization_pack_m1_docs_preserve_honest_scope():
    pack_doc = (DOCS / "productization_pack_m1.md").read_text(encoding="utf-8").lower()
    provider_doc = (DOCS / "provider_setup_guide.md").read_text(encoding="utf-8").lower()

    assert "open-source rc/mvp" in pack_doc
    assert "validated core" in pack_doc
    assert "dry-run-first" in pack_doc
    assert "not a production-ready platform" in pack_doc
    assert "localstorage" in pack_doc

    assert "does not receive raw secret values" in provider_doc
    assert "onboarding progress" in provider_doc
    assert "not a production-ready platform" in provider_doc
