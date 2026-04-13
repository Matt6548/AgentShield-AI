import pytest

from src.connectors import ConnectorExecutor


def test_connector_executor_selects_shell_adapter_for_shell_tool():
    executor = ConnectorExecutor()
    adapter = executor.select_adapter(tool="shell")
    assert adapter.adapter_id == "shell_stub_adapter"


def test_connector_executor_selects_generic_adapter_for_unknown_tool():
    executor = ConnectorExecutor()
    adapter = executor.select_adapter(tool="unknown_tool")
    assert adapter.adapter_id == "generic_stub_adapter"


def test_connector_executor_selects_adapter_by_connector_name():
    executor = ConnectorExecutor()
    adapter = executor.select_adapter(tool="shell", connector_name="stub_generic_connector")
    assert adapter.adapter_id == "generic_stub_adapter"


def test_connector_executor_returns_normalized_dry_run_response():
    executor = ConnectorExecutor()
    result = executor.execute(
        {
            "run_id": "conn-safe",
            "actor": "tester",
            "tool": "shell",
            "command": "ls",
            "params": {"depth": 1},
            "payload": {"note": "safe"},
        },
        dry_run=True,
    )

    assert result["status"] == "DRY_RUN_SIMULATED"
    assert result["success"] is True
    assert result["normalized_request"]["tool"] == "shell"
    assert result["raw_result"]["status"] == "STUBBED"


def test_connector_executor_blocked_path_does_not_execute_connector():
    executor = ConnectorExecutor()
    result = executor.execute(
        {"run_id": "conn-blocked", "actor": "tester", "tool": "shell", "command": "rm -rf /"},
        dry_run=True,
        blocked_by=["policy:DENY"],
    )

    assert result["status"] == "BLOCKED"
    assert result["success"] is False
    assert result["reasons"] == ["policy:DENY"]
    assert result["raw_result"] == {}


def test_connector_executor_non_dry_run_is_not_implemented():
    executor = ConnectorExecutor()
    result = executor.execute(
        {"run_id": "conn-live", "actor": "tester", "tool": "shell", "command": "ls"},
        dry_run=False,
    )

    assert result["status"] == "NOT_IMPLEMENTED"
    assert result["success"] is False


def test_connector_executor_rejects_non_dict_requests():
    executor = ConnectorExecutor()
    with pytest.raises(TypeError):
        executor.execute(["invalid"])  # type: ignore[arg-type]
