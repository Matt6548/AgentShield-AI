# Public Launch Pack

## First Release Title Suggestion

`SafeCore v0.1.0 — First Public OSS RC/MVP Release`

## What SafeCore Is

An open-source RC/MVP validated core and product shell for guarded AI agent execution.

## What SafeCore Is Not

Not a production-ready enterprise platform, not another agent runtime, and not a generic arbitrary execution layer.

## First Release Body Draft

### What SafeCore Is

SafeCore is an open-source security/control layer for AI agents. It sits between agent intent and external execution, applies explicit safety checks, and returns a guarded result before action proceeds.

### What Is Included Now

- explicit `ALLOW` / `NEEDS_APPROVAL` / `DENY` decisions
- dry-run-first guarded execution posture
- local product shell with onboarding, history, approval visibility, and audit viewer
- safe provider visibility without secret leakage

### First Practical Use Case

The clearest practical use case today is the allowlisted read-only HTTP status path. SafeCore can already sit in front of one narrow connector boundary and allow only safe local `GET` requests for status-style paths while blocking unknown hosts and unsafe methods.

### Product Shell Highlights

The local UI shows project identity, onboarding, reference product flow, first practical integration path, run history, approval visibility, audit viewer, provider status, and advisory-only assistant visibility.

### Baseline Integrations

This release includes a baseline provider gateway plus baseline LangChain, LangGraph, and MCP-style adapter surfaces. They are intended as adoption helpers, not as a claim of full framework coverage.

### Advisory Copilot Note

The Safety Copilot is advisory-only. It can improve explanation quality and operator guidance when explicitly enabled, but it does not change or override final policy decisions.

### Honest Boundaries

SafeCore should be evaluated honestly as an open-source RC/MVP validated core. It is not a production-ready enterprise platform, not a cloud control plane, and not a new agent runtime.

### How To Try It Locally

```bash
pip install -r requirements.txt
uvicorn src.api.app:app --reload
```

Open `http://127.0.0.1:8000/ui`, complete onboarding, run the first practical integration path, and inspect run history plus audit viewer.

## Recommended Launch Sequence

1. Share the README first.
2. Point to the release notes.
3. Show the local UI and onboarding.
4. Run the first practical integration path.
5. Show run history and audit viewer.
6. Close with the honest scope and current boundaries.

## Recommended First Links To Share

- [README.md](../README.md)
- [RELEASE_NOTES.md](../RELEASE_NOTES.md)
- [docs/open_source_release_pack_m2.md](open_source_release_pack_m2.md)
- [docs/first_use_case.md](first_use_case.md)

## Recommended Screenshot Order

1. overview hero with project identity and status chips
2. onboarding flow
3. first practical integration path with allowed result
4. blocked host or blocked method comparison
5. run history and audit viewer
6. provider status section

## Recommended First Short Demo / Video Order

1. explain SafeCore in one sentence
2. show onboarding and overview
3. run the first practical integration path
4. compare it with a blocked case
5. open run history and audit viewer
6. close with the honest scope: RC/MVP validated core, not a production-ready enterprise platform
