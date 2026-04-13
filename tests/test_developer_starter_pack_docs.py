from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_developer_starter_pack_docs_exist_and_are_non_empty():
    required = [
        ROOT / "README.md",
        DOCS / "developer_starter_pack.md",
        DOCS / "integration_flow_reference.md",
        DOCS / "copy_paste_integration_example.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing developer starter pack docs: {missing}"

    for path in required:
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"


def test_readme_links_to_developer_starter_pack():
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    assert "developer starter pack" in text
    assert "docs/developer_starter_pack.md" in text
    assert "docs/integration_flow_reference.md" in text
    assert "docs/copy_paste_integration_example.md" in text
    assert "safe_http_status" in text


def test_starter_pack_keeps_honest_scope_and_real_workflow_message():
    starter = (DOCS / "developer_starter_pack.md").read_text(encoding="utf-8").lower()
    flow = (DOCS / "integration_flow_reference.md").read_text(encoding="utf-8").lower()
    example = (DOCS / "copy_paste_integration_example.md").read_text(encoding="utf-8").lower()

    assert "app or agent" in starter
    assert "safe_http_status" in starter
    assert "not a production-ready platform" in starter

    assert "post /v1/guarded-execute" in flow
    assert "policyengine" in flow
    assert "auditlogger" in flow

    assert "service.execute_guarded_request(request)" in example
    assert "safe_read_only_fetched" in example
    assert "not" in example and "production-ready connector platform" in example
