from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_first_use_case_docs_exist_and_are_non_empty():
    required = [
        ROOT / "README.md",
        DOCS / "first_use_case.md",
        DOCS / "safe_http_connector_example.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing first use case docs: {missing}"

    for path in required:
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"


def test_readme_promotes_first_use_case_honestly():
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    assert "first practical use case" in text
    assert "safe_http_status connector" in text
    assert "http://127.0.0.1:8000/ui" in text
    assert "allowlisted_get" in text
    assert "blocked_host" in text
    assert "blocked_method" in text
    assert "not a universal http executor" in text
    assert "production-ready platform" in text


def test_first_use_case_doc_explains_workflow_and_boundaries():
    text = (DOCS / "first_use_case.md").read_text(encoding="utf-8").lower()

    assert "ai agent -> safecore -> safe_http_status connector -> allowed or blocked result" in text
    assert "what is allowed" in text
    assert "what is blocked" in text
    assert "how to run it locally" in text
    assert "how to verify behavior" in text
    assert "honest limitations" in text
    assert "open-source rc/mvp" in text
    assert "validated core" in text
    assert "not a production-ready platform" in text
