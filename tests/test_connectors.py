import pytest

from src.connectors import StubConnector


def test_stub_connector_returns_deterministic_stub_response():
    connector = StubConnector()
    request = {"operation": "list_resources", "params": {"scope": "local"}}

    first = connector.execute(request)
    second = connector.execute(request)

    assert first == second
    assert first["status"] == "STUBBED"
    assert first["success"] is False
    assert first["output"]["request"] == request


def test_stub_connector_rejects_non_dict_requests():
    connector = StubConnector()
    with pytest.raises(TypeError):
        connector.execute(["not", "a", "dict"])  # type: ignore[arg-type]


def test_stub_connector_live_call_is_not_implemented():
    connector = StubConnector()
    with pytest.raises(NotImplementedError):
        connector.perform_live_call({"operation": "noop"})

