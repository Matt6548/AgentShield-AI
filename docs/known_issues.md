# Known Issues

This register distinguishes accepted MVP limitations, deferred scope, and true RC blockers.

## Accepted MVP Limitations (Non-Blockers)

- Runtime is dry-run-only by design.
- API is foundation-level and not production-hardened.
- OPA path is optional; fallback policy evaluation is primary in CI/local.
- Prompt pack is versioned artifact/spec and not fully runtime-wired.
- Observability is local/in-process (no external telemetry backend).

## Deferred Scope (Planned, Not RC Blocking)

- Production authN/authZ stack
- Real connector side effects and external integrations
- Database persistence
- Web UI
- Cloud deployment stack
- Automated final publish/release pipeline

## RC Blockers (Must Be Empty For GO)

Current status: **NO OPEN CRITICAL RC BLOCKERS**.

Open release conditions (non-critical blockers):

- none currently open

This status is aligned with:

- `docs/signoff_status.md` -> overall status `APPROVED`
- `docs/final_go_no_go.md` -> recommendation `GO`
- `docs/release_readiness_summary.md` -> readiness gates passed

Blocking examples:

- regression in core safety invariants
- contract validation boundary failures in guarded flow
- unresolved broken audit integrity behavior
- policy pack default silently switching from `v1` to `v2`
- required stakeholder signoff missing
