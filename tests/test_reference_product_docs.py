from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_reference_product_docs_exist_and_are_non_empty():
    required = [
        ROOT / "README.md",
        DOCS / "reference_product_app.md",
        DOCS / "product_user_flow.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing reference product docs: {missing}"

    for path in required:
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"


def test_readme_links_to_reference_product_app_honestly():
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    assert "reference product app" in text
    assert "docs/reference_product_app.md" in text
    assert "docs/product_user_flow.md" in text
    assert "not a production-ready platform" in text


def test_reference_product_docs_preserve_product_value_without_platform_claims():
    app_doc = (DOCS / "reference_product_app.md").read_text(encoding="utf-8").lower()
    flow_doc = (DOCS / "product_user_flow.md").read_text(encoding="utf-8").lower()

    assert "safe_http_status" in app_doc
    assert "reference product flow" in app_doc
    assert "not a production-ready platform" in app_doc

    assert "user or app" in flow_doc
    assert "guarded result" in flow_doc
    assert "allowed flow" in flow_doc
    assert "blocked host flow" in flow_doc
    assert "blocked method flow" in flow_doc
