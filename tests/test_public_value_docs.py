from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_public_value_docs_exist_and_are_non_empty():
    required = [
        ROOT / "README.md",
        DOCS / "public_positioning.md",
        DOCS / "demo_quickstart.md",
        DOCS / "demo_scenarios.md",
        DOCS / "demo_value.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing public value docs: {missing}"

    for path in required:
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"


def test_readme_is_demo_first_and_public_facing():
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "security control layer for AI agents" in text
    assert 'not another agent runtime' in text.lower()
    assert "python scripts/demo_smoke.py" in text
    assert "ALLOW" in text
    assert "NEEDS_APPROVAL" in text
    assert "DENY" in text
    assert "docs/demo_quickstart.md" in text
    assert "docs/demo_scenarios.md" in text
    assert "docs/demo_value.md" in text


def test_demo_scenarios_doc_covers_three_expected_paths():
    text = (DOCS / "demo_scenarios.md").read_text(encoding="utf-8")

    assert "| `ALLOW` |" in text
    assert "| `NEEDS_APPROVAL` |" in text
    assert "| `DENY` |" in text
    assert "DRY_RUN_SIMULATED" in text
    assert "PENDING" in text
    assert "approval not applicable" in text.lower()


def test_public_positioning_and_demo_value_preserve_non_goal_message():
    positioning = (DOCS / "public_positioning.md").read_text(encoding="utf-8").lower()
    demo_value = (DOCS / "demo_value.md").read_text(encoding="utf-8").lower()

    assert "real external side effects" in positioning
    assert "production auth/authz" in positioning
    assert "dry-run posture" in positioning
    assert "control layer" in demo_value
    assert "not \"just another agent.\"" in demo_value.lower()
