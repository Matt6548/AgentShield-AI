# Operations Runbook

This runbook covers day-to-day local operation and verification for the SafeCore MVP foundation.

## Local Startup and Testing

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run targeted gates:
   - `python -m pytest -q tests/test_prompt_files.py`
   - `python -m pytest -q tests/test_docs_handoff_consistency.py`
   - `python -m pytest -q tests/test_rc_freeze_consistency.py`
4. Run full suite:
   - `python -m pytest -q`
5. Compile sanity check:
   - `python -m compileall src tests`
6. Build package artifacts:
   - `python -m pip install build`
   - `python -m build`
7. Optional local API startup:
   - `uvicorn src.api.app:app --reload`

## Integrity-Check Procedure

1. Ensure audit evidence exists by running:
   - `python examples/example_run.py`
2. Verify integrity through service output (`audit_integrity`) or logger utility path used in tests.
3. Run integrity-focused tests:
   - `python -m pytest -q tests/test_audit_integrity.py tests/test_api_audit_integrity_integration.py`
4. Treat any `valid: false` integrity result as an incident condition.

## Broken Audit Chain Incident Steps

1. Stop relying on the affected audit file for trust decisions.
2. Preserve the file for investigation; do not mutate it in place.
3. Re-run integrity tests and confirm reproduction:
   - `python -m pytest -q tests/test_audit_integrity.py`
4. Inspect the `broken_indices` and `errors` fields from integrity reports.
5. Rotate to a fresh audit file for new dry-run validation.
6. Document the incident and update release readiness status before RC sign-off.

## Policy Pack Selection Verification

1. Confirm default is still `v1`:
   - run guarded request without `policy_pack` and inspect response.
2. Confirm explicit `v2` selection:
   - pass `policy_pack: "v2"` in request.
3. Confirm invalid pack fails safely (blocked path):
   - pass unknown pack value and verify blocked-safe response.
4. Run compatibility tests:
   - `python -m pytest -q tests/test_policy_v1_v2_compat.py tests/test_policy_pack_v2.py`

## Expected Observability Signals

For one guarded request, stage events should include:

- `request`
- `policy`
- `data_guard`
- `tool_guard`
- `approval`
- `escalation`
- `model_routing`
- `connector_execution`
- `execution`
- `audit`
- `audit_integrity`

Key counters/timers are exposed via `observability` in service/API responses.
Blocked flows should still emit observability and audit evidence.

## RC Freeze Execution

1. Complete `docs/launch_checklist.md`.
2. Update signoff fields in `docs/stakeholder_review_pack.md`.
3. Run manual RC freeze workflow:
   - `.github/workflows/rc-freeze.yml`
4. Confirm `docs/known_issues.md` has no open RC blockers before GO recommendation.
