# Copy-Paste Integration Example

This is the smallest practical shape for routing one request through SafeCore.

It is intentionally short and aligned with the current safe posture.

## Minimal Request Example

```python
from src.api.service import GuardedExecutionService

service = GuardedExecutionService()

request = {
    "run_id": "starter-http-status-001",
    "actor": "developer.local",
    "action": "fetch_status",
    "tool": "safe_http_status",
    "command": "GET",
    "target": "http://127.0.0.1:8000/health",
    "params": {
        "method": "GET",
        "url": "http://127.0.0.1:8000/health",
        "timeout_seconds": 2,
    },
    "payload": {},
    "dry_run": True,
}

result = service.execute_guarded_request(request)

print(result["policy_decision"]["decision"])
print(result["connector_execution"]["status"])
print(result["execution_result"]["output"]["status"])
print(result["audit_integrity"]["valid"])
```

## What This Shows

- your app sends one connector intent through SafeCore
- SafeCore evaluates it before execution
- the connector path is allowed only if it stays within the narrow safe HTTP boundary
- the result comes back with audit and decision context

## Expected Good-Case Outcome

For an allowlisted local `GET` health request, you should expect:

- decision: `ALLOW`
- connector status: `SAFE_READ_ONLY_FETCHED`
- execution status: `DRY_RUN_SIMULATED`

## Expected Blocked Cases

These shapes should not proceed:

```python
# unknown host
"target": "http://example.com/health"

# unsafe method
"command": "POST"
```

## When To Use This Pattern

Use this pattern when you want to:

- put SafeCore in front of a read-only status path
- demonstrate connector-boundary control locally
- start from one narrow real workflow before expanding scope

## What This Example Is Not

This is not:

- a universal HTTP client
- a production-ready connector platform
- a replacement for auth/authz, deployment, or enterprise governance

It is a starter integration example for the current RC/MVP validated core.
