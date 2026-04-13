"""Reusable JSON Schema validation helpers for SafeCore contracts."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema.validators import validator_for


CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "contracts"


class ContractValidationError(ValueError):
    """Raised when a payload does not satisfy a SafeCore JSON contract."""


@lru_cache(maxsize=None)
def _load_contract_schema(contract_filename: str) -> dict[str, Any]:
    contract_path = CONTRACTS_DIR / contract_filename
    if not contract_path.exists():
        raise ContractValidationError(f"Contract file not found: {contract_filename}")

    with contract_path.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema


@lru_cache(maxsize=None)
def _build_validator(contract_filename: str):
    schema = _load_contract_schema(contract_filename)
    validator_cls = validator_for(schema)
    validator_cls.check_schema(schema)
    return validator_cls(schema)


def validate_against_contract(payload: dict[str, Any], contract_filename: str) -> None:
    """Validate payload against a contract file and raise on first error."""
    validator = _build_validator(contract_filename)
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda item: tuple(str(token) for token in item.absolute_path),
    )
    if not errors:
        return

    first = errors[0]
    path_tokens = [str(token) for token in first.absolute_path]
    path = ".".join(path_tokens) if path_tokens else "$"
    raise ContractValidationError(
        f"{contract_filename} validation failed at '{path}': {first.message}"
    )


def validate_safety_decision(payload: dict[str, Any]) -> None:
    """Validate payload as SafetyDecision contract."""
    validate_against_contract(payload, "SafetyDecision.json")


def validate_tool_call(payload: dict[str, Any]) -> None:
    """Validate payload as ToolCall contract."""
    validate_against_contract(payload, "ToolCall.json")


def validate_audit_record(payload: dict[str, Any]) -> None:
    """Validate payload as AuditRecord contract."""
    validate_against_contract(payload, "AuditRecord.json")

