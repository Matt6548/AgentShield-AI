# RC Freeze Notes

This document defines the release-candidate (RC) freeze posture for the current SafeCore MVP and final decision pack.

## Frozen Scope

- Final RC decision step is limited to release-readiness artifacts:
  - freeze notes
  - stakeholder review pack
  - launch checklist
  - known issues register
  - final go/no-go recommendation
  - signoff status tracking
  - release readiness summary
  - deterministic CI/workflow checks
- Runtime/business behavior is frozen.
- Decision semantics are frozen.
- API contract shape is frozen unless fixing an objective docs/test mismatch.

## Prohibited Changes During Freeze

- No new runtime/business features.
- No policy/approval/escalation semantic changes.
- No connector side-effect expansion.
- No contract schema redesign.
- No unrelated refactors.

## Accepted Risk and Known Limitations

- Runtime remains dry-run-only.
- `DENY` remains non-overridable.
- `NEEDS_APPROVAL` remains blocked unless explicit `APPROVED`.
- Escalation never authorizes execution.
- Policy pack `v2` remains opt-in; default stays `v1`.
- No production authN/authZ, DB persistence, web UI, or cloud stack in this stage.

See `docs/known_issues.md` for tracked details.

## Rollback Trigger Conditions

Rollback from RC candidacy is required when any of the following occurs:

- any core invariant regression (deny/approval/escalation semantics)
- contract validation boundary failure in guarded flow
- audit integrity failures not explained by intentional test tamper scenarios
- policy pack default switching away from `v1` without explicit selection
- non-deterministic CI failure pattern across required checks

## Change-Control Procedure

1. Document proposed freeze-period change in PR description.
2. Classify change as docs-only or deterministic release-check-only.
3. Link evidence from tests/workflows.
4. Require reviewer acknowledgement that runtime semantics are unchanged.
