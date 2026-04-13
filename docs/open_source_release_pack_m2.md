# Open-Source Release Pack M2

## What Is Ready Now

SafeCore is ready to be presented publicly as:

- an open-source project
- an RC/MVP validated core
- a security/control layer for AI agents
- a local product shell for evaluation and demo

A new visitor can already evaluate:

- explicit `ALLOW` / `NEEDS_APPROVAL` / `DENY` behavior
- dry-run-only guarded execution posture
- local product shell with onboarding, history, approval visibility, and audit viewer
- one practical integration path through the allowlisted read-only HTTP status connector
- safe provider visibility without secret leakage

## What Is Intentionally Out Of Scope

This release should be described honestly.

It is not:

- a production-ready platform
- a cloud control plane
- a new agent runtime
- a generic HTTP executor
- a production auth/authz system
- a full enterprise operator portal

## How To Evaluate SafeCore Quickly

Recommended first path:

1. install dependencies
2. run the local UI
3. finish the onboarding flow
4. run the first safe integration example
5. compare it with blocked cases
6. inspect run history and audit viewer

Commands:

```bash
pip install -r requirements.txt
uvicorn src.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/ui
```

## Recommended First Demo Flow

Use this order in the UI:

1. `Overview`
2. `Onboarding`
3. `Reference Product Flow`
4. `First Practical Integration Path`
5. `Product Shell`
6. `Run History`
7. `Approval And Audit`
8. `Provider Status`

This order shows both value and boundaries quickly.

## Safe Expectations For Users

Users should expect:

- a strong control core
- a usable local product shell
- explicit safety decisions before connector execution
- clear dry-run-first behavior
- local audit evidence

Users should not expect:

- real destructive execution
- enterprise support guarantees
- production-grade infrastructure
- arbitrary provider execution through the UI

## Release Notes Draft

Suggested draft notes for the public release:

- SafeCore is now packaged as a clearer open-source RC/MVP validated core for guarded agent execution.
- The repository includes a local product shell with onboarding, history, approval visibility, audit viewer, multilingual UI, and safe provider visibility.
- The first practical integration path is an allowlisted read-only HTTP status connector that demonstrates how SafeCore can sit in front of a real connector boundary.
- The release remains intentionally conservative: dry-run-first, no destructive external side effects, and no production-ready claims.

## Public Launch Checklist

Before publishing publicly, verify:

- README matches the current repository state
- community health files are present
- issue and PR templates reflect RC/MVP scope
- demo and UI quickstart steps still work
- docs do not claim production-ready behavior
- release-facing docs reference real existing files and endpoints only

## GitHub About Text Suggestions

Short About text:

`Security/control layer for AI agents. SafeCore evaluates tool requests before execution and keeps risky actions blocked by default.`

Alternative About text:

`Open-source RC/MVP validated core for guarded agent execution, with a local product shell and one safe practical integration path.`

## Project Description Suggestions

One-line description:

`SafeCore is a security control layer for AI agents that evaluates requests before tools are touched.`

Medium-length description:

`SafeCore is an open-source RC/MVP validated core for guarded agent execution. It sits between an AI agent and external tools, applies policy and guard checks, preserves approval and audit boundaries, and demonstrates one safe practical integration path through a local product shell.`

## Repo Topics / Tags Suggestions

Suggested repository topics:

- `ai-safety`
- `agent-security`
- `agent-controls`
- `policy-engine`
- `approval-workflow`
- `audit-trail`
- `dry-run`
- `open-source`
- `python`
- `security-middleware`

## Recommended Screenshots

If screenshots are added later, use this order:

1. overview hero with product identity and status chips
2. onboarding flow
3. reference product flow result
4. first practical integration path with allowed vs blocked cases
5. product shell summary and run history
6. approval and audit viewer
7. provider status cards

## Recommended First Public Video Order

For a short first video:

1. explain what SafeCore is in one sentence
2. show the UI overview
3. run the first safe reference flow
4. show a blocked host or blocked method case
5. open run history and audit viewer
6. show provider status and explain why keys stay in backend env only
7. close with the honest scope: RC/MVP validated core, not a production-ready platform

## Related Docs

- [README.md](../README.md)
- [RELEASE_NOTES.md](../RELEASE_NOTES.md)
- [docs/github_about_pack.md](github_about_pack.md)
- [docs/public_launch_pack.md](public_launch_pack.md)
- [docs/demo_quickstart.md](demo_quickstart.md)
- [docs/first_use_case.md](first_use_case.md)
- [docs/reference_product_app.md](reference_product_app.md)
- [docs/product_shell_user_guide.md](product_shell_user_guide.md)
- [docs/provider_setup_guide.md](provider_setup_guide.md)
- [docs/open_source_scope.md](open_source_scope.md)
