"""Deterministic connector stub for SafeCore foundation work."""

from __future__ import annotations

from typing import Any

from src.connectors.base import BaseConnector


class StubConnector(BaseConnector):
    """A non-side-effecting connector placeholder."""

    def __init__(self, name: str = "stub_connector") -> None:
        super().__init__(name=name)

    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        validated_request = self.validate_request(request)
        return {
            "connector": self.name,
            "success": False,
            "status": "STUBBED",
            "output": {
                "message": "Connector runtime is not implemented in this iteration.",
                "request": validated_request,
            },
        }

