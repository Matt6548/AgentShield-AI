"""Connector request sanitization utilities."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any


ALLOWED_TOP_LEVEL_FIELDS = {
    "run_id",
    "actor",
    "user",
    "action",
    "tool",
    "connector",
    "command",
    "params",
    "payload",
    "environment",
    "env",
    "target",
    "target_system",
    "dry_run",
    "policy_pack",
}

DANGEROUS_KEY_FRAGMENTS = (
    "__proto__",
    "__class__",
    "__dict__",
    "token",
    "secret",
    "password",
    "api_key",
    "authorization",
    "traceback",
    "stack",
    "raw_request",
    "raw_response",
)

MAX_TOP_LEVEL_FIELDS = 24
MAX_COMMAND_LENGTH = 2048
MAX_SERIALIZED_BYTES = 12000
MAX_LIST_LENGTH = 200


class ConnectorRequestSanitizer:
    """Sanitize connector requests and reject unsafe request shapes."""

    def sanitize(self, request: dict[str, Any]) -> dict[str, Any]:
        """Return deterministic sanitization result for connector requests."""
        if not isinstance(request, dict):
            return {
                "valid": False,
                "sanitized_request": {},
                "reasons": ["Connector request must be a dictionary."],
                "stripped_fields": [],
                "stripped_nested_paths": [],
            }

        stripped_fields = sorted(
            key for key in request.keys() if key not in ALLOWED_TOP_LEVEL_FIELDS
        )
        sanitized_request = {
            key: deepcopy(value)
            for key, value in request.items()
            if key in ALLOWED_TOP_LEVEL_FIELDS
        }
        reasons: list[str] = []

        if len(request.keys()) > MAX_TOP_LEVEL_FIELDS:
            reasons.append(
                f"Connector request has too many top-level fields ({len(request.keys())} > {MAX_TOP_LEVEL_FIELDS})."
            )

        tool = str(sanitized_request.get("tool", "")).strip()
        if not tool:
            reasons.append("Connector request is missing a non-empty 'tool' field.")

        command = str(sanitized_request.get("command", ""))
        if len(command) > MAX_COMMAND_LENGTH:
            reasons.append(
                f"Connector command exceeds maximum length ({len(command)} > {MAX_COMMAND_LENGTH})."
            )

        stripped_nested_paths: list[str] = []
        for field in ("params", "payload"):
            value = sanitized_request.get(field, {})
            if not isinstance(value, dict):
                value = {f"raw_{field}": deepcopy(value)}
            cleaned, stripped = self._sanitize_nested_dict(value, parent=field)
            sanitized_request[field] = cleaned
            stripped_nested_paths.extend(stripped)

        if stripped_nested_paths:
            reasons.append("Connector request contained unsafe nested keys that were stripped.")

        serialized_bytes = len(
            json.dumps(sanitized_request, sort_keys=True, ensure_ascii=True).encode("utf-8")
        )
        if serialized_bytes > MAX_SERIALIZED_BYTES:
            reasons.append(
                f"Connector request payload is too large ({serialized_bytes} > {MAX_SERIALIZED_BYTES} bytes)."
            )

        return {
            "valid": len(reasons) == 0,
            "sanitized_request": sanitized_request,
            "reasons": reasons,
            "stripped_fields": stripped_fields,
            "stripped_nested_paths": sorted(stripped_nested_paths),
        }

    def _sanitize_nested_dict(
        self,
        value: dict[str, Any],
        *,
        parent: str,
    ) -> tuple[dict[str, Any], list[str]]:
        sanitized: dict[str, Any] = {}
        stripped: list[str] = []

        for key, item in value.items():
            key_str = str(key)
            lowered = key_str.lower()
            if any(fragment in lowered for fragment in DANGEROUS_KEY_FRAGMENTS):
                stripped.append(f"{parent}.{key_str}")
                continue

            if isinstance(item, dict):
                nested_cleaned, nested_stripped = self._sanitize_nested_dict(
                    item,
                    parent=f"{parent}.{key_str}",
                )
                sanitized[key_str] = nested_cleaned
                stripped.extend(nested_stripped)
            elif isinstance(item, list):
                sanitized[key_str] = self._sanitize_list(item, parent=f"{parent}.{key_str}")
            else:
                sanitized[key_str] = deepcopy(item)
        return sanitized, stripped

    def _sanitize_list(self, items: list[Any], *, parent: str) -> list[Any]:
        cleaned: list[Any] = []
        for index, item in enumerate(items):
            if index >= MAX_LIST_LENGTH:
                break
            if isinstance(item, dict):
                nested, _ = self._sanitize_nested_dict(item, parent=f"{parent}[{index}]")
                cleaned.append(nested)
            elif isinstance(item, list):
                cleaned.append(self._sanitize_list(item, parent=f"{parent}[{index}]"))
            else:
                cleaned.append(deepcopy(item))
        return cleaned
