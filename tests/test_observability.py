import json
import logging
from datetime import datetime, timezone

from src.utils.observability import Observability


class ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


def test_observability_emits_structured_log_and_counters():
    logger = logging.getLogger("test_observability_logger")
    logger.handlers.clear()
    handler = ListHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    obs = Observability(
        logger=logger,
        now_fn=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    obs.emit_event(
        run_id="run-1",
        stage="policy",
        status="ALLOW",
        decision_summary="ALLOW:20",
        details={"risk_score": 20},
        duration_ms=3,
    )

    snapshot = obs.snapshot(run_id="run-1")
    assert snapshot["event_count"] == 1
    assert snapshot["counters"]["policy:ALLOW"] == 1
    assert snapshot["timers"]["policy"]["count"] == 1
    assert snapshot["timers"]["policy"]["avg_ms"] == 3

    assert handler.messages
    parsed = json.loads(handler.messages[-1])
    assert parsed["run_id"] == "run-1"
    assert parsed["stage"] == "policy"
    assert parsed["status"] == "ALLOW"
    assert parsed["decision_summary"] == "ALLOW:20"


def test_observability_timer_helpers_record_non_negative_duration():
    calls = iter([100.0, 100.002])
    obs = Observability(perf_counter_fn=lambda: next(calls))
    token = obs.start_timer()
    duration = obs.stop_timer(token)
    assert duration >= 0
    assert duration == 2

