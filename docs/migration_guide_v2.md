# Migration Guide v2

This guide explains how to adopt policy pack v2 safely while preserving current runtime guarantees.

## 1) Enable / Select v2

v2 is opt-in and never enabled silently.

Choose one explicit activation method:

1. Engine construction:

```python
from src.policy import PolicyEngine

engine = PolicyEngine(policy_pack="v2", opa_binary="definitely-not-opa")
```

2. Per-call override:

```python
decision = engine.evaluate(input_data, policy_pack="v2")
```

3. API request:

```json
{
  "run_id": "example",
  "actor": "tester",
  "action": "deploy_service",
  "tool": "config_reader",
  "command": "",
  "policy_pack": "v2",
  "dry_run": true
}
```

4. Service default via environment:

```bash
SAFECORE_POLICY_PACK=v2
```

## 2) Rollback Path to v1

Rollback is explicit and immediate:

- remove `policy_pack: "v2"` from API requests, or
- call `evaluate(..., policy_pack="v1")`, or
- set `SAFECORE_POLICY_PACK=v1`, or
- instantiate `PolicyEngine(policy_pack="v1")`.

No data migration is required because this package does not introduce persistent storage changes.

## 3) Compatibility Notes

- SafetyDecision shape is unchanged.
- Risk thresholds are unchanged:
  - `0..33` -> `ALLOW`
  - `34..66` -> `NEEDS_APPROVAL`
  - `67..100` -> `DENY`
- Approval semantics are unchanged:
  - `DENY` non-overridable
  - `NEEDS_APPROVAL` blocked unless explicit `APPROVED`
  - escalation cannot authorize execution
- Dry-run-only execution behavior is unchanged.
- OPA remains optional; fallback evaluator remains deterministic.

## 4) Known Behavior Differences (v1 vs v2)

- Shell chaining/redirection is denied in v2 (`&&`, `||`, `;`, `|`, `>`, `<`, `` ` ``, `$(`).
- Production mutations without change-ticket metadata are denied in v2.
- Sensitive exfiltration signals are more strictly denied in v2.
- Missing action/tool context is more likely to return `NEEDS_APPROVAL` in v2.

## 5) Safeguards and Operational Impact

- Default remains v1 unless v2 is explicitly selected.
- Invalid `policy_pack` inputs return blocked validation-safe responses.
- Connector request sanitization runs before adapter execution.
- Invalid connector inputs emit both audit and observability evidence and remain dry-run.
- Hardening introduces no real external side effects.

Recommended rollout sequence:

1. Run tests for v1/v2 compatibility and connector hardening.
2. Enable v2 for a controlled request subset.
3. Monitor audit + observability counters for decision deltas.
4. Roll back explicitly to v1 if needed.

