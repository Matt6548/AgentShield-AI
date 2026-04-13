from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_productization_pack_b_docs_exist_and_are_linked():
    required = [
        ROOT / "README.md",
        DOCS / "productization_pack_b.md",
        DOCS / "provider_setup_guide.md",
    ]
    for path in required:
        assert path.exists(), f"Missing file: {path.relative_to(ROOT)}"
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"

    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    assert "multilingual product shell" in readme
    assert "provider status / configuration" in readme
    assert "docs/productization_pack_b.md" in readme
    assert "docs/provider_setup_guide.md" in readme


def test_productization_pack_b_docs_preserve_honest_scope():
    pack_doc = (DOCS / "productization_pack_b.md").read_text(encoding="utf-8").lower()
    provider_doc = (DOCS / "provider_setup_guide.md").read_text(encoding="utf-8").lower()

    assert "open-source rc/mvp" in pack_doc
    assert "validated core" in pack_doc
    assert "not a production-ready platform" in pack_doc
    assert "dry-run-first" in pack_doc

    assert "openai_api_key" in provider_doc
    assert "anthropic_api_key" in provider_doc
    assert "openrouter_api_key" in provider_doc
    assert "does not receive raw secret values" in provider_doc
    assert "not a production-ready platform" in provider_doc
