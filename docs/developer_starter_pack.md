# Developer Starter Pack

## What SafeCore Is For Developers

SafeCore is the control layer you place between an agent-style application and the connector path that would otherwise execute directly.

Its job is not to replace your app or agent runtime.

Its job is to evaluate the request before execution and return a guarded result:

- `ALLOW`
- `NEEDS_APPROVAL`
- `DENY`

That makes SafeCore useful when you want one explicit place for policy, guards, approval, audit, and blocked-path behavior.

## Where To Place SafeCore In A Workflow

The minimal placement looks like this:

```text
app or agent
  ->
SafeCore
  ->
connector boundary
  ->
guarded result
```

In the current repository, the clearest example is:

```text
app or agent
  ->
SafeCore
  ->
safe_http_status connector
  ->
allowed or blocked result
```

The important rule is simple:

your app should not call the connector directly when you want SafeCore to be the control boundary.

## Minimal Integration Pattern

The minimum useful pattern is:

1. Build a request with:
   - `run_id`
   - `actor`
   - `action`
   - `tool`
   - `params`
   - `target`
   - `payload`
2. Send it through SafeCore.
3. Read the guarded response:
   - decision
   - blockers
   - connector status
   - execution status
   - audit evidence

For the current starter path, `tool` is:

```text
safe_http_status
```

## How The Current Safe HTTP Example Maps To A Real Workflow

A simple real workflow is:

- an internal app wants service health or status
- the app asks SafeCore to fetch that status
- SafeCore checks whether the request is narrow and trusted
- SafeCore allows or blocks it
- the result is returned with audit evidence

That makes the current example useful for:

- internal health/status checks
- trusted local metadata reads
- early adoption of SafeCore in front of one real connector path

## What Is Allowed

The current starter path allows only:

- `GET`
- allowlisted local hosts
- allowlisted read-only paths:
  - `/health`
  - `/status`
  - `/metadata`
  - `/version`

## What Is Intentionally Limited

The current starter path does not try to be broad.

It does not allow:

- arbitrary HTTP access
- non-`GET` methods
- unknown hosts
- production auth/authz
- destructive side effects
- generic connector execution

This is deliberate.

The goal is to make adoption easy without weakening the current RC/MVP posture.

## How To Start Locally In A Few Minutes

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the API and local UI:

```bash
uvicorn src.api.app:app --reload
```

3. Open:

```text
http://127.0.0.1:8000/ui
```

4. Go to:

```text
First Practical Integration Path
```

5. Run:

- `allowlisted_get`
- `blocked_host`
- `blocked_method`

## What A Developer Should Learn From This

After five minutes with this starter pack, a developer should understand:

- where SafeCore sits in a real workflow
- what the current control boundary looks like
- how a connector request becomes an allowed or blocked result
- how to start with one narrow practical path before expanding scope

## Current Honest Posture

This starter pack should still be read honestly:

- open-source
- RC/MVP
- validated core
- dry-run-first guarded execution
- not a production-ready platform
