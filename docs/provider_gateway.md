# Provider Gateway

## What It Is

The provider gateway is a backend-only abstraction layer for provider configuration and future extension.

It gives SafeCore a clean place to describe provider support without exposing secrets in the UI or changing the guarded core.

Current code lives under:

- `src/providers/base.py`
- `src/providers/gateway.py`
- `src/providers/openai_adapter.py`
- `src/providers/openai_compatible_adapter.py`

## Supported Adapters

Current baseline adapters are:

- `openai`
- `openai_compatible`
- `openrouter`
- `claude`
- `local_demo`

`local_demo` is the only provider path enabled in the current product shell.

The others are backend-only adapters for safe status visibility and opt-in integrations.

## Safe Status Contract

The gateway exposes only safe status metadata such as:

- configured / not configured
- enabled / disabled in current shell
- masked key status
- base URL status
- local/demo mode
- safe capability metadata
- safe health summary

It never returns:

- raw API keys
- auth headers
- token values
- raw secret env payloads

## OpenAI-Compatible Bridge

The main flexible bridge is `OpenAICompatibleProviderAdapter`.

It is designed for:

- local compatible servers
- self-hosted compatible endpoints
- future proxy layers
- configurable `base_url`
- optional bearer token usage

It builds backend request specs only.

It does not turn the SafeCore UI into a generic model execution console.

## Base URL Rules

The gateway supports safe `base_url` handling:

- default public API URLs can be represented safely
- local overrides like `http://127.0.0.1:11434/v1` can be represented safely
- remote custom overrides are shown as `Custom base URL configured`

This keeps the status surface useful without exposing internal environment details unnecessarily.

## Example Environment Variables

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `SAFECORE_OPENAI_COMPATIBLE_API_KEY`
- `SAFECORE_OPENAI_COMPATIBLE_BASE_URL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`

## What This Is Not

The provider gateway is not:

- a production secrets platform
- a cloud control plane
- arbitrary provider execution through the browser
- a production-ready provider orchestration system
