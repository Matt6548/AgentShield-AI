import json

from src.audit import AuditLogger


def test_audit_logger_appends_valid_record_with_hash(tmp_path):
    audit_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(audit_file)

    appended = logger.append_record(
        {
            "timestamp": "2026-01-01T00:00:00Z",
            "run_id": "run-001",
            "actor": "tester",
            "step": "exec_guard",
            "action": "dry_run_execute",
            "data": {"status": "ok"},
        }
    )

    assert isinstance(appended["hash"], str)
    assert len(appended["hash"]) == 64

    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    loaded = json.loads(lines[0])
    assert loaded["hash"] == appended["hash"]
    assert loaded["run_id"] == "run-001"


def test_audit_hash_is_deterministic_for_same_file_state(tmp_path):
    audit_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(audit_file)
    record = {
        "timestamp": "2026-01-01T00:00:00Z",
        "run_id": "run-002",
        "actor": "tester",
        "step": "data_guard",
        "action": "inspect",
        "data": {"status": "ok"},
    }

    first_hash = logger.compute_hash(record)
    second_hash = logger.compute_hash(record)

    assert first_hash == second_hash


def test_audit_hash_chain_changes_when_records_append(tmp_path):
    audit_file = tmp_path / "audit.jsonl"
    logger = AuditLogger(audit_file)

    first = logger.append_record(
        {
            "timestamp": "2026-01-01T00:00:00Z",
            "run_id": "run-003",
            "actor": "tester",
            "step": "step-1",
            "action": "first",
            "data": {"value": 1},
        }
    )
    second = logger.append_record(
        {
            "timestamp": "2026-01-01T00:00:01Z",
            "run_id": "run-003",
            "actor": "tester",
            "step": "step-2",
            "action": "second",
            "data": {"value": 2},
        }
    )

    assert first["hash"] != second["hash"]

