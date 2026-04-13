"""Optional advisory-only safety copilot for the product shell."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Literal, Protocol
from urllib import error, parse, request

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from src.api.ui_i18n import normalize_ui_lang, tr
from src.utils.safe_http import SAFE_HTTP_TOOL

DEFAULT_MODE = "disabled"
DEFAULT_PROVIDER = "openai_compatible"
DEFAULT_MODEL = "safecore-safety-copilot"
SAFE_MODES = {"disabled", "local_only", "external"}

TOKEN_PATTERNS = (
    (re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"\b(?:Bearer|bearer)\s+[A-Za-z0-9\-._~+/]+=*\b"), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*([^\s,;]+)"), r"\1=[REDACTED]"),
    (re.compile(r"\b[A-Za-z0-9_-]{24,}\b"), "[REDACTED_TOKEN]"),
)
UNSAFE_OUTPUT_PATTERNS = (
    re.compile(r"````?"),
    re.compile(r"https?://", re.IGNORECASE),
    re.compile(r"\b(?:curl|wget|powershell|bash|rm|sudo|Invoke-WebRequest)\b", re.IGNORECASE),
    re.compile(r"\b(?:ignore previous|override|change decision|force allow)\b", re.IGNORECASE),
)


class SafetyContext(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user_intent: str = Field(min_length=1, max_length=240)
    planned_tools: list[str] = Field(default_factory=list)
    policy_result: Literal["ALLOW", "NEEDS_APPROVAL", "DENY"]
    risk_factors: list[str] = Field(default_factory=list)
    approval_needed_reason: str | None = Field(default=None, max_length=240)
    audit_id: str = Field(min_length=1, max_length=240)
    lang: Literal["en", "ru", "uz"] = "en"

    @field_validator("user_intent", "approval_needed_reason", "audit_id", mode="before")
    @classmethod
    def _validate_text(cls, value: Any) -> str | None:
        if value is None:
            return None
        return _sanitize(value)

    @field_validator("planned_tools", "risk_factors", mode="before")
    @classmethod
    def _validate_list(cls, value: Any) -> list[str]:
        items = value if isinstance(value, list) else ([value] if value not in (None, "") else [])
        return [_sanitize(item, max_length=180) for item in items if str(item).strip()][:4]


class AssistantInsight(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    advisory_only: Literal[True] = True
    summary: str = Field(min_length=1, max_length=320)
    highlighted_risks: list[str] = Field(default_factory=list)
    operator_guidance: list[str] = Field(default_factory=list)
    suggested_follow_up: list[str] = Field(default_factory=list)
    policy_suggestion_summary: str | None = Field(default=None, max_length=240)

    @field_validator("summary", "policy_suggestion_summary", mode="before")
    @classmethod
    def _validate_text(cls, value: Any) -> str | None:
        if value is None:
            return None
        return _validate_advisory_text(value)

    @field_validator("highlighted_risks", "operator_guidance", "suggested_follow_up", mode="before")
    @classmethod
    def _validate_list(cls, value: Any) -> list[str]:
        items = value if isinstance(value, list) else ([value] if value not in (None, "") else [])
        return [_validate_advisory_text(item, max_length=180) for item in items if str(item).strip()][:4]


class AssistantInsightRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payload: dict[str, Any]
    lang: str | None = None
    source: str | None = Field(default="product_shell", max_length=80)


class SafetyCopilotBackend(Protocol):
    def generate_insight(self, context: SafetyContext) -> dict[str, Any]:
        ...


class LocalDeterministicSafetyCopilotBackend:
    def generate_insight(self, context: SafetyContext) -> dict[str, Any]:
        language = context.lang
        risks = context.risk_factors[:3]
        if context.policy_result == "ALLOW":
            return {
                "advisory_only": True,
                "summary": tr(
                    language,
                    en="SafeCore allowed this request inside the current guarded boundary.",
                    ru="SafeCore разрешил этот запрос внутри текущей guarded boundary.",
                    uz="SafeCore bu so'rovga joriy guarded boundary ichida ruxsat berdi.",
                ),
                "highlighted_risks": risks or [_default_risk(language, context.policy_result)],
                "operator_guidance": [
                    tr(
                        language,
                        en="Keep the action inside the same low-risk or read-only boundary.",
                        ru="Сохраняйте действие внутри той же low-risk или read-only boundary.",
                        uz="Harakatni shu low-risk yoki read-only boundary ichida saqlang.",
                    ),
                    tr(
                        language,
                        en="Use the audit record if you need evidence for this decision.",
                        ru="Используйте audit record, если вам нужно evidence для этого решения.",
                        uz="Bu qaror uchun evidence kerak bo'lsa audit record'dan foydalaning.",
                    ),
                ],
                "suggested_follow_up": [
                    tr(
                        language,
                        en="Continue with the same guarded pattern.",
                        ru="Продолжайте с тем же guarded pattern.",
                        uz="Shu guarded pattern bilan davom eting.",
                    )
                ],
                "policy_suggestion_summary": tr(
                    language,
                    en="Final decision remains ALLOW. Advisory cannot change it.",
                    ru="Итоговое решение остаётся ALLOW. Advisory не может его изменить.",
                    uz="Yakuniy qaror ALLOW bo'lib qoladi. Advisory uni o'zgartira olmaydi.",
                ),
            }
        if context.policy_result == "NEEDS_APPROVAL":
            return {
                "advisory_only": True,
                "summary": tr(
                    language,
                    en="SafeCore held this request until explicit approval exists.",
                    ru="SafeCore удержал этот запрос до появления явного approval.",
                    uz="SafeCore bu so'rovni aniq approval paydo bo'lguncha ushlab turdi.",
                ),
                "highlighted_risks": risks or [_default_risk(language, context.policy_result)],
                "operator_guidance": [
                    tr(
                        language,
                        en="Check scope, target, and reason for the approval gate before approving anything.",
                        ru="Проверьте scope, target и причину approval gate, прежде чем что-либо утверждать.",
                        uz="Har qanday tasdiqlashdan oldin scope, target va approval gate sababini tekshiring.",
                    ),
                    tr(
                        language,
                        en="Approval stays explicit. Advisory cannot authorize execution.",
                        ru="Approval остаётся явным. Advisory не может авторизовать execution.",
                        uz="Approval aniq bo'lib qoladi. Advisory execution'ni authorize qila olmaydi.",
                    ),
                ],
                "suggested_follow_up": [
                    tr(
                        language,
                        en="Review the approval queue and audit evidence.",
                        ru="Проверьте approval queue и audit evidence.",
                        uz="Approval queue va audit evidence'ni ko'rib chiqing.",
                    )
                ],
                "policy_suggestion_summary": tr(
                    language,
                    en="Final decision remains NEEDS_APPROVAL. Advisory cannot change it.",
                    ru="Итоговое решение остаётся NEEDS_APPROVAL. Advisory не может его изменить.",
                    uz="Yakuniy qaror NEEDS_APPROVAL bo'lib qoladi. Advisory uni o'zgartira olmaydi.",
                ),
            }
        return {
            "advisory_only": True,
            "summary": tr(
                language,
                en="SafeCore blocked this request because it crossed a protected boundary.",
                ru="SafeCore заблокировал этот запрос, потому что он пересёк защищённую boundary.",
                uz="SafeCore bu so'rovni blokladi, chunki u himoyalangan boundary'dan o'tdi.",
            ),
            "highlighted_risks": risks or [_default_risk(language, context.policy_result)],
            "operator_guidance": [
                tr(
                    language,
                    en="Do not bypass the block. Reduce scope or switch to an allowlisted read-only path.",
                    ru="Не обходите блок. Сузьте scope или переключитесь на allowlisted read-only path.",
                    uz="Blokni chetlab o'tmang. Scope'ni toraytiring yoki allowlisted read-only path'ga o'ting.",
                ),
                tr(
                    language,
                    en="Use the audit record to explain the block.",
                    ru="Используйте audit record, чтобы объяснить блокировку.",
                    uz="Blokni tushuntirish uchun audit record'dan foydalaning.",
                ),
            ],
            "suggested_follow_up": [
                tr(
                    language,
                    en="Submit a smaller explicitly safe request if needed.",
                    ru="При необходимости отправьте меньший и явно безопасный запрос.",
                    uz="Kerak bo'lsa kichikroq va aniq xavfsiz so'rov yuboring.",
                )
            ],
            "policy_suggestion_summary": tr(
                language,
                en="Final decision remains DENY. Advisory cannot change it.",
                ru="Итоговое решение остаётся DENY. Advisory не может его изменить.",
                uz="Yakuniy qaror DENY bo'lib qoladi. Advisory uni o'zgartira olmaydi.",
            ),
        }


class ExternalOpenAICompatibleSafetyCopilotBackend:
    def __init__(self, *, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def generate_insight(self, context: SafetyContext) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Safety Copilot for SafeCore. Advisory only. Never change the final decision. "
                        "Never suggest bypassing controls. Return JSON only with keys summary, highlighted_risks, "
                        "operator_guidance, suggested_follow_up, policy_suggestion_summary. No code, commands, URLs, or secrets."
                    ),
                },
                {"role": "user", "content": json.dumps(context.model_dump(), ensure_ascii=False)},
            ],
            "response_format": {"type": "json_object"},
        }
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=15) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except (error.URLError, json.JSONDecodeError) as exc:
            raise ValueError("Assistant provider request failed.") from exc
        try:
            content = parsed["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("Assistant provider returned an unexpected response shape.") from exc
        if isinstance(content, list):
            content = "".join(str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in content)
        if not isinstance(content, str):
            raise ValueError("Assistant provider did not return a text content field.")
        try:
            candidate = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Assistant provider did not return valid JSON.") from exc
        if not isinstance(candidate, dict):
            raise ValueError("Assistant provider JSON must be an object.")
        return candidate


class SafetyCopilotService:
    def __init__(self, *, backend: SafetyCopilotBackend | None = None) -> None:
        self._backend_override = backend

    def capabilities(self, lang: str | None = None) -> dict[str, Any]:
        selected_lang = normalize_ui_lang(lang)
        runtime = self._resolve_runtime()
        enabled = bool(runtime["enabled"])
        return {
            "enabled": enabled,
            "configured": bool(runtime["configured"]),
            "mode": str(runtime["mode"]),
            "provider": str(runtime["provider"]),
            "model": str(runtime["model"]),
            "base_url": runtime["base_url_label"],
            "key_status": runtime["key_status"],
            "external_sharing": bool(runtime["external_sharing"]),
            "advisory_only": True,
            "headline": tr(selected_lang, en="Safety Copilot Advisory", ru="Safety Copilot Advisory", uz="Safety Copilot Advisory"),
            "subtext": tr(
                selected_lang,
                en="Optional plain-language guidance for the latest guarded result. It never changes the final decision.",
                ru="Необязательное plain-language guidance для последнего guarded result. Оно не меняет итоговое решение.",
                uz="So'nggi guarded result uchun ixtiyoriy plain-language guidance. U yakuniy qarorni o'zgartirmaydi.",
            ),
            "safe_note": tr(
                selected_lang,
                en="Only a minimized safety snapshot is used. Raw secrets, env values, and full payload dumps are not forwarded.",
                ru="Используется только минимизированный safety snapshot. Сырые секреты, env values и полные payload dumps не пересылаются.",
                uz="Faqat minimallashtirilgan safety snapshot ishlatiladi. Xom sirlar, env values va to'liq payload dumps uzatilmaydi.",
            ),
            "status_label": tr(selected_lang, en="Enabled" if enabled else "Disabled", ru="Включено" if enabled else "Отключено", uz="Yoqilgan" if enabled else "O'chirilgan"),
            "availability_reason": runtime["reason"] or tr(selected_lang, en="Assistant insight is ready for advisory-only use.", ru="Assistant insight готов для advisory-only использования.", uz="Assistant insight advisory-only foydalanish uchun tayyor."),
            "how_to_enable": self._how_to_enable(selected_lang, enabled=enabled, mode=str(runtime["mode"])),
            "data_scope": [
                tr(selected_lang, en="User intent summary", ru="Краткое описание user intent", uz="User intent qisqacha mazmuni"),
                tr(selected_lang, en="Planned tools", ru="Планируемые инструменты", uz="Rejalashtirilgan tool'lar"),
                tr(selected_lang, en="Policy result and risk factors", ru="Policy result и факторы риска", uz="Policy result va risk factors"),
                tr(selected_lang, en="Approval reason and audit id", ru="Причина approval и audit id", uz="Approval sababi va audit id"),
            ],
        }

    def explain_latest_result(self, payload: dict[str, Any], *, lang: str | None = None, source: str | None = None) -> dict[str, Any]:
        selected_lang = normalize_ui_lang(lang)
        context = build_safety_context_snapshot(payload, lang=selected_lang)
        runtime = self._resolve_runtime()
        response = {
            "enabled": bool(runtime["enabled"]),
            "configured": bool(runtime["configured"]),
            "mode": str(runtime["mode"]),
            "provider": str(runtime["provider"]),
            "model": str(runtime["model"]),
            "advisory_only": True,
            "decision": context.policy_result,
            "source": str(source or "product_shell"),
            "context": context.model_dump(),
            "insight": None,
            "disabled_reason": None,
        }
        if not runtime["enabled"]:
            response["disabled_reason"] = runtime["reason"] or tr(selected_lang, en="Safety Copilot is disabled by default.", ru="Safety Copilot по умолчанию отключён.", uz="Safety Copilot sukut bo'yicha o'chirilgan.")
            return response
        backend = runtime["backend"]
        if backend is None:
            response["disabled_reason"] = runtime["reason"] or tr(selected_lang, en="No assistant backend is available.", ru="Assistant backend недоступен.", uz="Assistant backend mavjud emas.")
            return response
        try:
            response["insight"] = AssistantInsight.model_validate(backend.generate_insight(context)).model_dump()
        except ValidationError as exc:
            raise ValueError("Assistant output failed strict schema validation.") from exc
        return response

    def _resolve_runtime(self) -> dict[str, Any]:
        mode = _normalize_mode(os.getenv("SAFECORE_SAFETY_COPILOT_MODE", DEFAULT_MODE))
        provider = (os.getenv("SAFECORE_SAFETY_COPILOT_PROVIDER", DEFAULT_PROVIDER) or DEFAULT_PROVIDER).strip().lower()
        model = (os.getenv("SAFECORE_SAFETY_COPILOT_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL).strip()
        api_key = (os.getenv("SAFECORE_SAFETY_COPILOT_API_KEY", "") or "").strip()
        base_url = (os.getenv("SAFECORE_SAFETY_COPILOT_BASE_URL", "") or "").strip()
        safe_base_url = _safe_base_url(base_url)
        if self._backend_override is not None:
            return {
                "enabled": mode != "disabled",
                "configured": mode != "disabled",
                "mode": mode,
                "provider": provider,
                "model": model,
                "base_url_label": _safe_base_url_label(base_url),
                "key_status": "Configured via env (masked)" if api_key else "Not configured",
                "external_sharing": mode == "external",
                "reason": None if mode != "disabled" else "Safety Copilot is disabled by default.",
                "backend": self._backend_override if mode != "disabled" else None,
            }
        if mode == "disabled":
            return {
                "enabled": False,
                "configured": False,
                "mode": mode,
                "provider": provider,
                "model": model,
                "base_url_label": _safe_base_url_label(base_url),
                "key_status": "Not configured",
                "external_sharing": False,
                "reason": "Safety Copilot is disabled by default.",
                "backend": None,
            }
        if mode == "local_only":
            return {
                "enabled": True,
                "configured": True,
                "mode": mode,
                "provider": "local_only",
                "model": "deterministic-local",
                "base_url_label": "Not applicable",
                "key_status": "No key needed",
                "external_sharing": False,
                "reason": None,
                "backend": LocalDeterministicSafetyCopilotBackend(),
            }
        if not api_key or not safe_base_url:
            return {
                "enabled": False,
                "configured": False,
                "mode": "external",
                "provider": provider,
                "model": model,
                "base_url_label": _safe_base_url_label(base_url),
                "key_status": "Configured via env (masked)" if api_key else "Not configured",
                "external_sharing": False,
                "reason": "External mode needs SAFECORE_SAFETY_COPILOT_API_KEY and SAFECORE_SAFETY_COPILOT_BASE_URL.",
                "backend": None,
            }
        return {
            "enabled": True,
            "configured": True,
            "mode": "external",
            "provider": provider,
            "model": model,
            "base_url_label": _safe_base_url_label(base_url),
            "key_status": "Configured via env (masked)",
            "external_sharing": True,
            "reason": None,
            "backend": ExternalOpenAICompatibleSafetyCopilotBackend(base_url=safe_base_url, api_key=api_key, model=model),
        }

    def _how_to_enable(self, lang: str, *, enabled: bool, mode: str) -> list[str]:
        if enabled and mode == "local_only":
            return [
                tr(
                    lang,
                    en="Local-only mode is active. The advisory layer stays deterministic and never calls an external model.",
                    ru="Режим local_only активен. Advisory layer остаётся детерминированным и не вызывает внешнюю модель.",
                    uz="Local_only rejimi faol. Advisory layer deterministik bo'lib qoladi va tashqi modelni chaqirmaydi.",
                )
            ]
        if enabled and mode == "external":
            return [
                tr(
                    lang,
                    en="External mode is active with a minimized context snapshot only.",
                    ru="Режим external активен и использует только минимизированный context snapshot.",
                    uz="External mode faqat minimallashtirilgan context snapshot bilan faol.",
                ),
                tr(
                    lang,
                    en="Keep provider credentials in the backend environment only.",
                    ru="Храните provider credentials только в backend environment.",
                    uz="Provayder credentials'larini faqat backend environment ichida saqlang.",
                ),
            ]
        return [
            tr(
                lang,
                en="Set SAFECORE_SAFETY_COPILOT_MODE=local_only for deterministic local guidance.",
                ru="Установите SAFECORE_SAFETY_COPILOT_MODE=local_only для детерминированного локального guidance.",
                uz="Deterministik lokal guidance uchun SAFECORE_SAFETY_COPILOT_MODE=local_only ni o'rnating.",
            ),
            tr(
                lang,
                en="Use SAFECORE_SAFETY_COPILOT_MODE=external only with SAFECORE_SAFETY_COPILOT_BASE_URL and SAFECORE_SAFETY_COPILOT_API_KEY configured in the backend environment.",
                ru="Используйте SAFECORE_SAFETY_COPILOT_MODE=external только если SAFECORE_SAFETY_COPILOT_BASE_URL и SAFECORE_SAFETY_COPILOT_API_KEY настроены в backend environment.",
                uz="SAFECORE_SAFETY_COPILOT_MODE=external rejimini faqat SAFECORE_SAFETY_COPILOT_BASE_URL va SAFECORE_SAFETY_COPILOT_API_KEY backend environment ichida sozlangan bo'lsa ishlating.",
            ),
        ]


def build_safety_context_snapshot(payload: dict[str, Any], *, lang: str | None = None) -> SafetyContext:
    selected_lang = normalize_ui_lang(lang or payload.get("lang"))
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    result = payload.get("result", {}) if isinstance(payload, dict) else {}
    request_payload = payload.get("request", {}) if isinstance(payload, dict) else {}
    decision = _resolve_policy_result(payload)
    approval_status = str(summary.get("approval_status") or _nested(result, "approval", "status") or "").upper()
    approval_reason = None
    if approval_status == "PENDING":
        approval_reason = _sanitize(
            _nested(result, "approval", "reason")
            or payload.get("what_safecore_protects")
            or "Approval is still required before execution can continue."
        )
    return SafetyContext.model_validate(
        {
            "user_intent": _describe_user_intent(payload, request_payload),
            "planned_tools": _planned_tools(request_payload),
            "policy_result": decision,
            "risk_factors": _risk_factors(payload, decision),
            "approval_needed_reason": approval_reason,
            "audit_id": _audit_id(payload, summary, request_payload),
            "lang": selected_lang,
        }
    )


def _describe_user_intent(payload: dict[str, Any], request_payload: dict[str, Any]) -> str:
    title = str(payload.get("title") or payload.get("user_task") or payload.get("scenario") or payload.get("example") or payload.get("flow") or "").strip()
    action = str(request_payload.get("action", "")).strip()
    tool = str(request_payload.get("tool", "")).strip()
    if tool == SAFE_HTTP_TOOL:
        parsed = parse.urlparse(str(request_payload.get("url", "")).strip())
        host = parsed.hostname or "unknown-host"
        safe_host = host if host in {"127.0.0.1", "localhost"} else "external-host"
        method = _sanitize(request_payload.get("method", "GET"), max_length=24).upper()
        detail = f"{SAFE_HTTP_TOOL} {method} {safe_host}{parsed.path or '/'}"
        return _sanitize(f"{title}: {detail}" if title else detail)
    if action:
        return _sanitize(f"{title}: {action}" if title else action)
    return _sanitize(title or "guarded action request")


def _planned_tools(request_payload: dict[str, Any]) -> list[str]:
    tool = str(request_payload.get("tool", "")).strip()
    if not tool:
        return ["guarded_path"]
    if tool == SAFE_HTTP_TOOL:
        return [f"{SAFE_HTTP_TOOL}:read-only"]
    return [_sanitize(tool, max_length=48)]


def _risk_factors(payload: dict[str, Any], decision: str) -> list[str]:
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    result = payload.get("result", {}) if isinstance(payload, dict) else {}
    policy = result.get("policy_decision", {}) if isinstance(result, dict) else {}
    risks: list[str] = []
    reasons = policy.get("reasons", []) if isinstance(policy, dict) else []
    if isinstance(reasons, list):
        risks.extend(_sanitize(item, max_length=180) for item in reasons[:2] if str(item).strip())
    if bool(summary.get("blocked", False)):
        risks.append("The request is currently blocked by the guarded path.")
    if str(summary.get("approval_status", "")).upper() == "PENDING":
        risks.append("Approval is still pending before execution can continue.")
    connector_status = str(summary.get("connector_status", "")).strip().upper()
    if connector_status and connector_status not in {"SAFE_READ_ONLY_FETCHED", "NOT_APPLICABLE"}:
        risks.append(_sanitize(f"Connector state: {connector_status}", max_length=120))
    execution_status = str(summary.get("execution_status", "")).strip().upper()
    if execution_status == "BLOCKED":
        risks.append("Execution remains blocked-safe and did not proceed.")
    elif execution_status == "DRY_RUN_SIMULATED":
        risks.append("Execution still stays inside the dry-run-first posture.")
    if not risks:
        risks.append(_default_risk("en", decision))
    return risks[:4]


def _default_risk(lang: str, decision: str) -> str:
    mapping = {
        "ALLOW": tr(
            lang,
            en="The request stayed inside the current low-risk boundary.",
            ru="Запрос остался внутри текущей low-risk boundary.",
            uz="So'rov joriy low-risk boundary ichida qoldi.",
        ),
        "NEEDS_APPROVAL": tr(
            lang,
            en="The request crossed the low-risk boundary and now needs explicit approval.",
            ru="Запрос пересёк low-risk boundary и теперь требует явного approval.",
            uz="So'rov low-risk boundary'dan o'tdi va endi aniq approval talab qiladi.",
        ),
        "DENY": tr(
            lang,
            en="The request crossed a protected boundary and must stay blocked.",
            ru="Запрос пересёк защищённую boundary и должен оставаться заблокированным.",
            uz="So'rov himoyalangan boundary'dan o'tdi va bloklangan holda qolishi kerak.",
        ),
    }
    return mapping.get(decision, "The guarded path applied a decision boundary.")


def _resolve_policy_result(payload: dict[str, Any]) -> Literal["ALLOW", "NEEDS_APPROVAL", "DENY"]:
    decision = (
        payload.get("summary", {}).get("decision")
        or _nested(payload.get("result", {}), "policy_decision", "decision")
        or payload.get("decision")
        or "DENY"
    )
    normalized = str(decision).strip().upper()
    return normalized if normalized in {"ALLOW", "NEEDS_APPROVAL", "DENY"} else "DENY"


def _audit_id(payload: dict[str, Any], summary: dict[str, Any], request_payload: dict[str, Any]) -> str:
    audit_path = str(summary.get("audit_path", "")).strip()
    if audit_path:
        return _sanitize(Path(audit_path).name or audit_path)
    run_id = str(request_payload.get("run_id", "")).strip()
    return _sanitize(run_id or "local-audit")


def _nested(value: Any, *path: str) -> Any:
    current = value
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _sanitize(value: Any, *, max_length: int = 240) -> str:
    text = " ".join(str(value).split())
    for pattern, replacement in TOKEN_PATTERNS:
        text = pattern.sub(replacement, text)
    return (text[: max_length - 3].rstrip() + "...") if len(text) > max_length else (text or "N/A")


def _validate_advisory_text(value: Any, *, max_length: int = 240) -> str:
    text = _sanitize(value, max_length=max_length)
    if any(pattern.search(text) for pattern in UNSAFE_OUTPUT_PATTERNS):
        raise ValueError("Assistant insight contains unsafe or executable content.")
    return text


def _normalize_mode(value: str | None) -> str:
    normalized = str(value or DEFAULT_MODE).strip().lower()
    return normalized if normalized in SAFE_MODES else DEFAULT_MODE


def _safe_base_url(value: str | None) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    parsed = parse.urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    return raw.rstrip("/")


def _safe_base_url_label(value: str | None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "Not configured"
    parsed = parse.urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return "Invalid base URL"
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{parsed.hostname}{port}"
