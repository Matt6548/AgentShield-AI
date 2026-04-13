"""Demo UI content and safe scenario runner for the SafeCore local web UI."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

from src.integrations import build_safe_http_example_request as build_integration_safe_http_example_request
from src.api.service import GuardedExecutionService
from src.api.product_shell import ProductShellStore
from src.api.ui_i18n import language_options, normalize_ui_lang, tr
from src.approval import ApprovalManager
from src.audit import AuditLogger
from src.data_guard import DataGuard
from src.exec_guard import ExecutionGuard
from src.policy import PolicyEngine
from src.utils.safe_http import SAFE_HTTP_TOOL
from src.utils.tool_policies import ToolGuard


ROOT_DIR = Path(__file__).resolve().parents[2]
DEMO_INPUT_DIR = ROOT_DIR / "examples" / "demo_inputs"
DEFAULT_UI_AUDIT_DIR = ROOT_DIR / "examples" / "demo_ui_audit"


class CounterIdFactory:
    """Provide stable approval request ids for demo UI readability."""

    def __init__(self) -> None:
        self.counter = 0

    def __call__(self) -> str:
        self.counter += 1
        return f"apr-ui-{self.counter:04d}"


SCENARIO_CONTENT = {
    "allow_case": {
        "title": "ALLOW",
        "meaning": "Low-risk actions can proceed through the guarded path.",
        "example": "Safe read-only shell action such as `ls`.",
        "why_it_matters": "Shows that low-risk actions can pass policy and guard checks without real side effects.",
        "current_rc_behavior": "Execution remains DRY_RUN_SIMULATED.",
    },
    "approval_case": {
        "title": "NEEDS_APPROVAL",
        "meaning": "Risky actions stay blocked until explicit approval exists.",
        "example": "Production-style config change or suspicious outbound action.",
        "why_it_matters": "Shows that approval is a real execution gate, not a cosmetic status.",
        "current_rc_behavior": "Request stays blocked with approval status PENDING until APPROVED.",
    },
    "deny_case": {
        "title": "DENY",
        "meaning": "Clearly dangerous actions must not proceed.",
        "example": "Privileged destructive shell action such as `rm -rf /`.",
        "why_it_matters": "Shows that dangerous actions are stopped outright and do not route through normal approval override.",
        "current_rc_behavior": "Request remains blocked and non-overridable.",
    },
}

SAFE_HTTP_EXAMPLE_CONTENT = {
    "allowlisted_get": {
        "title": "Allowlisted read-only GET",
        "meaning": "A narrow real connector path can fetch a trusted local health/status endpoint.",
        "example": "GET http://127.0.0.1:8000/health",
        "why_it_matters": "Shows how SafeCore can sit in front of a real integration path without widening execution scope.",
        "current_rc_behavior": "Connector performs one allowlisted safe read-only fetch; execution guard remains dry-run only.",
    },
    "blocked_host": {
        "title": "Blocked untrusted host",
        "meaning": "Requests to non-allowlisted hosts must not proceed.",
        "example": "GET http://example.com/health",
        "why_it_matters": "Shows explicit destination allowlisting instead of arbitrary outbound HTTP access.",
        "current_rc_behavior": "Request is blocked before connector execution can proceed.",
    },
    "blocked_method": {
        "title": "Blocked non-GET request",
        "meaning": "The example connector is strictly read-only and GET only.",
        "example": "POST http://127.0.0.1:8000/health",
        "why_it_matters": "Shows that the integration path stays intentionally narrow and cannot be repurposed for mutation.",
        "current_rc_behavior": "Request is blocked and stays dry-run-safe.",
    },
}

REFERENCE_PRODUCT_FLOW_CONTENT = {
    "safe_status_check": {
        "title": "Check trusted local service health",
        "user_task": "A user wants to check whether a trusted local service is healthy.",
        "safe_http_example": "allowlisted_get",
        "what_safecore_protects": "SafeCore makes sure the request stays inside the narrow allowlisted read-only connector boundary.",
        "why_it_matters": "Shows the good path: a useful status check is allowed without turning SafeCore into a generic HTTP executor.",
    },
    "blocked_external_status": {
        "title": "Try an untrusted service host",
        "user_task": "A user tries to check status on a host that is not explicitly trusted.",
        "safe_http_example": "blocked_host",
        "what_safecore_protects": "SafeCore prevents arbitrary outbound access and blocks the connector path before it can proceed.",
        "why_it_matters": "Shows that allowlisting is real and that unknown destinations are blocked-safe by default.",
    },
    "blocked_unsafe_status_method": {
        "title": "Try an unsafe status method",
        "user_task": "A user tries to use a non-GET method for a status-style request.",
        "safe_http_example": "blocked_method",
        "what_safecore_protects": "SafeCore enforces the read-only boundary and rejects mutation-style requests.",
        "why_it_matters": "Shows that the connector path cannot be widened into a generic or destructive integration route.",
    },
}


UI_CONTENT = {
    "identity": {
        "name": "SafeCore",
        "positioning": "Security/control layer for AI agents.",
        "summary": (
            "SafeCore sits between an AI agent and external tools or systems, "
            "evaluates risk, and returns a guarded result before execution."
        ),
        "status": [
            "Open-source RC/MVP",
            "Validated core",
            "Apache 2.0",
            "Dry-run only",
        ],
    },
    "overview": {
        "headline": "SafeCore makes agent execution controllable before tools are touched.",
        "subtext": (
            "It is not another agent runtime. It is the middleware around execution: "
            "policy, guards, approval, audit, routing, and blocked-path behavior."
        ),
    },
    "capabilities": [
        {
            "title": "Policy decision layer",
            "detail": "Returns ALLOW, NEEDS_APPROVAL, or DENY with risk score and reasons.",
        },
        {
            "title": "Data Guard",
            "detail": "Detects sensitive payload patterns and supports redact/block behavior.",
        },
        {
            "title": "Tool Guard",
            "detail": "Checks shell and tool usage against explicit allow/deny rules.",
        },
        {
            "title": "Execution Guard",
            "detail": "Keeps the current repository dry-run-only and blocks unsafe execution paths.",
        },
        {
            "title": "Approval and escalation logic",
            "detail": "Requires explicit approval for risky actions; escalation never authorizes execution by itself.",
        },
        {
            "title": "Audit logging",
            "detail": "Writes local JSONL audit records with hash chaining.",
        },
        {
            "title": "Audit integrity",
            "detail": "Verifies the audit chain and surfaces broken-link conditions explicitly.",
        },
        {
            "title": "Model routing foundation",
            "detail": "Selects deterministic routing profiles based on decision context.",
        },
        {
            "title": "Connector boundary",
            "detail": "Normalizes and sanitizes connector requests and responses through dry-run-safe adapters, including one narrow read-only HTTP status example.",
        },
        {
            "title": "Demo path",
            "detail": "Runnable CLI and local UI flows demonstrate ALLOW, NEEDS_APPROVAL, and DENY outcomes.",
        },
        {
            "title": "Docs and release posture",
            "detail": "Public docs, release posture, and open-source materials are already part of the repository.",
        },
    ],
    "architecture": {
        "flow": (
            "AI Agent -> SafeCore -> Policy / Data Guard / Tool Guard / Approval / "
            "Model Router / Connector Boundary / Execution Guard / Audit -> Result"
        ),
        "layers": [
            {
                "title": "Policy",
                "detail": "Turns a request into a decision, risk score, reasons, and constraints.",
            },
            {
                "title": "Data Guard",
                "detail": "Checks payload content for sensitive material and outbound risk markers.",
            },
            {
                "title": "Tool Guard",
                "detail": "Stops obviously unsafe tool or shell usage early.",
            },
            {
                "title": "Approval / Escalation",
                "detail": "Blocks risky requests until explicit approval exists; escalation cannot unblock execution.",
            },
            {
                "title": "Model Router",
                "detail": "Selects an explainable route profile for the guarded flow.",
            },
            {
                "title": "Connector Boundary",
                "detail": "Keeps integrations sanitized, stubbed, and dry-run-safe.",
            },
            {
                "title": "Execution Guard",
                "detail": "Maintains dry-run-only execution posture.",
            },
            {
                "title": "Audit",
                "detail": "Captures evidence and verifies integrity of the local audit chain.",
            },
        ],
    },
    "scope": {
        "current_use": [
            {
                "title": "Local API",
                "detail": "Run `uvicorn src.api.app:app --reload` and use `/health`, `/v1/guarded-execute`, or this local UI.",
            },
            {
                "title": "CLI demo",
                "detail": "Run `python scripts/demo_smoke.py` for the three canonical scenarios.",
            },
            {
                "title": "Example flow",
                "detail": "Run `python examples/example_run.py` for guarded workflow snapshots.",
            },
            {
                "title": "Connector posture",
                "detail": "Current connectors are boundary foundations with sanitization and stub adapters, plus one narrow allowlisted read-only HTTP status example.",
            },
        ],
        "included": [
            "Modular core",
            "Demo path",
            "Public docs",
            "Release posture",
            "Apache 2.0",
            "Tests and presentation layer",
        ],
        "not_included": [
            "No real destructive external side effects",
            "No production auth/authz",
            "No audit DB or cloud stack",
            "No advanced approval portal",
            "No full enterprise platform",
            "No production-ready claim",
        ],
    },
    "audiences": [
        {
            "title": "Security engineer",
            "detail": "A visible control boundary before tool execution, with policy, approval, audit, and blocked-flow evidence.",
        },
        {
            "title": "Platform engineer",
            "detail": "Middleware that makes the execution path explicit and easier to reason about.",
        },
        {
            "title": "AI / agent developer",
            "detail": "A layer that decides when an agent can act, when it must pause, and when it must stop.",
        },
        {
            "title": "Technical founder",
            "detail": "A credible way to show real control surfaces around agent execution rather than direct model-to-tool flow.",
        },
    ],
    "roadmap": [
        "Deepen policy coverage without weakening deterministic control behavior.",
        "Move from dry-run foundations toward safer real execution paths over time.",
        "Strengthen operational and deployment maturity without inflating scope today.",
    ],
    "safe_integration": {
        "headline": "First practical integration path",
        "subtext": (
            "SafeCore already supports one practical connector path today: "
            "an allowlisted read-only HTTP status flow for trusted local endpoints."
        ),
        "connects_to": "Trusted local or internal-style health/status/metadata endpoints on allowlisted hosts only.",
        "workflow": "AI agent -> SafeCore -> safe_http_status connector -> allowed or blocked result",
        "allowed": [
            "GET only",
            "localhost / 127.0.0.1 only",
            "health, status, metadata, or version paths only",
            "connector request still passes through policy, tool guard, approval, audit, and execution boundaries",
        ],
        "blocked": [
            "non-allowlisted hosts",
            "non-GET methods",
            "arbitrary outbound HTTP targets",
            "mutation-style requests pretending to be a status call",
        ],
        "why_it_matters": (
            "It shows where SafeCore fits in a real workflow: directly in front of a connector "
            "boundary, with explicit allow/block behavior and audit evidence."
        ),
        "how_to_use": (
            "Start the local API, open the UI, run allowlisted_get, then compare it with "
            "blocked_host and blocked_method to see the practical control boundary."
        ),
        "developer_placement": (
            "Developers should place SafeCore between their app or agent and the connector call, "
            "so the request is evaluated before the connector path is touched."
        ),
    },
    "reference_product": {
        "headline": "Try SafeCore in a real workflow",
        "subtext": (
            "This reference product flow takes a simple user task, turns it into a connector request, "
            "runs it through SafeCore, and returns a guarded result with decision, audit, and blocked-path context."
        ),
        "workflow": "user or app -> SafeCore -> safe_http_status connector -> guarded result",
        "what_user_is_doing": "Checking trusted local service status through one narrow safe path.",
        "what_safecore_is_protecting": (
            "SafeCore protects the connector boundary by enforcing allowlisted hosts, GET-only access, "
            "and blocked-safe behavior for anything outside the narrow policy."
        ),
        "why_it_matters": (
            "It makes the project feel like a usable product flow, not only a core with docs: "
            "a user task becomes an action request, SafeCore evaluates it, and the result is visible immediately."
        ),
    },
    "product_shell": {
        "headline": "Product shell features",
        "subtext": (
            "This shell adds monitoring, run history, approval visibility, and audit evidence "
            "on top of the current SafeCore demo and reference product flow."
        ),
        "what_is_happening": (
            "Each run writes local audit evidence, updates a small local shell history, and makes "
            "the current guarded state easier to inspect."
        ),
        "why_it_matters": (
            "A new user can see what SafeCore allowed, what it blocked, what still needs approval, "
            "and where the evidence lives without reading the whole repository first."
        ),
        "what_to_do_next": (
            "Run one allowed example, one blocked example, and the approval_case scenario. "
            "Then inspect the summary, queue, and audit viewer."
        ),
        "history_hint": "Use the decision filter to focus on ALLOW, NEEDS_APPROVAL, or DENY runs.",
        "approval_hint": (
            "Pending items stay blocked. Operators should review the reason and operator checks "
            "before deciding outside this demo shell."
        ),
        "audit_hint": (
            "Audit viewer shows the recent local evidence trail. Integrity issues are surfaced explicitly."
        ),
    },
    "assistant": {
        "headline": "Optional safety copilot",
        "subtext": (
            "Use a minimized advisory layer to explain the latest guarded result in plainer language. "
            "It never changes the final decision."
        ),
        "why_it_matters": (
            "Operators can understand blocked or approval-required results faster without turning SafeCore "
            "into a new agent runtime."
        ),
        "how_it_works": "latest guarded result -> minimized safety snapshot -> advisory-only insight",
    },
}


def _build_onboarding(lang: str) -> dict[str, Any]:
    return {
        "headline": tr(
            lang,
            en="Start in five short steps",
            ru="Начните за пять коротких шагов",
            uz="Besh qisqa qadamda boshlang",
        ),
        "subtext": tr(
            lang,
            en=(
                "This onboarding stays inside the current product shell. "
                "It explains the safest first path before you read deeper docs."
            ),
            ru=(
                "Это onboarding внутри текущего product shell. "
                "Он показывает самый безопасный первый путь до того, как вы пойдёте в более глубокие docs."
            ),
            uz=(
                "Bu onboarding joriy product shell ichida qoladi. "
                "U chuqurroq docs'ga o'tishdan oldin eng xavfsiz birinchi yo'lni ko'rsatadi."
            ),
        ),
        "safe_note": tr(
            lang,
            en="Progress is stored only in localStorage in your browser. No secrets are stored.",
            ru="Прогресс хранится только в localStorage в вашем браузере. Секреты не сохраняются.",
            uz="Progress faqat brauzeringizdagi localStorage ichida saqlanadi. Hech qanday sir saqlanmaydi.",
        ),
        "workflow": tr(
            lang,
            en="user or app -> SafeCore -> guarded connector path -> decision, approval, and audit evidence",
            ru="user или app -> SafeCore -> guarded connector path -> decision, approval и audit evidence",
            uz="user yoki app -> SafeCore -> guarded connector path -> decision, approval va audit evidence",
        ),
        "status_labels": {
            "current": tr(lang, en="Current", ru="Текущий", uz="Joriy"),
            "completed": tr(lang, en="Completed", ru="Завершено", uz="Bajarilgan"),
            "up_next": tr(lang, en="Up next", ru="Дальше", uz="Keyingi"),
            "progress": tr(lang, en="Progress", ru="Прогресс", uz="Progress"),
        },
        "steps": [
            {
                "id": "language",
                "title": tr(lang, en="Language", ru="Язык", uz="Til"),
                "summary": tr(
                    lang,
                    en="Pick the language you want to use in the shell before you explore the product.",
                    ru="Сначала выберите язык, на котором вам удобнее изучать shell.",
                    uz="Product shell'ni ko'rishdan oldin o'zingizga qulay tilni tanlang.",
                ),
                "why_it_matters": tr(
                    lang,
                    en="The shell explains decisions in plain language. Start in the language your team can follow quickly.",
                    ru="Shell объясняет решения простыми словами. Начните на языке, который ваша команда понимает быстрее всего.",
                    uz="Shell qarorlarni oddiy tilda tushuntiradi. Jamoangiz tez tushunadigan tildan boshlang.",
                ),
                "what_to_do": tr(
                    lang,
                    en="Use the language switcher in the top bar. Nothing else changes in the core.",
                    ru="Используйте переключатель языка в верхней панели. В core больше ничего не меняется.",
                    uz="Yuqori paneldagi til almashtirgichdan foydalaning. Core ichida boshqa hech narsa o'zgarmaydi.",
                ),
                "anchor": "overview",
                "action_label": tr(lang, en="Open overview", ru="Открыть overview", uz="Overview'ni ochish"),
            },
            {
                "id": "provider_setup",
                "title": tr(lang, en="Provider setup", ru="Настройка провайдера", uz="Provayder sozlamasi"),
                "summary": tr(
                    lang,
                    en="Check which providers are configured in the backend and which path is actually enabled in the shell.",
                    ru="Проверьте, какие провайдеры настроены в backend и какой путь реально включён в shell.",
                    uz="Qaysi provayderlar backend'da sozlanganini va shell ichida qaysi yo'l haqiqatan yoqilganini ko'ring.",
                ),
                "why_it_matters": tr(
                    lang,
                    en="SafeCore can show configuration posture without exposing keys or turning the shell into a model runner.",
                    ru="SafeCore умеет показывать posture конфигурации без раскрытия ключей и без превращения shell в model runner.",
                    uz="SafeCore kalitlarni oshkor qilmasdan va shell'ni model runner'ga aylantirmasdan configuration posture'ni ko'rsata oladi.",
                ),
                "what_to_do": tr(
                    lang,
                    en="Open Provider Status and confirm that Local / demo mode is the only enabled path today.",
                    ru="Откройте Provider Status и подтвердите, что Local / demo mode — единственный enabled path сегодня.",
                    uz="Provider Status'ni oching va bugun Local / demo mode yagona enabled path ekanini tasdiqlang.",
                ),
                "anchor": "providers",
                "action_label": tr(lang, en="Open provider status", ru="Открыть Provider Status", uz="Provider Status'ni ochish"),
            },
            {
                "id": "first_safe_run",
                "title": tr(lang, en="First safe run", ru="Первый безопасный запуск", uz="Birinchi xavfsiz run"),
                "summary": tr(
                    lang,
                    en="Run the trusted local status check to see SafeCore allow one narrow practical request.",
                    ru="Запустите trusted local status check, чтобы увидеть, как SafeCore разрешает один узкий практический request.",
                    uz="SafeCore bitta tor practical request'ga ruxsat berishini ko'rish uchun trusted local status check'ni ishga tushiring.",
                ),
                "why_it_matters": tr(
                    lang,
                    en="This is the fastest way to see SafeCore protecting a real connector boundary without broad execution.",
                    ru="Это самый быстрый способ увидеть, как SafeCore защищает реальную connector boundary без broad execution.",
                    uz="Bu SafeCore real connector boundary'ni broad execution'siz qanday himoya qilishini ko'rishning eng tez yo'li.",
                ),
                "what_to_do": tr(
                    lang,
                    en="Open Reference Product Flow or First Practical Integration Path and run the allowlisted safe case.",
                    ru="Откройте Reference Product Flow или First Practical Integration Path и запустите allowlisted safe case.",
                    uz="Reference Product Flow yoki First Practical Integration Path bo'limini oching va allowlisted safe case'ni ishga tushiring.",
                ),
                "anchor": "reference-product-flow",
                "action_label": tr(lang, en="Run the first safe flow", ru="Запустить первый safe flow", uz="Birinchi safe flow'ni ishga tushirish"),
            },
            {
                "id": "approval_explanation",
                "title": tr(lang, en="Approval explanation", ru="Объяснение approval", uz="Approval tushuntirishi"),
                "summary": tr(
                    lang,
                    en="Look at a request that needs approval and see why it stays blocked.",
                    ru="Посмотрите на request, которому нужен approval, и увидьте, почему он остаётся blocked.",
                    uz="Approval kerak bo'lgan request'ni ko'ring va u nega blocked bo'lib qolishini tushuning.",
                ),
                "why_it_matters": tr(
                    lang,
                    en="SafeCore does not treat approval as a cosmetic badge. It is a real execution gate.",
                    ru="SafeCore не считает approval косметическим badge. Это реальный execution gate.",
                    uz="SafeCore approval'ni oddiy badge deb hisoblamaydi. Bu haqiqiy execution gate.",
                ),
                "what_to_do": tr(
                    lang,
                    en="Run approval_case, then inspect the approval queue and the operator checks.",
                    ru="Запустите approval_case, затем посмотрите approval queue и operator checks.",
                    uz="approval_case'ni ishga tushiring, keyin approval queue va operator checks'ni ko'ring.",
                ),
                "anchor": "approval-audit",
                "action_label": tr(lang, en="Open approval view", ru="Открыть approval view", uz="Approval view'ni ochish"),
            },
            {
                "id": "audit_viewer",
                "title": tr(lang, en="Audit viewer", ru="Audit viewer", uz="Audit viewer"),
                "summary": tr(
                    lang,
                    en="Trace what happened after a run and confirm whether the local audit chain is still valid.",
                    ru="Проследите, что произошло после run, и подтвердите, что локальная audit chain всё ещё валидна.",
                    uz="Run'dan keyin nima bo'lganini kuzating va lokal audit chain hamon valid ekanini tasdiqlang.",
                ),
                "why_it_matters": tr(
                    lang,
                    en="Product users need evidence, not only a decision badge. Audit is where that evidence lives.",
                    ru="Пользователю продукта нужно evidence, а не только decision badge. Audit — это место, где это evidence живёт.",
                    uz="Product foydalanuvchisiga faqat decision badge emas, evidence ham kerak. Audit shu evidence yashaydigan joydir.",
                ),
                "what_to_do": tr(
                    lang,
                    en="Open Approval And Audit, confirm the local audit path, and review the latest integrity state.",
                    ru="Откройте Approval And Audit, подтвердите локальный audit path и проверьте последнее integrity state.",
                    uz="Approval And Audit bo'limini oching, lokal audit path'ni tasdiqlang va so'nggi integrity state'ni ko'ring.",
                ),
                "anchor": "approval-audit",
                "action_label": tr(lang, en="Open audit viewer", ru="Открыть audit viewer", uz="Audit viewer'ni ochish"),
            },
        ],
    }


def _build_filter_options(lang: str) -> dict[str, Any]:
    return {
        "decision": [
            {"value": "ALL", "label": tr(lang, en="All decisions", ru="Все решения", uz="Barcha qarorlar")},
            {"value": "ALLOW", "label": "ALLOW"},
            {"value": "NEEDS_APPROVAL", "label": "NEEDS_APPROVAL"},
            {"value": "DENY", "label": "DENY"},
        ],
        "run_status": [
            {"value": "ALL", "label": tr(lang, en="All run states", ru="Все состояния", uz="Barcha holatlar")},
            {"value": "ALLOWED", "label": tr(lang, en="Allowed", ru="Разрешено", uz="Ruxsat etilgan")},
            {"value": "PENDING_APPROVAL", "label": tr(lang, en="Pending approval", ru="Ожидает approval", uz="Approval kutilmoqda")},
            {"value": "BLOCKED", "label": tr(lang, en="Blocked", ru="Заблокировано", uz="Bloklangan")},
        ],
        "provider": [
            {"value": "ALL", "label": tr(lang, en="All provider modes", ru="Все provider modes", uz="Barcha provider mode'lar")},
            {"value": "LOCAL_DEMO", "label": tr(lang, en="Local / demo mode", ru="Local / demo mode", uz="Lokal / demo mode")},
        ],
        "integrity": [
            {"value": "ALL", "label": tr(lang, en="All integrity states", ru="Все состояния integrity", uz="Barcha integrity holatlari")},
            {"value": "VALID", "label": tr(lang, en="Valid", ru="Валидно", uz="Valid")},
            {"value": "BROKEN", "label": tr(lang, en="Broken", ru="Нарушено", uz="Buzilgan")},
        ],
    }


def build_ui_content(lang: str | None = None) -> dict[str, Any]:
    """Return UI content as a JSON-serializable structure."""
    selected_lang = normalize_ui_lang(lang)
    content = _build_localized_ui_content(selected_lang)
    content["onboarding"] = _build_onboarding(selected_lang)
    content["demo"] = {
        "scenarios": [
            {
                "name": name,
                **_scenario_content(name, selected_lang),
            }
            for name in SCENARIO_CONTENT
        ]
    }
    content["safe_integration"]["examples"] = [
        {"name": name, **_safe_http_example_content(name, selected_lang)}
        for name in SAFE_HTTP_EXAMPLE_CONTENT
    ]
    content["reference_product"]["flows"] = [
        {"name": name, **_reference_product_flow_content(name, selected_lang)}
        for name in REFERENCE_PRODUCT_FLOW_CONTENT
    ]
    return content


def load_demo_request(name: str) -> dict[str, Any]:
    """Load one frozen demo scenario request from JSON."""
    scenario_name = str(name).strip()
    if scenario_name not in SCENARIO_CONTENT:
        raise KeyError(f"Unknown demo scenario: {name}")
    scenario_path = DEMO_INPUT_DIR / f"{scenario_name}.json"
    payload = json.loads(scenario_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Demo scenario '{scenario_name}' must be a JSON object.")
    return payload


def run_demo_scenario(
    name: str,
    *,
    audit_dir: Path | None = None,
    product_shell_store_path: Path | None = None,
    lang: str | None = None,
) -> dict[str, Any]:
    """Run one demo scenario through the current guarded path."""
    scenario_name = str(name).strip()
    if scenario_name not in SCENARIO_CONTENT:
        raise KeyError(f"Unknown demo scenario: {name}")
    selected_lang = normalize_ui_lang(lang)
    details = _scenario_content(scenario_name, selected_lang)

    resolved_audit_dir = Path(audit_dir) if audit_dir is not None else DEFAULT_UI_AUDIT_DIR
    resolved_audit_dir.mkdir(parents=True, exist_ok=True)
    audit_file = resolved_audit_dir / f"{scenario_name}.jsonl"
    if audit_file.exists():
        audit_file.unlink()

    service = _build_demo_ui_service(audit_file)
    request = load_demo_request(scenario_name)
    response = service.execute_guarded_request(request)
    policy_decision = response.get("policy_decision", {})
    approval = response.get("approval", {})
    execution_result = response.get("execution_result", {})
    execution_output = execution_result.get("output", {}) if isinstance(execution_result, dict) else {}
    audit_integrity = response.get("audit_integrity", {})

    payload = {
        "scenario": scenario_name,
        "title": details["title"],
        "meaning": details["meaning"],
        "example": details["example"],
        "why_it_matters": details["why_it_matters"],
        "current_rc_behavior": details["current_rc_behavior"],
        "request": request,
        "summary": {
            "decision": policy_decision.get("decision"),
            "risk_score": policy_decision.get("risk_score"),
            "blocked": bool(response.get("blocked", True)),
            "approval_status": approval.get("status"),
            "execution_status": execution_output.get("status"),
            "audit_integrity": bool(audit_integrity.get("valid", False)),
            "audit_path": _display_path(audit_file),
        },
        "result": {
            "policy_decision": policy_decision,
            "approval": approval,
            "model_route": response.get("model_route", {}),
            "execution_result": execution_result,
            "connector_execution": response.get("connector_execution", {}),
            "audit_integrity": audit_integrity,
        },
    }
    _record_product_shell_run(
        source="demo_scenario",
        payload=payload,
        run_id=str(request.get("run_id", scenario_name)),
        action=str(request.get("action", "")),
        tool=str(request.get("tool", "")),
        audit_file=audit_file,
        product_shell_store_path=product_shell_store_path,
        short_explanation=_demo_scenario_explanation(
            lang=selected_lang,
            decision=str(policy_decision.get("decision", "")),
            blocked=bool(payload["summary"]["blocked"]),
            approval_status=str(approval.get("status", "")),
        ),
    )
    return payload


def build_safe_http_example_request(name: str, *, url: str | None = None) -> dict[str, Any]:
    """Build one frozen safe HTTP integration example request."""
    default_url = url or os.getenv("SAFECORE_SAFE_HTTP_DEMO_URL", "http://127.0.0.1:8000/health")
    return build_integration_safe_http_example_request(name, url=default_url)


def run_safe_http_example(
    name: str,
    *,
    url: str | None = None,
    audit_dir: Path | None = None,
    product_shell_store_path: Path | None = None,
    record_product_shell: bool = True,
    lang: str | None = None,
) -> dict[str, Any]:
    """Run one safe HTTP integration example through the current guarded path."""
    example_name = str(name).strip()
    if example_name not in SAFE_HTTP_EXAMPLE_CONTENT:
        raise KeyError(f"Unknown safe integration example: {name}")
    selected_lang = normalize_ui_lang(lang)
    details = _safe_http_example_content(example_name, selected_lang)

    resolved_audit_dir = Path(audit_dir) if audit_dir is not None else DEFAULT_UI_AUDIT_DIR
    resolved_audit_dir.mkdir(parents=True, exist_ok=True)
    audit_file = resolved_audit_dir / f"safe-http-{example_name}.jsonl"
    if audit_file.exists():
        audit_file.unlink()

    service = _build_demo_ui_service(audit_file)
    request = build_safe_http_example_request(example_name, url=url)
    response = service.execute_guarded_request(request)
    policy_decision = response.get("policy_decision", {})
    approval = response.get("approval", {})
    execution_result = response.get("execution_result", {}) if isinstance(response, dict) else {}
    execution_output = execution_result.get("output", {}) if isinstance(execution_result, dict) else {}
    connector_execution = response.get("connector_execution", {})
    audit_integrity = response.get("audit_integrity", {})

    payload = {
        "example": example_name,
        "title": details["title"],
        "meaning": details["meaning"],
        "example_text": details["example"],
        "why_it_matters": details["why_it_matters"],
        "current_rc_behavior": details["current_rc_behavior"],
        "request": request,
        "summary": {
            "decision": policy_decision.get("decision"),
            "risk_score": policy_decision.get("risk_score"),
            "blocked": bool(response.get("blocked", True)),
            "approval_status": approval.get("status"),
            "execution_status": execution_output.get("status"),
            "connector_status": connector_execution.get("status"),
            "audit_integrity": bool(audit_integrity.get("valid", False)),
            "audit_path": _display_path(audit_file),
        },
        "result": {
            "policy_decision": policy_decision,
            "tool_guard_result": response.get("tool_guard_result", {}),
            "approval": approval,
            "connector_execution": connector_execution,
            "execution_result": execution_result,
            "audit_integrity": audit_integrity,
        },
    }
    if record_product_shell:
        _record_product_shell_run(
            source="safe_integration",
            payload=payload,
            run_id=str(request.get("run_id", example_name)),
            action=str(request.get("action", "")),
            tool=str(request.get("tool", "")),
            audit_file=audit_file,
            product_shell_store_path=product_shell_store_path,
            short_explanation=_safe_http_explanation(
                lang=selected_lang,
                decision=str(policy_decision.get("decision", "")),
                blocked=bool(payload["summary"]["blocked"]),
                connector_status=str(connector_execution.get("status", "")),
            ),
        )
    return payload


def run_reference_product_flow(
    name: str,
    *,
    url: str | None = None,
    audit_dir: Path | None = None,
    product_shell_store_path: Path | None = None,
    lang: str | None = None,
) -> dict[str, Any]:
    """Run one user-facing reference product flow through the current guarded path."""
    flow_name = str(name).strip()
    if flow_name not in REFERENCE_PRODUCT_FLOW_CONTENT:
        raise KeyError(f"Unknown reference product flow: {name}")
    selected_lang = normalize_ui_lang(lang)
    details = _reference_product_flow_content(flow_name, selected_lang)

    example_name = str(REFERENCE_PRODUCT_FLOW_CONTENT[flow_name]["safe_http_example"])
    example_result = run_safe_http_example(
        example_name,
        url=url,
        audit_dir=audit_dir,
        product_shell_store_path=product_shell_store_path,
        record_product_shell=False,
        lang=selected_lang,
    )
    summary = example_result["summary"]
    decision = str(summary.get("decision", "WAITING"))

    payload = {
        "flow": flow_name,
        "title": details["title"],
        "user_task": details["user_task"],
        "workflow": _build_localized_ui_content(selected_lang)["reference_product"]["workflow"],
        "what_safecore_protects": details["what_safecore_protects"],
        "why_it_matters": details["why_it_matters"],
        "short_explanation": _reference_flow_explanation(
            lang=selected_lang,
            decision=decision,
            blocked=bool(summary.get("blocked", True)),
            connector_status=str(summary.get("connector_status", "")),
        ),
        "request": deepcopy(example_result["request"]),
        "summary": deepcopy(summary),
        "result": deepcopy(example_result["result"]),
    }
    _record_product_shell_run(
        source="reference_product",
        payload=payload,
        run_id=str(payload["request"].get("run_id", flow_name)),
        action=str(payload["request"].get("action", "")),
        tool=str(payload["request"].get("tool", "")),
        audit_file=_resolve_audit_file(summary.get("audit_path")),
        product_shell_store_path=product_shell_store_path,
        short_explanation=str(payload["short_explanation"]),
    )
    return payload


def build_product_shell_view(
    *,
    lang: str | None = None,
    product_shell_store_path: Path | None = None,
) -> dict[str, Any]:
    selected_lang = normalize_ui_lang(lang)
    store = ProductShellStore(product_shell_store_path) if product_shell_store_path else ProductShellStore()
    history = [_localize_shell_run(run, selected_lang) for run in store.list_runs(limit=12)]
    return {
        "summary": _localize_summary(store.build_summary(), selected_lang),
        "history": history,
        "history_filters": _build_filter_options(selected_lang),
        "approval_queue": [
            _localize_approval_item(item, selected_lang) for item in store.build_approval_queue(limit=8)
        ],
        "audit_view": [_localize_audit_record(record, selected_lang) for record in store.build_audit_view(limit=20)],
        "audit_filters": _build_filter_options(selected_lang),
    }


def build_product_shell_history(
    *,
    decision: str | None = None,
    run_status: str | None = None,
    provider: str | None = None,
    lang: str | None = None,
    product_shell_store_path: Path | None = None,
) -> dict[str, Any]:
    selected_lang = normalize_ui_lang(lang)
    store = ProductShellStore(product_shell_store_path) if product_shell_store_path else ProductShellStore()
    normalized = str(decision).upper() if decision else "ALL"
    normalized_status = str(run_status).upper() if run_status else "ALL"
    normalized_provider = str(provider).upper() if provider else "ALL"
    return {
        "decision_filter": normalized,
        "run_status_filter": normalized_status,
        "provider_filter": normalized_provider,
        "filters": _build_filter_options(selected_lang),
        "runs": [
            _localize_shell_run(run, selected_lang)
            for run in store.list_runs(
                limit=20,
                decision=normalized,
                run_status=normalized_status,
                provider=normalized_provider,
            )
        ],
    }


def build_product_shell_approval_queue(
    *,
    lang: str | None = None,
    product_shell_store_path: Path | None = None,
) -> dict[str, Any]:
    selected_lang = normalize_ui_lang(lang)
    store = ProductShellStore(product_shell_store_path) if product_shell_store_path else ProductShellStore()
    return {
        "items": [_localize_approval_item(item, selected_lang) for item in store.build_approval_queue(limit=12)]
    }


def build_product_shell_audit_view(
    *,
    decision: str | None = None,
    integrity_state: str | None = None,
    provider: str | None = None,
    lang: str | None = None,
    product_shell_store_path: Path | None = None,
) -> dict[str, Any]:
    selected_lang = normalize_ui_lang(lang)
    store = ProductShellStore(product_shell_store_path) if product_shell_store_path else ProductShellStore()
    normalized_decision = str(decision).upper() if decision else "ALL"
    normalized_integrity = str(integrity_state).upper() if integrity_state else "ALL"
    normalized_provider = str(provider).upper() if provider else "ALL"
    return {
        "decision_filter": normalized_decision,
        "integrity_filter": normalized_integrity,
        "provider_filter": normalized_provider,
        "filters": _build_filter_options(selected_lang),
        "records": [
            _localize_audit_record(record, selected_lang)
            for record in store.build_audit_view(
                limit=20,
                decision=normalized_decision,
                integrity_state=normalized_integrity,
                provider=normalized_provider,
            )
        ],
    }


def _build_localized_ui_content(lang: str) -> dict[str, Any]:
    content = deepcopy(UI_CONTENT)
    content["language"] = {"selected": lang, "supported": language_options()}
    content["ui_labels"] = _ui_labels(lang)
    content["identity"]["positioning"] = tr(
        lang,
        en=content["identity"]["positioning"],
        ru="Security/control layer для AI agents.",
        uz="AI agentlar uchun security/control layer.",
    )
    content["identity"]["summary"] = tr(
        lang,
        en=content["identity"]["summary"],
        ru=(
            "SafeCore стоит между AI agent и внешними инструментами или системами, "
            "оценивает риск и возвращает guarded result до выполнения."
        ),
        uz=(
            "SafeCore AI agent bilan tashqi tool yoki tizim o'rtasida turadi, "
            "riskni baholaydi va executiondan oldin guarded result qaytaradi."
        ),
    )
    content["identity"]["status"] = [
        tr(lang, en="Open-source RC/MVP", ru="Open-source RC/MVP", uz="Open-source RC/MVP"),
        tr(lang, en="Validated core", ru="Validated core", uz="Validated core"),
        "Apache 2.0",
        tr(lang, en="Dry-run only", ru="Только dry-run", uz="Faqat dry-run"),
    ]
    content["overview"]["headline"] = tr(
        lang,
        en=content["overview"]["headline"],
        ru="SafeCore делает выполнение agent controllable до обращения к инструментам.",
        uz="SafeCore agent execution'ni tool ishlatilishidan oldin controllable qiladi.",
    )
    content["overview"]["subtext"] = tr(
        lang,
        en=content["overview"]["subtext"],
        ru=(
            "Это не ещё один agent runtime. Это middleware вокруг execution: "
            "policy, guards, approval, audit, routing и blocked-path behavior."
        ),
        uz=(
            "Bu yana bir agent runtime emas. Bu execution atrofidagi middleware: "
            "policy, guards, approval, audit, routing va blocked-path behavior."
        ),
    )
    content["safe_integration"]["headline"] = tr(
        lang,
        en=content["safe_integration"]["headline"],
        ru="Первый practical integration path",
        uz="Birinchi practical integration path",
    )
    content["safe_integration"]["subtext"] = tr(
        lang,
        en=content["safe_integration"]["subtext"],
        ru=(
            "SafeCore уже поддерживает один practical connector path: "
            "allowlisted read-only HTTP status flow для trusted local endpoints."
        ),
        uz=(
            "SafeCore hozirning o'zida bitta practical connector path'ni qo'llab-quvvatlaydi: "
            "trusted local endpoints uchun allowlisted read-only HTTP status flow."
        ),
    )
    content["safe_integration"]["connects_to"] = tr(
        lang,
        en=content["safe_integration"]["connects_to"],
        ru="Только trusted local или internal-style health/status/metadata endpoints на allowlisted hosts.",
        uz="Faqat allowlisted host'lardagi trusted local yoki internal-style health/status/metadata endpoint'lar.",
    )
    content["safe_integration"]["allowed"] = [
        tr(lang, en="GET only", ru="Только GET", uz="Faqat GET"),
        tr(lang, en="localhost / 127.0.0.1 only", ru="Только localhost / 127.0.0.1", uz="Faqat localhost / 127.0.0.1"),
        tr(lang, en="health, status, metadata, or version paths only", ru="Только пути health, status, metadata или version", uz="Faqat health, status, metadata yoki version path'lari"),
        tr(lang, en="connector request still passes through policy, tool guard, approval, audit, and execution boundaries", ru="connector request всё равно проходит через policy, tool guard, approval, audit и execution boundaries", uz="connector request baribir policy, tool guard, approval, audit va execution boundaries orqali o'tadi"),
    ]
    content["safe_integration"]["blocked"] = [
        tr(lang, en="non-allowlisted hosts", ru="не-allowlisted hosts", uz="allowlist'da yo'q host'lar"),
        tr(lang, en="non-GET methods", ru="не-GET методы", uz="GET bo'lmagan method'lar"),
        tr(lang, en="arbitrary outbound HTTP targets", ru="произвольные outbound HTTP targets", uz="ixtiyoriy outbound HTTP target'lar"),
        tr(lang, en="mutation-style requests pretending to be a status call", ru="mutation-style requests, притворяющиеся status call", uz="status call ko'rinishidagi mutation-style requests"),
    ]
    content["safe_integration"]["why_it_matters"] = tr(
        lang,
        en=content["safe_integration"]["why_it_matters"],
        ru="Показывает, где SafeCore стоит в реальном workflow: прямо перед connector boundary, с явным allow/block behavior и audit evidence.",
        uz="SafeCore real workflow ichida qayerda turishini ko'rsatadi: connector boundary oldida, aniq allow/block behavior va audit evidence bilan.",
    )
    content["safe_integration"]["how_to_use"] = tr(
        lang,
        en=content["safe_integration"]["how_to_use"],
        ru="Запустите local API, откройте UI, выполните allowlisted_get, затем сравните его с blocked_host и blocked_method.",
        uz="Local API'ni ishga tushiring, UI'ni oching, allowlisted_get'ni bajaring va uni blocked_host hamda blocked_method bilan solishtiring.",
    )
    content["safe_integration"]["developer_placement"] = tr(
        lang,
        en=content["safe_integration"]["developer_placement"],
        ru="Разработчики должны ставить SafeCore между app или agent и connector call.",
        uz="Developerlar SafeCore'ni app yoki agent bilan connector call o'rtasiga qo'yishi kerak.",
    )
    content["reference_product"]["headline"] = tr(
        lang,
        en=content["reference_product"]["headline"],
        ru="Попробуйте SafeCore в реальном workflow",
        uz="SafeCore'ni real workflow ichida sinab ko'ring",
    )
    content["reference_product"]["subtext"] = tr(
        lang,
        en=content["reference_product"]["subtext"],
        ru="Этот reference product flow превращает простую user task в connector request, проводит её через SafeCore и возвращает guarded result.",
        uz="Bu reference product flow oddiy user task'ni connector request'ga aylantiradi, uni SafeCore orqali o'tkazadi va guarded result qaytaradi.",
    )
    content["reference_product"]["what_user_is_doing"] = tr(
        lang,
        en=content["reference_product"]["what_user_is_doing"],
        ru="Проверяет статус trusted local service через один узкий safe path.",
        uz="Trusted local service status'ini bitta tor safe path orqali tekshirmoqda.",
    )
    content["reference_product"]["what_safecore_is_protecting"] = tr(
        lang,
        en=content["reference_product"]["what_safecore_is_protecting"],
        ru="SafeCore защищает connector boundary через allowlisted hosts, доступ только по GET и blocked-safe behavior вне узкой policy.",
        uz="SafeCore connector boundary'ni allowlisted hosts, faqat GET access va tor policy'dan tashqarida blocked-safe behavior orqali himoya qiladi.",
    )
    content["reference_product"]["why_it_matters"] = tr(
        lang,
        en=content["reference_product"]["why_it_matters"],
        ru="Это делает проект похожим на usable product flow, а не только на core с docs.",
        uz="Bu loyihani faqat docs bilan core emas, balki usable product flow sifatida ko'rsatadi.",
    )
    content["product_shell"]["headline"] = tr(lang, en=content["product_shell"]["headline"], ru="Функции product shell", uz="Product shell funksiyalari")
    content["product_shell"]["subtext"] = tr(
        lang,
        en=content["product_shell"]["subtext"],
        ru="Этот shell добавляет monitoring, run history, approval visibility и audit evidence поверх текущих SafeCore flows.",
        uz="Bu shell joriy SafeCore flowlari ustiga monitoring, run history, approval visibility va audit evidence qo'shadi.",
    )
    content["product_shell"]["what_is_happening"] = tr(
        lang,
        en=content["product_shell"]["what_is_happening"],
        ru="Каждый run пишет локальное audit evidence, обновляет local shell history и делает guarded state понятнее.",
        uz="Har bir run lokal audit evidence yozadi, local shell history'ni yangilaydi va guarded state'ni tushunarli qiladi.",
    )
    content["product_shell"]["why_it_matters"] = tr(
        lang,
        en=content["product_shell"]["why_it_matters"],
        ru="Новый пользователь может быстро увидеть, что SafeCore разрешил, что заблокировал и где лежит evidence.",
        uz="Yangi foydalanuvchi SafeCore nimani ruxsat bergani, nimani bloklagani va evidence qayerda ekanini tez ko'ra oladi.",
    )
    content["product_shell"]["what_to_do_next"] = tr(
        lang,
        en=content["product_shell"]["what_to_do_next"],
        ru="Запустите один allowed example, один blocked example и approval_case, затем посмотрите summary, queue и audit viewer.",
        uz="Bitta allowed example, bitta blocked example va approval_case'ni ishga tushiring, keyin summary, queue va audit viewer'ni ko'ring.",
    )
    content["product_shell"]["history_hint"] = tr(
        lang,
        en=content["product_shell"]["history_hint"],
        ru="Используйте decision filter, чтобы сфокусироваться на ALLOW, NEEDS_APPROVAL или DENY runs.",
        uz="ALLOW, NEEDS_APPROVAL yoki DENY run'lariga e'tibor qaratish uchun decision filter'dan foydalaning.",
    )
    content["product_shell"]["approval_hint"] = tr(
        lang,
        en=content["product_shell"]["approval_hint"],
        ru="Pending items остаются blocked. Оператор должен проверить reason и operator checks.",
        uz="Pending items blocked bo'lib qoladi. Operator reason va operator checks'ni ko'rishi kerak.",
    )
    content["product_shell"]["audit_hint"] = tr(
        lang,
        en=content["product_shell"]["audit_hint"],
        ru="Audit viewer показывает недавний локальный evidence trail. Проблемы integrity отображаются явно.",
        uz="Audit viewer yaqindagi lokal evidence trail'ni ko'rsatadi. Integrity muammolari aniq ko'rsatiladi.",
    )
    return content


def _scenario_content(name: str, lang: str) -> dict[str, Any]:
    details = deepcopy(SCENARIO_CONTENT[name])
    if name == "allow_case":
        details["meaning"] = tr(lang, en=details["meaning"], ru="Низкорисковые действия могут пройти через guarded path.", uz="Past riskli action'lar guarded path orqali o'tishi mumkin.")
        details["example"] = tr(lang, en=details["example"], ru="Безопасное read-only shell действие, например `ls`.", uz="`ls` kabi xavfsiz read-only shell action.")
        details["why_it_matters"] = tr(lang, en=details["why_it_matters"], ru="Показывает, что low-risk actions проходят policy и guard checks без реальных side effects.", uz="Low-risk action'lar real side effects'siz policy va guard checks'dan o'tishini ko'rsatadi.")
        details["current_rc_behavior"] = tr(lang, en=details["current_rc_behavior"], ru="Execution остаётся DRY_RUN_SIMULATED.", uz="Execution DRY_RUN_SIMULATED holatida qoladi.")
    elif name == "approval_case":
        details["meaning"] = tr(lang, en=details["meaning"], ru="Рискованные действия остаются blocked до явного approval.", uz="Risky action'lar aniq approval bo'lmaguncha blocked bo'lib qoladi.")
        details["example"] = tr(lang, en=details["example"], ru="Production-style изменение конфигурации или suspicious outbound action.", uz="Production-style config change yoki suspicious outbound action.")
        details["why_it_matters"] = tr(lang, en=details["why_it_matters"], ru="Показывает, что approval — это реальный execution gate, а не косметический статус.", uz="Approval haqiqiy execution gate ekanini, oddiy status emasligini ko'rsatadi.")
        details["current_rc_behavior"] = tr(lang, en=details["current_rc_behavior"], ru="Request остаётся blocked со статусом approval PENDING до APPROVED.", uz="Request approval status PENDING bo'lib, APPROVED bo'lguncha blocked qoladi.")
    else:
        details["meaning"] = tr(lang, en=details["meaning"], ru="Явно опасные действия не должны выполняться.", uz="Aniq xavfli action'lar bajarilmasligi kerak.")
        details["example"] = tr(lang, en=details["example"], ru="Привилегированное destructive shell действие, например `rm -rf /`.", uz="`rm -rf /` kabi privileged destructive shell action.")
        details["why_it_matters"] = tr(lang, en=details["why_it_matters"], ru="Показывает, что опасные действия останавливаются сразу и не проходят через обычный approval override.", uz="Xavfli action'lar darhol to'xtatilishini va oddiy approval override orqali o'tmasligini ko'rsatadi.")
        details["current_rc_behavior"] = tr(lang, en=details["current_rc_behavior"], ru="Request остаётся blocked и non-overridable.", uz="Request blocked va non-overridable bo'lib qoladi.")
    return details


def _safe_http_example_content(name: str, lang: str) -> dict[str, Any]:
    details = deepcopy(SAFE_HTTP_EXAMPLE_CONTENT[name])
    if name == "allowlisted_get":
        details["title"] = tr(lang, en=details["title"], ru="Allowlisted read-only GET", uz="Allowlisted read-only GET")
        details["meaning"] = tr(lang, en=details["meaning"], ru="Узкий реальный connector path может получить trusted local health/status endpoint.", uz="Tor real connector path trusted local health/status endpoint'ni olishi mumkin.")
        details["why_it_matters"] = tr(lang, en=details["why_it_matters"], ru="Показывает, как SafeCore может стоять перед реальным integration path без расширения execution scope.", uz="SafeCore real integration path oldida execution scope'ni kengaytirmasdan turishi mumkinligini ko'rsatadi.")
        details["current_rc_behavior"] = tr(lang, en=details["current_rc_behavior"], ru="Connector выполняет один allowlisted safe read-only fetch; execution guard остаётся dry-run only.", uz="Connector bitta allowlisted safe read-only fetch bajaradi; execution guard dry-run only bo'lib qoladi.")
    elif name == "blocked_host":
        details["title"] = tr(lang, en=details["title"], ru="Заблокированный недоверенный host", uz="Bloklangan ishonchsiz host")
        details["meaning"] = tr(lang, en=details["meaning"], ru="Requests к non-allowlisted hosts не должны выполняться.", uz="Non-allowlisted host'larga requests o'tmasligi kerak.")
        details["why_it_matters"] = tr(lang, en=details["why_it_matters"], ru="Показывает явный destination allowlisting вместо произвольного outbound HTTP access.", uz="Ixtiyoriy outbound HTTP access o'rniga aniq destination allowlisting'ni ko'rsatadi.")
        details["current_rc_behavior"] = tr(lang, en=details["current_rc_behavior"], ru="Request блокируется до выполнения connector execution.", uz="Request connector execution boshlanishidan oldin bloklanadi.")
    else:
        details["title"] = tr(lang, en=details["title"], ru="Заблокированный non-GET request", uz="Bloklangan non-GET request")
        details["meaning"] = tr(lang, en=details["meaning"], ru="Example connector строго read-only и только GET.", uz="Example connector qat'iy read-only va faqat GET.")
        details["why_it_matters"] = tr(lang, en=details["why_it_matters"], ru="Показывает, что integration path намеренно остаётся узким и не может быть использован для mutation.", uz="Integration path ataylab tor qolishini va mutation uchun ishlatib bo'lmasligini ko'rsatadi.")
        details["current_rc_behavior"] = tr(lang, en=details["current_rc_behavior"], ru="Request блокируется и остаётся dry-run-safe.", uz="Request bloklanadi va dry-run-safe bo'lib qoladi.")
    return details


def _reference_product_flow_content(name: str, lang: str) -> dict[str, Any]:
    details = deepcopy(REFERENCE_PRODUCT_FLOW_CONTENT[name])
    if name == "safe_status_check":
        details["title"] = tr(lang, en=details["title"], ru="Проверить trusted local service health", uz="Trusted local service health'ni tekshirish")
        details["user_task"] = tr(lang, en=details["user_task"], ru="Пользователь хочет проверить, healthy ли trusted local service.", uz="Foydalanuvchi trusted local service healthy ekanini tekshirmoqchi.")
        details["what_safecore_protects"] = tr(lang, en=details["what_safecore_protects"], ru="SafeCore гарантирует, что request остаётся внутри узкой allowlisted read-only connector boundary.", uz="SafeCore request tor allowlisted read-only connector boundary ichida qolishini ta'minlaydi.")
        details["why_it_matters"] = tr(lang, en=details["why_it_matters"], ru="Показывает хороший путь: полезная status check разрешена, не превращая SafeCore в generic HTTP executor.", uz="Yaxshi yo'lni ko'rsatadi: foydali status check ruxsat etiladi, SafeCore'ni generic HTTP executor'ga aylantirmasdan.")
    elif name == "blocked_external_status":
        details["title"] = tr(lang, en=details["title"], ru="Попробовать недоверенный service host", uz="Ishonchsiz service host'ni sinash")
        details["user_task"] = tr(lang, en=details["user_task"], ru="Пользователь пытается проверить status на host, который явно не trusted.", uz="Foydalanuvchi aniq trusted bo'lmagan host'da status'ni tekshirmoqchi.")
        details["what_safecore_protects"] = tr(lang, en=details["what_safecore_protects"], ru="SafeCore предотвращает произвольный outbound access и блокирует connector path до начала выполнения.", uz="SafeCore ixtiyoriy outbound access'ni oldini oladi va connector path'ni boshlanishidan oldin bloklaydi.")
        details["why_it_matters"] = tr(lang, en=details["why_it_matters"], ru="Показывает, что allowlisting реально работает и неизвестные destinations по умолчанию blocked-safe.", uz="Allowlisting real ekanini va noma'lum destination'lar standart holatda blocked-safe ekanini ko'rsatadi.")
    else:
        details["title"] = tr(lang, en=details["title"], ru="Попробовать unsafe status method", uz="Unsafe status method'ni sinash")
        details["user_task"] = tr(lang, en=details["user_task"], ru="Пользователь пытается использовать non-GET method для status-style request.", uz="Foydalanuvchi status-style request uchun non-GET method ishlatmoqchi.")
        details["what_safecore_protects"] = tr(lang, en=details["what_safecore_protects"], ru="SafeCore принудительно соблюдает read-only boundary и отклоняет mutation-style requests.", uz="SafeCore read-only boundary'ni majburan saqlaydi va mutation-style requests'ni rad etadi.")
        details["why_it_matters"] = tr(lang, en=details["why_it_matters"], ru="Показывает, что connector path нельзя расширить до generic или destructive integration route.", uz="Connector path generic yoki destructive integration route'ga kengaytirib bo'lmasligini ko'rsatadi.")
    return details


def _ui_labels(lang: str) -> dict[str, Any]:
    return {
        "page_title": "SafeCore Product Shell",
        "navigation": {
            "overview": tr(lang, en="Overview", ru="Обзор", uz="Umumiy ko'rinish"),
            "onboarding": tr(lang, en="Onboarding", ru="Onboarding", uz="Onboarding"),
            "product_shell": tr(lang, en="Product Shell", ru="Product Shell", uz="Product Shell"),
            "providers": tr(lang, en="Providers", ru="Провайдеры", uz="Provayderlar"),
            "history": tr(lang, en="Run History", ru="История запусков", uz="Run tarixi"),
            "approval_audit": tr(lang, en="Approval And Audit", ru="Approval и Audit", uz="Approval va Audit"),
        },
        "hero": {
            "eyebrow": "SafeCore Product Shell",
            "title": tr(lang, en="Security/control layer for AI agents.", ru="Security/control layer для AI agents.", uz="AI agentlar uchun security/control layer."),
            "lead": tr(lang, en="Visualize the current SafeCore validated core, inspect the product shell, and run guarded local flows without leaving the dry-run posture.", ru="Визуализируйте текущий validated core SafeCore, изучайте product shell и запускайте guarded local flows, не выходя из dry-run posture.", uz="Joriy SafeCore validated core'ni ko'ring, product shell'ni o'rganing va dry-run posture'dan chiqmasdan guarded local flows'ni ishga tushiring."),
            "action_primary": tr(lang, en="Try reference product flow", ru="Запустить reference product flow", uz="Reference product flow'ni sinash"),
            "action_secondary": tr(lang, en="See product shell", ru="Смотреть product shell", uz="Product shell'ni ko'rish"),
            "language_label": tr(lang, en="Language", ru="Язык", uz="Til"),
        },
        "sections": {
            "overview_kicker": tr(lang, en="Overview", ru="Обзор", uz="Umumiy ko'rinish"),
            "overview_title": tr(lang, en="What SafeCore is right now", ru="Что такое SafeCore сейчас", uz="SafeCore hozir nima"),
            "project_identity": tr(lang, en="Project identity", ru="Идентичность проекта", uz="Loyiha identifikatori"),
            "what_safecore_does": tr(lang, en="What SafeCore does", ru="Что делает SafeCore", uz="SafeCore nima qiladi"),
            "onboarding_kicker": tr(lang, en="Onboarding", ru="Onboarding", uz="Onboarding"),
            "onboarding_title": tr(lang, en="Get oriented before your first guarded run", ru="Сориентируйтесь перед первым guarded run", uz="Birinchi guarded run oldidan yo'nalishni oling"),
            "onboarding_steps": tr(lang, en="Onboarding steps", ru="Шаги onboarding", uz="Onboarding qadamlari"),
            "reference_kicker": tr(lang, en="Reference Product Flow", ru="Reference Product Flow", uz="Reference Product Flow"),
            "reference_title": tr(lang, en="Turn one simple user task into a guarded SafeCore result", ru="Превратите одну простую задачу пользователя в guarded result SafeCore", uz="Bitta oddiy user task'ni guarded SafeCore result'ga aylantiring"),
            "reference_result": tr(lang, en="Reference Product Result", ru="Reference Product Result", uz="Reference Product Result"),
            "product_shell_kicker": tr(lang, en="Product Shell", ru="Product Shell", uz="Product Shell"),
            "product_shell_title": tr(lang, en="Monitoring, history, approval visibility, and audit evidence in one place", ru="Monitoring, история, visibility approval и audit evidence в одном месте", uz="Monitoring, tarix, approval visibility va audit evidence bir joyda"),
            "operations_overview": tr(lang, en="Operations overview", ru="Операционный обзор", uz="Operatsion overview"),
            "latest_events": tr(lang, en="Latest events", ru="Последние события", uz="So'nggi hodisalar"),
            "providers_kicker": tr(lang, en="Provider Status", ru="Статус провайдеров", uz="Provayder holati"),
            "providers_title": tr(lang, en="See configuration posture without exposing secrets", ru="Смотрите posture конфигурации без раскрытия секретов", uz="Sirlarni oshkor qilmasdan konfiguratsiya posture'ni ko'ring"),
            "history_kicker": tr(lang, en="Run History", ru="История запусков", uz="Run tarixi"),
            "history_title": tr(lang, en="See what SafeCore has allowed, blocked, or held for approval", ru="Смотрите, что SafeCore разрешил, заблокировал или удержал для approval", uz="SafeCore nimani ruxsat bergani, bloklagani yoki approval uchun ushlab turganini ko'ring"),
            "recent_runs": tr(lang, en="Recent runs", ru="Последние запуски", uz="So'nggi run'lar"),
            "approval_audit_kicker": tr(lang, en="Approval And Audit", ru="Approval и Audit", uz="Approval va Audit"),
            "approval_audit_title": tr(lang, en="Understand what needs attention and where the evidence lives", ru="Поймите, что требует внимания и где лежит evidence", uz="Nima e'tibor talab qilishini va evidence qayerda ekanini tushuning"),
            "approval_queue": tr(lang, en="Approval queue", ru="Очередь approval", uz="Approval navbati"),
            "audit_viewer": tr(lang, en="Audit viewer", ru="Audit viewer", uz="Audit viewer"),
            "decision_kicker": tr(lang, en="Three Decision States", ru="Три decision states", uz="Uchta decision holati"),
            "decision_title": "ALLOW, NEEDS_APPROVAL, DENY",
            "demo_kicker": tr(lang, en="Demo Runner", ru="Demo Runner", uz="Demo Runner"),
            "demo_title": tr(lang, en="Run the frozen scenarios through the current guarded path", ru="Запустите frozen scenarios через текущий guarded path", uz="Frozen scenario'larni joriy guarded path orqali ishga tushiring"),
            "scenario_result": tr(lang, en="Scenario Result", ru="Результат сценария", uz="Scenario natijasi"),
            "integration_kicker": tr(lang, en="First Practical Integration Path", ru="Первый practical integration path", uz="Birinchi practical integration path"),
            "integration_title": tr(lang, en="Use SafeCore in front of one real read-only connector boundary today", ru="Используйте SafeCore перед одной реальной read-only connector boundary уже сегодня", uz="Bugun SafeCore'ni bitta real read-only connector boundary oldida ishlating"),
            "integration_result": tr(lang, en="Integration Result", ru="Integration Result", uz="Integration Result"),
            "architecture_kicker": tr(lang, en="Architecture View", ru="Архитектура", uz="Arxitektura"),
            "architecture_title": tr(lang, en="How a request moves through SafeCore", ru="Как request проходит через SafeCore", uz="Request SafeCore orqali qanday o'tadi"),
            "scope_kicker": tr(lang, en="Current Scope", ru="Текущий scope", uz="Joriy scope"),
            "scope_title": tr(lang, en="Real today vs intentionally not included yet", ru="Что реально есть сегодня и что намеренно ещё не включено", uz="Bugun nima real, nimalar esa hali ataylab qo'shilmagan"),
            "use_today": tr(lang, en="How to use it today", ru="Как использовать сегодня", uz="Bugun qanday ishlatish"),
            "boundaries": tr(lang, en="Current boundaries", ru="Текущие границы", uz="Joriy chegaralar"),
            "audiences_kicker": tr(lang, en="For Whom It Matters", ru="Для кого это важно", uz="Kimlar uchun muhim"),
            "audiences_title": tr(lang, en="Who should care about this project", ru="Кому стоит обратить внимание на проект", uz="Bu loyiha kimlar uchun muhim"),
            "roadmap_kicker": tr(lang, en="Roadmap Direction", ru="Roadmap direction", uz="Roadmap yo'nalishi"),
            "roadmap_title": tr(lang, en="Where the project can grow without changing its identity", ru="Куда проект может расти без потери идентичности", uz="Loyiha identitetini o'zgartirmasdan qayerga o'sishi mumkin"),
        },
        "controls": {
            "choose_user_task": tr(lang, en="Choose user task", ru="Выберите задачу пользователя", uz="User task'ni tanlang"),
            "run_reference_flow": tr(lang, en="Run reference flow", ru="Запустить reference flow", uz="Reference flow'ni ishga tushirish"),
            "choose_demo_scenario": tr(lang, en="Choose demo scenario", ru="Выберите demo scenario", uz="Demo scenario'ni tanlang"),
            "run_scenario": tr(lang, en="Run scenario", ru="Запустить сценарий", uz="Scenario'ni ishga tushirish"),
            "choose_integration_example": tr(lang, en="Choose integration example", ru="Выберите integration example", uz="Integration example'ni tanlang"),
            "run_integration": tr(lang, en="Run integration example", ru="Запустить integration example", uz="Integration example'ni ishga tushirish"),
            "filter_by_decision": tr(lang, en="Filter by decision", ru="Фильтр по decision", uz="Decision bo'yicha filter"),
            "filter_by_status": tr(lang, en="Filter by run status", ru="Фильтр по статусу run", uz="Run status bo'yicha filter"),
            "filter_by_provider": tr(lang, en="Filter by provider mode", ru="Фильтр по provider mode", uz="Provider mode bo'yicha filter"),
            "filter_by_integrity": tr(lang, en="Filter by integrity", ru="Фильтр по integrity", uz="Integrity bo'yicha filter"),
            "refresh_history": tr(lang, en="Refresh history", ru="Обновить историю", uz="Tarixni yangilash"),
            "refresh_audit": tr(lang, en="Refresh audit view", ru="Обновить audit view", uz="Audit view'ni yangilash"),
            "open_section": tr(lang, en="Open section", ru="Открыть раздел", uz="Bo'limni ochish"),
            "mark_complete": tr(lang, en="Mark step complete", ru="Отметить шаг как завершённый", uz="Qadamni bajarilgan deb belgilash"),
            "next_onboarding_step": tr(lang, en="Next onboarding step", ru="Следующий шаг onboarding", uz="Keyingi onboarding qadami"),
            "reset_onboarding": tr(lang, en="Reset onboarding", ru="Сбросить onboarding", uz="Onboarding'ni tiklash"),
            "running": tr(lang, en="Running...", ru="Запуск...", uz="Ishga tushmoqda..."),
            "refreshing": tr(lang, en="Refreshing...", ru="Обновление...", uz="Yangilanmoqda..."),
        },
        "explanations": {
            "reference_microcopy": tr(lang, en="This is a minimal product shell around the current safe HTTP path. It remains honest: dry-run-first, narrow, and not a production platform.", ru="Это минимальный product shell вокруг текущего safe HTTP path. Он остаётся честным: dry-run-first, узкий и не production platform.", uz="Bu joriy safe HTTP path atrofidagi minimal product shell. U halol qoladi: dry-run-first, tor va production platform emas."),
            "demo_microcopy": tr(lang, en="This UI remains dry-run only and does not enable real external side effects.", ru="Этот UI остаётся только dry-run и не включает реальные external side effects.", uz="Bu UI dry-run holatida qoladi va real external side effects'ni yoqmaydi."),
            "integration_microcopy": tr(lang, en="This connector remains intentionally narrow: GET only, trusted local hosts only, blocked-safe for everything else.", ru="Этот connector намеренно остаётся узким: только GET, только trusted local hosts, blocked-safe для всего остального.", uz="Bu connector ataylab tor saqlanadi: faqat GET, faqat trusted local hosts, qolgan hammasi blocked-safe."),
            "allowed_title": tr(lang, en="Allowed", ru="Разрешено", uz="Ruxsat etilgan"),
            "blocked_title": tr(lang, en="Blocked", ru="Заблокировано", uz="Bloklangan"),
            "result_details": tr(lang, en="Result details", ru="Детали результата", uz="Result tafsilotlari"),
            "integration_details": tr(lang, en="Integration details", ru="Детали integration", uz="Integration tafsilotlari"),
            "reference_details": tr(lang, en="Reference product details", ru="Детали reference product", uz="Reference product tafsilotlari"),
        },
        "result_labels": {
            "decision": tr(lang, en="Decision", ru="Decision", uz="Decision"),
            "risk_score": tr(lang, en="Risk score", ru="Risk score", uz="Risk score"),
            "blocked": tr(lang, en="Blocked", ru="Blocked", uz="Blocked"),
            "approval": tr(lang, en="Approval", ru="Approval", uz="Approval"),
            "execution": tr(lang, en="Execution", ru="Execution", uz="Execution"),
            "connector": tr(lang, en="Connector", ru="Connector", uz="Connector"),
            "audit_integrity": tr(lang, en="Audit integrity", ru="Audit integrity", uz="Audit integrity"),
            "provider": tr(lang, en="Provider mode", ru="Provider mode", uz="Provider mode"),
            "run_status": tr(lang, en="Run status", ru="Run status", uz="Run status"),
            "meaning": tr(lang, en="Meaning", ru="Что происходит", uz="Nima bo'lyapti"),
            "example": tr(lang, en="Example", ru="Пример", uz="Misol"),
            "why_it_matters": tr(lang, en="Why it matters", ru="Почему это важно", uz="Nega bu muhim"),
            "current_behavior": tr(lang, en="Current RC behavior", ru="Текущее RC-поведение", uz="Joriy RC xulqi"),
            "audit_path": tr(lang, en="Audit path", ru="Путь к audit", uz="Audit yo'li"),
            "user_task": tr(lang, en="User task", ru="Задача пользователя", uz="User task"),
            "what_protects": tr(lang, en="What SafeCore protects", ru="Что защищает SafeCore", uz="SafeCore nimani himoya qiladi"),
            "short_explanation": tr(lang, en="Short explanation", ru="Короткое объяснение", uz="Qisqa tushuntirish"),
            "what_next": tr(lang, en="What this means for the user", ru="Что это значит для пользователя", uz="Bu foydalanuvchi uchun nimani anglatadi"),
            "why_waiting": tr(lang, en="Why it is waiting", ru="Почему ожидает", uz="Nega kutmoqda"),
            "what_to_check": tr(lang, en="What to check", ru="Что проверить", uz="Nimani tekshirish kerak"),
            "status": tr(lang, en="Status", ru="Статус", uz="Status"),
            "escalation": tr(lang, en="Escalation", ru="Эскалация", uz="Escalation"),
            "next_step": tr(lang, en="Next step", ru="Следующий шаг", uz="Keyingi qadam"),
            "integrity": tr(lang, en="Integrity", ru="Integrity", uz="Integrity"),
            "audit_file": tr(lang, en="Audit file", ru="Audit file", uz="Audit file"),
            "run": tr(lang, en="Run", ru="Run", uz="Run"),
        },
        "empty_states": {
            "summary": tr(lang, en="No runs yet. Start with the reference product flow or the approval_case scenario.", ru="Пока нет runs. Начните с reference product flow или approval_case.", uz="Hali run yo'q. Reference product flow yoki approval_case'dan boshlang."),
            "history": tr(lang, en="No runs match this filter yet.", ru="Пока нет runs для этого filter.", uz="Bu filter uchun hali run yo'q."),
            "queue": tr(lang, en="No pending approval items yet. Run approval_case in the demo runner to see one here.", ru="Пока нет pending approval items. Запустите approval_case в demo runner.", uz="Hali pending approval item yo'q. Demo runner ichida approval_case'ni ishga tushiring."),
            "audit": tr(lang, en="No audit records available yet. Run a scenario to generate local evidence.", ru="Пока нет audit records. Запустите сценарий, чтобы создать local evidence.", uz="Hali audit records yo'q. Lokal evidence yaratish uchun scenario'ni ishga tushiring."),
        },
        "errors": {
            "ui_load_failed": tr(lang, en="SafeCore Product Shell failed to load.", ru="SafeCore Product Shell не удалось загрузить.", uz="SafeCore Product Shell yuklanmadi."),
            "scenario_failed": tr(lang, en="Scenario failed", ru="Сценарий завершился ошибкой", uz="Scenario xatoga uchradi"),
            "integration_failed": tr(lang, en="Integration example failed", ru="Integration example завершился ошибкой", uz="Integration example xatoga uchradi"),
            "reference_failed": tr(lang, en="Reference product flow failed", ru="Reference product flow завершился ошибкой", uz="Reference product flow xatoga uchradi"),
            "history_failed": tr(lang, en="History failed to load", ru="Не удалось загрузить историю", uz="Tarixni yuklab bo'lmadi"),
        },
    }


def _build_demo_ui_service(audit_file: Path) -> GuardedExecutionService:
    audit_logger = AuditLogger(audit_file)
    tool_guard = ToolGuard()
    approval_manager = ApprovalManager(
        audit_logger=audit_logger,
        id_factory=CounterIdFactory(),
    )
    return GuardedExecutionService(
        policy_engine=PolicyEngine(opa_binary="definitely-not-opa"),
        data_guard=DataGuard(),
        tool_guard=tool_guard,
        execution_guard=ExecutionGuard(tool_guard=tool_guard),
        audit_logger=audit_logger,
        approval_manager=approval_manager,
    )


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR)).replace("\\", "/")
    except ValueError:
        return str(path)


def _reference_flow_explanation(*, lang: str, decision: str, blocked: bool, connector_status: str) -> str:
    if decision == "ALLOW" and not blocked:
        return tr(
            lang,
            en=(
                "SafeCore allowed the trusted read-only status check. "
                f"The connector path completed with status {connector_status} and the broader execution posture remained dry-run-first."
            ),
            ru=(
                "SafeCore разрешил trusted read-only status check. "
                f"Connector path завершился со статусом {connector_status}, а общая execution posture осталась dry-run-first."
            ),
            uz=(
                "SafeCore trusted read-only status check'ga ruxsat berdi. "
                f"Connector path {connector_status} statusi bilan tugadi va umumiy execution posture dry-run-first bo'lib qoldi."
            ),
        )
    return tr(
        lang,
        en=(
            "SafeCore blocked the user task before it could widen beyond the narrow safe connector boundary. "
            f"Connector status: {connector_status or 'BLOCKED'}."
        ),
        ru=(
            "SafeCore заблокировал user task до того, как она могла выйти за узкую safe connector boundary. "
            f"Connector status: {connector_status or 'BLOCKED'}."
        ),
        uz=(
            "SafeCore user task'ni tor safe connector boundary'dan chiqib ketishidan oldin blokladi. "
            f"Connector status: {connector_status or 'BLOCKED'}."
        ),
    )


def _demo_scenario_explanation(*, lang: str, decision: str, blocked: bool, approval_status: str) -> str:
    if decision == "ALLOW" and not blocked:
        return tr(lang, en="SafeCore judged the action low-risk, so the request stayed on the safe dry-run path.", ru="SafeCore посчитал действие low-risk, поэтому request остался на safe dry-run path.", uz="SafeCore action'ni low-risk deb baholadi, shuning uchun request safe dry-run path ichida qoldi.")
    if decision == "NEEDS_APPROVAL":
        return tr(
            lang,
            en=(
                "SafeCore kept the request blocked because explicit approval is still required. "
                f"Current approval status: {approval_status or 'PENDING'}."
            ),
            ru=(
                "SafeCore оставил request blocked, потому что всё ещё требуется явное approval. "
                f"Текущий approval status: {approval_status or 'PENDING'}."
            ),
            uz=(
                "SafeCore request'ni blocked holatda qoldirdi, chunki hali ham aniq approval kerak. "
                f"Joriy approval status: {approval_status or 'PENDING'}."
            ),
        )
    return tr(lang, en="SafeCore blocked the request because it crossed a dangerous policy boundary.", ru="SafeCore заблокировал request, потому что она пересекла опасную policy boundary.", uz="SafeCore request'ni blokladi, chunki u xavfli policy boundary'dan o'tdi.")


def _safe_http_explanation(*, lang: str, decision: str, blocked: bool, connector_status: str) -> str:
    if decision == "ALLOW" and not blocked:
        return tr(
            lang,
            en="SafeCore allowed the narrow read-only status request because the host, method, and path stayed inside the allowlist.",
            ru="SafeCore разрешил узкий read-only status request, потому что host, method и path остались внутри allowlist.",
            uz="SafeCore tor read-only status request'ga ruxsat berdi, chunki host, method va path allowlist ichida qoldi.",
        )
    return tr(
        lang,
        en=(
            "SafeCore blocked the request before connector execution could widen. "
            f"Connector status: {connector_status or 'BLOCKED'}."
        ),
        ru=(
            "SafeCore заблокировал request до того, как connector execution мог расшириться. "
            f"Connector status: {connector_status or 'BLOCKED'}."
        ),
        uz=(
            "SafeCore connector execution kengayishidan oldin request'ni blokladi. "
            f"Connector status: {connector_status or 'BLOCKED'}."
        ),
    )


def _record_product_shell_run(
    *,
    source: str,
    payload: dict[str, Any],
    run_id: str,
    action: str,
    tool: str,
    audit_file: Path | None,
    product_shell_store_path: Path | None,
    short_explanation: str,
) -> None:
    summary = payload.get("summary", {})
    result = payload.get("result", {})
    policy_decision = result.get("policy_decision", {}) if isinstance(result, dict) else {}
    approval = result.get("approval", {}) if isinstance(result, dict) else {}
    escalation = approval.get("escalation", {}) if isinstance(approval, dict) else {}
    reasons = policy_decision.get("reasons", []) if isinstance(policy_decision, dict) else []
    operator_checks = policy_decision.get("operator_checks", []) if isinstance(policy_decision, dict) else []
    store = ProductShellStore(product_shell_store_path) if product_shell_store_path else ProductShellStore()
    store.append_run(
        {
            "run_id": run_id,
            "source": source,
            "name": payload.get("scenario") or payload.get("example") or payload.get("flow"),
            "title": payload.get("title"),
            "request_type": action or tool,
            "provider_mode": "LOCAL_DEMO",
            "decision": summary.get("decision"),
            "risk_score": summary.get("risk_score"),
            "blocked": bool(summary.get("blocked", True)),
            "approval_status": summary.get("approval_status"),
            "connector_status": summary.get("connector_status"),
            "execution_status": summary.get("execution_status"),
            "audit_integrity": bool(summary.get("audit_integrity", False)),
            "audit_path": summary.get("audit_path"),
            "audit_file": str(audit_file) if audit_file is not None else "",
            "short_explanation": short_explanation,
            "why_blocked": reasons[0] if reasons else short_explanation,
            "operator_checks": operator_checks if isinstance(operator_checks, list) else [],
            "next_step": _next_step_from_summary(
                lang="en",
                decision=str(summary.get("decision", "")),
                blocked=bool(summary.get("blocked", True)),
                approval_status=str(summary.get("approval_status", "")),
            ),
            "escalation_state": escalation.get("state", "NONE") if isinstance(escalation, dict) else "NONE",
        }
    )


def _next_step_from_summary(*, lang: str, decision: str, blocked: bool, approval_status: str) -> str:
    if decision == "ALLOW" and not blocked:
        return tr(lang, en="Review the audit trail, then keep using the same narrow path for safe status checks.", ru="Проверьте audit trail и продолжайте использовать тот же узкий path для safe status checks.", uz="Audit trail'ni ko'rib chiqing, keyin safe status checks uchun shu tor path'dan foydalanishda davom eting.")
    if approval_status == "PENDING":
        return tr(lang, en="An operator should review the reason and operator checks before deciding outside this demo shell.", ru="Оператор должен проверить reason и operator checks перед принятием решения вне этого demo shell.", uz="Operator bu demo shell tashqarisida qaror qilishdan oldin reason va operator checks'ni ko'rishi kerak.")
    return tr(lang, en="Adjust the request so it stays inside the allowed connector boundary or choose a safer action.", ru="Измените request так, чтобы она оставалась внутри allowed connector boundary, или выберите более безопасное действие.", uz="Request'ni allowed connector boundary ichida qoladigan qilib o'zgartiring yoki xavfsizroq action tanlang.")


def _why_blocked_from_summary(
    *,
    lang: str,
    decision: str,
    blocked: bool,
    approval_status: str,
    connector_status: str,
) -> str:
    if decision == "NEEDS_APPROVAL":
        return tr(lang, en=f"Approval is still required. Current status: {approval_status or 'PENDING'}.", ru=f"Approval всё ещё требуется. Текущий статус: {approval_status or 'PENDING'}.", uz=f"Approval hali ham kerak. Joriy status: {approval_status or 'PENDING'}.")
    if blocked:
        return tr(lang, en=f"SafeCore blocked the request before it could widen. Connector status: {connector_status or 'BLOCKED'}.", ru=f"SafeCore заблокировал request до расширения. Connector status: {connector_status or 'BLOCKED'}.", uz=f"SafeCore request'ni kengayishidan oldin blokladi. Connector status: {connector_status or 'BLOCKED'}.")
    return tr(lang, en="The request stayed inside the current safe boundary.", ru="Request остался внутри текущей safe boundary.", uz="Request joriy safe boundary ichida qoldi.")


def _resolve_audit_file(audit_path: Any) -> Path | None:
    if not isinstance(audit_path, str) or not audit_path.strip():
        return None
    candidate = Path(audit_path)
    if candidate.is_absolute():
        return candidate
    return ROOT_DIR / audit_path


def _localize_summary(summary: dict[str, Any], lang: str) -> dict[str, Any]:
    localized = deepcopy(summary)
    localized["latest_events"] = [
        {
            **event,
            "summary": _localize_event_summary(event, lang),
            "provider_mode_label": _provider_mode_label(str(event.get("provider_mode", "LOCAL_DEMO")), lang),
            "run_status_label": _run_status_label(str(event.get("run_status", "")), lang),
        }
        for event in summary.get("latest_events", [])
    ]
    return localized


def _localize_event_summary(event: dict[str, Any], lang: str) -> str:
    decision = str(event.get("decision", "")).upper()
    blocked = bool(event.get("blocked", True))
    if decision == "ALLOW" and not blocked:
        return tr(lang, en="SafeCore allowed this run and kept it inside the current safe boundary.", ru="SafeCore разрешил этот run и оставил его внутри текущей safe boundary.", uz="SafeCore bu run'ga ruxsat berdi va uni joriy safe boundary ichida qoldirdi.")
    if decision == "NEEDS_APPROVAL":
        return tr(lang, en="SafeCore kept this run waiting for explicit approval.", ru="SafeCore оставил этот run в ожидании явного approval.", uz="SafeCore bu run'ni aniq approval kutish holatida qoldirdi.")
    return tr(lang, en="SafeCore blocked this run before it could proceed.", ru="SafeCore заблокировал этот run до выполнения.", uz="SafeCore bu run'ni davom etishidan oldin blokladi.")


def _localize_shell_run(run: dict[str, Any], lang: str) -> dict[str, Any]:
    localized = deepcopy(run)
    decision = str(run.get("decision", "")).upper()
    approval_status = str(run.get("approval_status", ""))
    connector_status = str(run.get("connector_status", ""))
    blocked = bool(run.get("blocked", True))
    if str(run.get("source", "")) == "safe_integration":
        localized["short_explanation"] = _safe_http_explanation(
            lang=lang,
            decision=decision,
            blocked=blocked,
            connector_status=connector_status,
        )
    elif str(run.get("source", "")) == "reference_product":
        localized["short_explanation"] = _reference_flow_explanation(
            lang=lang,
            decision=decision,
            blocked=blocked,
            connector_status=connector_status,
        )
    else:
        localized["short_explanation"] = _demo_scenario_explanation(
            lang=lang,
            decision=decision,
            blocked=blocked,
            approval_status=approval_status,
        )
    localized["next_step"] = _next_step_from_summary(
        lang=lang,
        decision=decision,
        blocked=blocked,
        approval_status=approval_status,
    )
    localized["provider_mode_label"] = _provider_mode_label(str(run.get("provider_mode", "LOCAL_DEMO")), lang)
    localized["run_status_label"] = _run_status_label(str(run.get("run_status", "")), lang)
    localized["why_blocked"] = _why_blocked_from_summary(
        lang=lang,
        decision=decision,
        blocked=blocked,
        approval_status=approval_status,
        connector_status=connector_status,
    )
    return localized


def _localize_approval_item(item: dict[str, Any], lang: str) -> dict[str, Any]:
    localized = deepcopy(item)
    localized["why_blocked"] = tr(
        lang,
        en=str(item.get("why_blocked", "")),
        ru=str(item.get("why_blocked", "")),
        uz=str(item.get("why_blocked", "")),
    )
    localized["next_step"] = tr(
        lang,
        en=str(item.get("next_step", "")),
        ru=str(item.get("next_step", "")),
        uz=str(item.get("next_step", "")),
    )
    return localized


def _localize_audit_record(record: dict[str, Any], lang: str) -> dict[str, Any]:
    localized = deepcopy(record)
    localized["integrity_state_label"] = tr(
        lang,
        en=str(record.get("integrity_state", "")),
        ru=str(record.get("integrity_state", "")),
        uz=str(record.get("integrity_state", "")),
    )
    localized["provider_mode_label"] = _provider_mode_label(str(record.get("provider_mode", "LOCAL_DEMO")), lang)
    localized["run_status_label"] = _run_status_label(str(record.get("run_status", "")), lang)
    localized["plain_summary"] = _plain_audit_summary(record, lang)
    localized["next_step"] = _audit_next_step(record, lang)
    return localized


def _provider_mode_label(value: str, lang: str) -> str:
    normalized = str(value or "LOCAL_DEMO").upper()
    if normalized == "LOCAL_DEMO":
        return tr(lang, en="Local / demo mode", ru="Local / demo mode", uz="Lokal / demo mode")
    return normalized


def _run_status_label(value: str, lang: str) -> str:
    normalized = str(value or "").upper()
    if normalized == "ALLOWED":
        return tr(lang, en="Allowed", ru="Разрешено", uz="Ruxsat etilgan")
    if normalized == "PENDING_APPROVAL":
        return tr(lang, en="Pending approval", ru="Ожидает approval", uz="Approval kutilmoqda")
    if normalized == "BLOCKED":
        return tr(lang, en="Blocked", ru="Заблокировано", uz="Bloklangan")
    return normalized or tr(lang, en="Unknown", ru="Неизвестно", uz="Noma'lum")


def _plain_audit_summary(record: dict[str, Any], lang: str) -> str:
    integrity_state = str(record.get("integrity_state", "")).upper()
    decision = str(record.get("decision", "")).upper()
    if integrity_state == "BROKEN":
        return tr(
            lang,
            en="This audit chain needs attention because integrity is broken.",
            ru="Эта audit chain требует внимания, потому что integrity нарушена.",
            uz="Bu audit chain e'tibor talab qiladi, chunki integrity buzilgan.",
        )
    if decision == "ALLOW":
        return tr(
            lang,
            en="This record shows a run that stayed inside the current safe boundary.",
            ru="Этот record показывает run, который остался внутри текущей safe boundary.",
            uz="Bu record joriy safe boundary ichida qolgan run'ni ko'rsatadi.",
        )
    if decision == "NEEDS_APPROVAL":
        return tr(
            lang,
            en="This record shows a run that stopped and waited for explicit approval.",
            ru="Этот record показывает run, который остановился и ждёт explicit approval.",
            uz="Bu record to'xtagan va explicit approval kutayotgan run'ni ko'rsatadi.",
        )
    return tr(
        lang,
        en="This record shows a run that SafeCore blocked before it could proceed.",
        ru="Этот record показывает run, который SafeCore заблокировал до выполнения.",
        uz="Bu record SafeCore davom etishidan oldin bloklagan run'ni ko'rsatadi.",
    )


def _audit_next_step(record: dict[str, Any], lang: str) -> str:
    integrity_state = str(record.get("integrity_state", "")).upper()
    if integrity_state == "BROKEN":
        return tr(
            lang,
            en="Inspect the local audit file and verify the latest linked records before trusting this trail.",
            ru="Проверьте локальный audit file и последние связанные записи, прежде чем доверять этому trail.",
            uz="Bu trail'ga ishonishdan oldin lokal audit file va so'nggi bog'langan yozuvlarni tekshiring.",
        )
    return tr(
        lang,
        en="Use the audit path if you need to inspect the underlying evidence in more detail.",
        ru="Используйте audit path, если нужно подробнее посмотреть underlying evidence.",
        uz="Underlying evidence'ni batafsil ko'rish kerak bo'lsa, audit path'dan foydalaning.",
    )
