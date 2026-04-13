from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_open_source_release_docs_exist_and_are_non_empty():
    required = [
        ROOT / "LICENSE",
        ROOT / "CONTRIBUTING.md",
        ROOT / "CODE_OF_CONDUCT.md",
        ROOT / "SECURITY.md",
        ROOT / "ROADMAP.md",
        ROOT / "SUPPORT.md",
        ROOT / "docs" / "open_source_scope.md",
        ROOT / "docs" / "open_source_release_pack_m2.md",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md",
        ROOT / ".github" / "pull_request_template.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing open-source release docs: {missing}"

    for path in required:
        assert path.read_text(encoding="utf-8").strip(), f"Empty file: {path.relative_to(ROOT)}"


def test_license_and_security_docs_match_public_release_posture():
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    security_text = (ROOT / "SECURITY.md").read_text(encoding="utf-8").lower()
    scope_text = (ROOT / "docs" / "open_source_scope.md").read_text(encoding="utf-8").lower()

    assert "Apache License" in license_text
    assert "Version 2.0" in license_text
    assert "report it privately" in security_text
    assert "dry-run-first" in security_text or "dry-run" in security_text
    assert "rc-stage validated core" in security_text or "rc/mvp" in security_text
    assert "apache 2.0" in scope_text
    assert "permissive open-source license" in scope_text


def test_readme_links_to_public_release_docs():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/public_positioning.md" in readme
    assert "docs/demo_quickstart.md" in readme
    assert "docs/demo_scenarios.md" in readme
    assert "docs/demo_value.md" in readme
    assert "docs/open_source_release_pack_m2.md" in readme
    assert "SUPPORT.md" in readme


def test_open_source_scope_and_roadmap_separate_current_core_from_future_scope():
    scope = (ROOT / "docs" / "open_source_scope.md").read_text(encoding="utf-8").lower()
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8").lower()

    assert "rc-stage validated core" in scope
    assert "what is intentionally not included yet" in scope
    assert "one practical safe integration path" in scope or "first practical safe integration path" in scope
    assert "intentionally later" in roadmap
    assert "production auth/authz" in roadmap


def test_contributing_support_and_pr_template_call_out_runtime_safety_review():
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8").lower()
    support = (ROOT / "SUPPORT.md").read_text(encoding="utf-8").lower()
    pr_template = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8").lower()

    assert "unsafe runtime changes require explicit review" in contributing
    assert "not a production-ready platform" in contributing
    assert "use `security.md`" in support or "use `security.md` for sensitive security reports" in support
    assert "no real external side effects enabled" in pr_template
    assert "no unintended runtime semantic regression" in pr_template
    assert "rc/mvp posture" in pr_template
