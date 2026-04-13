# Provider Setup Guide

## Purpose

The SafeCore product shell can show provider configuration posture without exposing secrets in the browser.

This is a visibility layer, not a full provider execution system.

## Providers Shown In The Shell

The shell currently shows cards for:

- `OpenAI`
- `OpenAI-compatible`
- `Claude`
- `OpenRouter`
- `Local / demo mode`

## How Configuration Works

The backend checks whether these environment variables are present:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `SAFECORE_OPENAI_COMPATIBLE_API_KEY`
- `SAFECORE_OPENAI_COMPATIBLE_BASE_URL`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`

The UI receives only safe status information such as:

- configured or not configured
- enabled or disabled
- masked key status
- environment source label
- base URL status
- baseline gateway support
- safe how-to-enable guidance

The UI does not receive raw secret values.

## Configured vs Not Configured

`Configured` means the backend detected the expected environment variable.

`Not configured` means the variable is absent in the current local environment.

This does not mean the provider is actively used by the shell.

## Enabled vs Disabled

In the current RC/MVP shell:

- external provider cards are visibility-only
- `Local / demo mode` is the only enabled path in the shell
- backend gateway adapters can still exist for future opt-in integrations

This is intentional. The provider section should explain configuration posture without turning SafeCore into an arbitrary model execution layer.

## OpenAI-Compatible Bridge

The main flexible bridge for future provider adoption is the `OpenAI-compatible` adapter.

It is meant for:

- local compatible servers
- self-hosted compatible endpoints
- proxy or bridge layers
- safe backend-only `base_url` configuration

It does not expose tokens in the browser and it does not enable arbitrary UI execution.

## Example Local Setup

PowerShell:

```powershell
$env:OPENAI_API_KEY = \"sk-example\"
uvicorn src.api.app:app --reload
```

Then open:

```text
http://127.0.0.1:8000/ui
```

In `Provider Status`, the `OpenAI` card should move from `Not configured` to `Configured via env (masked)`.

If you set:

```powershell
$env:SAFECORE_OPENAI_COMPATIBLE_BASE_URL = "http://127.0.0.1:11434/v1"
uvicorn src.api.app:app --reload
```

the `OpenAI-compatible` card should show a local base URL override without exposing secrets.

## Security Posture

Key handling is intentionally narrow:

- keys are read from backend environment variables only
- keys are never stored in browser state as plaintext
- keys are never returned through the product shell API payload
- onboarding progress is stored only in browser `localStorage`, without secrets

## What This Is Not

This is not:

- a production secrets system
- a cloud provider control plane
- a full provider orchestration layer
- a production provider gateway platform
- not a production-ready platform

It is a safe, local configuration visibility layer for the current SafeCore RC/MVP shell.
