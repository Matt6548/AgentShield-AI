# LangGraph Integration

## Status

Baseline support only.

This package adds a minimal node wrapper, not full LangGraph orchestration support.

## What Exists Now

Current adapter:

- `src/integrations/langgraph_adapter.py`

Main class:

- `SafeCoreLangGraphNode`

## Integration Shape

```text
LangGraph state -> SafeCoreLangGraphNode -> GuardedExecutionService -> state patch with guarded result
```

## Minimal Example

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

## Why This Matters

This shows exactly where SafeCore should sit in a graph-style workflow:

`graph node input -> SafeCore -> guarded decision -> next state`

## What It Does Not Do

- it does not implement a full LangGraph runtime
- it does not add graph persistence or orchestration features
- it does not claim production-ready LangGraph support
