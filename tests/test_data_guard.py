from src.data_guard import DataGuard


def test_data_guard_clean_payload_is_allowed():
    guard = DataGuard()
    payload = {"action": "read_status", "note": "safe payload"}

    result = guard.evaluate(payload)

    assert result["action"] == "ALLOW"
    assert result["allowed"] is True
    assert result["risk_score"] <= 33
    assert result["findings"] == []
    assert result["redacted_payload"] == payload


def test_data_guard_redacts_sensitive_payload():
    guard = DataGuard()
    payload = {"email": "user@example.com", "message": "contact me later"}

    result = guard.evaluate(payload)

    assert result["action"] == "REDACT"
    assert result["allowed"] is True
    assert result["risk_score"] >= 34
    assert result["redacted_payload"]["email"] == "[REDACTED]"


def test_data_guard_blocks_high_risk_payload():
    guard = DataGuard()
    payload = {
        "api_key": "sk-1234567890abcdef1234567890abcdef",
        "card": "4111 1111 1111 1111",
        "destination": "https://external.example/upload",
    }

    result = guard.evaluate(payload)

    assert result["action"] == "BLOCK"
    assert result["allowed"] is False
    assert result["risk_score"] >= 67
    assert result["redacted_payload"]["api_key"] == "[REDACTED]"
    assert result["redacted_payload"]["card"] == "[REDACTED]"


def test_data_guard_is_deterministic_for_same_payload():
    guard = DataGuard()
    payload = {"phone": "+1 (555) 123-4567", "note": "same input"}

    first = guard.evaluate(payload)
    second = guard.evaluate(payload)

    assert first == second

