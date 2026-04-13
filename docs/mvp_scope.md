# MVP Scope

This document defines the current SafeCore MVP scope after Packages A-J, with Package K consolidation.

## Runtime Guarantees

- Execution is dry-run only.
- `DENY` is non-overridable.
- `NEEDS_APPROVAL` remains blocked unless explicitly `APPROVED`.
- Escalation never authorizes execution by itself.
- Policy pack `v1` is the default; `v2` is opt-in only.

## In Scope (Implemented Foundations)

- Policy engine with deterministic fallback evaluation and optional OPA path.
- Data guard, tool guard, execution guard, and connector hardening boundaries.
- Approval workflow with escalation metadata and audit evidence.
- Audit logging with hash chaining and integrity verification.
- Model routing with explicit routing profiles.
- API skeleton (`/health`, `/v1/guarded-execute`) with guarded orchestration.
- Contract validation at key runtime boundaries.
- Prompt Pack v1 artifacts.
- Local Docker/Compose baseline for development.
- CI baseline with regression harness and package build checks.

## Out of Scope (Deferred)

- Production authN/authZ.
- Real connector side effects and external integrations.
- Database persistence.
- Web UI.
- Cloud deployment stack.
- Production-grade sandboxing beyond dry-run posture.

## Operational Notes

- Prompt artifacts under `prompts/v1` are versioned specifications and are not fully runtime-wired.
- Release workflow remains draft/non-publishing by default.
- Final release action remains manual or explicitly gated.
