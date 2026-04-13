# Release Baseline

This document defines the current SafeCore release baseline.

## Scope

- Verification and artifact generation only.
- No publish to package registries in this iteration.
- Release workflow is draft-oriented and manually gated.
- Public open-source release framing is summarized in `docs/open_source_release_pack_m2.md`.

## Local Verification Checklist

1. Prompt-pack consistency gate:

```bash
python -m pytest -q tests/test_prompt_files.py
```

2. Docs/handoff consistency gate:

```bash
python -m pytest -q tests/test_docs_handoff_consistency.py
```

3. RC freeze consistency gate:

```bash
python -m pytest -q tests/test_rc_freeze_consistency.py
```

4. Final RC decision consistency gate:

```bash
python -m pytest -q tests/test_final_rc_decision_consistency.py
```

5. Security harness subset:

```bash
python -m pytest -q   tests/test_security_invariants.py   tests/test_blocked_flows_regression.py   tests/test_contract_failure_regression.py   tests/test_dry_run_no_side_effects.py   tests/test_release_artifacts.py
```

6. Package I policy-pack/connector hardening subset:

```bash
python -m pytest -q   tests/test_connector_sanitization.py   tests/test_connector_hardening.py   tests/test_policy_pack_v2.py   tests/test_policy_v1_v2_compat.py
```

7. Package J model-router/audit-integrity subset:

```bash
python -m pytest -q   tests/test_model_router_profiles.py   tests/test_audit_integrity.py   tests/test_api_audit_integrity_integration.py
```

8. Full tests:

```bash
python -m pytest -q
```

9. Compile check:

```bash
python -m compileall src tests
```

10. Build package:

```bash
python -m pip install build
python -m build
```

11. Confirm outputs:

- `dist/*.tar.gz`
- `dist/*.whl`

## Draft Release Workflow

- File: `.github/workflows/release-draft.yml`
- Behavior:
  - runs verification checks
  - builds artifacts
  - uploads artifacts + draft metadata
- Current limit:
  - does not publish to any package registry
  - does not perform automatic final release

## RC Freeze Workflow

- File: `.github/workflows/rc-freeze.yml`
- Trigger: manual `workflow_dispatch`
- Behavior:
  - runs deterministic RC gates (contracts, prompts, RC consistency, full tests, compile, build)
  - does not publish artifacts to external registries
  - supports stakeholder go/no-go review readiness

## Included Assets

Packaging baseline includes:

- `contracts/*.json`
- `prompts/v1/*.md`
- `src/policy/rules/*.rego`
- `src/policy/rules/v2/*.rego`
- core docs
- infra baseline files

## Notes

- Build success is a sanity gate, not a production guarantee.
- Runtime remains dry-run-first in this stage.
- Final release action remains manual/gated by maintainers.
- See `docs/release_candidate_checklist.md` for RC gating.
- See `docs/open_source_release_pack_m2.md` for public GitHub release framing.
- See `RELEASE_NOTES.md`, `docs/github_about_pack.md`, and `docs/public_launch_pack.md` for final public launch assets.
- Consolidated MVP docs for handoff are:
  - `docs/mvp_scope.md`
  - `docs/operations_runbook.md`
  - `docs/handoff_pack.md`

