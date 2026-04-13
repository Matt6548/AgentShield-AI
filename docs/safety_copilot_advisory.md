# Safety Copilot Advisory

SafeCore can expose an optional Safety Copilot advisory layer for the local product shell.

This layer is advisory only:

- it does not change `ALLOW`, `NEEDS_APPROVAL`, or `DENY`
- it does not authorize execution
- it does not bypass approval
- it does not turn SafeCore into a new agent runtime

## What It Does

When enabled, the advisory layer takes the latest guarded result and produces:

- a short plain-language summary
- highlighted risks
- operator guidance
- suggested follow-up

This is meant to help an operator or evaluator understand why a request was allowed, blocked, or held for approval.

## What Data It Uses

The advisory path uses a minimized safety snapshot only.

Included fields:

- user intent summary
- planned tools
- policy result
- risk factors
- approval-needed reason when present
- audit id
- UI language

Not forwarded:

- raw API keys
- token-like strings
- raw env values
- full tool payload dumps
- raw audit file content

## Modes

SafeCore supports these modes:

- `disabled` (default)
- `local_only`
- `external`

### Disabled

Default posture. The assistant endpoints return a safe disabled status.

### Local Only

Set:

```bash
SAFECORE_SAFETY_COPILOT_MODE=local_only
```

This enables a deterministic local advisory backend for testing and demos.
It does not call an external model.

### External

Set backend environment variables:

```bash
SAFECORE_SAFETY_COPILOT_MODE=external
SAFECORE_SAFETY_COPILOT_BASE_URL=http://your-openai-compatible-endpoint
SAFECORE_SAFETY_COPILOT_API_KEY=...
SAFECORE_SAFETY_COPILOT_MODEL=...
```

External mode is opt-in only. It still uses the minimized safety snapshot and it still cannot change the final decision.

This is not a production secrets system. Keys stay in the backend environment and are never returned to the browser.

## API Endpoints

Safe endpoints:

- `GET /v1/demo-ui/assistant-capabilities`
- `POST /v1/demo-ui/assistant-insight`

`assistant-capabilities` shows only safe metadata such as:

- enabled / disabled
- mode
- provider label
- model label
- masked key status
- safe base URL label

`assistant-insight` returns validated advisory output only when the assistant is enabled.

## UI Behavior

The product shell includes a small `Safety Copilot Advisory` panel.

When disabled:

- the panel explains that the feature is off by default
- no assistant insight is returned

When enabled:

- the panel can explain the latest scenario, integration example, or reference product flow
- the panel does not mutate the original decision

## Safety Guarantees In This Package

This package preserves SafeCore core semantics:

- `ALLOW / NEEDS_APPROVAL / DENY` are unchanged
- dry-run-first posture is unchanged
- guarded flow meaning is unchanged
- assistant output is schema-validated before use
- invalid assistant output is rejected

## Current Scope

What exists now:

- optional advisory layer
- strict context minimization
- strict insight schema validation
- deterministic local mode for tests and demos
- optional external OpenAI-compatible advisory path

What is intentionally not included yet:

- assistant authority over decisions
- autonomous follow-up actions
- production auth/authz
- enterprise GenAI governance platform claims
- heavy UI redesign
