import json

from src.audit import AuditLogger
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.policy import PolicyEngine
from src.utils.tool_policies import ToolGuard


def _run_guarded_workflow(request: dict, audit_file_path) -> dict:
    policy_engine = PolicyEngine(opa_binary="definitely-not-opa")
    data_guard = DataGuard()
    tool_guard = ToolGuard()
    exec_guard = ExecutionGuard(tool_guard=tool_guard)
    audit_logger = AuditLogger(audit_file_path)

    policy_decision = policy_engine.evaluate(request)
    data_result = data_guard.evaluate(request.get("payload", {}))
    tool_result = tool_guard.evaluate(request)

    blocked_by: list[str] = []
    if policy_decision["decision"] != "ALLOW":
        blocked_by.append(f"policy:{policy_decision['decision']}")
    if data_result["action"] == "BLOCK":
        blocked_by.append("data_guard:BLOCK")
    if not tool_result["allowed"]:
        blocked_by.append(f"tool_guard:{tool_result['decision']}")

    exec_request = {
        "tool": request.get("tool", ""),
        "command": request.get("command", ""),
        "blocked_by": blocked_by,
    }
    exec_result = exec_guard.execute(exec_request, dry_run=True)

    audit_record = audit_logger.append_record(
        {
            "run_id": str(request.get("run_id", "run-unknown")),
            "actor": str(request.get("actor", "unknown")),
            "step": "guarded_workflow",
            "action": "execute",
            "data": {
                "policy": policy_decision,
                "data_guard": data_result,
                "tool_guard": tool_result,
                "execution": exec_result,
            },
        }
    )

    return {
        "policy": policy_decision,
        "data_guard": data_result,
        "tool_guard": tool_result,
        "execution": exec_result,
        "audit_record": audit_record,
    }


def test_guarded_workflow_safe_read_only_path(tmp_path):
    request = {
        "run_id": "safe-run",
        "actor": "analyst",
        "action": "read_status",
        "tool": "shell",
        "command": "ls",
        "payload": {"query": "status"},
    }
    result = _run_guarded_workflow(request, tmp_path / "safe-audit.jsonl")

    assert result["policy"]["decision"] in {"ALLOW", "NEEDS_APPROVAL", "DENY"}
    assert result["data_guard"]["action"] == "ALLOW"
    assert result["tool_guard"]["allowed"] is True
    assert result["execution"]["success"] is True
    assert result["execution"]["output"]["status"] == "DRY_RUN_SIMULATED"
    assert len(result["audit_record"]["hash"]) == 64


def test_guarded_workflow_sensitive_payload_redacts(tmp_path):
    request = {
        "run_id": "redact-run",
        "actor": "analyst",
        "action": "read_status",
        "tool": "shell",
        "command": "ls",
        "payload": {"email": "person@example.com"},
    }
    result = _run_guarded_workflow(request, tmp_path / "redact-audit.jsonl")

    assert result["data_guard"]["action"] == "REDACT"
    assert result["data_guard"]["redacted_payload"]["email"] == "[REDACTED]"
    assert result["execution"]["success"] is True


def test_guarded_workflow_dangerous_command_is_denied_before_execution(tmp_path):
    request = {
        "run_id": "deny-run",
        "actor": "analyst",
        "action": "execute",
        "tool": "shell",
        "command": "rm -rf /",
        "payload": {"note": "danger"},
    }
    result = _run_guarded_workflow(request, tmp_path / "deny-audit.jsonl")

    assert result["tool_guard"]["allowed"] is False
    assert result["execution"]["success"] is False
    assert result["execution"]["output"]["status"] == "BLOCKED"


def test_blocked_execution_still_generates_audit_evidence(tmp_path):
    audit_file = tmp_path / "blocked-audit.jsonl"
    request = {
        "run_id": "blocked-evidence-run",
        "actor": "analyst",
        "action": "execute",
        "tool": "shell",
        "command": "rm -rf /",
        "payload": {"card": "4111 1111 1111 1111", "destination": "https://evil.example"},
    }
    result = _run_guarded_workflow(request, audit_file)

    assert result["execution"]["success"] is False
    assert len(result["audit_record"]["hash"]) == 64

    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    loaded = json.loads(lines[0])
    assert loaded["run_id"] == "blocked-evidence-run"
    assert loaded["data"]["execution"]["output"]["status"] == "BLOCKED"

