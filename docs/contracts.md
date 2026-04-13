# Contracts

This document tracks SafeCore's core JSON Schema contracts.

## Source of Truth

All canonical contracts are defined in `contracts/`:

- `Run.json`
- `Step.json`
- `SafetyDecision.json`
- `ToolCall.json`
- `AuditRecord.json`

Later modules must consume and emit data that conforms to these schemas.

## SafetyDecision Notes

`SafetyDecision.json` is the policy-output contract for `PolicyEngine.evaluate()`.

Required shape:

- `decision`: one of `ALLOW`, `DENY`, `NEEDS_APPROVAL`
- `risk_score`: integer from `0` to `100`
- `reasons`: list of strings
- `constraints`: list of strings
- `operator_checks`: list of strings

Current baseline mapping from risk score to decision:

- `0..33` => `ALLOW`
- `34..66` => `NEEDS_APPROVAL`
- `67..100` => `DENY`

Policy engine output must always normalize to this shape, including fallback mode.

## Guard Pack A Contract Alignment Notes

### Data Guard

`DataGuard.evaluate(payload)` returns a deterministic guard result:

- `allowed`: boolean
- `risk_score`: integer in `0..100`
- `findings`: list of strings
- `redacted_payload`: object
- `action`: `ALLOW` | `REDACT` | `BLOCK`

This is an internal guard contract for now and intentionally separate from `SafetyDecision`.

### Tool Guard + Execution Guard

- `ToolGuard.evaluate(request)` returns deterministic allow/deny guidance with reasons and risk score.
- `ExecutionGuard.execute(request, dry_run=True)` returns objects aligned to `ToolCall.json` top-level shape:
  - `tool`, `command`, `success`, `output`, `timestamp`
- In this iteration, execution is dry-run or explicit `NOT_IMPLEMENTED`; no real side effects.

### Audit Logger

- `AuditLogger.append_record(record)` writes records aligned with `AuditRecord.json`:
  - `timestamp`, `run_id`, `actor`, `step`, `action`, `data`, `hash`
- Hash is deterministic and chain-aware (`previous_hash` input) for tamper-evident local logs.

### Approval Layer (Package B)

`ApprovalManager` uses a small internal approval request object:

- `request_id`
- `created_at`
- `status` (`PENDING` | `APPROVED` | `REJECTED`)
- `policy_decision`
- `risk_score`
- `context`
- `approver`
- `reason`
- `decided_at`

Contract rules:

- Approval is required for `NEEDS_APPROVAL`.
- `ALLOW` bypasses approval.
- `DENY` is never overridable in this iteration.
- Approval request creation and approval decisions always emit audit records through `AuditLogger`.

### API Skeleton + Connectors (Package C)

API request/response models are defined in `src/api/schemas.py`:

- `GuardedExecutionRequest`
- `ApprovalDecisionPayload`
- `GuardedExecutionResponse`
- `HealthResponse`

`POST /v1/guarded-execute` returns module-aligned outputs:

- SafetyDecision-compatible policy output
- data guard result
- tool guard result
- approval state
- ToolCall-shaped execution result
- AuditRecord-shaped audit record

Connector notes:

- `src/connectors/base.py` defines abstract connector interface only.
- `src/connectors/stub_connector.py` returns deterministic stub responses.
- Connectors are placeholders and perform no real network/runtime side effects in this iteration.

### Prompt Pack v1 (Package D)

Prompt artifacts are stored under `prompts/v1/` with EN/RU pairs.

Contract alignment requirements:

- SafetyGate prompts must emit JSON compatible with `SafetyDecision.json`.
- AuditWriter prompts must emit JSON compatible with `AuditRecord.json`.
- Executor/API prompts must preserve ToolCall/Audit semantics used by current service responses.

Runtime status:

- Prompt pack files are versioned specs in this iteration.
- They are not yet fully wired into runtime prompt-orchestration paths.

### Runtime Contract Validation (Package E)

Validation utility:

- `src/utils/contract_validation.py`

Validated boundaries:

- `SafetyDecision.json` for policy decisions
- `ToolCall.json` for execution outputs
- `AuditRecord.json` for audit entries

Service integration:

- `src/api/service.py` validates these boundaries during orchestration.
- On contract mismatch, service returns a blocked-safe response and emits audit evidence for the validation failure.

### Model Routing + Connector Adapters + Observability (Package F)

Model routing contract (internal foundation object):

- `route_id`
- `model_profile`
- `reason`
- `constraints`
- `action_class`

Source:

- `src/model_router/router.py`
- `src/model_router/policies.py`

Connector adapter execution object (internal foundation object):

- `adapter_id`
- `connector`
- `tool`
- `dry_run`
- `status`
- `success`
- `reasons`
- `normalized_request`
- `raw_result`

