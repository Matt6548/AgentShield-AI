# Professional Demo Pack

Use this pack when you want to show SafeCore to a technical reviewer in about one minute.

## One-Minute Demo Order

1. Show the safe action
2. Show the risky action
3. Show the denied action

That order works because it tells the full control story:

- SafeCore can allow low-risk behavior
- SafeCore can stop risky behavior pending approval
- SafeCore can deny dangerous behavior outright

## Exact Demo Command

```bash
python scripts/demo_smoke.py
```

## What To Say During The Demo

### 1) Safe Action

"This is a low-risk request. SafeCore returns `ALLOW`, but the repository still keeps execution in dry-run mode."

What the audience should notice:

- policy decision exists
- the action is not blocked
- execution still stays controlled

### 2) Risky Action

"This request crosses the risk threshold. SafeCore returns `NEEDS_APPROVAL`, and the action stays blocked until explicit approval exists."

What the audience should notice:

- risky requests do not auto-execute
- approval is a real gate, not a cosmetic status

### 3) Denied Action

"This is a clearly dangerous request. SafeCore returns `DENY`, and the request remains blocked."

What the audience should notice:

- dangerous actions are stopped outright
- `DENY` is non-overridable in the current model

## What The Viewer Should Understand After One Minute

- SafeCore is not an agent runtime
- SafeCore is a security/control layer around agent actions
- it creates an explicit `ALLOW / NEEDS_APPROVAL / DENY` path
- it preserves audit evidence
- current posture is intentionally RC/MVP and dry-run-only

## Short Spoken Script

"SafeCore sits between an AI agent and the tools it wants to use. The point is not to make the agent more capable. The point is to make execution controllable. In this demo, the first request is allowed, the second is held for approval, and the third is denied. That gives you a concrete security control layer for agent execution, with audit evidence, while the repository stays dry-run-only."
