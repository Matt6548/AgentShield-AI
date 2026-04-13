# SafeCore

SafeCore is a security control layer for AI agents: it sits between an agent and external tools, evaluates risk, and blocks unsafe actions before execution.

Project status: open-source RC/MVP, validated core, product shell included, not a production-ready platform.

## Why It Exists

Without a control layer, an agent can move too quickly from model output to tool execution.

SafeCore inserts explicit checks into that path:

`AI agent -> SafeCore -> policy / data / tool / approval / execution / audit controls -> guarded result`

SafeCore is not another agent runtime. It is the middleware around agent execution.

## What You Get Today

- explicit `ALLOW` / `NEEDS_APPROVAL` / `DENY` decisions
- dry-run-only guarded execution posture
- data, tool, approval, and audit controls
- local product shell UI with onboarding, history, approval visibility, and audit viewer
- one practical safe integration example: allowlisted read-only HTTP status checks
- provider gateway metadata plus baseline LangChain / LangGraph / MCP-style adapters
- public docs, release posture, and open-source governance files

## 30-Second Quickstart

Install and run the CLI demo:

```bash
pip install -r requirements.txt
python scripts/demo_smoke.py
```

You will see the three current decision states:

- `ALLOW`
- `NEEDS_APPROVAL`
- `DENY`

Expected output shape:

```text
[allow_case] decision=ALLOW risk_score=15 blocked=False approval_status=BYPASSED execution_status=DRY_RUN_SIMULATED audit_integrity=True audit=examples/demo_audit.log.jsonl
[approval_case] decision=NEEDS_APPROVAL risk_score=55 blocked=True approval_status=PENDING execution_status=BLOCKED audit_integrity=True audit=examples/demo_audit.log.jsonl
[deny_case] decision=DENY risk_score=90 blocked=True approval_status=NOT_APPLICABLE_DENY execution_status=BLOCKED audit_integrity=True audit=examples/demo_audit.log.jsonl
```

For the fastest local UI path, see [quickstart_3min.md](docs/quickstart_3min.md) and [first_run_checklist.md](docs/first_run_checklist.md).

## Local Product Shell

Run the local UI:

```bash
uvicorn src.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/ui
```

What you will see in the UI:

- project overview and architecture
- onboarding flow
- reference product flow
- first practical integration path
- run history
- approval visibility
- audit viewer
- provider status / configuration

## First Practical Use Case

The clearest practical use case today is the built-in safe HTTP status path.

SafeCore can already sit in front of one real connector boundary and allow only a narrow, read-only request shape:

- `GET` only
- `localhost` / `127.0.0.1` only
- health/status/metadata/version-style paths only
- blocked-safe by default for unknown hosts or unsafe methods

In practice:

`AI agent -> SafeCore -> safe_http_status connector -> allowed or blocked result`

How to check it:

1. start the local UI
2. open `First Practical Integration Path`
3. run `allowlisted_get`
4. compare it with `blocked_host` and `blocked_method`

This is intentionally narrow and safe. It is not a universal HTTP executor and it does not change the current RC/MVP posture.

See [first_use_case.md](docs/first_use_case.md) and [safe_http_connector_example.md](docs/safe_http_connector_example.md).

## Developer Starter Pack

If you want to place SafeCore in a real workflow as a developer, start here:

- [developer_starter_pack.md](docs/developer_starter_pack.md)
- [integration_flow_reference.md](docs/integration_flow_reference.md)
- [copy_paste_integration_example.md](docs/copy_paste_integration_example.md)

These docs turn the current `safe_http_status` path into a practical adoption path.

## Reference Product App

SafeCore also includes a minimal local reference product app flow on top of the same safe connector path.

Use it to see:

- a simple user task become an action request
- SafeCore evaluate that request before connector execution
- a guarded result with decision, risk, approval, and audit context

See [reference_product_app.md](docs/reference_product_app.md) and [product_user_flow.md](docs/product_user_flow.md).

## Product Shell Features

The local UI already behaves like a minimal product shell on top of the current validated core.

It includes:

- overview
- onboarding
- run history
- approval visibility
- audit viewer
- provider status guidance

See [productization_pack_a.md](docs/productization_pack_a.md), [productization_pack_b.md](docs/productization_pack_b.md), [productization_pack_m1.md](docs/productization_pack_m1.md), and [product_shell_user_guide.md](docs/product_shell_user_guide.md).

## Product Shell Onboarding

The `/ui` shell includes a lightweight onboarding flow for first-time users:

1. language
2. provider setup
3. first safe run
4. approval explanation
5. audit viewer

Onboarding progress is stored only in browser `localStorage`. It does not store keys or secrets.

See [productization_pack_m1.md](docs/productization_pack_m1.md).

## Multilingual Product Shell

The local shell supports three languages:

- English
- Russian
- Uzbek

The language switcher changes the product text layer only. It does not change policy behavior, guarded flow, or execution posture.

See [productization_pack_b.md](docs/productization_pack_b.md).

## Provider Status / Configuration

The shell includes a safe provider visibility layer for:

- OpenAI
- OpenAI-compatible bridge
- Claude
- OpenRouter
- Local / demo mode

It shows only safe fields such as:

- configured / not configured
- enabled / disabled
- masked key status
- backend env-based posture
- short safe how-to-enable guidance

