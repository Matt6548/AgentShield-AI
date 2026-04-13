from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_integrations_pack_n_docs_exist_and_are_non_empty():
    required = [
        ROOT / "docs" / "integrations_pack_n.md",
        ROOT / "docs" / "provider_gateway.md",
        ROOT / "docs" / "langchain_integration.md",
        ROOT / "docs" / "langgraph_integration.md",
        ROOT / "docs" / "mcp_adapter.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing Package N docs: {missing}"

    for path in required:
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"


def test_readme_links_to_integrations_pack_n_docs():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    assert "integrations pack" in readme
    assert "docs/integrations_pack_n.md" in readme
    assert "docs/provider_gateway.md" in readme
    assert "docs/langchain_integration.md" in readme
    assert "docs/langgraph_integration.md" in readme
    assert "docs/mcp_adapter.md" in readme


def test_integrations_pack_n_preserves_honest_positioning_and_real_files():
    combined = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8").lower(),
            (ROOT / "docs" / "integrations_pack_n.md").read_text(encoding="utf-8").lower(),
            (ROOT / "docs" / "provider_gateway.md").read_text(encoding="utf-8").lower(),
        ]
    )

    assert "security control layer for ai agents" in combined or "security/control layer for ai agents" in combined
    assert "validated core" in combined
    assert "not a production-ready platform" in combined
    assert "baseline support" in combined

    referenced = [
        ROOT / "src" / "providers" / "base.py",
        ROOT / "src" / "providers" / "gateway.py",
        ROOT / "src" / "providers" / "openai_adapter.py",
        ROOT / "src" / "providers" / "openai_compatible_adapter.py",
        ROOT / "src" / "integrations" / "langchain_adapter.py",
        ROOT / "src" / "integrations" / "langgraph_adapter.py",
        ROOT / "src" / "integrations" / "mcp_adapter.py",
    ]
    for path in referenced:
        assert path.exists(), f"Referenced Package N file missing: {path.relative_to(ROOT)}"
