"""Safe provider/configuration visibility for the local product shell."""

from __future__ import annotations

from typing import Any

from src.api.ui_i18n import normalize_ui_lang, tr
from src.providers import build_default_provider_gateway


PROVIDER_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "openai_compatible": "SAFECORE_OPENAI_COMPATIBLE_API_KEY",
}


def build_provider_status(lang: str | None = None) -> dict[str, Any]:
    """Return safe provider status content for the product shell."""
    selected_lang = normalize_ui_lang(lang)
    gateway = build_default_provider_gateway()
    catalog = gateway.safe_status_catalog()
    providers = [_localize_provider(snapshot, selected_lang) for snapshot in catalog["providers"]]

    return {
        "headline": tr(
            selected_lang,
            en="Provider status and integration gateway",
            ru="Статус провайдеров и integration gateway",
            uz="Provayder holati va integration gateway",
        ),
        "subtext": tr(
            selected_lang,
            en=(
                "This shell shows provider visibility and baseline gateway support only. "
                "It does not execute arbitrary model calls and it never exposes raw keys to the browser."
            ),
            ru=(
                "Этот shell показывает только видимость провайдеров и baseline gateway support. "
                "Он не выполняет произвольные model calls и никогда не отдаёт сырые ключи в браузер."
            ),
            uz=(
                "Bu shell faqat provayder holati va baseline gateway support'ni ko'rsatadi. "
                "U ixtiyoriy model chaqiruvlarini bajarmaydi va xom kalitlarni brauzerga bermaydi."
            ),
        ),
        "why_safe": tr(
            selected_lang,
            en="Keys stay in the backend environment. The UI receives status and safe bridge metadata only.",
            ru="Ключи остаются в backend environment. UI получает только статус и безопасные bridge metadata.",
            uz="Kalitlar backend env ichida qoladi. UI faqat holat va xavfsiz bridge metadata oladi.",
        ),
        "configured_help": tr(
            selected_lang,
            en="Configured means the backend found the required env variables or safe base_url settings for that adapter.",
            ru="Configured означает, что backend нашёл нужные env variables или безопасные base_url settings для этого adapter.",
            uz="Configured degani backend shu adapter uchun kerakli env variable yoki xavfsiz base_url settings'ni topdi.",
        ),
        "enabled_help": tr(
            selected_lang,
            en=(
                "Enabled means the current shell can use that provider path. "
                "Disabled means visibility only in this shell, even if a baseline backend gateway adapter exists."
            ),
            ru=(
                "Enabled означает, что текущий shell может использовать этот provider path. "
                "Disabled означает только видимость в этом shell, даже если baseline backend gateway adapter уже есть."
            ),
            uz=(
                "Enabled degani joriy shell shu provider path'dan foydalana oladi. "
                "Disabled esa bu shellda faqat visibility holati, hatto baseline backend gateway adapter mavjud bo'lsa ham."
            ),
        ),
        "gateway_help": tr(
            selected_lang,
            en="Gateway support shows whether SafeCore already includes a baseline backend adapter for future opt-in integrations.",
            ru="Gateway support показывает, включает ли SafeCore уже baseline backend adapter для будущих opt-in integrations.",
            uz="Gateway support SafeCore'da kelajakdagi opt-in integrations uchun baseline backend adapter mavjudligini ko'rsatadi.",
        ),
        "how_to_enable_title": tr(
            selected_lang,
            en="How to enable a provider card safely",
            ru="Как безопасно включить карточку провайдера",
            uz="Provayder kartasini qanday xavfsiz yoqish mumkin",
        ),
        "how_to_enable_steps": [
            tr(
                selected_lang,
                en="Set provider keys and optional base_url values in the backend environment, not in the browser.",
                ru="Задавайте ключи провайдера и при необходимости base_url в backend environment, а не в браузере.",
                uz="Provayder kalitlari va kerak bo'lsa base_url qiymatlarini brauzerda emas, backend environment ichida sozlang.",
            ),
            tr(
                selected_lang,
                en="Restart the local API so SafeCore can detect the new configuration.",
                ru="Перезапустите local API, чтобы SafeCore увидел новую конфигурацию.",
                uz="SafeCore yangi konfiguratsiyani ko'rishi uchun local API'ni qayta ishga tushiring.",
            ),
            tr(
                selected_lang,
                en="The shell will still show masked status only. Baseline backend integrations remain opt-in.",
                ru="Shell всё равно покажет только masked status. Baseline backend integrations остаются opt-in.",
                uz="Shell baribir faqat masked status'ni ko'rsatadi. Baseline backend integrations esa opt-in bo'lib qoladi.",
            ),
        ],
        "field_labels": {
            "configured": tr(selected_lang, en="Configured", ru="Configured", uz="Configured"),
            "enabled": tr(selected_lang, en="Enabled", ru="Enabled", uz="Enabled"),
            "key": tr(selected_lang, en="Key", ru="Ключ", uz="Kalit"),
            "source": tr(selected_lang, en="Source", ru="Источник", uz="Manba"),
            "base_url": tr(selected_lang, en="Base URL", ru="Base URL", uz="Base URL"),
            "gateway": tr(selected_lang, en="Gateway", ru="Gateway", uz="Gateway"),
            "health": tr(selected_lang, en="Health", ru="Health", uz="Health"),
            "capabilities": tr(selected_lang, en="Capabilities", ru="Возможности", uz="Imkoniyatlar"),
            "next_step": tr(selected_lang, en="How to enable", ru="Как включить", uz="Qanday yoqiladi"),
        },
        "gateway": {
            "headline": tr(
                selected_lang,
                en="Baseline backend adapters",
                ru="Baseline backend adapters",
                uz="Baseline backend adapters",
            ),
            "summary": tr(
                selected_lang,
                en="Provider adapters are opt-in and backend-only. They are meant to make SafeCore easier to adopt inside external stacks.",
                ru="Provider adapters являются opt-in и backend-only. Они нужны, чтобы SafeCore было проще встроить во внешние стеки.",
                uz="Provider adapters opt-in va faqat backend uchun. Ular SafeCore'ni tashqi steklarga ulashni osonlashtiradi.",
            ),
            "current_shell_enabled_ids": catalog["summary"]["current_shell_enabled_ids"],
            "opt_in_gateway_ids": catalog["summary"]["opt_in_gateway_ids"],
            "openai_compatible_bridge_ids": catalog["summary"]["openai_compatible_bridge_ids"],
            "framework_adapter_ids": catalog["summary"]["framework_adapter_ids"],
        },
        "providers": providers,
    }


