"""Simple file-based audit logger with hash chaining."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.audit.integrity import load_records_from_jsonl, verify_audit_file


REQUIRED_AUDIT_FIELDS = ("run_id", "actor", "step", "action", "data")


class AuditLogger:
    """Append audit records to a local JSON-lines file."""

    def __init__(self, file_path: str | Path = "audit.log.jsonl") -> None:
        self.file_path = Path(file_path)

    def compute_hash(self, record: dict[str, Any]) -> str:
        """Compute deterministic hash for a record using previous-hash chaining."""
        if not isinstance(record, dict):
            raise TypeError("AuditLogger.compute_hash expects a dict record.")

        payload = dict(record)
        payload.pop("hash", None)
        payload["previous_hash"] = self._read_last_hash()
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def append_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Validate, hash, and append one audit record."""
        if not isinstance(record, dict):
            raise TypeError("AuditLogger.append_record expects a dict record.")

        normalized = dict(record)
        for field in REQUIRED_AUDIT_FIELDS:
            if field not in normalized:
                raise ValueError(f"Missing required audit field: {field}")

        if "timestamp" not in normalized:
            normalized["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        normalized["hash"] = self.compute_hash(normalized)

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(normalized, sort_keys=True, ensure_ascii=True))
            f.write("\n")

        return normalized

    def read_records(self) -> list[dict[str, Any]]:
        """Read all parseable audit records from file."""
        records, _ = load_records_from_jsonl(self.file_path)
        return records

    def verify_integrity(self) -> dict[str, Any]:
        """Verify file-level hash-chain integrity for current audit log."""
        return verify_audit_file(self.file_path)

    def _read_last_hash(self) -> str:
        if not self.file_path.exists():
            return ""
        last_hash = ""
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError:
                    continue
                value = parsed.get("hash")
                if isinstance(value, str):
                    last_hash = value
        return last_hash
