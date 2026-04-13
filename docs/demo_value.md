# Demo Value

SafeCore is not "just another agent." It is the control layer that sits between an agent and tools or external systems and decides whether an action should be allowed, blocked, or held for approval before execution.

## What the Demo Shows

- low-risk action -> allowed in dry-run mode
- medium/high-risk action -> `NEEDS_APPROVAL` and stays blocked
- dangerous action -> `DENY` and stays blocked

In 30 seconds, a user can understand that SafeCore is about control, not autonomous execution:

- it inspects intent before execution
- it applies policy and guard checks
- it preserves audit evidence
- it keeps risky actions from silently running

## Why This Matters

Without a control layer, an agent can go directly from model output to tools. SafeCore inserts explicit policy, data, tool, approval, execution, routing, and audit boundaries in that path.

For the exact run commands, see `docs/demo_quickstart.md`.
For the compact scenario matrix, see `docs/demo_scenarios.md`.

## What Is Intentionally Not Included Yet

- real external connector side effects
- production auth/authz
- cloud deployment stack
- UI portal
- any runtime change beyond the existing RC-safe dry-run posture
