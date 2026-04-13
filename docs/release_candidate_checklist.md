# Release Candidate Checklist

This checklist is the minimum readiness gate before marking a SafeCore release candidate.

## 1) Pre-release validation

1. Run full test suite:
   - `python -m pytest -q`
2. Run prompt-pack consistency gate:
   - `python -m pytest -q tests/test_prompt_files.py`
3. Run docs/handoff consistency gate:
   - `python -m pytest -q tests/test_docs_handoff_consistency.py`
4. Run RC freeze consistency gate:
   - `python -m pytest -q tests/test_rc_freeze_consistency.py`
5. Run targeted security and integrity subsets:
   - `python -m pytest -q tests/test_security_invariants.py tests/test_audit_integrity.py tests/test_api_audit_integrity_integration.py`
6. Run compile check:
   - `python -m compileall src tests`

## 2) Build and packaging checks

1. Build artifacts:
   - `python -m build`
2. Confirm both artifacts exist:
   - `dist/*.tar.gz`
   - `dist/*.whl`
3. Confirm packaging includes:
   - `contracts/*.json`
   - `prompts/v1/*.md`
   - `src/policy/rules/*.rego`
   - `src/policy/rules/v2/*.rego`

## 3) Policy-pack selection checks

1. Verify default behavior remains `v1`.
2. Verify explicit `v2` selection works by request/config.
3. Verify invalid policy-pack selection fails safely (blocked path).
4. Verify no silent switch from `v1` to `v2`.

## 4) Audit-integrity verification

1. Verify valid chain case (`AuditLogger.verify_integrity()` returns `valid: true`).
2. Verify tampered/broken chain case (`valid: false` with broken indices).
3. Verify service surfaces broken integrity state explicitly and observably.

## 5) Rollback and operational readiness

1. Confirm rollback path to `v1` policy pack is documented (`docs/migration_guide_v2.md`).
2. Confirm dry-run-only posture remains enforced.
3. Confirm no real connector side effects are introduced.
4. Confirm known limitations are documented and accepted.

## 6) Known limitations (current stage)

- Runtime is dry-run-first.
- No production authN/authZ stack.
- No database persistence.
- No real connector execution side effects.
- No cloud deployment stack.
- No web UI.

## 7) Handoff and operations docs check

1. Confirm `docs/mvp_scope.md` exists and reflects current scope.
2. Confirm `docs/operations_runbook.md` contains integrity and incident-safe procedures.
3. Confirm `docs/handoff_pack.md` contains architecture snapshot, ownership map, and onboarding steps.

## 8) RC freeze and stakeholder signoff check

1. Confirm `docs/rc_freeze_notes.md` is reviewed and accepted.
2. Confirm `docs/stakeholder_review_pack.md` includes owner fields and decision status.
3. Confirm `docs/launch_checklist.md` is complete.
4. Confirm `docs/known_issues.md` lists no open RC blockers for GO.
