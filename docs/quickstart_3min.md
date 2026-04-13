# 3-Minute Quickstart

This is the fastest practical path to understand SafeCore locally without changing any runtime semantics.

SafeCore remains an open-source RC/MVP validated core and product shell. It is not a production-ready platform.

## 1. Install

```bash
pip install -r requirements.txt
```

## 2. Start the local UI

```bash
uvicorn src.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/ui
```

## 3. Complete the first local run

In the UI:

1. finish onboarding
2. open `First Practical Integration Path`
3. run `allowlisted_get`
4. compare it with `blocked_host` and `blocked_method`

## 4. What to inspect

Focus on these fields:

- `decision`
- `risk_score`
- `blocked`
- `approval_status`
- `execution_status`
- `audit_integrity`
- `audit_path`

## 5. What this proves

- SafeCore sits between intent and execution
- `ALLOW`, `NEEDS_APPROVAL`, and `DENY` remain explicit
- runtime stays dry-run-first
- audit and history remain visible in the product shell

## Next Docs

- First run checklist: [first_run_checklist.md](first_run_checklist.md)
- Troubleshooting: [troubleshooting.md](troubleshooting.md)
- First practical use case: [first_use_case.md](first_use_case.md)
- Product shell guide: [product_shell_user_guide.md](product_shell_user_guide.md)
