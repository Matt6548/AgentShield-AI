# Presentation Outline

## Slide 1: SafeCore

- Security control layer for AI agents
- Sits between agent output and tool execution
- Built as an open-source RC/MVP validated core

Speaker note: Start with identity. SafeCore is not an agent runtime; it is the control layer around agent execution.

## Slide 2: The Problem

- Agents can move too quickly from intent to execution
- Tool access without control creates operational risk
- Policy, approval, and audit are often missing from the execution path

Speaker note: Frame the problem as uncontrolled execution, not as generic AI risk.

## Slide 3: High-Level Architecture

- AI Agent -> SafeCore -> guarded result
- Policy, Data Guard, Tool Guard, Approval, Execution Guard, Audit
- Model routing and connector boundaries stay explicit

Speaker note: Keep the architecture simple and readable. The audience should understand the control path in one glance.

## Slide 4: Three Decision States

- `ALLOW` for low-risk actions
- `NEEDS_APPROVAL` for risky actions that must stay blocked
- `DENY` for dangerous actions that must not proceed

Speaker note: This is the core operating model. The project becomes easy to understand once these three states are clear.

## Slide 5: Demo Path

- Run `python scripts/demo_smoke.py`
- Show safe action
- Show risky action
- Show denied action
- Then open the UI and run the first practical use case:
  - `allowlisted_get`
  - `blocked_host`
  - `blocked_method`

Speaker note: The demo proves two things: the core three-state model is runnable, and the repository already includes one real narrow connector path that developers can evaluate today.

## Slide 6: Current Maturity and Open-Source Posture

- RC/MVP validated core
- dry-run-only execution posture
- not a production-ready platform
- release and signoff artifacts already documented

Speaker note: Be explicit about maturity. Honest scope increases credibility.

## Slide 7: Roadmap

- deepen policy coverage
- move from dry-run foundations toward safer execution paths
- strengthen operational and deployment maturity over time

Speaker note: Show direction without promising enterprise completeness today.

## Slide 8: Closing / Call To Action

- evaluate the guarded path
- run the demo locally
- review the docs and tests
- contribute or open discussion around control-layer use cases

Speaker note: Close with action. The message is: this is a serious open-source core worth evaluating now.
