from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_visual_pack_docs_exist_and_are_non_empty():
    required = [
        ROOT / "README.md",
        DOCS / "visual_story.md",
        DOCS / "architecture_visual.md",
        DOCS / "professional_demo_pack.md",
        DOCS / "professional_positioning.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing visual pack docs: {missing}"

    for path in required:
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"


def test_readme_links_to_visual_pack_and_keeps_honest_positioning():
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    assert "docs/visual_story.md" in text
    assert "docs/architecture_visual.md" in text
    assert "docs/professional_demo_pack.md" in text
    assert "docs/professional_positioning.md" in text
    assert "validated core" in text or "rc/mvp" in text
    assert "production-ready platform" in text


def test_visual_docs_preserve_control_layer_message_without_production_claims():
    visual_story = (DOCS / "visual_story.md").read_text(encoding="utf-8").lower()
    architecture = (DOCS / "architecture_visual.md").read_text(encoding="utf-8").lower()
    demo_pack = (DOCS / "professional_demo_pack.md").read_text(encoding="utf-8").lower()
    positioning = (DOCS / "professional_positioning.md").read_text(encoding="utf-8").lower()

    assert "control layer" in visual_story
    assert "allow" in visual_story
    assert "needs_approval" in visual_story
    assert "deny" in visual_story

    assert "ai agent" in architecture
    assert "policy" in architecture
    assert "approval" in architecture
    assert "audit" in architecture

    assert "python scripts/demo_smoke.py" in demo_pack
    assert "one minute" in demo_pack
    assert "dry-run-only" in demo_pack

    assert "security engineer" in positioning
    assert "platform engineer" in positioning
    assert "technical founder" in positioning
    assert "not a production-ready platform" in positioning
