# Contributing

Thanks for considering a contribution to SafeCore.

SafeCore is an open-source RC/MVP validated core for guarded agent execution. Contributions should preserve that honesty: this repository is not a production-ready platform.

By contributing, assume accepted changes stay under the repository's Apache 2.0 license posture.

## Good First Contribution Paths

Good early contributions usually include:

- docs improvements
- reproducible bug fixes
- tests that tighten current safety guarantees
- product-shell clarity improvements that do not change core semantics

## Before You Propose Runtime Changes

Unsafe runtime changes require explicit review.

Call out your change clearly if it touches:

- decision semantics
- approval behavior
- dry-run guarantees
- connector side effects
- audit or validation boundaries

## Development Workflow

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the quick demo if relevant:

```bash
python scripts/demo_smoke.py
```

3. Run the local UI if relevant:

```bash
uvicorn src.api.app:app --reload
```

4. Run validation before opening a PR:

```bash
python -m pytest -q
python -m compileall src tests
python -m build
```

## Pull Request Expectations

A good PR should:

- explain what changed and why
- state whether runtime behavior changed
- state whether docs/tests were updated
- respect current RC/MVP scope and public positioning
- avoid fake production or enterprise claims

## Scope Reminder

Please keep proposals aligned with the current repository posture:

- open-source
- RC/MVP
- validated core
- not a production-ready platform

