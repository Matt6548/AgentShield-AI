# Deployment Baseline (Local/Container)

This baseline is for local and controlled development environments. It is not a production deployment stack.

## Files

- `infra/Dockerfile`
- `infra/docker-compose.yml`
- `infra/.env.example`

## Hardening Choices

- Container runs as non-root user (`safecore`).
- Python bytecode writes are disabled.
- Compose service runs with:
  - `read_only: true`
  - dropped Linux capabilities (`cap_drop: [ALL]`)
  - `no-new-privileges`
  - explicit healthcheck (`/health`)
- Durable writable path is isolated to `/app/runtime` via named volume.
- Source tree mount is read-only in compose (`..:/app:ro`) for safer local posture.

## Local Startup

```bash
docker compose -f infra/docker-compose.yml up --build
```

Optional environment overrides:

1. Copy `infra/.env.example` to `infra/.env`.
2. Edit values in `infra/.env`.
3. Re-run compose.

## Scope Limits

- No cloud-managed deployment resources.
- No production authN/authZ layer here.
- No external DB/service dependencies required.
- SafeCore execution path remains dry-run only.