def _localize_provider(snapshot: dict[str, Any], lang: str) -> dict[str, Any]:
    provider_id = str(snapshot["id"])
    configured = bool(snapshot["configured"])
    enabled = bool(snapshot["enabled"])
    local_demo_mode = bool(snapshot.get("local_demo_mode", False))
    base_url_label = str(snapshot.get("base_url_label", "Not configured"))
    base_url_status = str(snapshot.get("base_url_status", "NOT_CONFIGURED"))
    env_source = str(snapshot.get("env_source", "NO_KEY_REQUIRED"))
    base_url_env = str(snapshot.get("base_url_env", "NOT_APPLICABLE"))
    capability_names = [str(item) for item in snapshot.get("capability_names", [])]
    capability_details = snapshot.get("capability_details", [])
    health = snapshot.get("health", {})
    health_summary = str(health.get("summary", ""))

    if local_demo_mode:
        mode = tr(lang, en="Built in", ru="Встроенный", uz="Ichki")
        configured_label = tr(lang, en="Ready", ru="Готов", uz="Tayyor")
        enabled_label = tr(lang, en="Enabled", ru="Enabled", uz="Enabled")
        key_status = tr(lang, en="No key needed", ru="Ключ не нужен", uz="Kalit kerak emas")
        purpose = tr(
            lang,
            en="Built-in provider mode for the current shell, demo flows, and local product evaluation.",
            ru="Встроенный режим провайдера для текущего shell, demo flows и локальной оценки продукта.",
            uz="Joriy shell, demo flow va lokal product evaluation uchun ichki provider rejimi.",
        )
        status_summary = tr(
            lang,
            en="Built in and enabled for the current shell.",
            ru="Встроен и включён для текущего shell.",
            uz="Joriy shell uchun ichki va yoqilgan.",
        )
        how_to_enable = tr(
            lang,
            en="No setup required for local / demo mode.",
            ru="Для local / demo mode настройка не требуется.",
            uz="Lokal / demo mode uchun alohida sozlash kerak emas.",
        )
        safe_note = tr(
            lang,
            en="No provider key is used here. The shell stays local and dry-run-first.",
            ru="Здесь не используется ключ провайдера. Shell остаётся локальным и dry-run-first.",
            uz="Bu yerda provider kaliti ishlatilmaydi. Shell lokal va dry-run-first bo'lib qoladi.",
        )
    else:
        mode = _provider_mode_label(lang, adapter_kind=str(snapshot.get("adapter_kind", "")))
        configured_label = tr(
            lang,
            en="Configured" if configured else "Not configured",
            ru="Configured" if configured else "Not configured",
            uz="Configured" if configured else "Not configured",
        )
        enabled_label = tr(
            lang,
            en="Enabled" if enabled else "Disabled in current shell",
            ru="Enabled" if enabled else "Disabled в текущем shell",
            uz="Enabled" if enabled else "Joriy shellda disabled",
        )
        if bool(snapshot.get("masked_key_status", False)):
            key_status = tr(
                lang,
                en="Configured via env (masked)",
                ru="Configured через env (masked)",
                uz="Kalit env orqali sozlangan (masked)",
            )
        elif str(snapshot.get("auth_mode", "")).endswith("optional") and configured:
            key_status = tr(
                lang,
                en="No key required for current base URL",
                ru="Для текущего base URL ключ не нужен",
                uz="Joriy base URL uchun kalit kerak emas",
            )
        else:
            key_status = tr(
                lang,
                en="No key detected",
                ru="Ключ не найден",
                uz="Kalit topilmadi",
            )
        purpose = _provider_purpose(lang, provider_id=provider_id)
        status_summary = _provider_status_summary(
            lang,
            configured=configured,
            base_url_status=base_url_status,
            health_summary=health_summary,
        )
        how_to_enable = _how_to_enable(
            lang,
            env_source=env_source,
            base_url_env=base_url_env,
            base_url_status=base_url_status,
        )
        safe_note = tr(
            lang,
            en=f"UI receives only status. Raw {env_source} is never returned.",
            ru=f"UI получает только статус. Сырой {env_source} никогда не возвращается.",
            uz=f"UI faqat holatni oladi. Xom {env_source} hech qachon qaytarilmaydi.",
        )

    return {
        "id": provider_id,
        "name": snapshot["name"],
        "configured": configured,
        "enabled": enabled,
        "mode": mode,
        "configured_label": configured_label,
        "enabled_label": enabled_label,
        "key_status": key_status,
        "safe_note": safe_note,
        "purpose": purpose,
        "status_summary": status_summary,
        "how_to_enable": how_to_enable,
        "env_source": env_source,
        "base_url_env": base_url_env,
        "adapter_kind": snapshot.get("adapter_kind"),
        "gateway_support": _gateway_support_label(
            lang,
            support=str(snapshot.get("gateway_support", "baseline")),
        ),
        "base_url_status": base_url_status,
        "base_url_label": _base_url_label(lang, status=base_url_status, label=base_url_label),
        "local_demo_mode": local_demo_mode,
        "capabilities": [
            {
                "name": item.get("name"),
                "detail": item.get("detail"),
            }
            for item in capability_details
            if isinstance(item, dict)
        ],
        "capability_names": capability_names,
        "health": {
            "status": health.get("status"),
            "ok": bool(health.get("ok", False)),
            "summary": _health_summary_label(
                lang,
                configured=configured,
                enabled=enabled,
                summary=health_summary,
            ),
        },
    }


