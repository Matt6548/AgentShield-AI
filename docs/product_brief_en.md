# SafeCore Product Brief

## What SafeCore Is

SafeCore is a security control layer for AI agents.

It sits between an agent and external tools or systems, evaluates risk, and decides whether an action should be allowed, held for approval, or denied before execution.

## Problem

Many agent systems can move too quickly from model output to tool execution.

That creates practical gaps:

- unsafe tool usage
- risky production-style changes without enough control
- weak approval boundaries
- missing audit evidence
- unclear ownership of execution risk

## Solution

SafeCore inserts explicit control layers into that path:

- policy evaluation
- data and tool safety checks
- approval gating for risky actions
- dry-run-only execution guard
- audit evidence and integrity verification

## First Practical Use Case

The clearest practical path in the current repository is the built-in safe HTTP status connector.

It allows one intentionally narrow integration pattern:

- `GET` only
- trusted local hosts only
- health/status/metadata/version-style paths only
- blocked-safe behavior for everything else

This matters because it shows how SafeCore can be placed in front of a real connector boundary today, not only described as an abstract control core.

## Three Decision States

### `ALLOW`

Low-risk actions can proceed through the guarded path.

Current RC behavior: execution remains `DRY_RUN_SIMULATED`.

### `NEEDS_APPROVAL`

Risky actions stay blocked until explicit `APPROVED` status exists.

### `DENY`

Clearly dangerous actions remain blocked and are not overridable through the normal approval path.

## Why It Matters

SafeCore is designed for the point where agent capability meets operational risk.

Its value is not "doing more" on behalf of the agent. Its value is making execution controllable, reviewable, and auditable before anything touches a real system.

## Current State

SafeCore should be evaluated as an open-source RC/MVP validated core.

It already demonstrates:

- a working guarded execution path
- a first practical allowlisted read-only HTTP status path
- deterministic `ALLOW / NEEDS_APPROVAL / DENY` behavior
- audit evidence and integrity checks
- a runnable demo path
- documented release-readiness and open-source posture

It should not be described as a production-ready platform.

## What Is Included

- Policy Engine
- Data Guard
- Tool Guard
- Execution Guard
- Approval Layer
- Audit Layer
- Model Router foundation
- Connector boundary hardening
- API skeleton
- Prompt pack artifacts
- demo and release/public documentation

## What Is Intentionally Not Included Yet

- production auth/authz
- real external connector side effects
- database persistence
- cloud deployment stack
- UI portal
- enterprise operating depth beyond the current validated core
