"""Audit record integrity verification utilities."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_FIELDS = ("timestamp", "run_id", "actor", "step", "action", "data", "hash")


def verify_record(record: dict[str, Any]) -> bool:
    """Return whether a record looks valid at the single-record level."""
    if not isinstance(record, dict):
        return False
    for field in REQUIRED_FIELDS:
        if field not in record:
            return False
    if not isinstance(record.get("data"), dict):
        return False
    record_hash = record.get("hash")
    if not isinstance(record_hash, str):
        return False
    if not HASH_PATTERN.fullmatch(record_hash):
        return False
    return True


def compute_expected_hash(record: dict[str, Any], previous_hash: str) -> str:
    """Compute expected chained hash for one record."""
    payload = dict(record)
    payload.pop("hash", None)
    payload["previous_hash"] = previous_hash
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_chain(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Verify full audit chain integrity and return deterministic report."""
    report = {
        "valid": True,
        "record_count": len(records),
        "verified_count": 0,
        "broken_indices": [],
        "errors": [],
    }
    previous_hash = ""
    for index, record in enumerate(records):
        if not verify_record(record):
            report["valid"] = False
            report["broken_indices"].append(index)
            report["errors"].append(
                f"Record at index {index} failed structural verification."
            )
            hash_value = record.get("hash") if isinstance(record, dict) else None
            previous_hash = str(hash_value) if isinstance(hash_value, str) else previous_hash
            continue

        expected_hash = compute_expected_hash(record, previous_hash=previous_hash)
        actual_hash = str(record["hash"])
        if actual_hash != expected_hash:
            report["valid"] = False
            report["broken_indices"].append(index)
            report["errors"].append(
                f"Record at index {index} has broken chain hash linkage."
            )
        else:
            report["verified_count"] += 1

        previous_hash = actual_hash

    return report


def load_records_from_jsonl(file_path: str | Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Load JSON-lines audit records; return records and parse errors."""
    path = Path(file_path)
    if not path.exists():
        return [], []

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line_index, line in enumerate(f):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                errors.append(f"Invalid JSON on line {line_index + 1}.")
                continue
            if not isinstance(parsed, dict):
                errors.append(f"Non-object JSON record on line {line_index + 1}.")
                continue
            records.append(parsed)
    return records, errors


def verify_audit_file(file_path: str | Path) -> dict[str, Any]:
    """Verify chain integrity for a JSON-lines audit file."""
    records, parse_errors = load_records_from_jsonl(file_path)
    report = verify_chain(records)
    if parse_errors:
        report["valid"] = False
        report["errors"].extend(parse_errors)
    report["file_path"] = str(file_path)
    return report

