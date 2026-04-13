import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.demo_ui import build_safe_http_example_request
from src.api.service import GuardedExecutionService
from src.audit import AuditLogger
from src.policy import PolicyEngine


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps({"status": "ok", "service": "safe-http-test"}).encode("utf-8")
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


def _build_service(audit_file: Path) -> GuardedExecutionService:
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        audit_logger=AuditLogger(audit_file),
    )


def test_allowlisted_get_path_succeeds_in_safe_mode(tmp_path):
    service = _build_service(tmp_path / "safe_http_allow.jsonl")

    with _local_health_server() as url:
        response = service.execute_guarded_request(
            build_safe_http_example_request("allowlisted_get", url=url)
        )

    assert response["policy_decision"]["decision"] == "ALLOW"
    assert response["blocked"] is False
    assert response["approval"]["status"] == "BYPASSED"
    assert response["connector_execution"]["status"] == "SAFE_READ_ONLY_FETCHED"
    assert response["connector_execution"]["success"] is True
    assert response["connector_execution"]["raw_result"]["output"]["status_code"] == 200
    assert response["execution_result"]["output"]["status"] == "DRY_RUN_SIMULATED"
    assert response["audit_integrity"]["valid"] is True


def test_non_allowlisted_host_is_blocked(tmp_path):
    service = _build_service(tmp_path / "safe_http_blocked_host.jsonl")
    response = service.execute_guarded_request(build_safe_http_example_request("blocked_host"))

    assert response["policy_decision"]["decision"] == "DENY"
    assert response["blocked"] is True
    assert "tool_guard:DENY" in response["blockers"]
    assert response["connector_execution"]["status"] == "BLOCKED"
    assert response["execution_result"]["output"]["status"] == "BLOCKED"
    assert response["audit_integrity"]["valid"] is True


def test_non_get_method_is_blocked(tmp_path):
    service = _build_service(tmp_path / "safe_http_blocked_method.jsonl")

    with _local_health_server() as url:
        response = service.execute_guarded_request(
            build_safe_http_example_request("blocked_method", url=url)
        )

    assert response["policy_decision"]["decision"] == "DENY"
    assert response["blocked"] is True
    assert "tool_guard:DENY" in response["blockers"]
    assert response["connector_execution"]["status"] == "BLOCKED"
    assert response["execution_result"]["output"]["status"] == "BLOCKED"


def test_existing_deny_semantics_are_not_changed(tmp_path):
    service = _build_service(tmp_path / "existing_deny.jsonl")
    response = service.execute_guarded_request(
        {
            "run_id": "still-deny",
            "actor": "tester",
            "action": "delete_everything",
            "tool": "shell",
            "command": "rm -rf /",
            "payload": {"note": "danger"},
            "dry_run": True,
        }
    )

    assert response["policy_decision"]["decision"] == "DENY"
    assert response["approval"]["status"] == "NOT_APPLICABLE_DENY"
    assert response["blocked"] is True
    assert response["execution_result"]["output"]["status"] == "BLOCKED"


def test_demo_ui_surfaces_safe_integration_example_without_regressing_demo_shell(tmp_path):
    app = create_app(demo_ui_audit_dir=tmp_path / "ui_demo_audit")
    client = TestClient(app)

    ui_shell = client.get("/ui")
    assert ui_shell.status_code == 200
    assert "First Practical Integration Path" in ui_shell.text

    content = client.get("/v1/demo-ui/content")
    assert content.status_code == 200
    body = content.json()
    assert body["safe_integration"]["headline"] == "First practical integration path"
    assert len(body["safe_integration"]["examples"]) == 3

    allow_demo = client.get("/v1/demo-ui/scenarios/allow_case")
    assert allow_demo.status_code == 200
    assert allow_demo.json()["summary"]["decision"] == "ALLOW"
