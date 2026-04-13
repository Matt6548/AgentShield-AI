# Product User Flow

## Simple User Path

The current reference product flow is deliberately small:

1. the user chooses a simple status-check task
2. the app turns that into a SafeCore action request
3. the request goes through SafeCore
4. SafeCore returns a guarded result
5. the user sees why the action was allowed or blocked

## Where SafeCore Adds Value

The important boundary is:

```text
user or app
  ->
SafeCore
  ->
safe_http_status connector
  ->
guarded result
```

SafeCore is the layer in the middle that protects the connector path.

## The Three Product Scenarios

### 1. Allowed Flow

User intent:

- check trusted local service health

What happens:

- request stays inside the allowlisted read-only boundary
- SafeCore returns `ALLOW`
- connector path is permitted
- audit evidence is recorded

What the user sees:

- allowed result
- low risk score
- connector status
- audit status

### 2. Blocked Host Flow

User intent:

- check status on an untrusted host

What happens:

- SafeCore recognizes the host is not allowlisted
- request is blocked-safe
- connector path does not proceed

What the user sees:

- blocked result
- decision and risk score
- short explanation of why it was blocked

### 3. Blocked Method Flow

User intent:

- use a non-GET method for a status-style request

What happens:

- SafeCore enforces the read-only boundary
- request is blocked-safe
- no widened connector behavior is allowed

What the user sees:

- blocked result
- reason tied to method safety
- no fake success state

## Why This Matters

This product flow shows something concrete:

- SafeCore is not only a demo core
- it already protects one real connector boundary
- a user can understand the value in a few minutes

That is enough to make the project feel product-shaped without overstating maturity.
