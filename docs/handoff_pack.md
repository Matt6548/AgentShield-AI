# Handoff Pack

This document is the contributor handoff snapshot for the consolidated SafeCore MVP foundation.

## Architecture Snapshot

- Guarded flow: Policy -> Data Guard -> Tool Guard -> Approval -> Escalation -> Model Router -> Connector Executor -> Execution Guard -> Audit -> Audit Integrity.
- Runtime posture is dry-run only.
- Decision semantics:
  - `DENY` non-overridable.
  - `NEEDS_APPROVAL` blocked unless explicit `APPROVED`.
  - Escalation updates approval metadata only and never authorizes execution.
- Policy pack selection:
  - default `v1`
  - explicit opt-in `v2`
  - no silent pack switching

## Module Ownership Map

- Policy layer:
  - `src/policy/policy_engine.py`
  - `src/policy/rules/`
  - `src/policy/rules/v2/`
  - `src/policy/authoring.py`
  - `src/policy/rule_registry.py`
  - `src/policy/rule_linter.py`
- Approval/escalation:
  - `src/approval/approval_manager.py`
  - `src/approval/escalation.py`
  - `src/approval/escalation_policies.py`
- Guard path:
  - `src/data_guard/data_guard.py`
  - `src/utils/tool_policies.py`
  - `src/exec_guard/exec_guard.py`
  - `src/connectors/executor.py`
  - `src/connectors/hardening.py`
- Service/API:
  - `src/api/service.py`
  - `src/api/app.py`
  - `src/api/schemas.py`
- Audit/observability:
  - `src/audit/audit_logger.py`
  - `src/audit/integrity.py`
  - `src/utils/observability.py`
- Model routing:
  - `src/model_router/router.py`
  - `src/model_router/profiles.py`
  - `src/model_router/profile_selector.py`

## Test Strategy Map

- Contract and prompt gates:
  - `tests/test_contracts_smoke.py`
  - `tests/test_prompt_files.py`
- Guard/runtime invariants:
  - `tests/test_security_invariants.py`
  - `tests/test_blocked_flows_regression.py`
  - `tests/test_contract_failure_regression.py`
- Policy pack compatibility:
  - `tests/test_policy_pack_v2.py`
  - `tests/test_policy_v1_v2_compat.py`
- Audit integrity:
  - `tests/test_audit_integrity.py`
  - `tests/test_api_audit_integrity_integration.py`
- Package K docs/example consistency:
  - `tests/test_docs_handoff_consistency.py`

## Release and Rollback Pointers

- Release baseline checklist: `docs/release.md`
- Release candidate checklist: `docs/release_candidate_checklist.md`
- RC freeze notes: `docs/rc_freeze_notes.md`
- Stakeholder review pack: `docs/stakeholder_review_pack.md`
- Launch checklist: `docs/launch_checklist.md`
- Known issues register: `docs/known_issues.md`
- Policy pack v2 migration/rollback: `docs/migration_guide_v2.md`
- Compatibility baseline: `docs/compatibility_matrix.md`
- Operations procedures: `docs/operations_runbook.md`

## Deferred Scope

- Production authN/authZ.
- Real connector side effects and external integrations.
- Database persistence.
- Web UI.
- Cloud deployment stack.
- Production release publishing automation.

## First-Week Onboarding Steps

1. Read `README.md`, `docs/mvp_scope.md`, and `docs/architecture.md`.
2. Run baseline gates:
   - `python -m pytest -q tests/test_contracts_smoke.py tests/test_prompt_files.py tests/test_docs_handoff_consistency.py`
3. Run full suite:
   - `python -m pytest -q`
4. Run compile/build:
   - `python -m compileall src tests`
   - `python -m build`
5. Run the example:
   - `python examples/example_run.py`
6. Review migration and release docs before proposing RC changes.
7. Before RC review, complete `docs/launch_checklist.md` and update decision fields in `docs/stakeholder_review_pack.md`.
