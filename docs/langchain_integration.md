# LangChain Integration

## Status

Baseline support only.

SafeCore does not claim full LangChain platform integration in this package.

## What Exists Now

Current adapter:

- `src/integrations/langchain_adapter.py`

Main class:

- `SafeCoreLangChainToolAdapter`

This wrapper lets a LangChain-style tool call go through SafeCore before connector execution.

## Integration Shape

```text
LangChain tool call -> SafeCoreLangChainToolAdapter -> GuardedExecutionService -> guarded result
```

## Minimal Example

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
```

## What It Preserves

- SafeCore still decides `ALLOW`, `NEEDS_APPROVAL`, or `DENY`
- dry-run-first posture remains unchanged
- audit and approval visibility remain available in the guarded result

## What It Does Not Do

- it does not replace LangChain
- it does not add a new planner or agent runtime
- it does not provide full callback ecosystem coverage
- it does not claim production-ready LangChain support
