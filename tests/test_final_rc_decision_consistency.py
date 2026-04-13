from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_final_rc_docs_exist_and_are_non_empty():
    required = [
        DOCS / "final_go_no_go.md",
        DOCS / "signoff_status.md",
        DOCS / "release_readiness_summary.md",
        DOCS / "stakeholder_review_pack.md",
        DOCS / "launch_checklist.md",
        DOCS / "known_issues.md",
        DOCS / "rc_freeze_notes.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing final RC docs: {missing}"
    for path in required:
        assert path.read_text(encoding="utf-8").strip(), f"File is empty: {path.relative_to(ROOT)}"


def test_signoff_status_contains_required_sections_and_values():
    text = (DOCS / "signoff_status.md").read_text(encoding="utf-8")
    assert "## Allowed Status Values" in text
    assert "`PENDING`" in text
    assert "`APPROVED`" in text
    assert "`REJECTED`" in text
    assert "Engineering Owner" in text
    assert "Security Owner" in text
    assert "QA/Release Owner" in text
    assert "Product/Program Owner" in text
    assert "## Overall Signoff Summary" in text


def test_final_go_no_go_contains_logic_and_explicit_recommendation():
    text = (DOCS / "final_go_no_go.md").read_text(encoding="utf-8")
    lower = text.lower()
    signoff_text = (DOCS / "signoff_status.md").read_text(encoding="utf-8")

    assert "## Decision Logic" in text
    assert "`NO-GO` if critical blockers exist." in text
    assert "`GO WITH CONDITIONS` if no critical blockers exist but required signoffs are pending." in text
    assert "`GO` if all checks pass and required signoffs are approved." in text
    if "Pending: 0" in signoff_text and "Rejected: 0" in signoff_text:
        assert "Recommendation: GO" in text
        assert "required stakeholder signoffs are approved." in lower
    else:
        assert "Recommendation: GO WITH CONDITIONS" in text
        assert "required signoff approvals are still pending" in lower


def test_known_issues_distinguishes_limitations_deferred_and_blockers():
    text = (DOCS / "known_issues.md").read_text(encoding="utf-8")
    assert "## Accepted MVP Limitations (Non-Blockers)" in text
    assert "## Deferred Scope (Planned, Not RC Blocking)" in text
    assert "## RC Blockers (Must Be Empty For GO)" in text
    assert "Current status: **NO OPEN CRITICAL RC BLOCKERS**." in text


def test_release_readiness_summary_contains_required_operational_posture():
    text = (DOCS / "release_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "dry_run-only execution" in text
    assert "policy pack `v1` remains default".lower() in text
    assert "policy pack `v2` remains opt-in only".lower() in text
    assert "no real external connector side effects" in text


def test_recommendation_matches_signoff_state():
    signoff_text = (DOCS / "signoff_status.md").read_text(encoding="utf-8")
    go_no_go_text = (DOCS / "final_go_no_go.md").read_text(encoding="utf-8")
    if "Pending: 0" in signoff_text and "Rejected: 0" in signoff_text:
        assert "Recommendation: GO" in go_no_go_text
    elif "`PENDING`" in signoff_text and "Pending: 0" not in signoff_text:
        assert "Recommendation: GO WITH CONDITIONS" in go_no_go_text
        assert "Recommendation: GO\n" not in go_no_go_text


def test_final_docs_and_workflow_references_point_to_real_files():
    referenced = [
        "docs/known_issues.md",
        "docs/signoff_status.md",
        "docs/release_readiness_summary.md",
        "docs/final_go_no_go.md",
        "docs/stakeholder_review_pack.md",
        "docs/launch_checklist.md",
        "tests/test_final_rc_decision_consistency.py",
        ".github/workflows/rc-freeze.yml",
        ".github/workflows/ci.yml",
    ]
    for relative in referenced:
        assert (ROOT / relative).exists(), f"Referenced file missing: {relative}"


def test_workflows_include_final_rc_decision_gate():
    rc_workflow = (ROOT / ".github" / "workflows" / "rc-freeze.yml").read_text(encoding="utf-8")
    ci_workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "tests/test_final_rc_decision_consistency.py" in rc_workflow
    assert "tests/test_final_rc_decision_consistency.py" in ci_workflow
    assert "python -m pytest -q tests/test_prompt_files.py" in rc_workflow
    assert "python -m compileall src tests" in rc_workflow
    assert "python -m build" in rc_workflow