def _provider_mode_label(lang: str, *, adapter_kind: str) -> str:
    if adapter_kind == "openai_compatible":
        return tr(lang, en="OpenAI-compatible bridge", ru="OpenAI-compatible bridge", uz="OpenAI-compatible bridge")
    if adapter_kind == "anthropic":
        return tr(lang, en="Env-backed visibility", ru="Видимость через env", uz="Env orqali ko'rinish")
    return tr(lang, en="Env-backed visibility", ru="Видимость через env", uz="Env orqali ko'rinish")


def _provider_purpose(lang: str, *, provider_id: str) -> str:
    if provider_id == "openai_compatible":
        return tr(
            lang,
            en="Baseline OpenAI-compatible bridge for opt-in backend integrations and local or self-hosted compatible servers.",
            ru="Baseline OpenAI-compatible bridge для opt-in backend integrations и локальных или self-hosted compatible servers.",
            uz="Opt-in backend integrations hamda lokal yoki self-hosted compatible serverlar uchun baseline OpenAI-compatible bridge.",
        )
    if provider_id == "openrouter":
        return tr(
            lang,
            en="OpenAI-compatible provider card for future opt-in routing posture and proxy-style integrations.",
            ru="OpenAI-compatible provider card для будущего opt-in routing posture и proxy-style integrations.",
            uz="Kelajakdagi opt-in routing posture va proxy-style integrations uchun OpenAI-compatible provider card.",
        )
    if provider_id == "claude":
        return tr(
            lang,
            en="Safe backend visibility for Anthropic-style provider configuration and future extension.",
            ru="Безопасная backend visibility для Anthropic-style provider configuration и будущего расширения.",
            uz="Anthropic-style provider configuration va keyingi kengaytirish uchun xavfsiz backend visibility.",
        )
    return tr(
        lang,
        en="Visible for future integration posture, not used for arbitrary model execution in this shell.",
        ru="Показан для будущей integration posture, но не используется для произвольного model execution в этом shell.",
        uz="Kelajakdagi integration posture uchun ko'rsatiladi, ammo bu shellda ixtiyoriy model execution uchun ishlatilmaydi.",
    )


