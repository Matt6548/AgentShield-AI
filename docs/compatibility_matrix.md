# Compatibility Matrix

This matrix captures the current SafeCore foundation compatibility expectations.

## Runtime Matrix

- Python: `3.11` and `3.12` (CI matrix)
- OS:
  - Linux: primary CI environment (`ubuntu-latest`)
  - Windows/macOS: expected to work for local development
- Package build: `python -m build` (sdist + wheel)

## Local Development Baseline

- Virtual environment + `pip install -r requirements.txt`
- `pytest` for validation
- `uvicorn` for local API skeleton startup
- Dry-run-first posture only

## Docker / Compose Expectations

- `infra/Dockerfile` and `infra/docker-compose.yml` are local/dev baseline files
- Compose includes non-root container execution and healthcheck
- Runtime posture is still dry-run only
- Docker daemon is optional for tests in this repo; tests do not require daemon access

## OPA Compatibility

- OPA binary is optional
- If OPA is unavailable, `PolicyEngine` falls back to deterministic local evaluation
- Fallback path is the default expectation in CI and most local test runs

## Policy Pack Compatibility

- Supported packs: `v1` (default), `v2` (opt-in)
- Default runtime remains on `v1` unless explicitly configured for `v2`
- `SAFECORE_POLICY_PACK` may set the service default (`v1` or `v2`)
- API request field `policy_pack` can explicitly select a pack per request
- Invalid policy-pack selection returns a blocked validation-safe response

## FastAPI / TestClient

- FastAPI app is foundation-only (`/health`, `/v1/guarded-execute`)
- `fastapi.testclient.TestClient` is used for API tests
- API behavior remains deterministic and side-effect-safe in dry-run mode

## Release/Packaging Assumptions

- `pyproject.toml` + `MANIFEST.in` drive packaging baseline
- Prompt pack and contracts are included as release inputs
- Release workflow is draft/non-publishing in current scope
- RC freeze workflow exists for deterministic readiness checks:
  - `.github/workflows/rc-freeze.yml`
- Handoff/operations docs are maintained as release inputs:
  - `docs/mvp_scope.md`
  - `docs/operations_runbook.md`
  - `docs/handoff_pack.md`
  - `docs/rc_freeze_notes.md`
  - `docs/stakeholder_review_pack.md`
  - `docs/launch_checklist.md`
  - `docs/known_issues.md`

## Current Limitations

- No production authN/authZ
- No external connector side effects
- No database persistence
- No cloud deployment stack
- No web UI
- Connector hardening remains dry-run-only and intentionally non-side-effecting
