# Example Run

`examples/example_run.py` demonstrates SafeCore's current dry-run guarded path with approval gating.

## Flows Included

- Safe path (no approval needed)
- Approval-required path (approved and then executed in dry_run mode)
- Rejected path (blocked before execution)

## Run

```bash
python examples/example_run.py
```

## Printed Summary Per Flow

The script prints:

- policy decision (`decision`, `risk_score`, reasons/constraints metadata)
- approval status
- model route/profile metadata (`route_id`, `model_profile`, `profile_id`, `profile_name`)
- execution status
- connector execution status
- audit integrity status (`valid`, `broken_indices`)
- audit hash

## Notes

- Execution is dry-run only in this iteration.
- DENY is not overridable by approval.
- Approval records and decisions are both written to local audit evidence.
- Escalation metadata may change approval state tracking but never authorizes execution.
