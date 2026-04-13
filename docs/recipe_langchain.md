# Recipe: LangChain Starter Integration

## What This Recipe Shows

This recipe shows the smallest practical way to put SafeCore in front of a LangChain-style tool call.

Status: baseline integration only.

## Where SafeCore Sits

```text
LangChain tool call -> SafeCoreLangChainToolAdapter -> GuardedExecutionService -> guarded result
```

SafeCore remains the decision boundary before connector execution.

## Minimal Setup Assumptions

- you are working in this repository
- dependencies are installed with `pip install -r requirements.txt`
- you want a starter recipe for the current `safe_http_status` path
- you understand that execution stays dry-run-first

## Minimal Integration Steps

1. create a `SafeCoreIntegrationBridge`
2. wrap it with `SafeCoreLangChainToolAdapter`
3. pass a narrow status-style request
4. inspect the guarded result rather than bypassing it

## Copy-Paste-Friendly Example

```python
from src.integrations import SafeCoreIntegrationBridge, SafeCoreLangChainToolAdapter

bridge = SafeCoreIntegrationBridge()
tool = SafeCoreLangChainToolAdapter(bridge, provider_id="openai_compatible")

result = tool.invoke(
    {
        "url": "http://127.0.0.1:8000/health",
        "method": "GET",
    }
)

guarded = result["guarded_result"]
print(guarded["policy_decision"]["decision"])
print(guarded["blocked"])
print(result["explanation"])
```

## Expected Outcome

For an allowlisted local `GET` request, you should see:

- decision: `ALLOW`
- blocked: `False`
- execution status remains dry-run-safe

Blocked cases should still return blocked-safe results, not silent execution.

## Current Boundaries

This recipe does not cover:

- full LangChain runtime coverage
- callback ecosystem integration
- production-grade deployment concerns
- enterprise support guarantees

It is a copy-paste-friendly starting point for the current RC/MVP validated core.
