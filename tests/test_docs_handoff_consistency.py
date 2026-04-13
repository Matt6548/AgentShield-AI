from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.example_run import build_flow_summaries


def test_required_handoff_docs_exist():
    required = [
        DOCS_DIR / "handoff_pack.md",
        DOCS_DIR / "operations_runbook.md",
        DOCS_DIR / "mvp_scope.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing Package K docs: {missing}"


def test_handoff_and_runbook_have_required_sections():
    handoff = (DOCS_DIR / "handoff_pack.md").read_text(encoding="utf-8")
    runbook = (DOCS_DIR / "operations_runbook.md").read_text(encoding="utf-8")
    scope = (DOCS_DIR / "mvp_scope.md").read_text(encoding="utf-8")

    handoff_sections = [
        "## Architecture Snapshot",
        "## Module Ownership Map",
        "## Test Strategy Map",
        "## Deferred Scope",
        "## First-Week Onboarding Steps",
    ]
    runbook_sections = [
        "## Local Startup and Testing",
        "## Integrity-Check Procedure",
        "## Broken Audit Chain Incident Steps",
        "## Policy Pack Selection Verification",
        "## Expected Observability Signals",
    ]
    scope_sections = [
        "## Runtime Guarantees",
        "## In Scope (Implemented Foundations)",
        "## Out of Scope (Deferred)",
    ]

    for section in handoff_sections:
        assert section in handoff
    for section in runbook_sections:
        assert section in runbook
    for section in scope_sections:
        assert section in scope


def test_readme_references_package_k_docs():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/handoff_pack.md" in readme
    assert "docs/operations_runbook.md" in readme
    assert "docs/mvp_scope.md" in readme


def test_markdown_links_point_to_real_files():
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    checked_files = [
        ROOT / "README.md",
        DOCS_DIR / "handoff_pack.md",
        DOCS_DIR / "operations_runbook.md",
        DOCS_DIR / "mvp_scope.md",
    ]

    for file_path in checked_files:
        text = file_path.read_text(encoding="utf-8")
        for link in link_pattern.findall(text):
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            target = link.split("#", 1)[0].strip()
            if not target:
                continue
            if target.startswith("/"):
                resolved = ROOT / target.lstrip("/")
            else:
                resolved = (file_path.parent / target).resolve()
            assert resolved.exists(), f"Broken link in {file_path.name}: {link}"


def test_example_run_summary_contains_handoff_fields(tmp_path):
    summaries = build_flow_summaries(audit_file=tmp_path / "example_audit.jsonl")
    assert len(summaries) >= 3

    required_flows = {"safe_path", "approval_required_path", "rejected_path"}
    seen = {str(item.get("flow")) for item in summaries}
    assert required_flows.issubset(seen)

    for summary in summaries:
        assert "policy_decision" in summary
        assert "approval_status" in summary
        assert "model_route" in summary
        assert "audit_integrity" in summary

        policy_decision = summary["policy_decision"]
        assert isinstance(policy_decision, dict)
        assert "decision" in policy_decision
        assert "risk_score" in policy_decision

        model_route = summary["model_route"]
        assert isinstance(model_route, dict)
        assert "route_id" in model_route
        assert "model_profile" in model_route
        assert "profile_id" in model_route
        assert "profile_name" in model_route

        audit_integrity = summary["audit_integrity"]
        assert isinstance(audit_integrity, dict)
        assert "valid" in audit_integrity
        assert "broken_indices" in audit_integrity
