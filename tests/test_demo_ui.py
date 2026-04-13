from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.service import GuardedExecutionService
from src.approval import ApprovalManager
from src.audit import AuditLogger
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.policy import PolicyEngine
from src.utils.tool_policies import ToolGuard


class CounterIdFactory:
    def __init__(self) -> None:
        self.counter = 0

    def __call__(self) -> str:
        self.counter += 1
        return f"apr-ui-{self.counter:04d}"


def _build_client(audit_file: Path, demo_ui_audit_dir: Path) -> TestClient:
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    service = GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=ApprovalManager(audit_logger=audit_logger, id_factory=CounterIdFactory()),
    )
    app = create_app(service=service, demo_ui_audit_dir=demo_ui_audit_dir)
    return TestClient(app)


def test_demo_ui_shell_contains_project_sections(tmp_path):
    client = _build_client(tmp_path / "ui_shell_audit.jsonl", tmp_path / "ui-audits")
    response = client.get("/ui")

    assert response.status_code == 200
    text = response.text
    assert "SafeCore Demo UI" in text
    assert "Security/control layer for AI agents" in text
    assert "What SafeCore does" in text
    assert "Three Decision States" in text
    assert "Demo Runner" in text
    assert "Current Scope" in text


def test_demo_ui_content_endpoint_reflects_current_capabilities_and_boundaries(tmp_path):
    client = _build_client(tmp_path / "ui_content_audit.jsonl", tmp_path / "ui-audits")
    response = client.get("/v1/demo-ui/content")

    assert response.status_code == 200
    body = response.json()
    assert body["identity"]["name"] == "SafeCore"
    assert "Open-source RC/MVP" in body["identity"]["status"]
    assert "Validated core" in body["identity"]["status"]
    assert "Apache 2.0" in body["identity"]["status"]
    assert any(item["title"] == "Policy decision layer" for item in body["capabilities"])
    assert any(item["title"] == "Connector boundary" for item in body["capabilities"])
    assert "No production auth/authz" in body["scope"]["not_included"]


def test_demo_ui_scenario_runner_preserves_allow_approval_and_deny_states(tmp_path):
    client = _build_client(tmp_path / "ui_runner_audit.jsonl", tmp_path / "ui-audits")

    allow_case = client.get("/v1/demo-ui/scenarios/allow_case")
    approval_case = client.get("/v1/demo-ui/scenarios/approval_case")
    deny_case = client.get("/v1/demo-ui/scenarios/deny_case")

    assert allow_case.status_code == 200
    assert approval_case.status_code == 200
    assert deny_case.status_code == 200

    allow_body = allow_case.json()
    approval_body = approval_case.json()
    deny_body = deny_case.json()

    assert allow_body["summary"]["decision"] == "ALLOW"
    assert allow_body["summary"]["blocked"] is False
    assert allow_body["summary"]["execution_status"] == "DRY_RUN_SIMULATED"

    assert approval_body["summary"]["decision"] == "NEEDS_APPROVAL"
    assert approval_body["summary"]["blocked"] is True
    assert approval_body["summary"]["approval_status"] == "PENDING"

    assert deny_body["summary"]["decision"] == "DENY"
    assert deny_body["summary"]["blocked"] is True
    assert deny_body["summary"]["approval_status"] == "NOT_APPLICABLE_DENY"
    assert deny_body["summary"]["execution_status"] == "BLOCKED"

    assert allow_body["summary"]["audit_integrity"] is True
    assert approval_body["summary"]["audit_integrity"] is True
    assert deny_body["summary"]["audit_integrity"] is True
