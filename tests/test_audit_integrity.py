import json

from src.audit import AuditLogger, verify_chain, verify_record


def test_verify_record_accepts_valid_audit_record(tmp_path):
    audit_file = tmp_path / "audit_integrity_valid.jsonl"
    logger = AuditLogger(audit_file)
    record = logger.append_record(
        {
            "timestamp": "2026-01-01T00:00:00Z",
            "run_id": "run-int-1",
            "actor": "tester",
            "step": "api",
            "action": "guarded_execute",
            "data": {"status": "ok"},
        }
    )

    assert verify_record(record) is True


def test_verify_chain_detects_tampering(tmp_path):
    audit_file = tmp_path / "audit_integrity_tamper.jsonl"
    logger = AuditLogger(audit_file)
    logger.append_record(
        {
            "timestamp": "2026-01-01T00:00:00Z",
            "run_id": "run-int-2",
            "actor": "tester",
            "step": "api",
            "action": "first",
            "data": {"value": 1},
        }
    )
    logger.append_record(
        {
            "timestamp": "2026-01-01T00:00:01Z",
            "run_id": "run-int-2",
            "actor": "tester",
            "step": "api",
            "action": "second",
            "data": {"value": 2},
        }
    )

    lines = [line for line in audit_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    first = json.loads(lines[0])
    first["data"]["value"] = 999
    lines[0] = json.dumps(first, sort_keys=True, ensure_ascii=True)
    audit_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    records = logger.read_records()
    report = verify_chain(records)
    assert report["valid"] is False
    assert report["broken_indices"]


def test_audit_logger_verify_integrity_report_is_deterministic(tmp_path):
    audit_file = tmp_path / "audit_integrity_deterministic.jsonl"
    logger = AuditLogger(audit_file)
    logger.append_record(
        {
            "timestamp": "2026-01-01T00:00:00Z",
            "run_id": "run-int-3",
            "actor": "tester",
            "step": "api",
            "action": "only",
            "data": {"value": 1},
        }
    )

    first = logger.verify_integrity()
    second = logger.verify_integrity()
    assert first == second
    assert first["valid"] is True

