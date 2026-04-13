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
        return f"apr-pack-m1-{self.counter:04d}"


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


def test_onboarding_content_is_present_and_localized(tmp_path):
    client = _build_client(
        tmp_path / "pack_m1_onboarding.jsonl",
        tmp_path / "ui-audits",
        tmp_path / "product-shell-store.json",
    )

    en = client.get("/v1/demo-ui/content?lang=en").json()
    ru = client.get("/v1/demo-ui/content?lang=ru").json()
    uz = client.get("/v1/demo-ui/content?lang=uz").json()

    expected_ids = [
        "language",
        "provider_setup",
        "first_safe_run",
        "approval_explanation",
        "audit_viewer",
    ]
    assert [step["id"] for step in en["onboarding"]["steps"]] == expected_ids
    assert "localStorage" in en["onboarding"]["safe_note"]
    assert ru["onboarding"]["headline"] != en["onboarding"]["headline"]
    assert uz["onboarding"]["headline"] != en["onboarding"]["headline"]


def test_provider_status_payload_stays_safe_and_explanatory(tmp_path, monkeypatch):
    client = _build_client(
        tmp_path / "pack_m1_provider.jsonl",
        tmp_path / "ui-audits",
        tmp_path / "product-shell-store.json",
    )
    raw_secret = "sk-pack-m1-openai-secret"
    monkeypatch.setenv("OPENAI_API_KEY", raw_secret)

    response = client.get("/v1/demo-ui/provider-status?lang=en")
    assert response.status_code == 200
    body = response.json()

    assert body["configured_help"]
    assert body["enabled_help"]
    assert len(body["how_to_enable_steps"]) == 3

    providers = {item["id"]: item for item in body["providers"]}
    assert providers["openai"]["configured"] is True
    assert providers["openai"]["enabled"] is False
    assert providers["openai"]["key_status"] == "Configured via env (masked)"
    assert "OPENAI_API_KEY" in providers["openai"]["how_to_enable"]
    assert raw_secret not in response.text


def test_product_shell_history_and_audit_filters_work(tmp_path):
    client = _build_client(
        tmp_path / "pack_m1_filters.jsonl",
        tmp_path / "ui-audits",
        tmp_path / "product-shell-store.json",
    )

    client.get("/v1/demo-ui/scenarios/allow_case?lang=en")
    client.get("/v1/demo-ui/scenarios/approval_case?lang=en")
    client.get("/v1/demo-ui/scenarios/deny_case?lang=en")

    history = client.get(
        "/v1/demo-ui/product-shell/history?decision=ALLOW&run_status=ALLOWED&provider=LOCAL_DEMO&lang=en"
    )
    audit = client.get(
        "/v1/demo-ui/product-shell/audit-view?decision=DENY&integrity_state=VALID&provider=LOCAL_DEMO&lang=en"
    )

    assert history.status_code == 200
    assert audit.status_code == 200

    history_body = history.json()
    assert history_body["decision_filter"] == "ALLOW"
    assert history_body["run_status_filter"] == "ALLOWED"
    assert history_body["provider_filter"] == "LOCAL_DEMO"
    assert history_body["runs"]
    assert all(run["decision"] == "ALLOW" for run in history_body["runs"])
    assert all(run["run_status"] == "ALLOWED" for run in history_body["runs"])
    assert all(run["provider_mode"] == "LOCAL_DEMO" for run in history_body["runs"])

    audit_body = audit.json()
    assert audit_body["decision_filter"] == "DENY"
    assert audit_body["integrity_filter"] == "VALID"
    assert audit_body["provider_filter"] == "LOCAL_DEMO"
    assert audit_body["records"]
    assert all(record["decision"] == "DENY" for record in audit_body["records"])
    assert all(record["integrity_state"] == "VALID" for record in audit_body["records"])


def test_ui_shell_contains_onboarding_and_product_shell_filters(tmp_path):
    client = _build_client(
        tmp_path / "pack_m1_ui.jsonl",
        tmp_path / "ui-audits",
        tmp_path / "product-shell-store.json",
    )
    response = client.get("/ui")

    assert response.status_code == 200
    text = response.text
    assert 'id="onboarding"' in text
    assert 'id="onboarding-mark-complete"' in text
    assert 'id="history-status-filter"' in text
    assert 'id="audit-integrity-filter"' in text
