# Visual Story

SafeCore is a control layer for AI agents.

It sits between an agent and the tools or systems that agent wants to touch. Instead of going straight from model output to execution, the request is forced through explicit safety and control checks first.

## Why A Control Layer Exists

Modern agents can generate commands, API calls, and configuration changes quickly.

That speed is useful, but it also creates a real problem: without a control layer, the same system that plans an action can immediately try to execute it.

SafeCore changes that path.

It makes the action stop and answer a harder question first:

"Should this request be allowed at all?"

## Not Just Another Agent

SafeCore does not try to be the smartest planner in the room.

Its value is different:

- it evaluates risk before execution
- it keeps risky actions blocked until explicitly approved
- it denies clearly dangerous actions outright
- it preserves audit evidence around that decision

## Three Core Scenarios

### `ALLOW`

A safe low-risk action can move through the guarded path.

Current RC behavior: it still stays dry-run-only and returns a simulated execution result.

### `NEEDS_APPROVAL`

A risky action, such as a production-style change or suspicious outbound operation, does not auto-execute.

It stays blocked until an explicit `APPROVED` decision exists.

### `DENY`

A clearly dangerous action, such as a destructive privileged command, does not proceed.

It remains blocked and is not overridable through the normal approval path.

## Why This Matters In The Real World

In real systems, the hardest failures are often not "the model was wrong" but "the model was allowed to act without enough control."

SafeCore is meant to sit in that gap:

- between intent and execution
- between tool access and policy
- between risky requests and human review
- between action history and audit evidence

That is why the project reads as a security/control layer, not as another autonomous agent runtime.
