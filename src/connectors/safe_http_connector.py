"""Narrow safe read-only HTTP status connector example for SafeCore."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.connectors.base import BaseConnector
from src.utils.safe_http import (
    SAFE_HTTP_MAX_RESPONSE_BYTES,
    extract_safe_http_request,
)


class SafeHttpStatusConnector(BaseConnector):
    """Perform one intentionally narrow allowlisted read-only HTTP fetch."""

    def __init__(self, name: str = "safe_http_status_connector") -> None:
        super().__init__(name=name)

    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute the safe read-only fetch or return a blocked-safe response."""
        validated = self.validate_request(request)
        safe_http = extract_safe_http_request(validated)
        if not safe_http["allowed"]:
            return self._blocked_result(safe_http)

        response_body = ""
        content_type = "unknown"
        status_code = 0

        req = Request(
            safe_http["url"],
            method=safe_http["method"],
            headers={"Accept": "application/json, text/plain;q=0.9, */*;q=0.1"},
        )

        try:
            with urlopen(req, timeout=safe_http["timeout_seconds"]) as response:  # noqa: S310
                status_code = int(getattr(response, "status", response.getcode()))
                content_type = str(response.headers.get("Content-Type", "unknown"))
                raw_bytes = response.read(SAFE_HTTP_MAX_RESPONSE_BYTES)
                response_body = raw_bytes.decode("utf-8", errors="replace")
        except HTTPError as exc:
            status_code = int(exc.code)
            content_type = str(exc.headers.get("Content-Type", "unknown"))
            response_body = exc.read(SAFE_HTTP_MAX_RESPONSE_BYTES).decode(
                "utf-8",
                errors="replace",
            )
        except URLError as exc:
            return {
                "connector": self.name,
                "status": "SAFE_READ_ONLY_UNAVAILABLE",
                "success": False,
                "output": {
                    "message": str(exc.reason),
                    "url": safe_http["url"],
                    "method": safe_http["method"],
                    "read_only": True,
                },
            }

        return {
            "connector": self.name,
            "status": "SAFE_READ_ONLY_FETCHED",
            "success": 200 <= status_code < 400,
            "output": {
                "url": safe_http["url"],
                "method": safe_http["method"],
                "status_code": status_code,
                "content_type": content_type,
                "body_preview": _truncate_preview(response_body),
                "parsed_preview": _coerce_json_preview(response_body),
                "read_only": True,
                "allowlisted": True,
            },
        }

    def perform_live_call(self, request: dict[str, Any]) -> dict[str, Any]:
        """Alias explicit live connector entrypoint to the same narrow safe fetch."""
        return self.execute(request)

    def _blocked_result(self, safe_http: dict[str, Any]) -> dict[str, Any]:
        return {
            "connector": self.name,
            "status": "BLOCKED",
            "success": False,
            "reasons": list(safe_http["reasons"]),
            "output": {
                "url": safe_http["url"],
                "method": safe_http["method"],
                "host": safe_http["host"],
                "path": safe_http["path"],
                "read_only": True,
                "allowlisted": False,
            },
        }


def _truncate_preview(text: str) -> str:
    stripped = text.strip()
    if len(stripped) <= 300:
        return stripped
    return stripped[:297] + "..."


def _coerce_json_preview(text: str) -> dict[str, Any] | str:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return _truncate_preview(text)
    if isinstance(parsed, dict):
        return {key: parsed[key] for key in list(parsed)[:8]}
    if isinstance(parsed, list):
        return parsed[:5]
    return parsed
