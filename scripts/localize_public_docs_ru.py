#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


DOC_MAP = {
    "introduction": {
        "title": "Документация One Link Cloud",
        "description": "Публичная документация One Link Cloud: коммуникации, CRM, расписание, Captain AI, интеграции и API.",
        "sidebarTitle": "Введение",
        "heading": "One Link Cloud",
        "summary": """
One Link Cloud — это единое облачное рабочее пространство для клиентских коммуникаций и операционной работы.

В одном продукте объединены:

- каналы и inbox-очереди
- CRM и гибкие поля
- расписание, записи и оплаты
- Captain AI
- автоматизация и интеграции

Ниже оставлена английская версия страницы как вторичный reference-слой.
""".strip(),
    },
    "getting-started/quick-start": {
        "title": "Быстрый старт",
        "description": "Практический путь запуска One Link Cloud для команд, которым нужно быстро настроить коммуникации, CRM, расписание и AI-процессы.",
        "sidebarTitle": "Быстрый старт",
        "heading": "Быстрый старт",
        "summary": """
Эта страница помогает быстро пройти путь от пустого workspace до рабочей операционной среды.

Базовый порядок запуска:

1. создать workspace
2. пригласить команду
3. настроить inbox-очереди и маршрутизацию
4. подключить интеграции
5. включить CRM, расписание, Captain и автоматизации
""".strip(),
    },
    "getting-started/workspace-setup": {
        "title": "Настройка рабочего пространства",
        "description": "Как администраторы настраивают пользователей, команды, inbox-очереди, права доступа и клиентскую конфигурацию в One Link Cloud.",
        "sidebarTitle": "Настройка Workspace",
        "heading": "Настройка рабочего пространства",
        "summary": """
Настройка workspace определяет, как единое ядро One Link Cloud будет работать именно для вашей организации.

Основные слои настройки:

- пользователи и роли
- команды и membership
- inbox-очереди
- метки и кастомные поля
- интеграции
- автоматизации
""".strip(),
    },
    "platform/overview": {
        "title": "Обзор платформы One Link Cloud",
        "description": "Единая модель продукта, основные возможности и логика работы One Link Cloud.",
        "sidebarTitle": "Обзор",
        "heading": "Обзор One Link Cloud",
        "summary": """
One Link Cloud — это единая операционная платформа, а не набор отдельных отраслевых продуктов.

Персонализация для клиента строится внутри общего ядра через:

- права доступа
- кастомные поля
- автоматизации
- интеграции
- настройки Captain AI
""".strip(),
    },
    "platform/workspace-and-access": {
        "title": "Рабочее пространство и доступ",
        "description": "Как One Link Cloud разделяет workspace, пользователей, команды, доступ к inbox-очередям и видимость данных.",
        "sidebarTitle": "Workspace и доступ",
        "heading": "Рабочее пространство и доступ",
        "summary": """
В One Link Cloud у всех клиентов одно общее функциональное ядро. Управление различиями происходит через модель доступа.

Ключевые элементы:

- настройки workspace
- роли и права
- membership в inbox-очередях
- команды
- кастомные поля
- автоматизации и интеграции
""".strip(),
    },
    "platform/communication-workflows": {
        "title": "Коммуникационные процессы",
        "description": "Как в One Link Cloud связаны каналы, inbox-очереди, контакты, диалоги и сообщения.",
        "sidebarTitle": "Коммуникации",
        "heading": "Коммуникационные процессы",
        "summary": """
Коммуникации — это центральная операционная поверхность One Link Cloud.

Независимо от источника, все каналы сводятся к общей модели:

- канал
- inbox
- contact inbox
- conversation
- message

Это позволяет работать из одного интерфейса, а не переключаться между разрозненными системами.
""".strip(),
    },
    "platform/crm-architecture": {
        "title": "CRM и гибкая структура данных",
        "description": "Как One Link Cloud организует клиентские записи, воронки, задачи и настраиваемые поля без продуктовых форков по доменам.",
        "sidebarTitle": "CRM и данные",
        "heading": "CRM и гибкая структура данных",
        "summary": """
В One Link Cloud CRM встроена в основной продукт и работает поверх общей модели данных.

Базовые сущности:

- контакт
- компания
- сделка
- воронка и этап
- задача
- кастомные поля

Платформа не делится на отдельные доменные CRM. Различия закрываются конфигурацией и структурой данных.
""".strip(),
    },
    "platform/entity-matrix": {
        "title": "Ключевые сущности",
        "description": "Основные сущности One Link Cloud и их связи между коммуникациями, CRM, расписанием, AI и контентом.",
        "sidebarTitle": "Сущности",
        "heading": "Ключевые сущности",
        "summary": """
Все операционные объекты в One Link Cloud живут внутри общей account-модели.

Это позволяет связывать между собой:

- клиентов и компании
- диалоги и сообщения
- сделки и задачи
- записи и оплаты
- AI-контекст и базы знаний
""".strip(),
    },
    "platform/integrations-architecture": {
        "title": "Автоматизации и интеграции",
        "description": "Как One Link Cloud связывает автоматизацию процессов, макросы, hooks, webhooks и внешние системы.",
        "sidebarTitle": "Автоматизации и интеграции",
        "heading": "Автоматизации и интеграции",
        "summary": """
One Link Cloud использует единый event-driven слой для коммуникаций, CRM, расписания и AI.

Основные строительные блоки:

- `AutomationRule`
- `Macro`
- `Integrations::App`
- `Integrations::Hook`
- `Webhook`
- `Captain::CustomTool`
""".strip(),
    },
    "platform/scheduling-and-payments": {
        "title": "Расписание и оплаты",
        "description": "Как One Link Cloud работает с ресурсами, услугами, записями, оплатами и операционными финансами.",
        "sidebarTitle": "Расписание и оплаты",
        "heading": "Расписание и оплаты",
        "summary": """
В One Link Cloud есть встроенный scheduling-модуль для команд, которым важно вести календарные операции в том же workspace, что и коммуникации и CRM.

Ключевые сущности:

- ресурсы
- услуги
- записи
- оплаты
- расходы
""".strip(),
    },
    "platform/captain-ai": {
        "title": "Captain AI",
        "description": "Как в One Link Cloud работают ассистенты, документы, сценарии, кастомные инструменты и copilot-процессы.",
        "sidebarTitle": "Captain AI",
        "heading": "Captain AI",
        "summary": """
Captain — это AI-слой внутри One Link Cloud. Он не заменяет продуктовую модель, а работает поверх общих сущностей платформы.

Captain использует:

- документы и знания
- сценарии и guardrails
- кастомные инструменты
- copilot-процессы
- связь с диалогами, CRM и расписанием
""".strip(),
    },
    "user-guide/inboxes-and-channels": {
        "title": "Inbox-очереди и каналы",
        "description": "Как организовать каналы, inbox-очереди, маршрутизацию и доступ агентов в One Link Cloud.",
        "sidebarTitle": "Inbox и каналы",
        "heading": "Inbox-очереди и каналы",
        "summary": """
Inbox — это основная операционная точка входа в One Link Cloud.

Практическая логика:

- канал является источником коммуникации
- inbox определяет операционную очередь
- команда и правила маршрутизации управляют обработкой
""".strip(),
    },
    "user-guide/contacts-and-conversations": {
        "title": "Контакты и диалоги",
        "description": "Как операторы работают с клиентскими карточками, диалогами, заметками, метками и назначениями в One Link Cloud.",
        "sidebarTitle": "Контакты и диалоги",
        "heading": "Контакты и диалоги",
        "summary": """
Контакты и диалоги — это ежедневная рабочая поверхность большинства команд.

На этой странице описана логика работы с:

- карточкой контакта
- тредом диалога
- сообщениями
- назначением на агента или команду
- заметками и метками
""".strip(),
    },
    "user-guide/automation-and-macros": {
        "title": "Автоматизации и макросы",
        "description": "Как стандартизировать работу в One Link Cloud через automation rules, macros, labels и webhook-действия.",
        "sidebarTitle": "Автоматизации и макросы",
        "heading": "Автоматизации и макросы",
        "summary": """
В One Link Cloud есть два базовых инструмента стандартизации процессов:

- automation rules для фоновой event-driven логики
- macros для быстрых действий оператора

Они решают разные классы задач и часто используются вместе.
""".strip(),
    },
    "user-guide/reports-and-analytics": {
        "title": "Отчёты и аналитика",
        "description": "Как команды измеряют коммуникации, производительность, SLA, CSAT и операционные результаты в One Link Cloud.",
        "sidebarTitle": "Отчёты и аналитика",
        "heading": "Отчёты и аналитика",
        "summary": """
Отчёты помогают администраторам и тимлидам понимать, что происходит в workspace и где нужны улучшения.

Обычно анализируются:

- коммуникации
- агенты и команды
- inbox-очереди
- SLA и CSAT
- операционные результаты
""".strip(),
    },
    "user-guide/knowledge-base": {
        "title": "База знаний",
        "description": "Как организовать порталы, категории, локали и статьи в базе знаний One Link Cloud.",
        "sidebarTitle": "База знаний",
        "heading": "База знаний",
        "summary": """
База знаний позволяет публиковать структурированный контент для клиентов, операторов и Captain.

Основная модель включает:

- портал
- категории и папки
- статьи
- локали
- поиск и AI-использование контента
""".strip(),
    },
    "api-reference/introduction": {
        "title": "Справочник API One Link Cloud",
        "description": "Обзор API One Link Cloud с пояснениями по Application API, Client API и Platform API.",
        "sidebarTitle": "Введение",
        "heading": "Справочник API One Link Cloud",
        "summary": """
One Link Cloud использует несколько API-поверхностей, потому что разные интеграционные сценарии требуют разных моделей доверия и доступа.

Основное правило выбора:

- `Application API` для операций внутри workspace
- `Client API` для клиентских чат-интерфейсов
- `Platform API` для provisioning и административных сценариев
""".strip(),
    },
    "integrators/api-resource-map": {
        "title": "Карта API-ресурсов",
        "description": "Практическая карта основных групп API-ресурсов One Link Cloud для интеграторов.",
        "sidebarTitle": "Карта API",
        "heading": "Карта API-ресурсов",
        "summary": """
Эта страница помогает быстро понять, где в API живут основные бизнес-объекты платформы.

Для большинства интеграций важно сначала определить:

- нужную API-поверхность
- нужную группу ресурсов
- необходимость webhook-синхронизации
""".strip(),
    },
    "integrators/authentication-and-api-model": {
        "title": "Аутентификация и модель API",
        "description": "Как интеграторы выбирают правильную API-поверхность One Link Cloud и модель аутентификации.",
        "sidebarTitle": "Auth и модель API",
        "heading": "Аутентификация и модель API",
        "summary": """
Интеграции с One Link Cloud работают на разных уровнях доверия, поэтому у платформы несколько API-поверхностей.

Выбирать нужно по роли интеграции:

- операторский или системный процесс внутри workspace
- клиентский чат-интерфейс
- provisioning и платформенное администрирование
""".strip(),
    },
    "integrators/webhooks-and-events": {
        "title": "Webhooks и события",
        "description": "Как работает доставка событий для интеграторов, использующих webhooks, automation triggers и event-driven синхронизацию в One Link Cloud.",
        "sidebarTitle": "Webhooks и события",
        "heading": "Webhooks и события",
        "summary": """
Если внешняя система должна реагировать на изменения внутри One Link Cloud, основной механизм интеграции — это webhooks и event-driven automation.

Этот слой подходит для:

- общей потоковой синхронизации
- selective event routing
- write-back сценариев во внешние системы
""".strip(),
    },
    "integrators/integration-patterns": {
        "title": "Паттерны интеграции",
        "description": "Рекомендуемые способы подключения внешних систем к One Link Cloud для коммуникаций, CRM, расписания, AI и базы знаний.",
        "sidebarTitle": "Паттерны интеграции",
        "heading": "Паттерны интеграции",
        "summary": """
Разные интеграционные задачи требуют разных паттернов подключения.

Основные варианты:

- workspace sync
- клиентский messaging surface
- connected app lifecycle
- AI action surface через Captain custom tools
""".strip(),
    },
    "integrators/agent-skills-for-integrators": {
        "title": "Agent Skills для интеграторов",
        "description": "Как партнёры и технические команды клиентов могут установить и использовать One Link integration skills в Codex и Claude Code.",
        "sidebarTitle": "Agent Skills",
        "heading": "Agent Skills для интеграторов",
        "summary": """
Для внешних API-потребителей подготовлен отдельный skill bundle.

Сейчас поддержаны два варианта:

- skill для Codex
- skill для Claude Code

Они помогают выбирать API-поверхность, модель auth, path family и event-driven сценарий интеграции.
""".strip(),
    },
    "reference/glossary": {
        "title": "Глоссарий",
        "description": "Основные термины One Link Cloud для коммуникаций, CRM, расписания, AI и интеграций.",
        "sidebarTitle": "Глоссарий",
        "heading": "Глоссарий",
        "summary": """
На этой странице собраны основные продуктовые термины One Link Cloud.

Русские определения даны как основной слой, а английские формулировки ниже остаются как reference для интеграторов и mixed-language команд.
""".strip(),
    },
    "reference/faq": {
        "title": "FAQ",
        "description": "Частые вопросы о настройке, операционной работе, интеграциях и продуктовой модели One Link Cloud.",
        "sidebarTitle": "FAQ",
        "heading": "FAQ",
        "summary": """
Здесь собраны короткие ответы на частые вопросы по модели продукта, workspace-структуре, интеграциям и способу настройки платформы под клиента.
""".strip(),
    },
}


