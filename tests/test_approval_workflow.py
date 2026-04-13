import json

from src.approval import APPROVAL_STATUS_APPROVED, APPROVAL_STATUS_PENDING, APPROVAL_STATUS_REJECTED
from src.approval import ApprovalManager
from src.audit import AuditLogger
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.policy import PolicyEngine
from src.policy.policy_engine import DECISION_DENY, DECISION_NEEDS_APPROVAL
from src.utils.tool_policies import ToolGuard


class CounterIdFactory:
    def __init__(self) -> None:
        self.counter = 0

    def __call__(self) -> str:
        self.counter += 1
        return f"apr-{self.counter:04d}"


def _new_components(audit_file):
    audit_logger = AuditLogger(audit_file)
    approval_manager = ApprovalManager(
        audit_logger=audit_logger,
        id_factory=CounterIdFactory(),
    )
    return {
        "policy": PolicyEngine(opa_binary="definitely-not-opa"),
        "data_guard": DataGuard(),
        "tool_guard": ToolGuard(),
        "exec_guard": ExecutionGuard(),
        "approval": approval_manager,
        "audit": audit_logger,
    }


def _execute_with_blockers(components, request: dict, blockers: list[str]) -> dict:
    exec_request = {
        "tool": request.get("tool", ""),
        "command": request.get("command", ""),
        "blocked_by": blockers,
    }
    return components["exec_guard"].execute(exec_request, dry_run=True)


def test_needs_approval_blocks_until_approved_then_executes(tmp_path):
    components = _new_components(tmp_path / "approval_workflow.jsonl")
    request = {
        "run_id": "run-approval-1",
        "actor": "operator",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"safe": True},
    }

    policy_decision = components["policy"].evaluate(request)
    assert policy_decision["decision"] == DECISION_NEEDS_APPROVAL
    assert components["approval"].is_required(
        policy_decision["risk_score"],
        policy_decision["decision"],
    )

    approval_request = components["approval"].create_request(
        {
            "run_id": request["run_id"],
            "actor": request["actor"],
            "policy_decision": policy_decision["decision"],
            "risk_score": policy_decision["risk_score"],
            "context": request,
        }
    )
    assert approval_request["status"] == APPROVAL_STATUS_PENDING

    blocked_exec = _execute_with_blockers(
        components,
        request,
        blockers=[f"approval:{approval_request['status']}"],
    )
    assert blocked_exec["success"] is False
    assert blocked_exec["output"]["status"] == "BLOCKED"

    approved = components["approval"].decide(
        approval_request["request_id"],
        "APPROVED",
        approver="security.lead",
        reason="change ticket validated",
    )
    assert approved["status"] == APPROVAL_STATUS_APPROVED

    data_result = components["data_guard"].evaluate(request["payload"])
    tool_result = components["tool_guard"].evaluate(request)
    blockers = []
    if data_result["action"] == "BLOCK":
        blockers.append("data_guard:BLOCK")
    if not tool_result["allowed"]:
        blockers.append(f"tool_guard:{tool_result['decision']}")

    final_exec = _execute_with_blockers(components, request, blockers=blockers)
    assert final_exec["success"] is True
    assert final_exec["output"]["status"] == "DRY_RUN_SIMULATED"


def test_rejected_request_stays_blocked(tmp_path):
    components = _new_components(tmp_path / "approval_rejected.jsonl")
    request = {
        "run_id": "run-approval-2",
        "actor": "operator",
        "action": "change_config",
        "environment": "prod",
        "tool": "config_reader",
        "command": "",
        "payload": {"safe": True},
    }

    policy_decision = components["policy"].evaluate(request)
    approval_request = components["approval"].create_request(
        {
            "run_id": request["run_id"],
            "actor": request["actor"],
            "policy_decision": policy_decision["decision"],
            "risk_score": policy_decision["risk_score"],
            "context": request,
        }
    )
    rejected = components["approval"].decide(
        approval_request["request_id"],
        "REJECTED",
        approver="security.lead",
        reason="insufficient change context",
    )
    assert rejected["status"] == APPROVAL_STATUS_REJECTED

    blocked_exec = _execute_with_blockers(
        components,
        request,
        blockers=[f"approval:{rejected['status']}"],
    )
    assert blocked_exec["success"] is False
    assert blocked_exec["output"]["status"] == "BLOCKED"


def test_deny_path_never_reaches_approval_override(tmp_path):
    audit_file = tmp_path / "approval_deny.jsonl"
    components = _new_components(audit_file)
    request = {
        "run_id": "run-approval-3",
        "actor": "operator",
        "action": "delete_everything",
        "tool": "shell",
        "command": "rm -rf /",
        "payload": {"safe": False},
    }

    policy_decision = components["policy"].evaluate(request)
    assert policy_decision["decision"] == DECISION_DENY
    assert components["approval"].is_required(
        policy_decision["risk_score"],
        policy_decision["decision"],
    ) is False

    blocked_exec = _execute_with_blockers(components, request, blockers=["policy:DENY"])
    assert blocked_exec["success"] is False
    assert blocked_exec["output"]["status"] == "BLOCKED"

    # No approval request should have been created/audited in this path.
    if audit_file.exists():
        content = audit_file.read_text(encoding="utf-8").strip()
        if content:
            actions = [json.loads(line)["action"] for line in content.splitlines()]
            assert "approval_request_created" not in actions
            assert "approval_decided" not in actions


def test_approval_does_not_bypass_tool_data_exec_guards(tmp_path):
    components = _new_components(tmp_path / "approval_respects_guards.jsonl")
    request = {
        "run_id": "run-approval-4",
        "actor": "operator",
        "action": "change_config",
        "environment": "prod",
        "tool": "unknown_tool",
        "command": "noop",
        "payload": {
            "api_key": "sk-1234567890abcdef1234567890abcdef",
            "destination": "https://external.example/upload",
        },
    }

    policy_decision = components["policy"].evaluate(request)
    assert policy_decision["decision"] == DECISION_NEEDS_APPROVAL

    approval_request = components["approval"].create_request(
        {
            "run_id": request["run_id"],
            "actor": request["actor"],
            "policy_decision": policy_decision["decision"],
            "risk_score": policy_decision["risk_score"],
            "context": request,
        }
    )
    _ = components["approval"].decide(
        approval_request["request_id"],
        "APPROVED",
        approver="security.lead",
        reason="approval granted",
    )

    data_result = components["data_guard"].evaluate(request["payload"])
    tool_result = components["tool_guard"].evaluate(request)
    blockers = []
    if data_result["action"] == "BLOCK":
        blockers.append("data_guard:BLOCK")
    if not tool_result["allowed"]:
        blockers.append(f"tool_guard:{tool_result['decision']}")

    blocked_exec = _execute_with_blockers(components, request, blockers=blockers)
    assert blocked_exec["success"] is False
    assert blocked_exec["output"]["status"] == "BLOCKED"


def test_approval_create_and_decide_actions_emit_audit_evidence(tmp_path):
    audit_file = tmp_path / "approval_evidence.jsonl"
    components = _new_components(audit_file)

    request = components["approval"].create_request(
        {
            "run_id": "run-approval-5",
            "actor": "operator",
            "policy_decision": DECISION_NEEDS_APPROVAL,
            "risk_score": 60,
            "context": {"action": "change"},
        }
    )
    components["approval"].decide(
        request["request_id"],
        "APPROVED",
        approver="security.lead",
        reason="looks good",
    )

    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    actions = [json.loads(line)["action"] for line in lines]
    assert actions.count("approval_request_created") == 1
    assert actions.count("approval_decided") == 1

