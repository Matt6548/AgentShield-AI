"""Shared security detection and redaction helpers for SafeCore guards."""

from __future__ import annotations

import re
from typing import Any


EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_REGEX = re.compile(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
TOKEN_VALUE_REGEX = re.compile(
    r"(?i)(?:sk-[a-z0-9]{16,}|api[_-]?key[\s:=]+[a-z0-9_\-]{8,}|token[\s:=]+[a-z0-9_\-]{8,})"
)

SECRET_FIELD_HINTS = {
    "api_key",
    "apikey",
    "token",
    "secret",
    "password",
    "passphrase",
    "auth",
    "credential",
    "private_key",
    "access_key",
}

SUSPICIOUS_OUTBOUND_MARKERS = {
    "http://",
    "https://",
    "ftp://",
    "s3://",
    "upload",
    "exfil",
    "pastebin",
    "dropbox",
    "drive.google",
}

REDACTION_TEXT = "[REDACTED]"


def detect_sensitive_findings(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Return deterministic findings for known sensitive patterns."""
    findings: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for path, key, text in _iter_scalar_values(payload):
        key_lower = key.lower()
        text_lower = text.lower()
        if not text.strip():
            continue

        if _is_secret_key(key_lower):
            _append_finding(findings, seen, "secret", path, "secret-like field name")
        if EMAIL_REGEX.search(text):
            _append_finding(findings, seen, "email", path, "email pattern")
        if PHONE_REGEX.search(text):
            _append_finding(findings, seen, "phone", path, "phone pattern")
        if _contains_credit_card_number(text):
            _append_finding(findings, seen, "credit_card", path, "credit-card-like pattern")
        if TOKEN_VALUE_REGEX.search(text_lower):
            _append_finding(findings, seen, "secret", path, "token-like value pattern")
        if _contains_any(text_lower, SUSPICIOUS_OUTBOUND_MARKERS):
            _append_finding(
                findings,
                seen,
                "suspicious_outbound",
                path,
                "suspicious outbound marker",
            )

    return sorted(findings, key=lambda item: (item["path"], item["type"], item["detail"]))


def redact_sensitive_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a payload copy with known sensitive values redacted."""
    if not isinstance(payload, dict):
        raise TypeError("redact_sensitive_payload expects a dict payload.")
    return _redact_value(payload, key_hint="")


def _redact_value(value: Any, key_hint: str) -> Any:
    if isinstance(value, dict):
        return {key: _redact_value(item, key) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_value(item, key_hint=key_hint) for item in value]

    text = _to_text(value)
    key_lower = key_hint.lower()
    if _should_redact_scalar(text, key_lower):
        return REDACTION_TEXT
    return value


def _should_redact_scalar(text: str, key_lower: str) -> bool:
    if _is_secret_key(key_lower):
        return True
    if EMAIL_REGEX.search(text):
        return True
    if PHONE_REGEX.search(text):
        return True
    if _contains_credit_card_number(text):
        return True
    if TOKEN_VALUE_REGEX.search(text.lower()):
        return True
    return False


def _contains_credit_card_number(text: str) -> bool:
    for match in CREDIT_CARD_REGEX.findall(text):
        digits = "".join(ch for ch in match if ch.isdigit())
        if 13 <= len(digits) <= 19 and _passes_luhn_check(digits):
            return True
    return False


def _passes_luhn_check(number: str) -> bool:
    digits = [int(ch) for ch in number]
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def _is_secret_key(key_lower: str) -> bool:
    return any(hint in key_lower for hint in SECRET_FIELD_HINTS)


def _append_finding(
    findings: list[dict[str, str]],
    seen: set[tuple[str, str]],
    finding_type: str,
    path: str,
    detail: str,
) -> None:
    key = (finding_type, path)
    if key in seen:
        return
    seen.add(key)
    findings.append({"type": finding_type, "path": path, "detail": detail})


def _contains_any(text: str, markers: set[str]) -> bool:
    return any(marker in text for marker in markers)


def _iter_scalar_values(value: Any, path: str = "") -> list[tuple[str, str, str]]:
    collected: list[tuple[str, str, str]] = []

    if isinstance(value, dict):
        for key in sorted(value.keys()):
            child = value[key]
            child_path = f"{path}.{key}" if path else key
            if isinstance(child, (dict, list)):
                collected.extend(_iter_scalar_values(child, child_path))
            else:
                collected.append((child_path, str(key), _to_text(child)))
        return collected

    if isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            if isinstance(child, (dict, list)):
                collected.extend(_iter_scalar_values(child, child_path))
            else:
                collected.append((child_path, "", _to_text(child)))
        return collected

    collected.append((path or "value", "", _to_text(value)))
    return collected


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)

