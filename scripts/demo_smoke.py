"""Frozen demo smoke runner for the current SafeCore RC repository."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.api.service import GuardedExecutionService
from src.approval import ApprovalManager
from src.audit import AuditLogger
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.policy import PolicyEngine
from src.utils.tool_policies import ToolGuard


DEMO_SCENARIOS = ("allow_case", "approval_case", "deny_case")
DEFAULT_INPUT_DIR = ROOT_DIR / "examples" / "demo_inputs"
DEFAULT_AUDIT_FILE = ROOT_DIR / "examples" / "demo_audit.log.jsonl"


class CounterIdFactory:
    """Provide stable approval request ids for demo readability."""

    def __init__(self) -> None:
        self.counter = 0

    def __call__(self) -> str:
        self.counter += 1
        return f"apr-demo-{self.counter:04d}"


def build_demo_service(audit_file: Path) -> GuardedExecutionService:
    """Build the current guarded service path without changing semantics."""
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    approval_manager = ApprovalManager(
        audit_logger=audit_logger,
        id_factory=CounterIdFactory(),
    )
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=approval_manager,
    )


def load_demo_request(scenario_name: str, input_dir: Path | None = None) -> dict[str, Any]:
    """Load one demo request from JSON."""
    resolved_input_dir = input_dir or DEFAULT_INPUT_DIR
    scenario_path = resolved_input_dir / f"{scenario_name}.json"
    payload = json.loads(scenario_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Demo scenario '{scenario_name}' must be a JSON object.")
    return payload


def run_demo_scenarios(
    input_dir: Path | None = None,
    audit_file: Path | None = None,
) -> list[dict[str, Any]]:
    """Run the three frozen demo scenarios against the current code path."""
    resolved_input_dir = input_dir or DEFAULT_INPUT_DIR
    resolved_audit_file = audit_file or DEFAULT_AUDIT_FILE

    if resolved_audit_file.exists():
        resolved_audit_file.unlink()

    service = build_demo_service(resolved_audit_file)
    results: list[dict[str, Any]] = []
    for scenario_name in DEMO_SCENARIOS:
        request = load_demo_request(scenario_name, resolved_input_dir)
        response = service.execute_guarded_request(request)
        results.append(
            {
                "scenario": scenario_name,
                "request": request,
                "response": response,
                "audit_file": resolved_audit_file,
            }
        )
    return results


def build_demo_summaries(
    input_dir: Path | None = None,
    audit_file: Path | None = None,
) -> list[dict[str, Any]]:
    """Build compact, human-readable summaries for each demo scenario."""
    summaries: list[dict[str, Any]] = []
    for item in run_demo_scenarios(input_dir=input_dir, audit_file=audit_file):
        response = item["response"]
        policy_decision = response.get("policy_decision", {})
        execution_result = response.get("execution_result", {})
        execution_output = execution_result.get("output", {}) if isinstance(execution_result, dict) else {}
        approval = response.get("approval", {})
        audit_integrity = response.get("audit_integrity", {})

        summaries.append(
            {
                "scenario": item["scenario"],
                "run_id": response.get("run_id"),
                "decision": policy_decision.get("decision"),
                "risk_score": policy_decision.get("risk_score"),
                "blocked": bool(response.get("blocked", True)),
                "approval_status": approval.get("status"),
                "execution_status": execution_output.get("status"),
                "dry_run": bool(response.get("dry_run", False)),
                "audit_integrity_valid": bool(audit_integrity.get("valid", False)),
                "audit_hash": response.get("audit_record", {}).get("hash"),
                "audit_file": _display_path(item["audit_file"]),
            }
        )
    return summaries


def format_summary_line(summary: dict[str, Any]) -> str:
    """Format one compact summary line for CLI output."""
    return (
        f"[{summary['scenario']}] "
        f"decision={summary['decision']} "
        f"risk_score={summary['risk_score']} "
        f"blocked={summary['blocked']} "
        f"approval_status={summary['approval_status']} "
        f"execution_status={summary['execution_status']} "
        f"audit_integrity={summary['audit_integrity_valid']} "
        f"audit={summary['audit_file']}"
    )


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR)).replace("\\", "/")
    except ValueError:
        return str(path)


def main() -> None:
    for summary in build_demo_summaries():
        print(format_summary_line(summary))


if __name__ == "__main__":
    main()
