import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
        return f"apr-ref-{self.counter:04d}"


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps({"status": "ok", "service": "reference-product-test"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: A003
        return


@contextmanager
def _local_health_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}/health"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


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


def test_reference_product_flow_content_is_exposed_in_ui_payload(tmp_path):
    client = _build_client(tmp_path / "reference_product_content.jsonl", tmp_path / "ui-audits")
    response = client.get("/v1/demo-ui/content")

    assert response.status_code == 200
    body = response.json()
    assert body["reference_product"]["headline"] == "Try SafeCore in a real workflow"
    assert "safe_http_status connector" in body["reference_product"]["workflow"]
    assert len(body["reference_product"]["flows"]) == 3


def test_reference_product_flow_allowed_path(tmp_path):
    client = _build_client(tmp_path / "reference_product_allow.jsonl", tmp_path / "ui-audits")
    import os

    # TestClient does not listen on 127.0.0.1:8000, so point the narrow safe HTTP
    # demo URL to a temporary local health server without changing runtime behavior.
    with _local_health_server() as url:
        previous = os.environ.get("SAFECORE_SAFE_HTTP_DEMO_URL")
        os.environ["SAFECORE_SAFE_HTTP_DEMO_URL"] = url
        try:
            response = client.get("/v1/demo-ui/reference-product-flows/safe_status_check")
        finally:
            if previous is None:
                os.environ.pop("SAFECORE_SAFE_HTTP_DEMO_URL", None)
            else:
                os.environ["SAFECORE_SAFE_HTTP_DEMO_URL"] = previous

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["decision"] == "ALLOW"
    assert body["summary"]["blocked"] is False
    assert body["summary"]["connector_status"] == "SAFE_READ_ONLY_FETCHED"
    assert body["summary"]["execution_status"] == "DRY_RUN_SIMULATED"
    assert body["summary"]["audit_integrity"] is True


def test_reference_product_flow_blocked_host_and_method(tmp_path):
    client = _build_client(tmp_path / "reference_product_blocked.jsonl", tmp_path / "ui-audits")

    blocked_host = client.get("/v1/demo-ui/reference-product-flows/blocked_external_status")
    blocked_method = client.get("/v1/demo-ui/reference-product-flows/blocked_unsafe_status_method")

    host_body = blocked_host.json()
    method_body = blocked_method.json()

    assert host_body["summary"]["decision"] == "DENY"
    assert host_body["summary"]["blocked"] is True
    assert host_body["summary"]["connector_status"] == "BLOCKED"

    assert method_body["summary"]["decision"] == "DENY"
    assert method_body["summary"]["blocked"] is True
    assert method_body["summary"]["connector_status"] == "BLOCKED"


def test_reference_product_ui_shell_is_present_without_regressing_demo_sections(tmp_path):
    client = _build_client(tmp_path / "reference_product_ui.jsonl", tmp_path / "ui-audits")
    response = client.get("/ui")

    assert response.status_code == 200
    text = response.text
    assert "Reference Product Flow" in text
    assert "Three Decision States" in text
    assert "First Practical Integration Path" in text
