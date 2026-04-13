"""Connector response sanitization utilities."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


UNSAFE_RESPONSE_KEY_FRAGMENTS = (
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


class ConnectorResponseSanitizer:
    """Normalize connector adapter responses into a safe deterministic envelope."""

    def sanitize(self, response: dict[str, Any]) -> dict[str, Any]:
        """Return sanitized connector execution response."""
        if not isinstance(response, dict):
            return {
                "adapter_id": "unknown_adapter",
                "connector": "unknown_connector",
                "tool": "",
                "dry_run": True,
                "status": "INVALID_RESULT",
                "success": False,
                "reasons": ["Connector response must be a dictionary."],
                "normalized_request": {},
                "raw_result": {},
            }

        normalized_request = response.get("normalized_request", {})
        if not isinstance(normalized_request, dict):
            normalized_request = {"raw_normalized_request": deepcopy(normalized_request)}
        cleaned_request, _ = self._sanitize_nested_dict(normalized_request)

        raw_result = response.get("raw_result", {})
        if not isinstance(raw_result, dict):
            raw_result = {"raw_result_value": deepcopy(raw_result)}
        cleaned_raw_result, stripped_raw_paths = self._sanitize_nested_dict(raw_result)

        reasons = response.get("reasons", [])
        if not isinstance(reasons, list):
            reasons = [str(reasons)]
        else:
            reasons = [str(reason) for reason in reasons]
        if stripped_raw_paths:
            reasons = reasons + ["Connector response contained unsafe keys that were stripped."]

        return {
            "adapter_id": str(response.get("adapter_id", "unknown_adapter")),
            "connector": str(response.get("connector", "unknown_connector")),
            "tool": str(response.get("tool", "")),
            "dry_run": bool(response.get("dry_run", True)),
            "status": str(response.get("status", "INVALID_RESULT")),
            "success": bool(response.get("success", False)),
            "reasons": reasons,
            "normalized_request": cleaned_request,
            "raw_result": cleaned_raw_result,
        }

    def _sanitize_nested_dict(
        self,
        value: dict[str, Any],
        *,
        parent: str = "root",
    ) -> tuple[dict[str, Any], list[str]]:
        cleaned: dict[str, Any] = {}
        stripped_paths: list[str] = []
        for key, item in value.items():
            key_str = str(key)
            lowered = key_str.lower()
            if any(fragment in lowered for fragment in UNSAFE_RESPONSE_KEY_FRAGMENTS):
                stripped_paths.append(f"{parent}.{key_str}")
                continue

            if isinstance(item, dict):
                nested_cleaned, nested_stripped = self._sanitize_nested_dict(
                    item,
                    parent=f"{parent}.{key_str}",
                )
                cleaned[key_str] = nested_cleaned
                stripped_paths.extend(nested_stripped)
            elif isinstance(item, list):
                nested_items: list[Any] = []
                for index, list_item in enumerate(item):
                    if isinstance(list_item, dict):
                        child_cleaned, child_stripped = self._sanitize_nested_dict(
                            list_item,
                            parent=f"{parent}.{key_str}[{index}]",
                        )
                        nested_items.append(child_cleaned)
                        stripped_paths.extend(child_stripped)
                    else:
                        nested_items.append(deepcopy(list_item))
                cleaned[key_str] = nested_items
            else:
                cleaned[key_str] = deepcopy(item)
        return cleaned, stripped_paths

