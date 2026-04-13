"""Base connector abstractions for SafeCore connector stubs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any


class BaseConnector(ABC):
    """Abstract connector interface used by future connector integrations."""

    def __init__(self, name: str) -> None:
        self.name = name

    def validate_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate connector request shape."""
        if not isinstance(request, dict):
            raise TypeError("Connector requests must be dictionaries.")
        return deepcopy(request)

    @abstractmethod
    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute connector request (stubbed in this iteration)."""

    def perform_live_call(self, request: dict[str, Any]) -> dict[str, Any]:
        """Placeholder for future side-effecting connector operations."""
        raise NotImplementedError("Live connector calls are not implemented in this iteration.")

