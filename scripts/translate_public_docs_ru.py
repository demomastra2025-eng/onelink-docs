#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path

try:
    from deep_translator import GoogleTranslator
    from deep_translator.exceptions import TranslationNotFound
except ImportError as exc:  # pragma: no cover - operator helper
    raise SystemExit(
        "Install deep-translator first, for example inside a venv, and rerun this script."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
LOCALIZER_PATH = ROOT / "scripts" / "localize_public_docs_ru.py"

LOCALIZER_NS = {"__file__": str(LOCALIZER_PATH), "__name__": "localize_public_docs_ru"}
exec(LOCALIZER_PATH.read_text(), LOCALIZER_NS)
DOC_MAP = LOCALIZER_NS["DOC_MAP"]
split_frontmatter = LOCALIZER_NS["split_frontmatter"]

TRANSLATOR = GoogleTranslator(source="en", target="ru")
CACHE: dict[str, str] = {}
PROTECTED_TERMS = [
    "One Link Cloud",
    "Application API",
    "Client API",
    "Platform API",
    "Captain AI",
    "Captain",
    "Codex",
    "Claude Code",
    "Agent Skills",
    "API",
    "CRM",
    "AI",
    "CSAT",
    "SLA",
    "workspace",
    "Workspace",
    "inbox",
    "Inbox",
    "inboxes",
    "Inboxes",
    "webhook",
    "Webhook",
    "webhooks",
    "Webhooks",
    "macro",
    "Macro",
    "macros",
    "Macros",
    "auth",
    "Auth",
    "copilot",
    "Copilot",
    "portal",
    "Portal",
    "go-live",
    "event-driven",
    "write-back",
    "WhatsApp",
    "Instagram",
    "Telegram",
]
FIXUPS = {
    "рабочая область": "workspace",
    "рабочей области": "workspace",
    "рабочую область": "workspace",
    "рабочем пространстве": "workspace",
    "рабочее пространство": "workspace",
    "рабочего пространства": "workspace",
    "Inboxes": "Inbox-очереди",
    "inboxes": "inbox-очереди",
    "веб-перехватчики": "webhooks",
    "Вебхуки": "Webhooks",
    "вебхуки": "webhooks",
    "разговоры": "диалоги",
    "Разговоры": "Диалоги",
    "конвейеры": "воронки",
    "В прямом эфире": "Запуск",
    "Паттерны рекомендации": "Паттерны интеграции",
    "Навыки агента": "Agent Skills",
    "API приложения": "Application API",
    "API платформы": "Platform API",
    "Клиентский API": "Client API",
    "Workspace Установочные слои": "Слои настройки workspace",
}


def english_heading(text: str) -> str | None:
    marker_match = re.search(r"## (?:Английская версия|English Version)\s+### (.+)", text, re.S)
    if marker_match:
        return marker_match.group(1).splitlines()[0].strip()
    h1_match = re.search(r"^# (.+)$", text, re.M)
    if h1_match:
        return h1_match.group(1).strip()
    return None


def build_label_map() -> dict[str, str]:
    labels: dict[str, str] = {}
    for page_id, cfg in DOC_MAP.items():
        path = ROOT / f"{page_id}.mdx"
        if not path.exists():
            path = ROOT / f"{page_id}.md"
        labels[cfg["heading"]] = cfg["heading"]
        heading = english_heading(path.read_text())
        if heading:
            labels[heading] = cfg["heading"]
    labels.update(
        {
            "API Introduction": "Справочник API One Link Cloud",
            "Workspace Setup": "Настройка рабочего пространства",
            "Inboxes And Channels": "Inbox-очереди и каналы",
            "Contacts And Conversations": "Контакты и диалоги",
            "CRM And Flexible Data": "CRM и гибкая структура данных",
            "Scheduling And Payments": "Расписание и оплаты",
            "Authentication And API Model": "Аутентификация и модель API",
            "Webhooks And Events": "Webhooks и события",
            "Integration Patterns": "Паттерны интеграции",
            "Agent Skills For Integrators": "Agent Skills для интеграторов",
            "Platform Overview": "Обзор платформы One Link Cloud",
            "Core Entities": "Ключевые сущности",
            "Workspace And Access": "Рабочее пространство и доступ",
            "Communication Workflows": "Коммуникационные процессы",
        }
    )
    return labels


LABEL_MAP = build_label_map()


def protect_terms(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    counter = 0

    def add(value: str) -> str:
        nonlocal counter
        token = f"ZZPH{counter}PHZZ"
        placeholders[token] = value
        counter += 1
        return token

    protected = text
    for term in sorted(PROTECTED_TERMS, key=len, reverse=True):
        protected = protected.replace(term, add(term))
    return protected, placeholders


def restore_placeholders(text: str, placeholders: dict[str, str]) -> str:
    restored = text
    for token, value in placeholders.items():
        restored = restored.replace(token, value)
    return restored


def apply_fixups(text: str) -> str:
    fixed = text
    for old, new in FIXUPS.items():
        fixed = fixed.replace(old, new)
    return fixed


def translate_fragment(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return text
    if not re.search(r"[A-Za-z]{2,}", text):
        return text
    if text in CACHE:
        return CACHE[text]
    protected, placeholders = protect_terms(text)
    try:
        translated = TRANSLATOR.translate(protected) or text
    except Exception:
        translated = text
    translated = restore_placeholders(translated, placeholders)
    translated = apply_fixups(translated)
    CACHE[text] = translated
    return translated


def localize_links(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        label, url = match.group(1), match.group(2)
        ru_label = LABEL_MAP.get(label, translate_fragment(label))
        return f"[{ru_label}]({url})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace, text)


def translate_mermaid_block(block: str) -> str:
    lines = block.splitlines()
    translated: list[str] = [lines[0]]

    def replace_group(match: re.Match[str]) -> str:
        opening, payload, closing = match.group(1), match.group(2), match.group(3)
        return f"{opening}{translate_fragment(payload)}{closing}"

    for line in lines[1:-1]:
        line = re.sub(r"(\[)([^\]]+)(\])", replace_group, line)
        line = re.sub(r"(\{)([^}]+)(\})", replace_group, line)
        line = re.sub(r"\|([^|]+)\|", lambda match: f"|{translate_fragment(match.group(1))}|", line)
        translated.append(line)

    translated.append(lines[-1])
    return "\n".join(translated)


def protect_code_blocks(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    counter = 0

    def add(value: str) -> str:
        nonlocal counter
        token = f"ZZCODE{counter}CODEZZ"
        placeholders[token] = value
        counter += 1
        return token

    def replace_block(match: re.Match[str]) -> str:
        block = match.group(0)
        if block.startswith("```mermaid"):
            block = translate_mermaid_block(block)
        return add(block)

    protected = re.sub(r"```[\s\S]*?```", replace_block, text)
    protected = re.sub(r"`[^`]+`", lambda match: add(match.group(0)), protected)
    return protected, placeholders


def extract_source_body(text: str, summary: str) -> str:
    _, body = split_frontmatter(text)
    if "## Английская версия" in body:
        body = body.split("## Английская версия", 1)[1].lstrip()
    elif "## English Version" in body:
        body = body.split("## English Version", 1)[1].lstrip()
    else:
        lines = body.splitlines()
        if lines and lines[0].startswith("# "):
            body = "\n".join(lines[1:]).lstrip("\n")

    if body.startswith(summary):
        body = body[len(summary) :].lstrip("\n")
    body = re.sub(r"^### .*\n+", "", body, count=1)
    return body.strip()


def translate_body(text: str, summary: str) -> str:
    body = extract_source_body(text, summary)
    if not body:
        return ""
    body = localize_links(body)
    body, code_placeholders = protect_code_blocks(body)
    body, term_placeholders = protect_terms(body)
    try:
        translated = TRANSLATOR.translate(body) or body
    except Exception:
        translated = body
    translated = restore_placeholders(translated, term_placeholders)
    translated = restore_placeholders(translated, code_placeholders)
    translated = apply_fixups(translated)
    return translated.strip()


def rewrite_page(page_id: str, cfg: dict[str, str]) -> None:
    path = ROOT / f"{page_id}.mdx"
    if not path.exists():
        path = ROOT / f"{page_id}.md"
    translated_body = translate_body(path.read_text(), cfg["summary"])

    frontmatter = (
        f"title: {cfg['title']}\n"
        f"description: {cfg['description']}\n"
        f"sidebarTitle: {cfg['sidebarTitle']}"
    )

    parts = [
        "---",
        frontmatter,
        "---",
        "",
        f"# {cfg['heading']}",
        "",
        cfg["summary"],
    ]
    if translated_body:
        parts.extend(["", translated_body])
    path.write_text("\n".join(parts).rstrip() + "\n")


def main() -> None:
    for page_id, cfg in DOC_MAP.items():
        rewrite_page(page_id, cfg)


if __name__ == "__main__":
    main()
