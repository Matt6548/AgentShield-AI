# Open Source Scope

## License Posture

SafeCore is distributed under Apache 2.0.

Apache 2.0 is a permissive open-source license and fits the current project posture well:

- it keeps the repository easy to adopt and evaluate
- it is a strong default for an open security/control layer
- it matches the current goal of publishing a serious open-source RC/MVP validated core

## What Is Already Included

SafeCore is already usable as an open-source RC-stage validated core for guarded agent execution.

Included today:

- policy decision layer
- data and tool safety guards
- approval and escalation controls
- dry-run execution guard
- audit logging and integrity verification
- model routing foundation
- connector boundary hardening
- local product shell UI
- first practical safe integration path
- demo scenarios and public quickstart

## What "RC-Stage Validated Core" Means

It means the repository already demonstrates and tests the core safety posture:

- safe actions can pass
- risky actions can require approval
- dangerous actions are blocked
- execution remains dry-run-only
- audit evidence is preserved
- a new visitor can evaluate the project through the local product shell

This is a validated control layer, not a finished production platform.

## What Is Intentionally Not Included Yet

- production auth/authz
- real external connector side effects beyond the narrow safe example
- cloud deployment stack
- enterprise operational features beyond current RC scope
- production-ready guarantees

## Target Audience

- engineers building AI agents with tool access
- teams evaluating control layers for agent execution
- security reviewers who want explicit policy and audit boundaries
- product and platform evaluators who want a usable local reference shell

