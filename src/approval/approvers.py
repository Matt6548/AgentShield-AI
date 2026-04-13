"""Approval status helpers for SafeCore."""

from __future__ import annotations


APPROVAL_STATUS_PENDING = "PENDING"
APPROVAL_STATUS_APPROVED = "APPROVED"
APPROVAL_STATUS_REJECTED = "REJECTED"

VALID_APPROVAL_STATUSES = {
    APPROVAL_STATUS_PENDING,
    APPROVAL_STATUS_APPROVED,
    APPROVAL_STATUS_REJECTED,
}


def normalize_approval_status(status: str) -> str:
    """Normalize and validate approval status values."""
    normalized = str(status).strip().upper()
    if normalized not in VALID_APPROVAL_STATUSES:
        raise ValueError(
            f"Invalid approval status '{status}'. Allowed: {sorted(VALID_APPROVAL_STATUSES)}"
        )
    return normalized

