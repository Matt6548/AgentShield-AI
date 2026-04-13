# Recipe: OpenAI-Compatible Local Starter Path

## What This Recipe Shows

This recipe shows how to represent a local or self-hosted OpenAI-compatible provider safely in backend setup while keeping SafeCore as the control layer before connector actions.

Status: baseline integration only.

## Where SafeCore Sits

```text
app or agent -> model/provider backend -> SafeCore -> connector boundary -> guarded result
```

The provider gateway describes backend provider status and request specs. SafeCore still owns the guarded decision before tool or connector execution.

## Minimal Setup Assumptions

- you have a local or self-hosted OpenAI-compatible endpoint
- you can set backend environment variables
- you want a safe backend bridge, not arbitrary browser-side model execution

Recommended environment variables:

```text
SAFECORE_OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:11434/v1
SAFECORE_OPENAI_COMPATIBLE_API_KEY=optional-token
```

## Minimal Integration Steps

1. configure the backend environment
2. create a `SafeCoreIntegrationBridge`
3. inspect the safe provider snapshot
4. build backend request specs from the provider gateway
5. keep real-world connector actions behind SafeCore guarded requests

## Copy-Paste-Friendly Example

```python
from src.integrations import SafeCoreIntegrationBridge, build_safe_http_status_request

bridge = SafeCoreIntegrationBridge()

provider = bridge.provider_snapshot("openai_compatible")
print(provider["configured"])
print(provider["base_url_status"])

request_spec = bridge.provider_gateway.build_request_spec(
    "openai_compatible",
    path="/chat/completions",
    body={
        "model": "local-model",
        "messages": [{"role": "user", "content": "Summarize current service health."}],
    },
)
print(request_spec["method"])
print(request_spec["url"])

guarded = bridge.execute(
    build_safe_http_status_request(
        url="http://127.0.0.1:8000/health",
        run_id="local-compatible-safe-http",
        actor="developer.local",
    )
)
print(guarded["policy_decision"]["decision"])
print(guarded["connector_execution"]["status"])
```

## Expected Outcome

You should be able to:

- confirm that the OpenAI-compatible backend bridge is configured safely
- build a backend request spec without exposing raw secrets
- keep connector actions behind SafeCore and receive a guarded result

## Current Boundaries

This recipe does not provide:

- arbitrary model execution through the UI
- a production secrets platform
- full provider orchestration
- production guarantees for local or self-hosted providers

It is a starter recipe for local adoption around the current validated core.
