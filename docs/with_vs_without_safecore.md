# With vs Without SafeCore

This comparison is meant to explain SafeCore quickly for a first-time visitor.

## Simple Comparison

| Without SafeCore | With SafeCore |
| --- | --- |
| The path from model output to action can be unclear. | The system passes through an explicit guarded boundary before action proceeds. |
| No clear decision boundary. | Explicit `ALLOW` / `NEEDS_APPROVAL` / `DENY` decision. |
| Human control can be vague or implicit. | Approval visibility is part of the guarded flow. |
| Outcomes can be hard to explain after the fact. | Plain-language explanation and traceability are available. |
| Action history may be weak or fragmented. | Audit and run history evidence stay visible in the product shell. |
| Risk can be hidden inside normal execution. | Risk is surfaced before execution. |

## What Changes In Practice

Without SafeCore:

- a tool call may look like a normal application step
- approval need can be unclear until after the attempt
- blocked vs allowed intent is harder to reason about

With SafeCore:

- the request is evaluated before connector execution
- the decision is visible immediately
- blocked and approval-oriented flows remain inspectable
- audit evidence and history stay attached to the run

## What This Comparison Does Not Claim

This comparison does not mean SafeCore is already:

- a production-ready enterprise platform
- a full cloud control plane
- another agent runtime

It means the repository already provides a clear control layer, a local product shell, and baseline integration paths for guarded adoption.
