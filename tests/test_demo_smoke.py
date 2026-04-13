from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.demo_smoke import build_demo_summaries, format_summary_line


def test_demo_smoke_covers_allow_approval_and_deny(tmp_path):
    audit_file = tmp_path / "demo_audit.log.jsonl"
    summaries = build_demo_summaries(audit_file=audit_file)
    by_name = {item["scenario"]: item for item in summaries}

    assert set(by_name) == {"allow_case", "approval_case", "deny_case"}

    allow_case = by_name["allow_case"]
    assert allow_case["decision"] == "ALLOW"
    assert allow_case["risk_score"] == 15
    assert allow_case["blocked"] is False
    assert allow_case["approval_status"] == "BYPASSED"
    assert allow_case["execution_status"] == "DRY_RUN_SIMULATED"
    assert allow_case["dry_run"] is True

    approval_case = by_name["approval_case"]
    assert approval_case["decision"] == "NEEDS_APPROVAL"
    assert approval_case["risk_score"] == 55
    assert approval_case["blocked"] is True
    assert approval_case["approval_status"] == "PENDING"
    assert approval_case["execution_status"] == "BLOCKED"
    assert approval_case["dry_run"] is True

    deny_case = by_name["deny_case"]
    assert deny_case["decision"] == "DENY"
    assert deny_case["risk_score"] == 90
    assert deny_case["blocked"] is True
    assert deny_case["approval_status"] == "NOT_APPLICABLE_DENY"
    assert deny_case["execution_status"] == "BLOCKED"
    assert deny_case["dry_run"] is True


def test_demo_smoke_keeps_audit_chain_and_human_readable_output(tmp_path):
    audit_file = tmp_path / "demo_audit.log.jsonl"
    summaries = build_demo_summaries(audit_file=audit_file)

    assert audit_file.exists()
    lines = [line for line in audit_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    parsed = [json.loads(line) for line in lines]
    actions = [item["action"] for item in parsed]

    assert "api_guarded_execute" in actions
    assert "approval_request_created" in actions
    assert all(item["audit_integrity_valid"] is True for item in summaries)

    formatted = [format_summary_line(item) for item in summaries]
    assert formatted[0].startswith("[allow_case] decision=ALLOW risk_score=15")
    assert formatted[1].startswith("[approval_case] decision=NEEDS_APPROVAL risk_score=55")
    assert formatted[2].startswith("[deny_case] decision=DENY risk_score=90")
    assert all("audit=" in line for line in formatted)
