# Productization Pack M1

## What Was Added

Productization Pack M1 tightens the local product shell without changing SafeCore core semantics.

It adds:

- a lightweight onboarding flow inside `/ui`
- safer, clearer provider configuration guidance
- better shell hierarchy and empty states
- plain-language explanations for history, approval, and audit views
- lightweight filters for run history and audit records
- one consistent multilingual product text path across English, Russian, and Uzbek

The core posture stays the same:

- open-source RC/MVP
- validated core
- dry-run-first
- not a production-ready platform

## Onboarding Flow

The shell now starts with a short onboarding wizard:

1. language
2. provider setup
3. first safe run
4. approval explanation
5. audit viewer

The goal is simple: a first-time user should understand what SafeCore protects before reading deeper docs.

Progress is stored only in browser `localStorage`.
No keys, tokens, or secrets are stored there.

## Provider Status UX

Provider cards are still visibility-only.

They now explain:

- configured or not configured
- enabled or disabled
- masked key status
- safe backend source label
- how to enable the provider card safely

The browser still never receives raw API keys or environment values.

## Audit And History Usability

The shell now makes recent runs and audit evidence easier to read:

- decision filter
- run-status filter
- provider-mode filter
- integrity filter for audit view
- clearer plain-language summaries
- clearer next-step guidance

These are product-shell filters only.
They do not change audit semantics or decision behavior.

## How To Use It

Run the local shell:

```bash
pip install -r requirements.txt
uvicorn src.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/ui
```

Recommended first path:

1. finish the onboarding flow
2. check `Provider Status`
3. run the allowlisted safe reference flow
4. inspect `Run History`
5. inspect `Approval And Audit`

## What Stays Intentionally Limited

- no production auth/authz
- no cloud provider platform
- no browser-side secret storage
- no arbitrary model execution layer
- no destructive external side effects
- no change to ALLOW / NEEDS_APPROVAL / DENY semantics

## Why This Matters

Before M1, the shell already showed useful information.

After M1, a new user can now:

- understand the shell faster
- see how provider configuration works safely
- trace what happened in plain language
- use the shell as a clearer product entrypoint without mistaking it for a production platform
