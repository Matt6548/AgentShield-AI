"""Connector hardening boundary helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.connectors.request_sanitizer import ConnectorRequestSanitizer
from src.connectors.response_sanitizer import ConnectorResponseSanitizer


class ConnectorHardening:
    """Apply request/response sanitization around connector adapter execution."""

    def __init__(
        self,
        request_sanitizer: ConnectorRequestSanitizer | None = None,
        response_sanitizer: ConnectorResponseSanitizer | None = None,
    ) -> None:
        self.request_sanitizer = request_sanitizer or ConnectorRequestSanitizer()
        self.response_sanitizer = response_sanitizer or ConnectorResponseSanitizer()

    def sanitize_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Sanitize connector request input before adapter selection/execution."""
        return self.request_sanitizer.sanitize(deepcopy(request))

    def sanitize_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Sanitize connector adapter response before returning to service."""
        return self.response_sanitizer.sanitize(deepcopy(response))

