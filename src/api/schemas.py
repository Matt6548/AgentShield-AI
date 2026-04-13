"""Pydantic schemas for SafeCore API skeleton."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ApprovalDecisionPayload(BaseModel):
    """Approval decision payload for guarded execution requests."""

    request_id: str | None = None
    decision: Literal["APPROVED", "REJECTED"] | None = None
    approver: str = ""
    reason: str = ""


class GuardedExecutionRequest(BaseModel):
    """Request schema for guarded dry-run execution."""

    run_id: str
    actor: str
    action: str
    tool: str
    command: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    environment: str | None = None
    target: str | None = None
    dry_run: bool = True
    policy_pack: Literal["v1", "v2"] | None = None
    approval: ApprovalDecisionPayload | None = None

    model_config = ConfigDict(extra="allow")


class ApprovalState(BaseModel):
    """Approval state returned by guarded execution."""

    class EscalationState(BaseModel):
        """Escalation metadata for pending approvals."""

        state: Literal["NONE", "ESCALATED", "EXPIRED"]
        target: str | None = None
        reason: str = ""
        updated_at: str | None = None
        elapsed_seconds: int = 0

    required: bool
    status: str
    request_id: str | None = None
    approver: str | None = None
    reason: str = ""
    escalation: EscalationState


class ModelRouteResponse(BaseModel):
    """Model router decision payload."""

    route_id: str
    model_profile: str
    reason: str
    constraints: list[str]
    action_class: str
    profile_id: str | None = None
    profile_name: str | None = None
    profile_reason: str | None = None
    profile_guardrails: list[str] = Field(default_factory=list)

    model_config = ConfigDict(protected_namespaces=())


class ConnectorExecutionResponse(BaseModel):
    """Normalized connector adapter execution response."""

    adapter_id: str
    connector: str
    tool: str
    dry_run: bool
    status: str
    success: bool
    reasons: list[str]
    normalized_request: dict[str, Any]
    raw_result: dict[str, Any]


class ObservabilitySnapshotResponse(BaseModel):
    """Per-run observability summary."""

    counters: dict[str, int]
    timers: dict[str, dict[str, int]]
    event_count: int


class AuditIntegrityResponse(BaseModel):
    """Audit chain integrity summary."""

    valid: bool
    record_count: int
    verified_count: int
    broken_indices: list[int]
    errors: list[str]
    file_path: str


class GuardedExecutionResponse(BaseModel):
    """Response schema for guarded dry-run execution."""

    run_id: str
    actor: str
    dry_run: bool
    requested_dry_run: bool
    policy_pack: Literal["v1", "v2"]
    blocked: bool
    blockers: list[str]
    policy_decision: dict[str, Any]
    data_guard_result: dict[str, Any]
    tool_guard_result: dict[str, Any]
    approval: ApprovalState
    model_route: ModelRouteResponse
    execution_result: dict[str, Any]
    connector_execution: ConnectorExecutionResponse
    audit_record: dict[str, Any]
    audit_integrity: AuditIntegrityResponse
    observability: ObservabilitySnapshotResponse

    model_config = ConfigDict(protected_namespaces=())


class HealthResponse(BaseModel):
    """Health endpoint response schema."""

    status: Literal["ok"]
    service: str
    dry_run_only: bool
