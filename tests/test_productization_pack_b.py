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
        return f"apr-pack-b-{self.counter:04d}"


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


def test_multilingual_content_and_shell_endpoints_work(tmp_path):
    client = _build_client(
        tmp_path / "pack_b_multilingual.jsonl",
        tmp_path / "ui-audits",
        tmp_path / "product-shell-store.json",
    )

    en = client.get("/v1/demo-ui/content?lang=en")
    ru = client.get("/v1/demo-ui/content?lang=ru")
    uz = client.get("/v1/demo-ui/content?lang=uz")

    assert en.status_code == 200
    assert ru.status_code == 200
    assert uz.status_code == 200

    en_body = en.json()
    ru_body = ru.json()
    uz_body = uz.json()

    assert en_body["language"]["selected"] == "en"
    assert ru_body["language"]["selected"] == "ru"
    assert uz_body["language"]["selected"] == "uz"

    assert en_body["ui_labels"]["navigation"]["providers"] == "Providers"
    assert uz_body["ui_labels"]["navigation"]["providers"] == "Provayderlar"
    assert ru_body["ui_labels"]["navigation"]["overview"] != "Overview"

    scenario = client.get("/v1/demo-ui/scenarios/allow_case?lang=uz")
    assert scenario.status_code == 200
    scenario_body = scenario.json()
    assert scenario_body["summary"]["decision"] == "ALLOW"
    assert scenario_body["summary"]["blocked"] is False
    assert scenario_body["summary"]["execution_status"] == "DRY_RUN_SIMULATED"

    shell = client.get("/v1/demo-ui/product-shell?lang=ru")
    assert shell.status_code == 200
    shell_body = shell.json()
    assert "summary" in shell_body
    assert "history" in shell_body
    assert "approval_queue" in shell_body
    assert "audit_view" in shell_body


def test_provider_status_is_safe_and_does_not_leak_raw_secrets(tmp_path, monkeypatch):
    client = _build_client(
        tmp_path / "pack_b_provider.jsonl",
        tmp_path / "ui-audits",
        tmp_path / "product-shell-store.json",
    )
    raw_secret = "sk-test-productization-pack-b-secret"
    monkeypatch.setenv("OPENAI_API_KEY", raw_secret)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-secret-value")

    response = client.get("/v1/demo-ui/provider-status?lang=en")

    assert response.status_code == 200
    body = response.json()

    providers = {item["id"]: item for item in body["providers"]}
    assert providers["openai"]["configured"] is True
    assert providers["openai"]["enabled"] is False
    assert providers["openai"]["key_status"] == "Configured via env (masked)"
    assert providers["openai"]["env_source"] == "OPENAI_API_KEY"

    assert providers["claude"]["configured"] is True
    assert providers["openrouter"]["configured"] is False
    assert providers["local_demo"]["configured"] is True
    assert providers["local_demo"]["enabled"] is True

    response_text = response.text
    assert raw_secret not in response_text
    assert "anthropic-secret-value" not in response_text
    assert "OPENAI_API_KEY" in response_text


def test_ui_shell_exposes_language_switcher_and_provider_section(tmp_path):
    client = _build_client(
        tmp_path / "pack_b_ui_shell.jsonl",
        tmp_path / "ui-audits",
        tmp_path / "product-shell-store.json",
    )
    response = client.get("/ui")

    assert response.status_code == 200
    text = response.text
    assert 'id="language-select"' in text
    assert "Provider Status" in text
    assert "See configuration posture without exposing secrets" in text
