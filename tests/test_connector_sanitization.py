from src.connectors.request_sanitizer import ConnectorRequestSanitizer
from src.connectors.response_sanitizer import ConnectorResponseSanitizer


def test_request_sanitizer_strips_unsafe_fields_and_rejects_payload():
    sanitizer = ConnectorRequestSanitizer()
    result = sanitizer.sanitize(
        {
            "run_id": "run-1",
            "actor": "tester",
            "tool": "shell",
            "command": "ls",
            "params": {"api_key": "secret", "depth": 1},
            "payload": {"nested": {"secret_token": "x"}, "note": "safe"},
            "debug_mode": True,
        }
    )

    assert result["valid"] is False
    assert "debug_mode" in result["stripped_fields"]
    assert result["sanitized_request"]["params"] == {"depth": 1}
    assert result["sanitized_request"]["payload"] == {"nested": {}, "note": "safe"}
    assert result["stripped_nested_paths"]


def test_request_sanitizer_rejects_oversized_payload():
    sanitizer = ConnectorRequestSanitizer()
    result = sanitizer.sanitize(
        {
            "run_id": "run-2",
            "actor": "tester",
            "tool": "shell",
            "command": "ls",
            "params": {},
            "payload": {"blob": "x" * 15000},
        }
    )

    assert result["valid"] is False
    assert any("too large" in reason.lower() for reason in result["reasons"])


def test_response_sanitizer_normalizes_and_strips_sensitive_output():
    sanitizer = ConnectorResponseSanitizer()
    sanitized = sanitizer.sanitize(
        {
            "adapter_id": "stub",
            "connector": "stub_connector",
            "tool": "shell",
            "dry_run": True,
            "status": "DRY_RUN_SIMULATED",
            "success": True,
            "reasons": [],
            "normalized_request": {"tool": "shell", "command": "ls"},
            "raw_result": {
                "status": "STUBBED",
                "output": {
                    "message": "ok",
                    "traceback": "hidden",
                    "secret": "hidden",
                },
            },
        }
    )

    assert sanitized["status"] == "DRY_RUN_SIMULATED"
    assert sanitized["raw_result"]["output"] == {"message": "ok"}
    assert any("unsafe keys" in reason.lower() for reason in sanitized["reasons"])

