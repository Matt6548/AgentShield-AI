from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_open_source_release_pack_m2_exists_and_is_linked():
    required = [
        ROOT / "README.md",
        ROOT / "SUPPORT.md",
        DOCS / "open_source_release_pack_m2.md",
    ]
    for path in required:
        assert path.exists(), f"Missing file: {path.relative_to(ROOT)}"
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"

    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    assert "what you get today" in readme
    assert "current boundaries" in readme
    assert "who this is for" in readme
    assert "project status" in readme
    assert "docs/open_source_release_pack_m2.md" in readme


def test_open_source_release_pack_m2_contains_release_facing_content():
    text = (DOCS / "open_source_release_pack_m2.md").read_text(encoding="utf-8").lower()

    assert "what is ready now" in text
    assert "what is intentionally out of scope" in text
    assert "recommended first demo flow" in text
    assert "release notes draft" in text
    assert "public launch checklist" in text
    assert "github about text suggestions" in text
    assert "repo topics / tags suggestions" in text
    assert "recommended screenshots" in text
    assert "recommended first public video order" in text


def test_public_release_pack_preserves_honest_positioning():
    combined = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8").lower(),
            (ROOT / "SUPPORT.md").read_text(encoding="utf-8").lower(),
            (DOCS / "open_source_release_pack_m2.md").read_text(encoding="utf-8").lower(),
        ]
    )

    assert "open-source rc/mvp" in combined
    assert "validated core" in combined
    assert "not a production-ready platform" in combined
    assert "not another agent runtime" in combined
