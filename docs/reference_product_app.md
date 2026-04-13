# Reference Product App

## What This Is

The reference product app is a minimal local product shell built on top of the current SafeCore core.

It does not replace SafeCore.

It shows how SafeCore looks when it is used as a real control layer between a user-facing task and a connector path.

## Why It Exists

SafeCore already had:

- guarded core logic
- a local demo UI
- a first practical connector path

This reference product app turns those pieces into a more product-shaped experience:

- a user chooses a simple task
- the task becomes a SafeCore request
- SafeCore evaluates it
- the user sees a clear guarded result

## What It Shows

The current reference product app demonstrates one narrow workflow:

- safe read-only status or health check through the existing `safe_http_status` path

It also shows two blocked cases:

- unknown host
- unsafe method

That gives a complete minimal product story:

- allowed path
- blocked path because of destination
- blocked path because of method

## How To Run It

1. Start the local API and UI:

```bash
uvicorn src.api.app:app --reload
```

2. Open:

```text
http://127.0.0.1:8000/ui
```

3. Go to:

```text
Reference Product Flow
```

4. Run:

- `safe_status_check`
- `blocked_external_status`
- `blocked_unsafe_status_method`

## What To Verify

For each run, check:

- decision
- risk score
- blocked
- approval status
- connector status
- execution status
- audit integrity
- audit path
- short explanation

## What Is Useful Already

This app already makes the project more usable for two audiences:

- a developer can see how to place SafeCore in front of a connector boundary
- a product viewer can understand the value without reading the whole repository first

It is practical because it shows one real user path, not just architecture language.

## Honest Limitations

This remains:

- open-source RC/MVP
- validated core
- dry-run-first
- not a production-ready platform

It does not add:

- production auth/authz
- broad connector execution
- destructive side effects
- enterprise platform depth

That narrowness is intentional.