def _provider_status_summary(lang: str, *, configured: bool, base_url_status: str, health_summary: str) -> str:
    if configured:
        if base_url_status == "LOCAL_OVERRIDE":
            return tr(
                lang,
                en="Backend configuration is present. This adapter can target a local compatible endpoint in opt-in backend integrations.",
                ru="Backend configuration присутствует. Этот adapter может работать с локальным compatible endpoint в opt-in backend integrations.",
                uz="Backend configuration mavjud. Bu adapter opt-in backend integrations ichida lokal compatible endpoint bilan ishlashi mumkin.",
            )
        return tr(
            lang,
            en="Backend configuration is visible. The current shell stays visibility-only, but baseline backend integration support is available.",
            ru="Backend configuration видна. Текущий shell остаётся только visibility-only, но baseline backend integration support уже есть.",
            uz="Backend configuration ko'rinadi. Joriy shell faqat visibility-only bo'lib qoladi, ammo baseline backend integration support allaqachon mavjud.",
        )
    return health_summary or tr(
        lang,
        en="No backend configuration is present for this adapter yet.",
        ru="Для этого adapter пока нет backend configuration.",
        uz="Bu adapter uchun backend configuration hozircha yo'q.",
    )


def _how_to_enable(lang: str, *, env_source: str, base_url_env: str, base_url_status: str) -> str:
    if env_source == "NO_KEY_REQUIRED":
        return tr(
            lang,
            en="No provider key is required for this path.",
            ru="Для этого пути ключ провайдера не требуется.",
            uz="Bu path uchun provider kaliti talab qilinmaydi.",
        )
    if base_url_env != "NOT_APPLICABLE":
        if base_url_status == "NOT_CONFIGURED":
            return tr(
                lang,
                en=f"Set {base_url_env} and optionally {env_source} in the backend environment, then restart the local API.",
                ru=f"Задайте {base_url_env} и при необходимости {env_source} в backend environment, затем перезапустите local API.",
                uz=f"{base_url_env} va kerak bo'lsa {env_source} ni backend environment ichida sozlang, so'ng local API'ni qayta ishga tushiring.",
            )
        return tr(
            lang,
            en=f"Set {env_source} in the backend environment and restart the local API. The shell will still show masked status only.",
            ru=f"Задайте {env_source} в backend environment и перезапустите local API. Shell всё равно покажет только masked status.",
            uz=f"{env_source} ni backend environment ichida sozlang va local API'ni qayta ishga tushiring. Shell baribir faqat masked status'ni ko'rsatadi.",
        )
    return tr(
        lang,
        en=f"Set {env_source} in the backend environment and restart the local API.",
        ru=f"Задайте {env_source} в backend environment и перезапустите local API.",
        uz=f"{env_source} ni backend environment ichida sozlang va local API'ni qayta ishga tushiring.",
    )


def _gateway_support_label(lang: str, *, support: str) -> str:
    if support == "built_in":
        return tr(lang, en="Built in", ru="Встроенный", uz="Ichki")
    return tr(lang, en="Baseline backend adapter available", ru="Baseline backend adapter доступен", uz="Baseline backend adapter mavjud")


def _base_url_label(lang: str, *, status: str, label: str) -> str:
    if status == "DEFAULT":
        return tr(lang, en="Default API URL", ru="Default API URL", uz="Default API URL")
    if status == "NOT_CONFIGURED":
        return tr(lang, en="Not configured", ru="Not configured", uz="Not configured")
    return label


def _health_summary_label(lang: str, *, configured: bool, enabled: bool, summary: str) -> str:
    if enabled:
        return tr(lang, en="Ready in current shell", ru="Готов в текущем shell", uz="Joriy shellda tayyor")
    if configured:
        return tr(
            lang,
            en="Ready for opt-in backend integrations",
            ru="Готов для opt-in backend integrations",
            uz="Opt-in backend integrations uchun tayyor",
        )
    return summary or tr(
        lang,
        en="Needs backend configuration",
        ru="Требуется backend configuration",
        uz="Backend configuration kerak",
    )
