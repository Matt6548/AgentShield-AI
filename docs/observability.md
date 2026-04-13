# Observability Baseline

SafeCore currently includes a lightweight in-process observability layer for guarded dry-run runs.

## Entry Point

- `src/utils/observability.py`

## Scope

- Structured JSON logging for guarded stages.
- In-memory counters by `stage:status`.
- In-memory timer summaries per stage.
- No external telemetry backend and no vendor-specific tracing in this iteration.

## Event Shape

Each emitted event includes:

- `run_id`
- `stage`
- `status`
- `decision_summary`
- `details`
- optional `duration_ms`

Log lines are emitted as JSON via the standard Python logger.

## Guarded Flow Stages

Current API/service orchestration emits observability events for:

- `policy`
- `data_guard`
- `tool_guard`
- `approval`
- `model_routing`
- `execution`
- `connector_execution`
- `audit`

Blocked and validation-failure paths also emit explicit observability events.

## Determinism Notes

- Counters and stage selection are deterministic for identical inputs.
- Durations depend on runtime timing and are treated as informational.
- This baseline is foundation-only and intended for local/dev visibility.

