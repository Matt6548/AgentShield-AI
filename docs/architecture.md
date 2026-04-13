# Architecture

SafeCore is middleware between AI agents and external systems.

## Module Map

- Policy Engine
- Data Guard
- Tool Guard
- Execution Guard
- Approval Layer
- Audit Layer
- Model Router
- Connectors
- Observability

## Foundation Status (Packages A-J)

### Runtime Guard Path

- Policy -> Data Guard -> Tool Guard -> Approval -> Model Routing -> Execution Guard -> Connector Adapter -> Audit
- Execution posture remains dry-run only.

### Decision/Approval Rules

- `DENY` remains non-overridable.
- `NEEDS_APPROVAL` remains blocked unless explicitly `APPROVED`.
- Escalation may update only approval/escalation metadata.
- Escalation never authorizes execution.

### Package G Foundations

- Policy authoring UX:
  - `src/policy/rule_registry.py`
  - `src/policy/rule_linter.py`
  - `src/policy/authoring.py`
- Approval escalation:
  - `src/approval/escalation_policies.py`
  - `src/approval/escalation.py`
- Deployment baseline:
  - `infra/Dockerfile`
  - `infra/docker-compose.yml`
  - `infra/.env.example`

### Package H Verification/Release Readiness

- Security harness:
  - `tests/test_security_invariants.py`
  - `tests/test_blocked_flows_regression.py`
  - `tests/test_contract_failure_regression.py`
  - `tests/test_dry_run_no_side_effects.py`
  - `tests/test_release_artifacts.py`
- Compatibility matrix:
  - `docs/compatibility_matrix.md`
- Release automation draft:
  - `.github/workflows/release-draft.yml`
- Prompt-pack consistency gate retained:
  - `tests/test_prompt_files.py` (explicit CI step)

### Package I Connector Hardening + Policy Pack v2

- Connector hardening boundary:
  - `src/connectors/request_sanitizer.py`
  - `src/connectors/response_sanitizer.py`
  - `src/connectors/hardening.py`
  - `src/connectors/executor.py` enforces sanitization before adapter execution.
- Policy pack versioning:
  - v1 (default): `src/policy/rules/*.rego`
  - v2 (opt-in): `src/policy/rules/v2/*.rego`
- Policy authoring/registry now supports explicit policy-pack discovery and lint targeting.
- API service includes explicit policy-pack selection and keeps default behavior on v1.
- Invalid connector input remains blocked and now emits both:
  - audit evidence
  - observability evidence

### Package J Router Profiles + Audit Integrity

- Model-router profile layer:
  - `src/model_router/profiles.py`
  - `src/model_router/profile_selector.py`
  - `src/model_router/router.py`
- Deterministic profiles:
  - `safe_low_risk`
  - `guarded_standard`
  - `high_risk_review`
  - `restricted_no_execute`
- Audit integrity verification:
  - `src/audit/integrity.py`
  - `AuditLogger.verify_integrity()` in `src/audit/audit_logger.py`
- Service integration:
  - guarded responses include `audit_integrity`
  - broken chains are surfaced explicitly with `audit_integrity:BROKEN_CHAIN`
  - observability emits `audit_integrity` stage events
- Release readiness:
  - `docs/release_candidate_checklist.md`

### Package K MVP Consolidation + Handoff

- No new runtime behavior is introduced in Package K.
- Consolidation aligns documentation with implemented and tested behavior under the RC freeze rule.
- New handoff/operations docs:
  - `docs/mvp_scope.md`
  - `docs/operations_runbook.md`
  - `docs/handoff_pack.md`
- Example alignment:
  - `examples/example_run.py` summaries include policy decision, approval status, model route/profile metadata, and audit integrity status.
- CI adds an explicit docs consistency gate:
  - `tests/test_docs_handoff_consistency.py`

## Risk Threshold Alignment

All implemented packages reuse Policy Engine thresholds as provisional shared constants:

- `0..33` => allow-level
- `34..66` => approval/redaction-level
- `67..100` => deny/block-level

## Deferred By Design

- Production authN/authZ
- External connector side effects
- External escalation/notification integrations
- Database persistence
- Web UI
- Cloud deployment stack
- Automatic final release publishing
