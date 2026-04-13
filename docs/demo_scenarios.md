# Demo Scenarios

| Scenario | Input idea | Expected outcome | Why it matters |
|---|---|---|---|
| `ALLOW` | Safe read-only shell action like `ls` | `ALLOW`, not blocked, execution stays `DRY_RUN_SIMULATED` | Shows that low-risk actions can pass policy and guards without real side effects |
| `NEEDS_APPROVAL` | Production config-style change | `NEEDS_APPROVAL`, blocked, approval status `PENDING` | Shows that risky actions do not auto-execute |
| `DENY` | Privileged destructive shell action like `rm -rf /` | `DENY`, blocked, approval not applicable | Shows that clearly dangerous actions are stopped outright |

## Notes

- All scenarios run through the current guarded path.
- All scenarios remain dry-run-only.
- Audit evidence is produced in the demo audit log.
