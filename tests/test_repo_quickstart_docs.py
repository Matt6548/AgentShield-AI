from __future__ import annotations

from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_license_matches_repository_license_choice():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    scope_text = (ROOT / "docs" / "open_source_scope.md").read_text(encoding="utf-8").lower()

    assert project["license"] == "Apache-2.0"
    assert "Apache License" in license_text
    assert "apache 2.0" in scope_text


def test_quickstart_first_run_and_troubleshooting_docs_exist_and_are_linked():
    required = [
        ROOT / "docs" / "quickstart_3min.md",
        ROOT / "docs" / "first_run_checklist.md",
        ROOT / "docs" / "troubleshooting.md",
    ]

    for path in required:
        assert path.exists(), f"Missing doc: {path.relative_to(ROOT)}"
        assert path.read_text(encoding="utf-8").strip(), f"Empty doc: {path.relative_to(ROOT)}"

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/quickstart_3min.md" in readme
    assert "docs/first_run_checklist.md" in readme
    assert "docs/troubleshooting.md" in readme


def test_quickstart_docs_reflect_current_safe_posture():
    quickstart = (ROOT / "docs" / "quickstart_3min.md").read_text(encoding="utf-8").lower()
    checklist = (ROOT / "docs" / "first_run_checklist.md").read_text(encoding="utf-8").lower()
    troubleshooting = (ROOT / "docs" / "troubleshooting.md").read_text(encoding="utf-8").lower()

    combined = "\n".join([quickstart, checklist, troubleshooting])

    assert "dry-run-first" in combined or "dry-run" in combined
    assert "rc/mvp" in combined
    assert "validated core" in combined
    assert "not a production-ready platform" in combined
    assert "allowlisted_get" in combined
    assert "blocked_host" in combined
    assert "blocked_method" in combined
    assert "provider status" in combined
    assert "advisory-only" in combined
