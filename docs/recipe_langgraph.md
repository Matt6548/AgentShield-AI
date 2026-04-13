# Recipe: LangGraph Starter Integration

## What This Recipe Shows

This recipe shows how to place SafeCore inside one graph step so that a state transition stays behind the guarded decision boundary.

Status: baseline integration only.

## Where SafeCore Sits

```text
LangGraph state -> SafeCoreLangGraphNode -> GuardedExecutionService -> state patch with guarded result
```

SafeCore still sits between graph intent and connector execution.

## Minimal Setup Assumptions

- you are using the repository-local baseline adapters
- you want one narrow guarded node, not a full graph runtime integration
- you are testing the current safe HTTP status path

## Minimal Integration Steps

1. create a `SafeCoreIntegrationBridge`
2. create a `SafeCoreLangGraphNode`
3. pass a state object with URL and method
4. consume the guarded patch in the next graph step

## Copy-Paste-Friendly Example

```python
from src.integrations import SafeCoreIntegrationBridge, SafeCoreLangGraphNode

bridge = SafeCoreIntegrationBridge()
node = SafeCoreLangGraphNode(bridge, provider_id="openai_compatible")

patch = node(
    {
        "run_id": "graph-safe-http",
        "actor": "graph-user",
        "url": "http://127.0.0.1:8000/health",
        "method": "GET",
    }
)

print(patch["safecore_result"]["policy_decision"]["decision"])
print(patch["safecore_explanation"])
```

## Expected Outcome

For the safe local `GET` path, the patch should include:

- a guarded result under `safecore_result`
- a plain-language explanation under `safecore_explanation`
- optional provider metadata if you requested a provider snapshot

## Current Boundaries

This recipe does not cover:

- full LangGraph orchestration support
- graph persistence
- custom state persistence strategies
- production-ready LangGraph support

It is a reference integration path for the current SafeCore RC/MVP posture.