NAV_LOCALIZATION = {
    "name": "Документация One Link Cloud",
    "description": "Публичная документация One Link Cloud: процессы, сущности, автоматизации, интеграции и API.",
    "anchors": {
        "Introduction": "Введение",
        "Getting Started": "Быстрый старт",
        "User Guide": "Руководство",
        "Integrators": "Интеграторам",
        "Concepts": "Концепции",
        "Reference": "Справка",
    },
    "groups": {
        "Start Here": "Начало работы",
        "Daily Operations": "Ежедневная работа",
        "API And Integration": "API и интеграции",
        "Product Model": "Модель продукта",
        "Reference": "Справка",
    },
}


PAGE_ORDER = list(DOC_MAP.keys())


def update_docs_json() -> None:
    path = ROOT / "docs.json"
    data = json.loads(path.read_text())
    data["name"] = NAV_LOCALIZATION["name"]
    data["description"] = NAV_LOCALIZATION["description"]
    for anchor in data["navigation"]["anchors"]:
        anchor_name = anchor["anchor"]
        anchor["anchor"] = NAV_LOCALIZATION["anchors"].get(anchor_name, anchor_name)
        for page_group in anchor.get("pages", []):
            if isinstance(page_group, dict) and "group" in page_group:
                group_name = page_group["group"]
                page_group["group"] = NAV_LOCALIZATION["groups"].get(group_name, group_name)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def split_frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        raise ValueError("Frontmatter not found")
    return match.group(1), match.group(2).lstrip("\n")


