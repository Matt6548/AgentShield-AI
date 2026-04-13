from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.service import GuardedExecutionService
from src.audit import AuditLogger
from src.integrations import (
    SafeCoreIntegrationBridge,
    SafeCoreLangChainToolAdapter,
    SafeCoreLangGraphNode,
    SafeCoreMcpBoundary,
)
from src.providers import build_default_provider_gateway


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps({"status": "ok", "service": "integration-pack-n"}).encode("utf-8")
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
    return GuardedExecutionService(audit_logger=AuditLogger(audit_file))


def test_provider_gateway_catalog_is_safe_and_extensible(monkeypatch):
    raw_secret = "sk-integrations-pack-n-openai"
    monkeypatch.setenv("OPENAI_API_KEY", raw_secret)

    gateway = build_default_provider_gateway()
    catalog = gateway.safe_status_catalog()
    providers = {item["id"]: item for item in catalog["providers"]}

    assert {"openai", "openai_compatible", "openrouter", "claude", "local_demo"} <= set(providers)
    assert providers["openai"]["configured"] is True
    assert providers["openai"]["enabled"] is False
    assert providers["openai"]["base_url_status"] == "DEFAULT"
    assert providers["local_demo"]["enabled"] is True

    catalog_text = json.dumps(catalog)
    assert raw_secret not in catalog_text
    assert "OPENAI_API_KEY" in catalog_text


def test_openai_compatible_bridge_supports_local_base_url_override(monkeypatch):
    monkeypatch.setenv("SAFECORE_OPENAI_COMPATIBLE_BASE_URL", "http://127.0.0.1:11434/v1")
    gateway = build_default_provider_gateway()

    snapshot = gateway.get_adapter("openai_compatible").safe_snapshot().as_public_dict()
    request_spec = gateway.build_request_spec(
        "openai_compatible",
        path="/chat/completions",
        body={"model": "demo", "messages": []},
    )

    assert snapshot["configured"] is True
    assert snapshot["base_url_status"] == "LOCAL_OVERRIDE"
    assert snapshot["base_url_label"] == "http://127.0.0.1:11434/v1"
    assert request_spec["url"] == "http://127.0.0.1:11434/v1/chat/completions"
    assert "Authorization" not in request_spec["headers"]


def test_langchain_wrapper_routes_request_through_guarded_service(tmp_path):
    service = _build_service(tmp_path / "langchain_wrapper.jsonl")
    bridge = SafeCoreIntegrationBridge(service=service)
    tool = SafeCoreLangChainToolAdapter(bridge)

    with _local_health_server() as url:
        payload = tool.invoke({"url": url, "method": "GET"})

    guarded = payload["guarded_result"]
    assert guarded["policy_decision"]["decision"] == "ALLOW"
    assert guarded["blocked"] is False
    assert guarded["connector_execution"]["status"] == "SAFE_READ_ONLY_FETCHED"
    assert guarded["execution_result"]["output"]["status"] == "DRY_RUN_SIMULATED"


def test_langgraph_node_returns_blocked_state_patch(tmp_path):
    service = _build_service(tmp_path / "langgraph_node.jsonl")
    bridge = SafeCoreIntegrationBridge(service=service)
    node = SafeCoreLangGraphNode(bridge)

    patch = node(
        {
            "run_id": "langgraph-blocked",
            "actor": "graph-user",
            "url": "http://example.com/health",
            "method": "GET",
        }
    )

    guarded = patch["safecore_result"]
    assert guarded["policy_decision"]["decision"] == "DENY"
    assert guarded["blocked"] is True
    assert guarded["connector_execution"]["status"] == "BLOCKED"


def test_mcp_boundary_blocks_unsafe_method(tmp_path):
    service = _build_service(tmp_path / "mcp_boundary.jsonl")
    bridge = SafeCoreIntegrationBridge(service=service)
    boundary = SafeCoreMcpBoundary(bridge)

    with _local_health_server() as url:
        payload = boundary.handle_tool_call(
            "safe_http_status",
            {"url": url, "method": "POST"},
            run_id="mcp-boundary-blocked",
        )

    guarded = payload["guarded_result"]
    assert guarded["policy_decision"]["decision"] == "DENY"
    assert guarded["blocked"] is True
    assert guarded["connector_execution"]["status"] == "BLOCKED"


def test_provider_status_endpoint_exposes_gateway_metadata_without_secret_leakage(tmp_path, monkeypatch):
    raw_secret = "sk-integrations-pack-n-endpoint"
    monkeypatch.setenv("OPENAI_API_KEY", raw_secret)
    monkeypatch.setenv("SAFECORE_OPENAI_COMPATIBLE_BASE_URL", "http://127.0.0.1:11434/v1")

    app = create_app(service=_build_service(tmp_path / "provider_status_endpoint.jsonl"))
    client = TestClient(app)

    response = client.get("/v1/demo-ui/provider-status?lang=en")
    assert response.status_code == 200
    body = response.json()

    providers = {item["id"]: item for item in body["providers"]}
    assert "gateway" in body
    assert "openai_compatible" in providers
    assert providers["openai"]["configured"] is True
    assert providers["openai"]["enabled"] is False
    assert providers["openai_compatible"]["base_url_label"] == "http://127.0.0.1:11434/v1"
    assert providers["openai_compatible"]["gateway_support"]
    assert providers["openai_compatible"]["capabilities"]
    assert raw_secret not in response.text
