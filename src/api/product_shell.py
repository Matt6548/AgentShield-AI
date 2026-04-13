"""Local persistence and view-model helpers for the SafeCore product shell."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.audit.integrity import load_records_from_jsonl, verify_audit_file


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_PRODUCT_SHELL_STORE = ROOT_DIR / "examples" / "product_shell" / "product_shell_store.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ProductShellStore:
    """Persist a small local product-shell history without introducing a database."""

    def __init__(self, file_path: str | Path = DEFAULT_PRODUCT_SHELL_STORE) -> None:
        self.file_path = Path(file_path)

    def append_run(self, entry: dict[str, Any]) -> dict[str, Any]:
        data = self._load()
        runs = data.setdefault("runs", [])
        normalized = dict(entry)
        normalized.setdefault("recorded_at", now_iso())
        normalized.setdefault("provider_mode", self._provider_mode(normalized))
        runs.append(normalized)
        if len(runs) > 200:
            data["runs"] = runs[-200:]
        self._write(data)
        return normalized

    def list_runs(
        self,
        *,
        limit: int = 20,
        decision: str | None = None,
        run_status: str | None = None,
        provider: str | None = None,
    ) -> list[dict[str, Any]]:
        runs = [self._decorate_run(run) for run in self._load().get("runs", [])]
        normalized_decision = str(decision or "ALL").upper()
        normalized_status = str(run_status or "ALL").upper()
        normalized_provider = str(provider or "ALL").upper()

        if normalized_decision != "ALL":
            runs = [run for run in runs if str(run.get("decision", "")).upper() == normalized_decision]
        if normalized_status != "ALL":
            runs = [run for run in runs if str(run.get("run_status", "")).upper() == normalized_status]
        if normalized_provider != "ALL":
            runs = [run for run in runs if str(run.get("provider_mode", "")).upper() == normalized_provider]

        runs.sort(key=lambda item: str(item.get("recorded_at", "")), reverse=True)
        return runs[: max(0, int(limit))]

    def build_summary(self) -> dict[str, Any]:
        runs = [self._decorate_run(run) for run in self._load().get("runs", [])]
        counts = {
            "total_runs": len(runs),
            "allow": 0,
            "needs_approval": 0,
            "deny": 0,
            "blocked": 0,
            "audit_integrity_issues": 0,
            "pending_approvals": 0,
        }
        for run in runs:
            decision = str(run.get("decision", "")).upper()
            if decision == "ALLOW":
                counts["allow"] += 1
            elif decision == "NEEDS_APPROVAL":
                counts["needs_approval"] += 1
            elif decision == "DENY":
                counts["deny"] += 1
            if bool(run.get("blocked", False)):
                counts["blocked"] += 1
            if not bool(run.get("audit_integrity", False)):
                counts["audit_integrity_issues"] += 1
            if str(run.get("approval_status", "")).upper() == "PENDING":
                counts["pending_approvals"] += 1

        latest_runs = self.list_runs(limit=5)
        latest_events = [
            {
                "recorded_at": run.get("recorded_at"),
                "title": run.get("title"),
                "source": run.get("source"),
                "decision": run.get("decision"),
                "blocked": run.get("blocked"),
                "summary": run.get("short_explanation"),
                "provider_mode": run.get("provider_mode"),
                "run_status": run.get("run_status"),
            }
            for run in latest_runs
        ]
        return {
            **counts,
            "latest_events": latest_events,
            "last_updated": latest_runs[0]["recorded_at"] if latest_runs else None,
        }

    def build_approval_queue(self, *, limit: int = 10) -> list[dict[str, Any]]:
        queue = []
        for run in self.list_runs(limit=200):
            approval_status = str(run.get("approval_status", "")).upper()
            escalation_state = str(run.get("escalation_state", "NONE")).upper()
            if approval_status != "PENDING" and escalation_state == "NONE":
                continue
            queue.append(
                {
                    "recorded_at": run.get("recorded_at"),
                    "title": run.get("title"),
                    "source": run.get("source"),
                    "decision": run.get("decision"),
                    "risk_score": run.get("risk_score"),
                    "approval_status": run.get("approval_status"),
                    "escalation_state": escalation_state,
                    "why_blocked": run.get("why_blocked"),
                    "operator_checks": run.get("operator_checks", []),
                    "next_step": run.get("next_step"),
                    "provider_mode": run.get("provider_mode"),
                }
            )
        return queue[: max(0, int(limit))]

    def build_audit_view(
        self,
        *,
        limit: int = 20,
        decision: str | None = None,
        provider: str | None = None,
        integrity_state: str | None = None,
    ) -> list[dict[str, Any]]:
        runs = self.list_runs(limit=200, decision=decision, provider=provider)
        run_lookup = {str(run.get("run_id", "")): run for run in runs}
        audit_files: dict[str, str] = {}
        for run in runs:
            audit_file = str(run.get("audit_file", "")).strip()
            audit_path = str(run.get("audit_path", "")).strip()
            if audit_file:
                audit_files[audit_file] = audit_path or audit_file

        normalized_integrity = str(integrity_state or "ALL").upper()
        events: list[dict[str, Any]] = []
        for audit_file, audit_path in audit_files.items():
            records, _ = load_records_from_jsonl(audit_file)
            integrity = verify_audit_file(audit_file)
            state = "VALID" if bool(integrity.get("valid", False)) else "BROKEN"
            if normalized_integrity != "ALL" and state != normalized_integrity:
                continue
            for record in records[-5:]:
                run = run_lookup.get(str(record.get("run_id", "")), {})
                events.append(
                    {
                        "timestamp": record.get("timestamp"),
                        "run_id": record.get("run_id"),
                        "action": record.get("action"),
                        "step": record.get("step"),
                        "decision": run.get("decision"),
                        "title": run.get("title"),
                        "integrity_state": state,
                        "audit_path": audit_path,
                        "provider_mode": run.get("provider_mode", self._provider_mode(run)),
                        "run_status": run.get("run_status", self._run_status(run)),
                    }
                )
        events.sort(key=lambda item: str(item.get("timestamp", "")), reverse=True)
        return events[: max(0, int(limit))]

    def _decorate_run(self, run: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(run)
        normalized["provider_mode"] = self._provider_mode(normalized)
        normalized["run_status"] = self._run_status(normalized)
        return normalized

    def _provider_mode(self, run: dict[str, Any]) -> str:
        value = str(run.get("provider_mode", "")).strip().upper()
        if value:
            return value
        return "LOCAL_DEMO"

    def _run_status(self, run: dict[str, Any]) -> str:
        if str(run.get("approval_status", "")).upper() == "PENDING":
            return "PENDING_APPROVAL"
        if bool(run.get("blocked", False)):
            return "BLOCKED"
        return "ALLOWED"

    def _load(self) -> dict[str, Any]:
        if not self.file_path.exists():
            return {"runs": []}
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"runs": []}
        if not isinstance(data, dict):
            return {"runs": []}
        runs = data.get("runs", [])
        if not isinstance(runs, list):
            runs = []
        return {"runs": runs}

    def _write(self, data: dict[str, Any]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
