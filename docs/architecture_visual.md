# Architecture Visual

SafeCore is easiest to understand as a guarded request path:

```text
AI Agent
  ->
SafeCore
  ->
Policy -> Data Guard -> Tool Guard -> Approval / Escalation
  -> Model Router -> Connector Boundary -> Execution Guard
  -> Audit -> Audit Integrity
  ->
Guarded Result
```

## What Each Layer Does

### Policy

Turns the incoming request into a decision shape:

- `ALLOW`
- `NEEDS_APPROVAL`
- `DENY`

It also assigns a risk score and reasons.

### Data Guard

Looks at payload content for sensitive material and suspicious outbound patterns.

Its job is to reduce accidental leakage before anything moves further.

### Tool Guard

Checks whether the requested tool or shell command is acceptable.

Its job is to stop obviously unsafe tool usage early.

### Approval / Escalation

Handles requests that should not proceed automatically.

Important current rule: escalation can change approval state and metadata, but it cannot authorize execution by itself.

### Model Router

Chooses a routing profile that matches the current decision context.

This is not about giving the agent more power. It is about keeping routing explicit and explainable.

### Connector Boundary

Normalizes and sanitizes connector requests and responses.

Current RC posture keeps this dry-run-safe and non-side-effecting.

### Execution Guard

Prevents unsafe execution paths and keeps the current repository in dry-run-only mode.

Even allowed requests do not become real destructive actions here.

### Audit + Audit Integrity

Records evidence of what happened and verifies that the audit chain remains intact.

This is part of the control story, not an afterthought.

## What A GitHub Reader Should Understand Quickly

- SafeCore is the middleware around agent execution.
- Its purpose is control, not autonomy.
- The project already demonstrates the guarded path.
- The current repository is an RC/MVP validated core, not a production-ready platform.
