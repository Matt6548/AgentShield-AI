# Security Policy

## Reporting a Vulnerability

If you believe you found a security issue, report it privately to the repository owner or maintainers before public disclosure.

Until a dedicated security contact is published, use a private maintainer contact route rather than opening a public issue for sensitive findings.
If you do not have a private contact path, open a minimal public issue requesting one without exploit details, secrets, or proof-of-concept payloads.

## In Scope

Reports are especially useful when they involve:

- bypass of `DENY` or `NEEDS_APPROVAL` protections
- execution escaping dry-run-only guarantees
- approval or escalation paths authorizing execution incorrectly
- broken contract validation causing unsafe execution
- audit integrity failures with security impact
- connector boundary or sanitization failures with real safety impact

## Out Of Scope

The current project is an RC-stage validated core, not a production platform.

Out-of-scope or lower-priority items include:

- missing enterprise integrations that are not implemented yet
- lack of production auth/authz stack
- lack of cloud deployment support
- requests for unsupported production guarantees
- non-security feature requests

## Responsible Disclosure

- do not publish exploit details before maintainers have time to review
- provide reproduction steps and affected files when possible
- avoid testing that creates real destructive side effects
- prefer the smallest safe reproduction that demonstrates the issue

## Current Maturity

SafeCore currently provides a dry-run-first security/control layer for agent execution.
It should be evaluated as an open-source RC/MVP validated core, not as a production-ready platform.

There is no bug bounty, no formal SLA, and no enterprise incident response promise in the current repository state.

