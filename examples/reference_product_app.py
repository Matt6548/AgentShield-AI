"""Minimal reference product app runner for the SafeCore local product flow."""

from __future__ import annotations

import json

from src.api.demo_ui import run_reference_product_flow


REFERENCE_FLOWS = (
    "safe_status_check",
    "blocked_external_status",
    "blocked_unsafe_status_method",
)


def main() -> None:
    for name in REFERENCE_FLOWS:
        payload = run_reference_product_flow(name)
        summary = payload["summary"]
        print(
            f"[{name}] "
            f"decision={summary['decision']} "
            f"risk_score={summary['risk_score']} "
            f"blocked={summary['blocked']} "
            f"approval_status={summary['approval_status']} "
            f"connector_status={summary['connector_status']} "
            f"execution_status={summary['execution_status']} "
            f"audit_integrity={summary['audit_integrity']} "
            f"audit={summary['audit_path']}"
        )
        print(payload["short_explanation"])
        print(json.dumps(payload["result"], indent=2))
        print()


if __name__ == "__main__":
    main()
