# Why SafeCore

SafeCore solves one practical problem: AI agents can plan actions quickly, but without a control layer they can move from model output to execution with weak visibility and weak safety boundaries.

## What Problem SafeCore Solves

Without an explicit control layer, an agent can:

- call tools without a clear decision boundary
- trigger risky actions without visible approval state
- leave weak audit evidence behind
- make outcomes harder to explain after the fact

SafeCore inserts a guarded layer between agent intent and action execution.

## Why AI Agents Need A Control Layer

The issue is not only whether a model is correct.

The bigger issue is whether the system is allowed to act before anyone can see:

- what the action is
- how risky it is
- whether approval is needed
- what evidence remains after the decision

SafeCore is designed to make that control boundary explicit.

## What SafeCore Adds

### Guarded decisions

SafeCore returns an explicit outcome before execution:

- `ALLOW`
- `NEEDS_APPROVAL`
- `DENY`

### Approval visibility

Risky actions do not silently blend into normal execution. The system makes approval-oriented states visible in the guarded result and the product shell.

### Audit evidence

SafeCore preserves audit and history signals so a developer or operator can inspect what happened instead of guessing later.

### Plain-language explanation

The product shell and advisory layer can explain, in simple language, why an action was allowed, held for approval, or blocked.

## What SafeCore Is Not

SafeCore is not:

- another agent runtime
- a replacement for your application or framework
- a production-ready enterprise platform

In short: not another agent runtime, and not a production-ready enterprise platform.

It should be evaluated honestly as an open-source RC/MVP validated core with a usable product shell and baseline integrations.

See also [with_vs_without_safecore.md](with_vs_without_safecore.md).
