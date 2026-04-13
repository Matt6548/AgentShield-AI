# First Use Case: Safe HTTP Status Path

## What The Use Case Is

The first practical SafeCore use case is intentionally narrow:

- an agent wants to read service status
- the request goes through SafeCore first
- SafeCore allows only a trusted read-only HTTP path
- everything outside that narrow path is blocked-safe

In concrete terms, the current repository supports one guarded connector pattern:

`AI agent -> SafeCore -> safe_http_status connector -> allowed or blocked result`

This is the first real applied path in the project. It shows how SafeCore can sit in front of a connector boundary without turning into a generic execution platform.

## Why It Matters

Before this use case, SafeCore already demonstrated policy, approval, audit, and blocked-flow behavior.

This use case adds something more practical:

- a developer can see one real connector path
- the path is useful enough to understand immediately
- the connector is narrow enough to remain safe and honest
- the project now shows how SafeCore can be placed in front of a real integration boundary

That makes the repository easier to evaluate as a product-shaped control layer, not only as a demo core.

## What Is Allowed

The current safe HTTP connector allows only:

- `GET`
- trusted local hosts only:
  - `localhost`
  - `127.0.0.1`
- trusted read-only paths only:
  - `/health`
  - `/status`
  - `/metadata`
  - `/version`

Example allowed request:

```text
GET http://127.0.0.1:8000/health
```

## What Is Blocked

The connector blocks:

- non-allowlisted hosts
- non-`GET` methods such as `POST`, `PUT`, `PATCH`, `DELETE`
- arbitrary outbound HTTP access
- requests that try to repurpose the connector into a generic HTTP executor

Example blocked requests:

```text
GET http://example.com/health
POST http://127.0.0.1:8000/health
```

## How To Run It Locally

1. Start the local API and UI:

```bash
uvicorn src.api.app:app --reload
```

2. Open the UI:

```text
http://127.0.0.1:8000/ui
```

3. Go to:

```text
First Practical Integration Path
```

4. Run the three built-in examples:

- `allowlisted_get`
- `blocked_host`
- `blocked_method`

## How To Verify Behavior

What you should see:

- `allowlisted_get`
  - decision: `ALLOW`
  - connector status: `SAFE_READ_ONLY_FETCHED`
  - execution: still `DRY_RUN_SIMULATED`

- `blocked_host`
  - blocked result
  - untrusted destination does not proceed

- `blocked_method`
  - blocked result
  - non-`GET` method does not proceed

You should also see:

- audit evidence path
- decision state
- risk score
- blocked / not blocked status
- approval status
- audit integrity state

## Where To Place SafeCore In A Real Workflow

The practical placement is:

```text
AI agent
  ->
SafeCore
  ->
safe_http_status connector
  ->
allowlisted read-only HTTP status fetch
  ->
guarded result
```

The important point is that the connector is not called directly by the agent.

SafeCore remains in front of it and controls whether the request is:

- allowed
- held
- blocked

## Honest Limitations

This use case is intentionally narrow.

It does not make the repository a production-ready platform.

Current boundaries still apply:

- open-source RC/MVP
- validated core
- not a production-ready platform
- dry-run-first guarded execution
- no production auth/authz
- no full external connector platform
- no destructive external side effects
- no generic arbitrary HTTP executor

That is the correct scope for the current repository state.