Source:

- `src/connectors/adapters.py`
- `src/connectors/executor.py`

Observability snapshot object (internal foundation object):

- `counters` (stage/status counts)
- `timers` (per-stage duration aggregates)
- `event_count`

Source:

- `src/utils/observability.py`

Service integration note:

- `src/api/service.py` now includes `model_route`, `connector_execution`, and `observability` in guarded responses.
- Contract validation boundaries remain unchanged and enforced for:
  - `SafetyDecision.json`
  - `ToolCall.json`
  - `AuditRecord.json`
- On validation failures, response remains blocked-safe and audit evidence is still produced.

### Policy Authoring + Escalation + Deployment Baseline (Package G)

Policy authoring internal objects:

- Rule registry entries:
  - `file_name`
  - `path`
  - `package`
  - `metadata`
  - `rule_id`
- Lint report:
  - `valid`
  - `issue_count`
  - `issues`
- Fallback summary preview:
  - thresholds and fallback signal lists from `PolicyEngine.fallback_rule_summary()`.

Approval escalation internal metadata:

- `escalation_state`: `NONE | ESCALATED | EXPIRED`
- `escalation_target`: string or null
- `escalation_reason`: string
- `escalation_updated_at`: timestamp or null
- `escalation_elapsed_seconds`: integer

Escalation safety rule:

- Escalation changes only approval/escalation metadata.
- Escalation never authorizes execution by itself.
- Only explicit `APPROVED` may unblock execution.

Audit alignment:

- Escalation transitions emit `approval_escalation_updated` audit records.
- Existing `AuditRecord.json` boundary remains unchanged.

Deployment baseline note:

- `infra/.env.example` provides local config defaults for escalation timing and API runtime.
- Docker/compose hardening is local foundation infrastructure, not production deployment.

### Security Harness + Compatibility + Release Draft (Package H)

No new JSON contract files are introduced in this package.

Package H strengthens verification around existing contract boundaries:

- `SafetyDecision.json` invariant checks via blocked-flow and failure-path tests.
- `ToolCall.json` invariant checks for blocked-safe and dry-run outputs.
- `AuditRecord.json` invariant checks that blocked and failure flows still emit evidence.

Release/readiness artifact checks validate that:

- required contracts exist
- prompt-pack assets remain present
- release workflow draft references real repository checks

Prompt-pack consistency gate:

- `tests/test_prompt_files.py` remains an explicit CI gate.
- SafetyGate keyword expectations remain enforced.

### Shared Risk Alignment Rule

Guard Pack A + Package B + Package C + Package D + Package E + Package F + Package G + Package H use existing Policy Engine thresholds as the provisional baseline:

- `0..33` => allow-level
- `34..66` => approval/redaction-level
- `67..100` => deny/block-level

### Package I: Connector Hardening + Policy Pack v2

Policy pack versioning:

- `v1` remains the default stable pack.
- `v2` is explicitly selectable only.
- No silent switch from `v1` to `v2`.

Policy output contract compatibility:

- Both packs must emit `SafetyDecision.json` shape.
- Risk thresholds remain unchanged across packs.

Connector hardening boundary (internal contract):

- Connector request sanitization is applied before adapter execution.
- Connector response sanitization normalizes output envelope and strips unsafe internals.
- Invalid connector inputs produce:
  - blocked connector status (`INVALID_INPUT`)
  - audit evidence (`AuditRecord` aligned)
  - observability stage evidence (`connector_execution:INVALID_INPUT`)

Runtime guarantees remain unchanged:

- `DENY` non-overridable
- `NEEDS_APPROVAL` blocked unless explicitly `APPROVED`
- escalation never authorizes execution
- dry-run-only execution posture

### Package J: Router Profiles + Audit Integrity

Model-router profile metadata (internal object extension):

- `profile_id`
- `profile_name`
- `profile_reason`
- `profile_guardrails`

These fields extend the existing model-route object while preserving prior route keys:

- `route_id`
- `model_profile`
- `reason`
- `constraints`
- `action_class`

Audit integrity report (internal object):

- `valid`: bool
- `record_count`: int
- `verified_count`: int
- `broken_indices`: list[int]
- `errors`: list[str]
- `file_path`: str

Behavioral contract:

- Broken audit chain must not be silently ignored.
- Service response surfaces integrity state explicitly.
- Observability includes `audit_integrity` stage status.

### Package K: MVP Consolidation (No Contract Drift)

Package K does not introduce new JSON schema contracts or runtime contract semantics.

Consolidation rules applied:

- Documentation aligns to implemented code and tests.
- Deferred behavior is explicitly marked as deferred (not implied as implemented).
- Example output documentation is aligned with current guarded response fields:
  - policy decision
  - approval status
  - model route/profile metadata
  - audit integrity status
