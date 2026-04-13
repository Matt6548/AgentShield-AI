"""Service-layer orchestration for SafeCore guarded dry-run API."""

from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from src.approval import (
    APPROVAL_STATUS_APPROVED,
    ApprovalEscalation,
    ApprovalManager,
    ESCALATION_STATE_NONE,
    EscalationPolicy,
)
from src.audit import AuditLogger
from src.connectors import ConnectorExecutor
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.model_router import ModelRouter
from src.policy import PolicyEngine
from src.policy.policy_engine import (
    DECISION_DENY,
    DECISION_NEEDS_APPROVAL,
    POLICY_PACK_V1,
    VALID_POLICY_PACKS,
)
from src.utils.contract_validation import (
    ContractValidationError,
    validate_audit_record,
    validate_safety_decision,
    validate_tool_call,
)
from src.utils.observability import Observability
from src.utils.tool_policies import ToolGuard


class GuardedExecutionService:
    """Orchestrate policy/data/tool/approval/routing/execution/audit for API requests."""

    def __init__(
        self,
        policy_engine: PolicyEngine | None = None,
        data_guard: DataGuard | None = None,
        tool_guard: ToolGuard | None = None,
        execution_guard: ExecutionGuard | None = None,
        audit_logger: AuditLogger | None = None,
        approval_manager: ApprovalManager | None = None,
        approval_escalation: ApprovalEscalation | None = None,
        model_router: ModelRouter | None = None,
        connector_executor: ConnectorExecutor | None = None,
        observability: Observability | None = None,
    ) -> None:
        env_policy_pack = os.getenv("SAFECORE_POLICY_PACK", POLICY_PACK_V1)
        normalized_env_pack = self._normalize_policy_pack(env_policy_pack)
        self.policy_engine = policy_engine or PolicyEngine(
            opa_binary="definitely-not-opa",
            policy_pack=normalized_env_pack,
        )
        self.default_policy_pack = self._normalize_policy_pack(
            getattr(self.policy_engine, "policy_pack", normalized_env_pack)
        )
        self.data_guard = data_guard or DataGuard()
        self.tool_guard = tool_guard or ToolGuard()
        self.execution_guard = execution_guard or ExecutionGuard(tool_guard=self.tool_guard)
        self.audit_logger = audit_logger or AuditLogger()
        self.approval_manager = approval_manager or ApprovalManager(audit_logger=self.audit_logger)
        self.approval_escalation = approval_escalation or ApprovalEscalation(
            self.approval_manager,
            policy=EscalationPolicy(
                escalate_after_seconds=self._env_int(
                    "SAFECORE_APPROVAL_ESCALATE_AFTER_SECONDS",
                    300,
                ),
                expire_after_seconds=self._env_int(
                    "SAFECORE_APPROVAL_EXPIRE_AFTER_SECONDS",
                    900,
                ),
                escalation_target=os.getenv(
                    "SAFECORE_APPROVAL_ESCALATION_TARGET",
                    "security-oncall",
                ),
            ),
        )
        self.model_router = model_router or ModelRouter()
        self.connector_executor = connector_executor or ConnectorExecutor()
        self.observability = observability or Observability()

    def execute_guarded_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Process one guarded dry-run request and return structured output."""
        if not isinstance(request, dict):
            raise TypeError("GuardedExecutionService.execute_guarded_request expects a dict request.")

        run_id = str(request.get("run_id", "run-unknown"))
        actor = str(request.get("actor", "unknown"))
        payload = request.get("payload", {})
        if not isinstance(payload, dict):
            payload = {"raw_payload": payload}
        requested_dry_run = bool(request.get("dry_run", True))
        try:
            selected_policy_pack = self._resolve_policy_pack(request)
        except ValueError as exc:
            return self._validation_failure_response(
                run_id=run_id,
                actor=actor,
                request=request,
                stage="policy_pack_selection",
                validation_error=str(exc),
            )

        policy_input = self._build_policy_input(request, actor=actor, payload=payload)
        policy_input["policy_pack"] = selected_policy_pack

        self.observability.emit_event(
            run_id=run_id,
            stage="request",
            status="RECEIVED",
            decision_summary="N/A",
            details={
                "tool": policy_input["tool"],
                "action": policy_input["action"],
                "requested_dry_run": requested_dry_run,
                "policy_pack": selected_policy_pack,
            },
        )

        policy_timer = self.observability.start_timer()
        try:
            policy_decision = self.policy_engine.evaluate(
                policy_input,
                policy_pack=selected_policy_pack,
            )
        except TypeError as exc:
            # Backward compatibility: support legacy custom test stubs that do not
            # accept policy_pack keyword arguments.
            if "policy_pack" not in str(exc):
                raise
            policy_decision = self.policy_engine.evaluate(policy_input)
        try:
            validate_safety_decision(policy_decision)
        except ContractValidationError as exc:
            return self._validation_failure_response(
                run_id=run_id,
                actor=actor,
                request=request,
                stage="policy_decision",
                validation_error=str(exc),
            )
        self._emit_stage_event(
            run_id=run_id,
            stage="policy",
            status=policy_decision["decision"],
            policy_decision=policy_decision,
            timer_token=policy_timer,
        )

        data_timer = self.observability.start_timer()
        data_guard_result = self.data_guard.evaluate(payload)
        self._emit_stage_event(
            run_id=run_id,
            stage="data_guard",
            status=data_guard_result["action"],
            policy_decision=policy_decision,
            details={"risk_score": data_guard_result["risk_score"]},
            timer_token=data_timer,
        )

        tool_timer = self.observability.start_timer()
        tool_guard_result = self.tool_guard.evaluate(policy_input)
        self._emit_stage_event(
            run_id=run_id,
            stage="tool_guard",
            status=tool_guard_result["decision"],
            policy_decision=policy_decision,
            details={"allowed": bool(tool_guard_result["allowed"])},
            timer_token=tool_timer,
        )

        blockers: list[str] = []
        approval_state = {
            "required": False,
            "status": "BYPASSED",
            "request_id": None,
            "approver": None,
            "reason": "",
            "escalation": {
                "state": ESCALATION_STATE_NONE,
                "target": None,
                "reason": "",
                "updated_at": None,
                "elapsed_seconds": 0,
            },
        }

        approval_timer = self.observability.start_timer()
        approval_outcome = self._handle_approval_gate(
            request=request,
            run_id=run_id,
            actor=actor,
            policy_decision=policy_decision,
        )
        approval_state.update(approval_outcome["approval"])
        blockers.extend(approval_outcome["blockers"])
        self._emit_stage_event(
            run_id=run_id,
            stage="approval",
            status=approval_state["status"],
            policy_decision=policy_decision,
            details={"required": bool(approval_state["required"])},
            timer_token=approval_timer,
        )
        self._emit_stage_event(
            run_id=run_id,
            stage="escalation",
            status=str(approval_state["escalation"]["state"]),
            policy_decision=policy_decision,
            details={"target": approval_state["escalation"]["target"]},
        )

        route_timer = self.observability.start_timer()
        model_route = self.model_router.route(policy_decision=policy_decision, context=policy_input)
        self._emit_stage_event(
            run_id=run_id,
            stage="model_routing",
            status=model_route["route_id"],
            policy_decision=policy_decision,
            details={
                "model_profile": model_route["model_profile"],
                "action_class": model_route["action_class"],
                "profile_id": model_route.get("profile_id"),
            },
            timer_token=route_timer,
        )

        if data_guard_result["action"] == "BLOCK":
            blockers.append("data_guard:BLOCK")
        if not tool_guard_result["allowed"]:
            blockers.append(f"tool_guard:{tool_guard_result['decision']}")
        if not requested_dry_run:
            blockers.append("execution:NON_DRY_RUN_NOT_SUPPORTED")

        connector_timer = self.observability.start_timer()
        connector_execution = self.connector_executor.execute(
            request=policy_input,
            dry_run=True,
            blocked_by=blockers,
        )
        self._emit_stage_event(
            run_id=run_id,
            stage="connector_execution",
            status=connector_execution["status"],
            policy_decision=policy_decision,
            details={
                "adapter_id": connector_execution["adapter_id"],
                "connector": connector_execution["connector"],
            },
            timer_token=connector_timer,
        )
        if str(connector_execution.get("status", "")).upper() == "INVALID_INPUT":
            blockers.append("connector:INVALID_INPUT")

        execution_timer = self.observability.start_timer()
        execution_request = deepcopy(policy_input)
        execution_request["blocked_by"] = list(blockers)
        execution_result = self.execution_guard.execute(execution_request, dry_run=True)
        execution_status = "INVALID_RESULT"
        execution_success = False
        if isinstance(execution_result, dict):
            execution_success = bool(execution_result.get("success", False))
            output = execution_result.get("output", {})
            if isinstance(output, dict):
                execution_status = str(output.get("status", "INVALID_RESULT"))
        self._emit_stage_event(
            run_id=run_id,
            stage="execution",
            status=execution_status,
            policy_decision=policy_decision,
            details={"success": execution_success},
            timer_token=execution_timer,
        )
        try:
            validate_tool_call(execution_result)
        except ContractValidationError as exc:
            return self._validation_failure_response(
                run_id=run_id,
                actor=actor,
                request=request,
                stage="execution_result",
                validation_error=str(exc),
                policy_decision=policy_decision,
                data_guard_result=data_guard_result,
                tool_guard_result=tool_guard_result,
                approval_state=approval_state,
                model_route=model_route,
                connector_execution=connector_execution,
            )

        response = {
            "run_id": run_id,
            "actor": actor,
            "dry_run": True,
            "requested_dry_run": requested_dry_run,
            "policy_pack": selected_policy_pack,
            "blocked": bool(blockers),
            "blockers": blockers,
            "policy_decision": policy_decision,
            "data_guard_result": data_guard_result,
            "tool_guard_result": tool_guard_result,
            "approval": approval_state,
            "model_route": model_route,
            "execution_result": execution_result,
            "connector_execution": connector_execution,
        }

        audit_timer = self.observability.start_timer()
        try:
            audit_record = self._append_validated_audit_record(
                run_id=run_id,
                actor=actor,
                step="api",
                action="api_guarded_execute",
                data={
                    "blocked": response["blocked"],
                    "blockers": response["blockers"],
                    "policy_decision": policy_decision["decision"],
                    "approval_status": approval_state["status"],
                    "escalation_state": approval_state["escalation"]["state"],
                    "route_id": model_route["route_id"],
                    "execution_status": execution_result["output"]["status"],
                    "connector_status": connector_execution["status"],
                    "policy_pack": selected_policy_pack,
                },
            )
        except ContractValidationError as exc:
            return self._validation_failure_response(
                run_id=run_id,
                actor=actor,
                request=request,
                stage="audit_record",
                validation_error=str(exc),
                policy_decision=policy_decision,
                data_guard_result=data_guard_result,
                tool_guard_result=tool_guard_result,
                approval_state=approval_state,
                model_route=model_route,
                connector_execution=connector_execution,
            )
        self._emit_stage_event(
            run_id=run_id,
            stage="audit",
            status="RECORDED",
            policy_decision=policy_decision,
            details={"action": audit_record["action"]},
            timer_token=audit_timer,
        )

        response["audit_record"] = audit_record
        integrity_timer = self.observability.start_timer()
        audit_integrity = self._verify_audit_integrity()
        if not bool(audit_integrity.get("valid", False)):
            blockers.append("audit_integrity:BROKEN_CHAIN")
        self._emit_stage_event(
            run_id=run_id,
            stage="audit_integrity",
            status="VALID" if bool(audit_integrity.get("valid", False)) else "BROKEN",
            policy_decision=policy_decision,
            details={
                "record_count": int(audit_integrity.get("record_count", 0)),
                "broken_indices": list(audit_integrity.get("broken_indices", [])),
            },
            timer_token=integrity_timer,
        )
        response["blocked"] = bool(blockers)
        response["blockers"] = blockers
        response["audit_integrity"] = audit_integrity
        response["observability"] = self.observability.snapshot(run_id=run_id)
        return response

    def _build_policy_input(
        self,
        request: dict[str, Any],
        actor: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        policy_input = deepcopy(request)
        policy_input["run_id"] = str(request.get("run_id", "run-unknown"))
        policy_input["user"] = actor
        policy_input["payload"] = payload
        policy_input["params"] = request.get("params", {})
        policy_input["environment"] = request.get("environment", request.get("env", ""))
        policy_input["target"] = request.get("target", request.get("target_system", ""))
        policy_input["tool"] = str(request.get("tool", ""))
        policy_input["command"] = str(request.get("command", ""))
        policy_input["action"] = str(request.get("action", ""))
        policy_input["actor"] = actor
        policy_input["policy_pack"] = request.get("policy_pack", self.default_policy_pack)
        return policy_input

    def _handle_approval_gate(
        self,
        request: dict[str, Any],
        run_id: str,
        actor: str,
        policy_decision: dict[str, Any],
    ) -> dict[str, Any]:
        blockers: list[str] = []
        approval = {
            "required": False,
            "status": "BYPASSED",
            "request_id": None,
            "approver": None,
            "reason": "",
            "escalation": {
                "state": ESCALATION_STATE_NONE,
                "target": None,
                "reason": "",
                "updated_at": None,
                "elapsed_seconds": 0,
            },
        }

        if policy_decision["decision"] == DECISION_DENY:
            blockers.append("policy:DENY")
            approval["status"] = "NOT_APPLICABLE_DENY"
            return {"approval": approval, "blockers": blockers}

        if not self.approval_manager.is_required(
            policy_decision["risk_score"],
            policy_decision["decision"],
        ):
            return {"approval": approval, "blockers": blockers}

        approval["required"] = True
        approval_payload = request.get("approval")
        context = {
            "run_id": run_id,
            "actor": actor,
            "policy_decision": policy_decision["decision"],
            "risk_score": policy_decision["risk_score"],
            "context": request,
        }

        if approval_payload is None:
            created = self.approval_manager.create_request(context)
            evaluated = self.approval_escalation.evaluate_request(created["request_id"]) or created
            approval.update(
                {
                    "status": evaluated["status"],
                    "request_id": evaluated["request_id"],
                    "escalation": self._extract_escalation_state(evaluated),
                }
            )
            blockers.append(f"approval:{approval['status']}")
            return {"approval": approval, "blockers": blockers}

        request_id = approval_payload.get("request_id")
        decision_raw = approval_payload.get("decision")
        decision = str(decision_raw).upper() if decision_raw is not None else ""
        approver = str(approval_payload.get("approver", ""))
        reason = str(approval_payload.get("reason", ""))

        if request_id:
            existing = self.approval_manager.get_request(request_id)
            if existing is None:
                approval.update(
                    {
                        "status": "REJECTED",
                        "request_id": request_id,
                        "approver": approver or None,
                        "reason": "Unknown approval request_id.",
                    }
                )
                blockers.append("approval:REJECTED")
                return {"approval": approval, "blockers": blockers}
        else:
            created = self.approval_manager.create_request(context)
            request_id = created["request_id"]

        if not decision:
            pending = self.approval_escalation.evaluate_request(request_id) or self.approval_manager.get_request(
                request_id
            )
            if pending is None:
                approval.update(
                    {
                        "status": "REJECTED",
                        "request_id": request_id,
                        "approver": approver or None,
                        "reason": "Approval request no longer exists.",
                    }
                )
                blockers.append("approval:REJECTED")
                return {"approval": approval, "blockers": blockers}

            approval.update(
                {
                    "status": pending["status"],
                    "request_id": pending["request_id"],
                    "approver": pending.get("approver"),
                    "reason": pending.get("reason", ""),
                    "escalation": self._extract_escalation_state(pending),
                }
            )
            blockers.append(f"approval:{approval['status']}")
            return {"approval": approval, "blockers": blockers}

        try:
            decided = self.approval_manager.decide(
                request_id=request_id,
                decision=decision,
                approver=approver,
                reason=reason,
            )
            approval.update(
                {
                    "status": decided["status"],
                    "request_id": decided["request_id"],
                    "approver": decided["approver"],
                    "reason": decided["reason"],
                    "escalation": self._extract_escalation_state(decided),
                }
            )
        except Exception as exc:  # noqa: BLE001
            approval.update(
                {
                    "status": "REJECTED",
                    "request_id": request_id,
                    "approver": approver or None,
                    "reason": f"Approval processing failed: {exc}",
                }
            )
            blockers.append("approval:REJECTED")
            return {"approval": approval, "blockers": blockers}

        if approval["status"] != APPROVAL_STATUS_APPROVED:
            blockers.append(f"approval:{approval['status']}")
        return {"approval": approval, "blockers": blockers}

    def _append_validated_audit_record(
        self,
        run_id: str,
        actor: str,
        step: str,
        action: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        record = self.audit_logger.append_record(
            {
                "run_id": run_id,
                "actor": actor,
                "step": step,
                "action": action,
                "data": data,
            }
        )
        validate_audit_record(record)
        return record

    def _validation_failure_response(
        self,
        run_id: str,
        actor: str,
        request: dict[str, Any],
        stage: str,
        validation_error: str,
        policy_decision: dict[str, Any] | None = None,
        data_guard_result: dict[str, Any] | None = None,
        tool_guard_result: dict[str, Any] | None = None,
        approval_state: dict[str, Any] | None = None,
        model_route: dict[str, Any] | None = None,
        connector_execution: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        blockers: list[str] = [f"contract_validation:{stage}"]
        if not bool(request.get("dry_run", True)):
            blockers.append("execution:NON_DRY_RUN_NOT_SUPPORTED")

        safe_policy = policy_decision or {
            "decision": DECISION_NEEDS_APPROVAL,
            "risk_score": 50,
            "reasons": [f"Contract validation failed at stage '{stage}'."],
            "constraints": ["Block execution until contract mismatch is resolved."],
            "operator_checks": [validation_error],
        }
        safe_data_guard = data_guard_result or {
            "allowed": False,
            "risk_score": 100,
            "findings": [f"Contract validation failure at stage '{stage}'."],
            "redacted_payload": {},
            "action": "BLOCK",
        }
        safe_tool_guard = tool_guard_result or {
            "allowed": False,
            "decision": DECISION_DENY,
            "risk_score": 100,
            "reasons": [f"Contract validation failure at stage '{stage}'."],
            "tool": str(request.get("tool", "")),
            "command": str(request.get("command", "")),
        }
        safe_approval = approval_state or {
            "required": False,
            "status": "REJECTED",
            "request_id": None,
            "approver": None,
            "reason": "Contract validation failed.",
            "escalation": {
                "state": ESCALATION_STATE_NONE,
                "target": None,
                "reason": "Contract validation failed.",
                "updated_at": None,
                "elapsed_seconds": 0,
            },
        }
        if "escalation" not in safe_approval or not isinstance(safe_approval["escalation"], dict):
            safe_approval["escalation"] = {
                "state": ESCALATION_STATE_NONE,
                "target": None,
                "reason": "",
                "updated_at": None,
                "elapsed_seconds": 0,
            }

        if safe_policy.get("decision") == DECISION_DENY:
            blockers.append("policy:DENY")
        if safe_data_guard.get("action") == "BLOCK":
            blockers.append("data_guard:BLOCK")
        if not bool(safe_tool_guard.get("allowed", False)):
            blockers.append(f"tool_guard:{safe_tool_guard.get('decision', 'DENY')}")
        if safe_approval.get("status") not in {"BYPASSED", "APPROVED", "NOT_APPLICABLE_DENY"}:
            blockers.append(f"approval:{safe_approval.get('status', 'REJECTED')}")

        safe_model_route = model_route or self.model_router.route(
            policy_decision=safe_policy,
            context=self._build_policy_input(
                request=request,
                actor=actor,
                payload=request.get("payload", {}) if isinstance(request.get("payload", {}), dict) else {},
            ),
        )

        execution_result = self.execution_guard.execute(
            {
                "tool": str(request.get("tool", "")),
                "command": str(request.get("command", "")),
                "blocked_by": blockers,
            },
            dry_run=True,
        )
        try:
            validate_tool_call(execution_result)
        except ContractValidationError:
            execution_result = self._fallback_blocked_tool_call(
                tool=str(request.get("tool", "")),
                command=str(request.get("command", "")),
                blockers=blockers,
            )

        safe_connector_execution = connector_execution or self.connector_executor.execute(
            request=self._build_policy_input(
                request=request,
                actor=actor,
                payload=request.get("payload", {}) if isinstance(request.get("payload", {}), dict) else {},
            ),
            dry_run=True,
            blocked_by=blockers,
        )
        if str(safe_connector_execution.get("status", "")).upper() == "INVALID_INPUT":
            blockers.append("connector:INVALID_INPUT")

        self.observability.emit_event(
            run_id=run_id,
            stage="contract_validation",
            status="FAILED",
            decision_summary=self._decision_summary(safe_policy),
            details={
                "stage": stage,
                "validation_error": validation_error,
                "blockers": blockers,
            },
        )
        self.observability.emit_event(
            run_id=run_id,
            stage="execution",
            status=execution_result["output"]["status"],
            decision_summary=self._decision_summary(safe_policy),
            details={"success": bool(execution_result["success"])},
        )
        self.observability.emit_event(
            run_id=run_id,
            stage="connector_execution",
            status=safe_connector_execution["status"],
            decision_summary=self._decision_summary(safe_policy),
            details={
                "adapter_id": safe_connector_execution["adapter_id"],
                "connector": safe_connector_execution["connector"],
            },
        )

        audit_record = self._safe_append_failure_audit(
            run_id=run_id,
            actor=actor,
            stage=stage,
            validation_error=validation_error,
            blockers=blockers,
        )

        self.observability.emit_event(
            run_id=run_id,
            stage="escalation",
            status=str(safe_approval["escalation"]["state"]),
            decision_summary=self._decision_summary(safe_policy),
            details={"target": safe_approval["escalation"]["target"]},
        )
        self.observability.emit_event(
            run_id=run_id,
            stage="audit",
            status="RECORDED",
            decision_summary=self._decision_summary(safe_policy),
            details={"action": audit_record["action"]},
        )
        audit_integrity = self._verify_audit_integrity()
        if not bool(audit_integrity.get("valid", False)):
            blockers.append("audit_integrity:BROKEN_CHAIN")
        self.observability.emit_event(
            run_id=run_id,
            stage="audit_integrity",
            status="VALID" if bool(audit_integrity.get("valid", False)) else "BROKEN",
            decision_summary=self._decision_summary(safe_policy),
            details={
                "record_count": int(audit_integrity.get("record_count", 0)),
                "broken_indices": list(audit_integrity.get("broken_indices", [])),
            },
        )

        return {
            "run_id": run_id,
            "actor": actor,
            "dry_run": True,
            "requested_dry_run": bool(request.get("dry_run", True)),
            "policy_pack": self._safe_policy_pack(request.get("policy_pack")),
            "blocked": True,
            "blockers": blockers,
            "policy_decision": safe_policy,
            "data_guard_result": safe_data_guard,
            "tool_guard_result": safe_tool_guard,
            "approval": safe_approval,
            "model_route": safe_model_route,
            "execution_result": execution_result,
            "connector_execution": safe_connector_execution,
            "audit_record": audit_record,
            "audit_integrity": audit_integrity,
            "observability": self.observability.snapshot(run_id=run_id),
        }

    def _safe_append_failure_audit(
        self,
        run_id: str,
        actor: str,
        stage: str,
        validation_error: str,
        blockers: list[str],
    ) -> dict[str, Any]:
        try:
            record = self.audit_logger.append_record(
                {
                    "run_id": run_id,
                    "actor": actor,
                    "step": "api",
                    "action": "api_guarded_execute_validation_failure",
                    "data": {
                        "stage": stage,
                        "validation_error": validation_error,
                        "blockers": blockers,
                    },
                }
            )
            validate_audit_record(record)
            return record
        except Exception:  # noqa: BLE001
            return self._fallback_audit_record(run_id, actor, stage, validation_error, blockers)

    def _fallback_blocked_tool_call(
        self,
        tool: str,
        command: str,
        blockers: list[str],
    ) -> dict[str, Any]:
        return {
            "tool": tool,
            "command": command,
            "success": False,
            "output": {
                "status": "BLOCKED",
                "dry_run": True,
                "reasons": blockers,
                "validation": {},
            },
            "timestamp": self._now_iso(),
        }

    def _fallback_audit_record(
        self,
        run_id: str,
        actor: str,
        stage: str,
        validation_error: str,
        blockers: list[str],
    ) -> dict[str, Any]:
        return {
            "timestamp": self._now_iso(),
            "run_id": run_id,
            "actor": actor,
            "step": "api",
            "action": "api_guarded_execute_validation_failure",
            "data": {
                "stage": stage,
                "validation_error": validation_error,
                "blockers": blockers,
            },
            "hash": "fallback_hash",
        }

    def _emit_stage_event(
        self,
        *,
        run_id: str,
        stage: str,
        status: str,
        policy_decision: dict[str, Any],
        details: dict[str, Any] | None = None,
        timer_token: float | None = None,
    ) -> None:
        duration_ms = self.observability.stop_timer(timer_token) if timer_token is not None else None
        self.observability.emit_event(
            run_id=run_id,
            stage=stage,
            status=status,
            decision_summary=self._decision_summary(policy_decision),
            details=details,
            duration_ms=duration_ms,
        )

    def _decision_summary(self, policy_decision: dict[str, Any]) -> str:
        decision = str(policy_decision.get("decision", "UNKNOWN"))
        risk_score = int(policy_decision.get("risk_score", 0))
        return f"{decision}:{risk_score}"

    def _extract_escalation_state(self, approval_request: dict[str, Any]) -> dict[str, Any]:
        try:
            elapsed_seconds = int(approval_request.get("escalation_elapsed_seconds", 0))
        except (TypeError, ValueError):
            elapsed_seconds = 0
        return {
            "state": str(approval_request.get("escalation_state", ESCALATION_STATE_NONE)),
            "target": approval_request.get("escalation_target"),
            "reason": str(approval_request.get("escalation_reason", "")),
            "updated_at": approval_request.get("escalation_updated_at"),
            "elapsed_seconds": max(0, elapsed_seconds),
        }

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _env_int(self, key: str, default: int) -> int:
        raw = os.getenv(key)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            return default

    def _resolve_policy_pack(self, request: dict[str, Any]) -> str:
        requested_pack = request.get("policy_pack")
        if requested_pack is None:
            return self.default_policy_pack
        return self._normalize_policy_pack(str(requested_pack))

    def _normalize_policy_pack(self, value: str) -> str:
        normalized = str(value).strip().lower()
        if normalized not in VALID_POLICY_PACKS:
            raise ValueError(
                f"Unsupported policy_pack '{value}'. Supported values: {sorted(VALID_POLICY_PACKS)}"
            )
        return normalized

    def _safe_policy_pack(self, value: Any) -> str:
        try:
            return self._normalize_policy_pack(str(value if value is not None else self.default_policy_pack))
        except ValueError:
            return self.default_policy_pack

    def _verify_audit_integrity(self) -> dict[str, Any]:
        try:
            report = self.audit_logger.verify_integrity()
        except Exception as exc:  # noqa: BLE001
            return {
                "valid": False,
                "record_count": 0,
                "verified_count": 0,
                "broken_indices": [],
                "errors": [f"audit_integrity_check_failed: {exc}"],
                "file_path": str(getattr(self.audit_logger, "file_path", "")),
            }

        if not isinstance(report, dict):
            return {
                "valid": False,
                "record_count": 0,
                "verified_count": 0,
                "broken_indices": [],
                "errors": ["audit_integrity_report_invalid_type"],
                "file_path": str(getattr(self.audit_logger, "file_path", "")),
            }

        broken_indices_raw = report.get("broken_indices", [])
        broken_indices: list[int] = []
        if isinstance(broken_indices_raw, list):
            for item in broken_indices_raw:
                try:
                    broken_indices.append(int(item))
                except (TypeError, ValueError):
                    continue

        try:
            record_count = int(report.get("record_count", 0))
        except (TypeError, ValueError):
            record_count = 0
        try:
            verified_count = int(report.get("verified_count", 0))
        except (TypeError, ValueError):
            verified_count = 0

        normalized = {
            "valid": bool(report.get("valid", False)),
            "record_count": max(0, record_count),
            "verified_count": max(0, verified_count),
            "broken_indices": broken_indices,
            "errors": [str(item) for item in report.get("errors", [])],
            "file_path": str(report.get("file_path", str(getattr(self.audit_logger, "file_path", "")))),
        }
        return normalized