It does not store keys in the browser, does not expose raw secrets, and does not turn SafeCore into a generic model execution platform.

See [provider_setup_guide.md](docs/provider_setup_guide.md) and [productization_pack_b.md](docs/productization_pack_b.md).

## Integrations Pack

SafeCore now includes a small integration layer for adoption inside external AI stacks.

Current additions:

- provider gateway abstraction
- OpenAI-compatible backend bridge with safe `base_url` support
- baseline LangChain wrapper
- baseline LangGraph node wrapper
- baseline MCP-style proxy boundary

These integrations are opt-in and conservative. They do not change core decisions or turn SafeCore into a new agent runtime.

Start with:

- [adoption_recipes.md](docs/adoption_recipes.md)
- [recipe_langchain.md](docs/recipe_langchain.md)
- [recipe_langgraph.md](docs/recipe_langgraph.md)
- [recipe_openai_compatible_local.md](docs/recipe_openai_compatible_local.md)
- [integrations_pack_n.md](docs/integrations_pack_n.md)
- [provider_gateway.md](docs/provider_gateway.md)
- [langchain_integration.md](docs/langchain_integration.md)
- [langgraph_integration.md](docs/langgraph_integration.md)
- [mcp_adapter.md](docs/mcp_adapter.md)

## Safety Copilot Advisory

SafeCore now also includes an optional advisory-only assistant path for the local product shell.

It can explain the latest guarded result in plainer language, but it cannot change the final decision.

Current posture:

- disabled by default
- minimized and redacted context only
- strict schema validation on assistant output
- advisory only, never authoritative

See [safety_copilot_advisory.md](docs/safety_copilot_advisory.md).

## Current Boundaries

SafeCore should be evaluated honestly as a strong open-source RC/MVP validated core.

Current boundaries:

- no production auth/authz
- no real destructive external side effects
- no cloud deployment stack
- no enterprise operator portal
- no arbitrary model execution platform
- no production-ready claim

## Who This Is For

- security engineers evaluating control layers for agent execution
- platform engineers who want explicit guarded flow boundaries
- AI/agent developers who need a safe execution gate before tools
- technical founders who want a credible safety/control layer around agent actions

## Project Status

SafeCore already includes:

- validated core controls
- a local product shell
- a first practical safe connector path
- public open-source governance files
- release-facing documentation for honest evaluation

SafeCore should not be described as a production-ready platform.

## Key Docs

Start here:

- 3-minute quickstart: [quickstart_3min.md](docs/quickstart_3min.md)
- First run checklist: [first_run_checklist.md](docs/first_run_checklist.md)
- Troubleshooting: [troubleshooting.md](docs/troubleshooting.md)
- Why SafeCore: [why_safecore.md](docs/why_safecore.md)
- With vs without SafeCore: [with_vs_without_safecore.md](docs/with_vs_without_safecore.md)
- Adoption recipes: [adoption_recipes.md](docs/adoption_recipes.md)
- Demo quickstart: [demo_quickstart.md](docs/demo_quickstart.md)
- Demo scenarios: [demo_scenarios.md](docs/demo_scenarios.md)
- Demo value: [demo_value.md](docs/demo_value.md)
- First use case: [first_use_case.md](docs/first_use_case.md)
- Developer starter pack: [developer_starter_pack.md](docs/developer_starter_pack.md)
- Reference product app: [reference_product_app.md](docs/reference_product_app.md)
- Product shell user guide: [product_shell_user_guide.md](docs/product_shell_user_guide.md)
- Open-source release pack M2: [open_source_release_pack_m2.md](docs/open_source_release_pack_m2.md)

Public-facing narrative and launch docs:

- Public positioning: [public_positioning.md](docs/public_positioning.md)
- Visual story: [visual_story.md](docs/visual_story.md)
- Architecture visual: [architecture_visual.md](docs/architecture_visual.md)
- Professional demo pack: [professional_demo_pack.md](docs/professional_demo_pack.md)
- Professional positioning: [professional_positioning.md](docs/professional_positioning.md)
- Product brief (EN): [product_brief_en.md](docs/product_brief_en.md)
- Product brief (RU): [product_brief_ru.md](docs/product_brief_ru.md)
- Presentation outline: [presentation_outline.md](docs/presentation_outline.md)
- NotebookLM source pack: [notebooklm_source_pack.md](docs/notebooklm_source_pack.md)
- Video script (EN, 90s): [video_script_en_90s.md](docs/video_script_en_90s.md)
- Video script (RU, 90s): [video_script_ru_90s.md](docs/video_script_ru_90s.md)

Launch assets:

- Release notes: [RELEASE_NOTES.md](RELEASE_NOTES.md)
- GitHub About pack: [github_about_pack.md](docs/github_about_pack.md)
- Public launch pack: [public_launch_pack.md](docs/public_launch_pack.md)

Project and community docs:

- Open-source scope: [open_source_scope.md](docs/open_source_scope.md)
- Handoff pack: [handoff_pack.md](docs/handoff_pack.md)
- Operations runbook: [operations_runbook.md](docs/operations_runbook.md)
- MVP scope: [mvp_scope.md](docs/mvp_scope.md)
- Support: [SUPPORT.md](SUPPORT.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security policy: [SECURITY.md](SECURITY.md)
- Roadmap: [ROADMAP.md](ROADMAP.md)
- License: [LICENSE](LICENSE)
