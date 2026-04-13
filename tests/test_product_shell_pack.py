from __future__ import annotations

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
        return f"apr-shell-{self.counter:04d}"


def _build_client(audit_file: Path, demo_ui_audit_dir: Path, product_shell_store: Path) -> TestClient:
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
    app = create_app(
        service=service,
        demo_ui_audit_dir=demo_ui_audit_dir,
        product_shell_store_path=product_shell_store,
    )
    return TestClient(app)


def test_product_shell_summary_history_queue_and_audit_are_available(tmp_path):
    client = _build_client(
        tmp_path / "product_shell_api.jsonl",
        tmp_path / "ui-audits",
        tmp_path / "product-shell-store.json",
    )

    client.get("/v1/demo-ui/scenarios/allow_case")
    client.get("/v1/demo-ui/scenarios/approval_case")
    client.get("/v1/demo-ui/scenarios/deny_case")

    summary = client.get("/v1/demo-ui/product-shell")
    history = client.get("/v1/demo-ui/product-shell/history?decision=DENY")
    queue = client.get("/v1/demo-ui/product-shell/approval-queue")
    audit = client.get("/v1/demo-ui/product-shell/audit-view")

    assert summary.status_code == 200
    assert history.status_code == 200
    assert queue.status_code == 200
    assert audit.status_code == 200

    summary_body = summary.json()
    assert summary_body["summary"]["total_runs"] >= 3
    assert summary_body["summary"]["allow"] >= 1
    assert summary_body["summary"]["needs_approval"] >= 1
    assert summary_body["summary"]["deny"] >= 1
    assert summary_body["summary"]["blocked"] >= 2
    assert summary_body["history"]
    assert summary_body["audit_view"]

    history_body = history.json()
    assert history_body["decision_filter"] == "DENY"
    assert history_body["runs"]
    assert all(run["decision"] == "DENY" for run in history_body["runs"])

    queue_body = queue.json()
    assert queue_body["items"]
    assert any(item["approval_status"] == "PENDING" for item in queue_body["items"])

    audit_body = audit.json()
    assert audit_body["records"]
    assert any(record["integrity_state"] == "VALID" for record in audit_body["records"])


def test_product_shell_ui_contains_monitoring_history_approval_and_audit_sections(tmp_path):
    client = _build_client(
        tmp_path / "product_shell_ui.jsonl",
        tmp_path / "ui-audits",
        tmp_path / "product-shell-store.json",
    )
    response = client.get("/ui")

    assert response.status_code == 200
    text = response.text
    assert "Product Shell" in text
    assert "Operations overview" in text
    assert "Run History" in text
    assert "Approval queue" in text
    assert "Audit viewer" in text
