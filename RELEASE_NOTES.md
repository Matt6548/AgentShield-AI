# SafeCore v0.1.0 — First Public OSS RC/MVP Release

## Release Summary

SafeCore is now packaged for its first public GitHub release as an open-source RC/MVP validated core for guarded AI agent execution.

This release includes a local product shell, one practical safe connector path, baseline integrations, and an advisory-only Safety Copilot. It should be evaluated as a strong control layer for AI agents, not a production-ready enterprise platform.

## Highlights In This Release

- explicit `ALLOW` / `NEEDS_APPROVAL` / `DENY` decisions
- dry-run-first guarded execution posture
- local product shell with onboarding, run history, approval visibility, and audit viewer
- one practical safe integration path through the allowlisted read-only HTTP status connector
- baseline provider gateway and framework adapters
- advisory-only Safety Copilot for plain-language operator guidance

## What You Can Evaluate Today

- how SafeCore sits between an agent and external connector boundaries
- how explicit safety decisions appear before execution
- how blocked and approval-oriented flows surface in the product shell
- how audit signals and run history make decisions easier to inspect
- how baseline integrations and provider metadata are exposed without leaking secrets

## First Recommended Demo Flow

1. Install dependencies: `pip install -r requirements.txt`
2. Start the UI: `uvicorn src.api.app:app --reload`
3. Open `http://127.0.0.1:8000/ui`
4. Complete onboarding
5. Run the first practical integration path:
   - `allowlisted_get`
   - `blocked_host`
   - `blocked_method`
6. Review run history and audit viewer

## Current Boundaries

SafeCore is:

- an open-source security/control layer for AI agents
- an RC/MVP validated core
- a local product shell for evaluation and demo
- a baseline integration surface for guarded adoption

SafeCore is not:

- a production-ready enterprise platform
- another agent runtime
- a generic arbitrary execution layer
- a cloud control plane

## Key Links

- README: [README.md](README.md)
- Open-source release pack M2: [docs/open_source_release_pack_m2.md](docs/open_source_release_pack_m2.md)
- GitHub About pack: [docs/github_about_pack.md](docs/github_about_pack.md)
- Public launch pack: [docs/public_launch_pack.md](docs/public_launch_pack.md)
- First practical use case: [docs/first_use_case.md](docs/first_use_case.md)
- Product shell guide: [docs/product_shell_user_guide.md](docs/product_shell_user_guide.md)
