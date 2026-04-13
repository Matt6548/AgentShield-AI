"""Localization helpers for the SafeCore product shell UI."""

from __future__ import annotations


SUPPORTED_UI_LANGS = ("en", "ru", "uz")
DEFAULT_UI_LANG = "en"

LANGUAGE_LABELS = {
    "en": "English",
    "ru": "Русский",
    "uz": "O'zbek",
}


def normalize_ui_lang(value: str | None) -> str:
    normalized = str(value or DEFAULT_UI_LANG).strip().lower()
    if normalized not in SUPPORTED_UI_LANGS:
        return DEFAULT_UI_LANG
    return normalized


def tr(lang: str, *, en: str, ru: str, uz: str) -> str:
    normalized = normalize_ui_lang(lang)
    if normalized == "ru":
        return ru
    if normalized == "uz":
        return uz
    return en


def language_options() -> list[dict[str, str]]:
    return [{"code": code, "label": LANGUAGE_LABELS[code]} for code in SUPPORTED_UI_LANGS]
