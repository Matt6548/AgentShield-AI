from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_launch_content_docs_exist_and_are_non_empty():
    required = [
        DOCS / "product_brief_en.md",
        DOCS / "product_brief_ru.md",
        DOCS / "presentation_outline.md",
        DOCS / "notebooklm_source_pack.md",
        DOCS / "video_script_en_90s.md",
        DOCS / "video_script_ru_90s.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing launch content docs: {missing}"

    for path in required:
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"


def test_readme_links_to_launch_content_pack():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/product_brief_en.md" in readme
    assert "docs/product_brief_ru.md" in readme
    assert "docs/presentation_outline.md" in readme
    assert "docs/notebooklm_source_pack.md" in readme
    assert "docs/video_script_en_90s.md" in readme
    assert "docs/video_script_ru_90s.md" in readme


def test_launch_content_pack_preserves_honest_positioning():
    files = [
        ROOT / "README.md",
        DOCS / "product_brief_en.md",
        DOCS / "product_brief_ru.md",
        DOCS / "presentation_outline.md",
        DOCS / "notebooklm_source_pack.md",
        DOCS / "video_script_en_90s.md",
        DOCS / "video_script_ru_90s.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in files)

    assert "validated core" in combined or "rc/mvp" in combined
    assert "not a production-ready platform" in combined or "не production-ready platform" in combined
    assert "open-source rc/mvp" in combined or "open-source rc-stage" in combined


def test_launch_content_pack_avoids_positive_production_ready_claims():
    files = [
        DOCS / "product_brief_en.md",
        DOCS / "product_brief_ru.md",
        DOCS / "presentation_outline.md",
        DOCS / "notebooklm_source_pack.md",
        DOCS / "video_script_en_90s.md",
        DOCS / "video_script_ru_90s.md",
    ]

    for path in files:
        text = path.read_text(encoding="utf-8").lower()
        assert "finished enterprise production platform" not in text
        assert (
            "production-ready" not in text
            or "not a production-ready platform" in text
            or "not be described as a production-ready platform" in text
            or "не production-ready platform" in text
            or "нельзя честно называть production-ready platform" in text
        )
