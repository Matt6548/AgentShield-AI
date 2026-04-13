from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_rc_artifact_files_exist_and_are_non_empty():
    required = [
        DOCS / "rc_freeze_notes.md",
        DOCS / "stakeholder_review_pack.md",
        DOCS / "launch_checklist.md",
        DOCS / "known_issues.md",
        ROOT / ".github" / "workflows" / "rc-freeze.yml",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing RC artifacts: {missing}"
    for path in required:
        text = path.read_text(encoding="utf-8").strip()
        assert text, f"File should not be empty: {path.relative_to(ROOT)}"


def test_freeze_notes_explicitly_freeze_runtime_semantics():
    text = (DOCS / "rc_freeze_notes.md").read_text(encoding="utf-8").lower()
    assert "runtime/business behavior is frozen" in text
    assert "decision semantics are frozen" in text
    assert "no new runtime/business features" in text
    assert "no policy/approval/escalation semantic changes" in text


def test_launch_checklist_contains_rollback_and_integrity_steps():
    text = (DOCS / "launch_checklist.md").read_text(encoding="utf-8").lower()
    assert "audit integrity verification" in text
    assert "rollback readiness" in text
    assert "policy pack selection verification" in text
    assert "tests/test_prompt_files.py" in text
    assert "tests/test_rc_freeze_consistency.py" in text


def test_stakeholder_pack_contains_signoff_and_go_no_go_sections():
    text = (DOCS / "stakeholder_review_pack.md").read_text(encoding="utf-8").lower()
    assert "signoff owners and status fields" in text
    assert "decision_status" in text
    assert "go/no-go criteria" in text
    assert "engineering owner" in text
    assert "security owner" in text
    assert "qa/release owner" in text


def test_known_issues_distinguishes_limitations_and_blockers():
    text = (DOCS / "known_issues.md").read_text(encoding="utf-8")
    assert "## Accepted MVP Limitations (Non-Blockers)" in text
    assert "## Deferred Scope (Planned, Not RC Blocking)" in text
    assert "## RC Blockers (Must Be Empty For GO)" in text


def test_rc_docs_reference_real_files():
    referenced_paths = [
        "docs/known_issues.md",
        "docs/migration_guide_v2.md",
        "docs/stakeholder_review_pack.md",
        "docs/rc_freeze_notes.md",
        "tests/test_contracts_smoke.py",
        "tests/test_prompt_files.py",
        "tests/test_rc_freeze_consistency.py",
        ".github/workflows/rc-freeze.yml",
    ]
    for relative in referenced_paths:
        assert (ROOT / relative).exists(), f"Referenced file missing: {relative}"


def test_rc_freeze_workflow_is_deterministic_and_non_publishing():
    workflow = (ROOT / ".github" / "workflows" / "rc-freeze.yml").read_text(encoding="utf-8")
    lower = workflow.lower()

    assert "name: RC Freeze Verification" in workflow
    assert "workflow_dispatch:" in workflow
    assert "tests/test_contracts_smoke.py" in workflow
    assert "tests/test_prompt_files.py" in workflow
    assert "tests/test_rc_freeze_consistency.py" in workflow
    assert "python -m pytest -q" in workflow
    assert "python -m compileall src tests" in workflow
    assert "python -m build" in workflow
    assert "publish" not in lower
