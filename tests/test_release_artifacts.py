from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_inputs_exist():
    required = [
        ROOT / "pyproject.toml",
        ROOT / "MANIFEST.in",
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".github" / "workflows" / "release-draft.yml",
        ROOT / "docs" / "release.md",
        ROOT / "docs" / "compatibility_matrix.md",
        ROOT / "docs" / "security_test_harness.md",
        ROOT / "docs" / "policy_pack_v2.md",
        ROOT / "docs" / "migration_guide_v2.md",
        ROOT / "docs" / "release_candidate_checklist.md",
        ROOT / "docs" / "mvp_scope.md",
        ROOT / "docs" / "operations_runbook.md",
        ROOT / "docs" / "handoff_pack.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing release artifact inputs: {missing}"


def test_release_workflow_looks_plausible():
    workflow_path = ROOT / ".github" / "workflows" / "release-draft.yml"
    text = workflow_path.read_text(encoding="utf-8")

    assert "name: Release Draft" in text
    assert "workflow_dispatch:" in text
    assert "python -m pytest -q" in text
    assert "tests/test_prompt_files.py" in text
    assert "python -m compileall src tests" in text
    assert "python -m build" in text
    assert "actions/upload-artifact" in text
    assert "publish" not in text.lower()


def test_release_docs_reference_manual_or_gated_publish():
    release_doc = (ROOT / "docs" / "release.md").read_text(encoding="utf-8").lower()
    assert "draft" in release_doc
    assert "manual" in release_doc or "gated" in release_doc
    assert "not publish" in release_doc or "no publish" in release_doc


def test_release_docs_include_package_k_handoff_artifacts():
    release_doc = (ROOT / "docs" / "release.md").read_text(encoding="utf-8")
    assert "docs/mvp_scope.md" in release_doc
    assert "docs/operations_runbook.md" in release_doc
    assert "docs/handoff_pack.md" in release_doc
