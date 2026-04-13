# Demo Quickstart

SafeCore is a security middleware layer for agent actions. This quickstart is the fastest way to see the current RC-stage value of the project without changing any runtime semantics.

## Local Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the demo smoke script:

```bash
python scripts/demo_smoke.py
```

3. Optional: run the demo test only:

```bash
python -m pytest -q tests/test_demo_smoke.py
```

## Expected Scenario Output

The script prints these three scenario lines:

```text
[allow_case] decision=ALLOW risk_score=15 blocked=False approval_status=BYPASSED execution_status=DRY_RUN_SIMULATED audit_integrity=True audit=examples/demo_audit.log.jsonl
[approval_case] decision=NEEDS_APPROVAL risk_score=55 blocked=True approval_status=PENDING execution_status=BLOCKED audit_integrity=True audit=examples/demo_audit.log.jsonl
[deny_case] decision=DENY risk_score=90 blocked=True approval_status=NOT_APPLICABLE_DENY execution_status=BLOCKED audit_integrity=True audit=examples/demo_audit.log.jsonl
```

## What To Look For

- `ALLOW` scenario executes only as `DRY_RUN_SIMULATED`
- `NEEDS_APPROVAL` does not auto-execute
- `DENY` remains blocked
- audit evidence is written to `examples/demo_audit.log.jsonl`

For the plain-language explanation, see `docs/demo_value.md`.
For the scenario table, see `docs/demo_scenarios.md`.
