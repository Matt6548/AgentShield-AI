# Safe HTTP Connector Example

SafeCore now includes one intentionally narrow practical integration path: an allowlisted read-only HTTP status connector.

## What It Is

This connector shows how to place SafeCore in front of one real integration path without turning the project into a generic HTTP executor.

It is designed for:

- local service health checks
- internal-style status endpoints
- read-only metadata fetches from trusted local endpoints

## What It Can Do

- accept `GET` only
- allow explicit trusted local hosts only: `localhost`, `127.0.0.1`
- allow health/status/metadata/version-style paths only
- pass through the current guarded flow:
  - policy
  - data guard
  - tool guard
  - approval logic
  - connector boundary
  - execution guard
  - audit evidence

## What It Does Not Do

- no arbitrary outbound HTTP
- no `POST`, `PUT`, `PATCH`, or `DELETE`
- no broad universal connector behavior
- no production auth/authz
- no destructive side effects
- no production-ready claim

## How To Run It Locally

1. Start the local SafeCore API:

```bash
uvicorn src.api.app:app --reload
```

2. Open the local UI:

```text
http://127.0.0.1:8000/ui
```

3. In the `Safe Integration Example` section, run:

- `allowlisted_get`
- `blocked_host`
- `blocked_method`

The default safe example fetches the local SafeCore health endpoint:

```text
GET http://127.0.0.1:8000/health
```

## Expected Behavior

- `allowlisted_get`
  - policy: `ALLOW`
  - connector: `SAFE_READ_ONLY_FETCHED`
  - execution guard: still `DRY_RUN_SIMULATED`

- `blocked_host`
  - policy/tool path: blocked-safe
  - connector does not proceed to an untrusted destination

- `blocked_method`
  - policy/tool path: blocked-safe
  - non-`GET` method is rejected

## Why This Matters

Before this example, SafeCore could already show guarded control logic in demo form.

This connector makes the practical use path clearer:

- a developer can see one real integration boundary
- SafeCore stays in front of that boundary
- only the explicitly allowlisted read-only path is permitted

That makes the repository more than an abstract control core, while still keeping it honest:

- open-source RC/MVP
- validated core
- dry-run-first execution posture
- not a production-ready platform
