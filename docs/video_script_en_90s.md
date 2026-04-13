# 90-Second Video Script (EN)

AI agents can move fast from model output to tool execution.

That speed is useful.

But without control, it also creates risk.

SafeCore is the layer that sits between an agent and the tools it wants to use.

It evaluates the request before execution.

It applies policy.

It checks data and tool safety.

It can require approval.

It preserves audit evidence.

And it keeps the current execution posture dry-run-only.

SafeCore works around three decision states.

`ALLOW` means a low-risk action can proceed through the guarded path.

`NEEDS_APPROVAL` means the action stays blocked until there is explicit approval.

`DENY` means the action is too dangerous and does not proceed.

Why does that matter?

Because the hardest problem in agent systems is not only planning.

It is control.

Who decides whether an action should actually happen?

Where does approval live?

Where is the audit trail?

SafeCore is built to answer those questions clearly.

Today, the project should be evaluated as an open-source RC/MVP validated core.

It already provides a runnable demo path, a guarded execution model, and one practical narrow connector path:

an allowlisted read-only HTTP status flow for trusted local endpoints.

It is not a production-ready platform, and it does not claim to be one.

If you want to understand the project quickly, run the demo and follow the three outcomes:

allow,

needs approval,

and deny.

Then open the UI and run the first practical use case to see what SafeCore can already guard in a real connector path today.

That is SafeCore in one minute and a half.
