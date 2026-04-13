"""Structured logs and lightweight in-process metrics for SafeCore runs."""

from __future__ import annotations

import json
import logging
import time
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Callable


class Observability:
    """Collect deterministic observability events for guarded execution flows."""

    def __init__(
        self,
        logger: logging.Logger | None = None,
        now_fn: Callable[[], datetime] | None = None,
        perf_counter_fn: Callable[[], float] | None = None,
    ) -> None:
        self.logger = logger or logging.getLogger("safecore.observability")
        if not self.logger.handlers:
            self.logger.addHandler(logging.NullHandler())
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))
        self._perf_counter_fn = perf_counter_fn or time.perf_counter
        self._events: list[dict[str, Any]] = []
        self._counters: dict[str, int] = {}
        self._timings: list[dict[str, Any]] = []

    def start_timer(self) -> float:
        """Return a timer token used to compute elapsed stage duration."""
        return self._perf_counter_fn()

    def stop_timer(self, token: float) -> int:
        """Convert a timer token into elapsed milliseconds."""
        elapsed = (self._perf_counter_fn() - token) * 1000.0
        return max(0, int(round(elapsed)))

    def emit_event(
        self,
        *,
        run_id: str,
        stage: str,
        status: str,
        decision_summary: str,
        details: dict[str, Any] | None = None,
        duration_ms: int | None = None,
    ) -> dict[str, Any]:
        """Emit one structured event and update in-process counters/timers."""
        normalized_stage = str(stage).strip().lower() or "unknown"
        normalized_status = str(status).strip().upper() or "UNKNOWN"
        summary = str(decision_summary).strip()
        event: dict[str, Any] = {
            "timestamp": self._now_iso(),
            "run_id": str(run_id),
            "stage": normalized_stage,
            "status": normalized_status,
            "decision_summary": summary,
            "details": deepcopy(details or {}),
        }
        if duration_ms is not None:
            bounded_duration = max(0, int(duration_ms))
            event["duration_ms"] = bounded_duration
            self._timings.append(
                {
                    "run_id": event["run_id"],
                    "stage": normalized_stage,
                    "status": normalized_status,
                    "duration_ms": bounded_duration,
                }
            )

        self._events.append(event)
        counter_key = f"{normalized_stage}:{normalized_status}"
        self._counters[counter_key] = self._counters.get(counter_key, 0) + 1
        self.logger.info(
            json.dumps(event, sort_keys=True, ensure_ascii=True)
        )
        return deepcopy(event)

    def snapshot(self, run_id: str | None = None) -> dict[str, Any]:
        """Return counters/timer summary for all events or a single run."""
        selected_events = [
            event
            for event in self._events
            if run_id is None or event["run_id"] == str(run_id)
        ]
        counters: dict[str, int] = {}
        for event in selected_events:
            key = f"{event['stage']}:{event['status']}"
            counters[key] = counters.get(key, 0) + 1

        selected_timings = [
            item
            for item in self._timings
            if run_id is None or item["run_id"] == str(run_id)
        ]
        timers: dict[str, dict[str, int]] = {}
        for item in selected_timings:
            stage = item["stage"]
            duration = int(item["duration_ms"])
            entry = timers.setdefault(
                stage,
                {"count": 0, "total_ms": 0, "min_ms": duration, "max_ms": duration},
            )
            entry["count"] += 1
            entry["total_ms"] += duration
            entry["min_ms"] = min(entry["min_ms"], duration)
            entry["max_ms"] = max(entry["max_ms"], duration)

        for entry in timers.values():
            count = entry["count"]
            entry["avg_ms"] = int(round(entry["total_ms"] / count)) if count else 0

        return {
            "counters": counters,
            "timers": timers,
            "event_count": len(selected_events),
        }

    def _now_iso(self) -> str:
        return self._now_fn().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

