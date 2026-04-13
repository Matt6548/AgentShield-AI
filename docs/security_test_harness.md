# Security Test Harness

SafeCore includes a regression-oriented security harness to protect core safety guarantees.

## Test Files

- `tests/test_security_invariants.py`
- `tests/test_blocked_flows_regression.py`
- `tests/test_contract_failure_regression.py`
- `tests/test_dry_run_no_side_effects.py`
- `tests/test_release_artifacts.py`

## Covered Invariants

- `DENY` paths never execute.
- `NEEDS_APPROVAL` paths never execute unless explicitly `APPROVED`.
- Escalation updates metadata only and never authorizes execution.
- Contract validation failures return blocked-safe responses.
- Blocked flows still emit audit evidence.
- Blocked flows still emit observability events.
- Dry-run paths avoid real side effects.

## Regression Scenarios

- Dangerous shell command patterns.
- Suspicious network egress patterns.
- Approval pending and rejected states.
- Escalation state progression (`NONE -> ESCALATED -> EXPIRED`).
- Contract boundary failure paths.

## Prompt Pack Consistency Gate

- Existing prompt-pack test remains active:
  - `tests/test_prompt_files.py`
- CI runs this test explicitly as a lightweight guard that required `prompts/v1` files and key contract keywords remain present.

## Execution

Run focused harness subset:

```bash
python -m pytest -q \
  tests/test_security_invariants.py \
  tests/test_blocked_flows_regression.py \
  tests/test_contract_failure_regression.py \
  tests/test_dry_run_no_side_effects.py \
  tests/test_release_artifacts.py
```

Run full suite:

```bash
python -m pytest -q
```

