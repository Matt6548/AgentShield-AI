"""Shared validation helpers for the SafeCore safe HTTP status example."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import urlparse


SAFE_HTTP_TOOL = "safe_http_status"
SAFE_HTTP_ALLOWED_METHODS = {"GET"}
SAFE_HTTP_ALLOWED_SCHEMES = {"http"}
SAFE_HTTP_ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
SAFE_HTTP_ALLOWED_PATH_PREFIXES = ("/health", "/status", "/metadata", "/version")
SAFE_HTTP_MAX_TIMEOUT_SECONDS = 3
SAFE_HTTP_MAX_RESPONSE_BYTES = 4096


def extract_safe_http_request(request: dict[str, Any]) -> dict[str, Any]:
    """Normalize one Safe HTTP request into a deterministic validation object."""
    if not isinstance(request, dict):
        raise TypeError("Safe HTTP extraction expects a dict request.")

    params = request.get("params", {})
    if not isinstance(params, dict):
        params = {}

    method = str(params.get("method", request.get("command", "GET")) or "GET").strip().upper()
    url = str(params.get("url", request.get("target", request.get("target_system", ""))) or "").strip()
    timeout = _coerce_timeout(params.get("timeout_seconds"))

    parsed = urlparse(url)
    host = (parsed.hostname or "").strip().lower()
    path = parsed.path or "/"
    scheme = (parsed.scheme or "").strip().lower()

    reasons: list[str] = []
    allowed = True

    if not url:
        reasons.append("Safe HTTP example requires an explicit URL.")
        allowed = False
    if method not in SAFE_HTTP_ALLOWED_METHODS:
        reasons.append("Safe HTTP example supports GET only.")
        allowed = False
    if scheme not in SAFE_HTTP_ALLOWED_SCHEMES:
        reasons.append("Safe HTTP example supports HTTP localhost endpoints only.")
        allowed = False
    if host not in SAFE_HTTP_ALLOWED_HOSTS:
        reasons.append("Safe HTTP example only allows explicitly trusted local hosts.")
        allowed = False
    if not any(path.startswith(prefix) for prefix in SAFE_HTTP_ALLOWED_PATH_PREFIXES):
        reasons.append("Safe HTTP example only allows health/status/metadata/version paths.")
        allowed = False

    return {
        "method": method,
        "url": url,
        "scheme": scheme,
        "host": host,
        "path": path,
        "timeout_seconds": timeout,
        "allowed": allowed,
        "reasons": reasons,
        "request": deepcopy(request),
    }


def is_safe_http_tool(tool: Any) -> bool:
    """Return whether the given tool string matches the safe HTTP example tool."""
    return str(tool or "").strip().lower() == SAFE_HTTP_TOOL


def _coerce_timeout(value: Any) -> int:
    try:
        timeout = int(value)
    except (TypeError, ValueError):
        timeout = SAFE_HTTP_MAX_TIMEOUT_SECONDS
    return max(1, min(timeout, SAFE_HTTP_MAX_TIMEOUT_SECONDS))
