# Policy Pack v2

Policy pack v2 is an expanded, deterministic starter rule pack that lives under:

- `src/policy/rules/v2/base_v2.rego`
- `src/policy/rules/v2/shell_guard_v2.rego`
- `src/policy/rules/v2/network_egress_v2.rego`
- `src/policy/rules/v2/data_exfiltration_v2.rego`
- `src/policy/rules/v2/privileged_ops_v2.rego`
- `src/policy/rules/v2/production_change_v2.rego`

## Activation Model

- v2 is opt-in.
- Default runtime behavior remains on stable `v1`.
- Selection is explicit via:
  - `PolicyEngine(policy_pack="v2")`
  - `PolicyEngine.evaluate(..., policy_pack="v2")`
  - API request field `policy_pack: "v2"`
  - environment variable `SAFECORE_POLICY_PACK=v2`

If `policy_pack` is not explicitly selected, SafeCore uses `v1`.

## Design Goals

- Preserve existing SafetyDecision shape and thresholds.
- Keep behavior deterministic and explainable.
- Expand coverage without introducing side effects.
- Keep OPA optional with fallback parity in Python.

## v2 Coverage Highlights

- Stricter shell handling:
  - command chaining/redirection patterns (`&&`, `||`, `;`, `|`, `>`, `<`, `` ` ``, `$(`) are denied.
- Production mutations:
  - prod change operations without change-ticket metadata are denied.
  - prod change with ticket metadata still requires approval.
- Network egress and exfiltration:
  - suspicious outbound transfer markers are denied.
  - sensitive payload transfer signals to external destinations are denied.
- Unknown context:
  - missing action/tool context escalates to `NEEDS_APPROVAL`.

## Runtime Guarantees Unchanged

- Dry-run-only execution posture remains unchanged.
- `DENY` remains non-overridable.
- `NEEDS_APPROVAL` remains blocked unless explicitly approved.
- Escalation never authorizes execution.

