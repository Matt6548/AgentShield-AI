# Public Positioning

## Target Audience

- teams building AI agents that need control before tool execution
- security-minded engineers evaluating agent safety infrastructure
- technical reviewers who want to understand project value quickly from GitHub

## User Value In Plain Language

SafeCore helps answer a simple question: before an agent touches a tool or external system, who decides whether that action is safe enough to proceed?

SafeCore is that decision and control layer.

## What Problem This Solves

Without a control layer, an agent can move directly from model output to tool execution. That creates gaps around:

- unsafe tool usage
- risky production changes
- missing human approval
- weak auditability
- unclear policy boundaries

SafeCore inserts explicit checks into that path and keeps risky actions from silently running.

## What Is Intentionally Not Included Yet

- real external side effects
- production auth/authz stack
- cloud deployment stack
- UI portal
- anything beyond the current RC-frozen dry-run posture

## Best Public Entry Points

- `README.md`
- `docs/demo_quickstart.md`
- `docs/demo_scenarios.md`
- `docs/demo_value.md`
