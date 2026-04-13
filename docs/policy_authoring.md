# Policy Authoring UX Foundation

SafeCore now includes a deterministic policy authoring layer for local rule maintenance.

## Entry Points

- `src/policy/rule_registry.py`
- `src/policy/rule_linter.py`
- `src/policy/authoring.py`

## Capabilities

- Deterministic discovery of `src/policy/rules/*.rego`.
- Structured metadata loading (`# key: value` comment lines).
- Rule lint checks:
  - required `package safecore`
  - duplicate metadata `rule_id` values
  - ambiguous `rule_id` metadata in one file
  - forbidden unconditional allow patterns
- Fallback policy summary preview via `PolicyEngine.fallback_rule_summary()`.

## Programmatic Usage

```python
from src.policy.authoring import PolicyAuthoringService

service = PolicyAuthoringService()
rules = service.list_available_rules()
lint_report = service.lint_rules()
fallback_summary = service.preview_fallback_summary()
```

## CLI-Ready Usage

```bash
python -m src.policy.authoring list
python -m src.policy.authoring lint
python -m src.policy.authoring summary
```

Behavior:

- `lint` returns process exit code `1` when lint is invalid.
- `list` and `summary` return exit code `0` on success.

