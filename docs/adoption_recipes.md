# Adoption Recipes

SafeCore already includes a validated core, a local product shell, and baseline integration surfaces. This page collects the most practical adoption recipes for developers who want a copy-paste-friendly starting point.

## Who These Recipes Are For

These recipes are for:

- AI/agent developers who need a guarded layer before tools or connector actions
- platform engineers who want a narrow reference integration path
- security-minded teams evaluating how to put SafeCore between agent intent and execution

## What "Baseline Support" Means

In this repository, baseline support means:

- a starter recipe exists
- the integration path is intentionally narrow and explicit
- SafeCore still owns the guarded decision
- the examples are useful for local adoption, not a claim of full framework coverage

It does not mean:

- enterprise-grade support
- production guarantees
- a full platform integration surface

## Where SafeCore Fits

SafeCore sits between an app or agent and real-world actions:

```text
app or agent -> SafeCore -> policy / guard checks -> connector boundary -> guarded result
```

The role stays the same across all recipes:

- your app builds an action request
- SafeCore evaluates it
- SafeCore returns `ALLOW`, `NEEDS_APPROVAL`, or `DENY`
- execution stays within the current dry-run-first posture

## Included Recipes

### 1. LangChain starter recipe

See [recipe_langchain.md](recipe_langchain.md).

What it shows:

- how to wrap a LangChain-style tool call
- how to route it through `SafeCoreLangChainToolAdapter`
- how to preserve guarded result visibility

### 2. LangGraph starter recipe

See [recipe_langgraph.md](recipe_langgraph.md).

What it shows:

- how to insert SafeCore into a graph node
- how to return a guarded state patch
- how to keep the next graph step behind the same decision boundary

### 3. OpenAI-compatible local starter recipe

See [recipe_openai_compatible_local.md](recipe_openai_compatible_local.md).

What it shows:

- how to represent a local or self-hosted OpenAI-compatible provider safely
- how provider status and request specs fit into backend setup
- how SafeCore remains the control layer before tool or connector execution

## Recommended Reading Order

1. [why_safecore.md](why_safecore.md)
2. [with_vs_without_safecore.md](with_vs_without_safecore.md)
3. [developer_starter_pack.md](developer_starter_pack.md)
4. [integration_flow_reference.md](integration_flow_reference.md)
5. one focused recipe from this pack
6. [integrations_pack_n.md](integrations_pack_n.md) for broader baseline context

## Current Boundaries

These recipes are intentionally narrow:

- they are starter paths, not complete framework integrations
- they do not weaken `ALLOW` / `NEEDS_APPROVAL` / `DENY`
- they do not change the dry-run-first posture
- they do not imply a production-ready platform
