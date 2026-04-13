# Troubleshooting

This page covers the most likely local setup issues for the current SafeCore repository.

## Dependencies fail to install

Check:

- Python version is 3.11 or newer
- you are installing from the repository root
- you are using `pip install -r requirements.txt`

If package installation still fails, run:

```bash
python -m pip --version
python --version
```

## Server starts but the UI does not load

Check:

- `uvicorn src.api.app:app --reload` is running without import errors
- you are opening `http://127.0.0.1:8000/ui`
- another local process is not already using port `8000`

If needed, restart the server and reload the page.

## Provider status looks confusing

Expected default posture:

- `Local / demo mode` is the only enabled path in the shell
- external providers show safe backend/env visibility only
- configured status does not mean active model execution in the UI

See [provider_setup_guide.md](provider_setup_guide.md).

## Safety Copilot is disabled

That is the expected default.

The advisory copilot is:

- opt-in
- advisory-only
- not allowed to change final decisions

See [safety_copilot_advisory.md](safety_copilot_advisory.md).

## The product shell feels local-only

That is also expected.

SafeCore should be evaluated honestly as:

- open-source
- RC/MVP
- validated core
- dry-run-first

It is not a production-ready platform in this repository state.
