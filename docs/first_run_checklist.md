# First Run Checklist

Use this checklist for the first local SafeCore run.

## Before you start

- Python 3.11+ is installed
- project dependencies are installed with `pip install -r requirements.txt`
- you expect a local RC/MVP product shell, not a production platform

## Start the shell

- run `uvicorn src.api.app:app --reload`
- open `http://127.0.0.1:8000/ui`
- confirm the overview page loads

## Complete one guarded run

- finish onboarding
- open `First Practical Integration Path`
- run `allowlisted_get`
- confirm the result shows:
  - `decision=ALLOW`
  - `execution_status=DRY_RUN_SIMULATED`
  - `audit_integrity=True`

## Compare blocked behavior

- run `blocked_host`
- run `blocked_method`
- confirm both show blocked-safe behavior rather than execution

## Inspect the product shell

- open `Run History`
- confirm a recent run appears
- open `Approval And Audit`
- confirm audit visibility is present

## Sanity-check provider and advisory status

- open `Provider Status / Configuration`
- expect `Local / demo mode` to be the only enabled path by default
- expect external providers to show configured/not configured status only
- expect the Safety Copilot to be disabled unless you explicitly enabled it

## If something looks wrong

See [troubleshooting.md](troubleshooting.md).
