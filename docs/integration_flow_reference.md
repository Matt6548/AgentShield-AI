# Integration Flow Reference

## One Clean Reference Flow

The current developer starter flow is:

```text
app or agent
  ->
SafeCore API
  ->
policy / guards / approval
  ->
safe_http_status connector
  ->
audit + guarded result
```

If you prefer a more explicit view:

```text
app or agent
  ->
POST /v1/guarded-execute
  ->
PolicyEngine
  ->
DataGuard
  ->
ToolGuard
  ->
Approval gate
  ->
Connector boundary
  ->
ExecutionGuard
  ->
AuditLogger + integrity check
  ->
response
```

## Step-By-Step

### 1. App or agent creates a request

Your app packages one connector intent into a SafeCore request.

For the current starter path that means:

- `tool = safe_http_status`
- `method = GET`
- a trusted local URL

### 2. SafeCore receives the request

The current API entrypoint is:

```text
/v1/guarded-execute
```

SafeCore turns that input into a guarded evaluation path instead of letting the connector run directly.

### 3. Policy decides the high-level risk posture

Policy determines whether the request should be:

- allowed
- held for approval
- denied

For the current starter path, the intended good case is a trusted local read-only status fetch.

### 4. Data and tool guards check local safety boundaries

Data Guard checks payload sensitivity.

Tool Guard checks whether the requested tool path is safe enough to proceed.

For the starter path, that means:

- `GET` only
- no broad HTTP execution
- no unsafe host or method

### 5. Approval remains explicit

If the request lands in `NEEDS_APPROVAL`, it stays blocked until there is explicit `APPROVED`.

Escalation alone never authorizes execution.

### 6. Connector boundary runs the narrow path

If the request is allowed and still within the current safe boundary, the connector path runs.

Today, the connector example is intentionally narrow:

- allowlisted read-only HTTP/status fetches only

### 7. Execution guard preserves the current posture

The repository remains dry-run-first.

Even when the connector path is permitted, the broader project posture does not turn into a production execution platform.

### 8. Audit and result are returned

The response includes:

- policy decision
- blockers
- approval status
- connector execution status
- execution status
- audit evidence
- audit integrity status

## Why This Reference Matters

This flow gives a developer one clear mental model:

SafeCore is the boundary before the connector, not an after-the-fact logger around connector execution.

That is the correct way to understand and adopt the current project.