def update_page(page_id: str, cfg: dict[str, str]) -> None:
    path = ROOT / f"{page_id}.mdx"
    if not path.exists():
        path = ROOT / f"{page_id}.md"
    original = path.read_text()
    _, body = split_frontmatter(original)
    lines = body.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"First heading not found in {page_id}")
    rest = "\n".join(lines[1:]).lstrip("\n")
    for marker in ("## Английская версия", "## English Version"):
        if marker in rest:
            rest = rest.split(marker, 1)[0].rstrip()
    if rest.startswith(cfg["summary"]):
        rest = rest[len(cfg["summary"]) :].lstrip("\n")

    frontmatter = (
        f"title: {cfg['title']}\n"
        f"description: {cfg['description']}\n"
        f"sidebarTitle: {cfg['sidebarTitle']}"
    )

    localized = (
        "---\n"
        f"{frontmatter}\n"
        "---\n\n"
        f"# {cfg['heading']}\n\n"
        f"{cfg['summary']}\n"
    )
    if rest.strip():
        localized += f"\n{rest.rstrip()}\n"
    path.write_text(localized)


def main() -> None:
    update_docs_json()
    for page_id in PAGE_ORDER:
        update_page(page_id, DOC_MAP[page_id])


if __name__ == "__main__":
    main()
