from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DOC = ROOT / "docs" / "safety_copilot_advisory.md"


def test_safety_copilot_doc_exists_and_is_linked_from_readme():
    assert DOC.exists()
    readme = README.read_text(encoding="utf-8-sig").lower()
    assert "safety copilot advisory" in readme
    assert "docs/safety_copilot_advisory.md" in readme


def test_safety_copilot_doc_preserves_honest_scope():
    text = DOC.read_text(encoding="utf-8").lower()
    assert "advisory only" in text
    assert "disabled" in text
    assert "does not change" in text
    assert "not a production" in text or "not included yet" in text
    assert "new agent runtime" in text
