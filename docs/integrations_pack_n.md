# Integrations Pack N

## Purpose

Package N makes SafeCore easier to adopt inside external AI stacks without changing core decision semantics.

This pack adds:

- a provider gateway abstraction
- an OpenAI-compatible bridge for backend-only provider request specs
- baseline framework adapters for LangChain, LangGraph, and an MCP-style boundary
- integration docs that explain what is supported now and what is still intentionally limited

## What Is Supported Now

Current baseline support includes:

- safe env-based provider config loading
- safe provider status metadata with no raw secret leakage
- OpenAI-style backend request spec generation with optional `base_url` override
- OpenRouter support through the same OpenAI-compatible bridge pattern
- minimal Anthropic metadata support
- lightweight framework wrappers that route requests through `GuardedExecutionService`

The adapters are intentionally small and opt-in.

They do not rewrite SafeCore and they do not bypass its guarded flow.

## What The Framework Adapters Actually Do

The current baseline adapters do one thing:

`external app or framework -> SafeCore wrapper -> GuardedExecutionService -> guarded result`

This means:

- SafeCore still decides `ALLOW`, `NEEDS_APPROVAL`, or `DENY`
- dry-run-first posture stays unchanged
- audit, approval, and blocked-path behavior remain visible

## Recommended First Integration Path

The first real integration path is still the narrow safe HTTP status flow:

`agent or app -> SafeCore -> safe_http_status -> guarded result`

Use that path first because it is:

- already implemented
- already tested
- already shown in the local UI
- narrow enough to stay honest and safe

## Baseline Support, Not Full Framework Support

The framework adapters in this package should be described as baseline support.

They are not:

- full LangChain platform support
- full LangGraph runtime orchestration
- a complete MCP server implementation
- a production provider orchestration platform

They are thin wrappers that show where SafeCore belongs in a real stack.

## Out Of Scope

This package does not add:

- destructive external execution
- cloud provider orchestration
- enterprise auth/authz
- assistant intelligence or a new model runtime
- fake claims of production-ready framework coverage

## Files To Start With

- [provider_gateway.md](provider_gateway.md)
- [langchain_integration.md](langchain_integration.md)
- [langgraph_integration.md](langgraph_integration.md)
- [mcp_adapter.md](mcp_adapter.md)
