# Productization Pack B

## What Was Added

Productization Pack B improves the existing SafeCore product shell without changing core decision semantics.

It adds:

- a multilingual UI layer with English, Russian, and Uzbek
- a plain-language UX pass across the product shell
- a safe provider status layer for backend environment visibility
- cleaner product-facing navigation and provider cards

The project posture stays the same:

- open-source RC/MVP
- validated core
- dry-run-first
- not a production-ready platform

## Why This Matters

Before this pack, the shell already showed flows, history, approval visibility, and audit evidence.

This pack makes the shell easier to understand quickly:

- a new user can switch language without leaving the current local app
- a product viewer can understand what SafeCore protects in plain language
- a developer can see provider posture without exposing secrets in the browser

The result is a cleaner local product shell, not a new platform.

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

Then:

1. switch between `English`, `Russian`, and `Uzbek`
2. inspect `Provider Status`
3. run `Reference Product Flow`
4. inspect `Product Shell`, `Run History`, and `Approval And Audit`

## How The Multilingual Layer Works

The UI now requests localized shell content from the backend with a `lang` query parameter.

Current supported languages:

- `en`
- `ru`
- `uz`

The language switch affects the product shell text layer only. It does not change policy logic, guard logic, or execution behavior.

## How The Provider Status Layer Works

The provider section is intentionally narrow.

It shows:

- whether provider environment variables are present
- whether a provider is enabled in the current shell
- masked status only
- local/demo mode as the currently enabled path

It does not:

- expose raw keys
- execute arbitrary model calls
- act as a cloud provider platform
- manage secrets like a production system

## What Stays Intentionally Limited

- no production auth/authz
- no cloud secrets manager
- no real arbitrary model execution
- no claim of a production-ready platform
- no change to dry-run-first posture

## Operational Note

Provider visibility is a shell-level convenience for local evaluation. It is useful because it tells a developer what is configured today without weakening the current SafeCore safety posture.
