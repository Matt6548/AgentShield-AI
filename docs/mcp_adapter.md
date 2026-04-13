# MCP Adapter

## Status

Baseline support only.

This is a minimal MCP-style proxy boundary, not a full MCP server implementation.

## What Exists Now

Current adapter:

- `src/integrations/mcp_adapter.py`

Main class:

- `SafeCoreMcpBoundary`

## Integration Shape

```text
MCP-style tool call -> SafeCoreMcpBoundary -> GuardedExecutionService -> guarded result
```

## Minimal Example

```python
from src.integrations import SafeCoreIntegrationBridge, SafeCoreMcpBoundary

bridge = SafeCoreIntegrationBridge()
boundary = SafeCoreMcpBoundary(bridge, provider_id="openai_compatible")

result = boundary.handle_tool_call(
    "safe_http_status",
    {
        "url": "http://127.0.0.1:8000/health",
        "method": "GET",
    },
)

print(result["guarded_result"]["policy_decision"]["decision"])
print(result["explanation"])
```

## Why This Matters

Many real adoption paths need a small proxy boundary rather than a full framework rewrite.

This adapter shows how to keep:

- tool mediation
- guarded decisions
- approval visibility
- audit visibility

inside SafeCore.

## What It Does Not Do

- it does not expose a full MCP transport/server
- it does not claim complete MCP ecosystem compatibility
- it does not bypass SafeCore for convenience
