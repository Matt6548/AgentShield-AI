from src.exec_guard import ExecutionGuard


def test_execution_guard_dry_run_success_for_safe_command():
    guard = ExecutionGuard()
    result = guard.execute({"tool": "shell", "command": "ls -la"}, dry_run=True)

    assert result["success"] is True
    assert result["output"]["status"] == "DRY_RUN_SIMULATED"
    assert result["output"]["dry_run"] is True
    assert result["tool"] == "shell"
    assert result["command"] == "ls -la"
    assert isinstance(result["timestamp"], str)


def test_execution_guard_blocks_dangerous_command():
    guard = ExecutionGuard()
    result = guard.execute({"tool": "shell", "command": "rm -rf /"}, dry_run=True)

    assert result["success"] is False
    assert result["output"]["status"] == "BLOCKED"
    assert result["output"]["dry_run"] is True


def test_execution_guard_respects_external_blockers():
    guard = ExecutionGuard()
    result = guard.execute(
        {
            "tool": "shell",
            "command": "ls",
            "blocked_by": ["data_guard:BLOCK sensitive payload"],
        },
        dry_run=True,
    )

    assert result["success"] is False
    assert result["output"]["status"] == "BLOCKED"
    assert "data_guard:BLOCK" in result["output"]["reasons"][0]


def test_execution_guard_non_dry_run_is_explicitly_not_implemented():
    guard = ExecutionGuard()
    result = guard.execute({"tool": "shell", "command": "pwd"}, dry_run=False)

    assert result["success"] is False
    assert result["output"]["status"] == "NOT_IMPLEMENTED"
    assert result["output"]["dry_run"] is False

