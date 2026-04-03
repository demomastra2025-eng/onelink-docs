#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPENAPI_ROOT = ROOT / "openapi"


INFO_TRANSLATIONS = {
    "title": "API One Link Cloud",
    "description": "Документация API сервера One Link Cloud.",
}


TAG_MAP = {
    "Account AgentBots": ("AgentBots аккаунта", "Боты-агенты, привязанные к аккаунту / Account-specific Agent Bots"),
    "Agents": ("Агенты", "API для управления агентами / Agent management APIs"),
    "Canned Responses": ("Шаблоны ответов", "Преднастроенные ответы для типовых запросов / Pre-defined responses for common queries"),
    "Contacts": ("Контакты", "API для управления контактами / Contact management APIs"),
    "Contact Labels": ("Метки контактов", "Управление метками контактов / Manage contact labels"),
    "Conversation Assignments": ("Назначения диалогов", "Управление назначениями диалогов / Manage conversation assignments"),
    "Conversation Labels": ("Метки диалогов", "Управление метками диалогов / Manage conversation labels"),
    "Conversations": ("Диалоги", "API для управления диалогами / Conversation management APIs"),
    "Custom Attributes": ("Кастомные атрибуты", "Кастомные поля для контактов и диалогов / Custom fields for contacts and conversations"),
    "Custom Filters": ("Пользовательские фильтры", "Сохранённые фильтры для диалогов / Saved filters for conversations"),
    "Inboxes": ("Inbox-очереди", "Настройка каналов коммуникации / Communication channels setup"),
    "Integrations": ("Интеграции", "Сторонние интеграции / Third-party integrations"),
    "Messages": ("Сообщения", "API для управления сообщениями / Message management APIs"),
    "Profile": ("Профиль", "API профиля пользователя / User profile APIs"),
    "Reports": ("Отчёты", "API аналитики и отчётности / Analytics and reporting APIs"),
    "Scheduling": ("Расписание", "API расписания, записей и кассы / Scheduling, appointment, and kassa APIs"),
    "Teams": ("Команды", "API для управления командами / Team management APIs"),
    "Webhooks": ("Webhooks", "Webhooks для уведомлений о событиях / Event notification webhooks"),
    "Automation Rule": ("Правила автоматизации", "Правила автоматизации рабочих процессов / Workflow automation rules"),
    "Help Center": ("База знаний", "Управление knowledge base / Knowledge base management"),
    "Contacts API": ("Contacts API", "Публичные API контактов / Public contact APIs"),
    "Conversations API": ("Conversations API", "Публичные API диалогов / Public conversation APIs"),
    "Messages API": ("Messages API", "Публичные API сообщений / Public message APIs"),
    "Accounts": ("Аккаунты", "API для управления аккаунтами / Account management APIs"),
    "Account Users": ("Пользователи аккаунта", "API для управления пользователями аккаунта / Account user management APIs"),
    "AgentBots": ("AgentBots", "Интеграции с ботами / Bot integrations"),
    "Users": ("Пользователи", "API для управления пользователями / User management APIs"),
    "CSAT Survey Page": ("Страница CSAT-опроса", "Опрос удовлетворённости клиентов / Customer satisfaction survey"),
}


SECURITY_DESCRIPTION_MAP = {
    "This token can be obtained by visiting the profile page or via rails console. Provides access to  endpoints based on the user permissions levels. This token can be saved by an external system when user is created via API, to perform activities on behalf of the user.": "Токен пользователя для доступа к API в рамках его прав. Обычно передаётся внешней системе после создания пользователя через API. / This token can be obtained by visiting the profile page or via rails console. Provides access to endpoints based on the user permission levels.",
    "This token should be provided by system admin or obtained via rails console. This token can be used to build bot integrations and can only access limited apis.": "Токен агент-бота для ограниченного набора API и bot-интеграций. / This token should be provided by system admin or obtained via rails console. This token can be used to build bot integrations and can only access limited APIs.",
    "This token can be obtained by the system admin after creating a platformApp. This token should be used to provision agent bots, accounts, users and their roles.": "Платформенный токен для provisioning аккаунтов, пользователей и agent bots. / This token can be obtained by the system admin after creating a platform app. This token should be used to provision agent bots, accounts, users and their roles.",
}


SUMMARY_EXACT = {
    "Account Conversation Metrics": "Метрики диалогов по аккаунту",
    "Account Reporting Events": "События отчётности по аккаунту",
    "Add Labels": "Добавить метки",
    "Add a New Agent": "Добавить нового агента",
    "Add a New Canned Response": "Добавить новый шаблон ответа",
    "Add a new article": "Добавить новую статью",
    "Add a new automation rule": "Добавить новое правило автоматизации",
    "Add a new category": "Добавить новую категорию",
    "Add a new custom attribute": "Добавить новый кастомный атрибут",
    "Add a new portal": "Добавить новый портал",
    "Add a webhook": "Добавить webhook",
    "Add or remove agent bot": "Привязать или отвязать agent bot",
    "Agent Conversation Metrics": "Метрики диалогов по агенту",
    "Assign Conversation": "Назначить диалог",
    "Cancel a scheduling appointment": "Отменить запись расписания",
    "Cancel all appointment payments": "Отменить все оплаты записи",
    "Contact Conversations": "Диалоги контакта",
    "Contact Filter": "Фильтр контактов",
    "Conversation Details": "Детали диалога",
    "Conversation Reporting Events": "События отчётности по диалогу",
    "Conversations Filter": "Фильтр диалогов",
    "Conversations List": "Список диалогов",
    "Create Contact": "Создать контакт",
    "Create New Conversation": "Создать новый диалог",
    "Create New Message": "Создать новое сообщение",
    "Create a custom filter": "Создать пользовательский фильтр",
    "Create a holiday": "Создать праздничный день",
    "Create a scheduling appointment": "Создать запись расписания",
    "Create a scheduling resource": "Создать ресурс расписания",
    "Create a scheduling service": "Создать услугу расписания",
    "Create a team": "Создать команду",
    "Create a time off entry": "Создать запись об отсутствии",
    "Create a workday override": "Создать переопределение рабочего дня",
    "Create an Agent Bot": "Создать Agent Bot",
    "Create an inbox": "Создать inbox",
    "Create an integration hook": "Создать integration hook",
    "Create contact inbox": "Создать contact inbox",
    "Create or enrich a scheduling contact": "Создать или обогатить scheduling-контакт",
    "Delete Contact": "Удалить контакт",
    "Delete a custom filter": "Удалить пользовательский фильтр",
    "Delete a holiday": "Удалить праздничный день",
    "Delete a message": "Удалить сообщение",
    "Delete a scheduling resource": "Удалить ресурс расписания",
    "Delete a scheduling service": "Удалить услугу расписания",
    "Delete a team": "Удалить команду",
    "Delete a time off entry": "Удалить запись об отсутствии",
    "Delete a webhook": "Удалить webhook",
    "Delete a workday override": "Удалить переопределение рабочего дня",
    "Delete an AgentBot": "Удалить AgentBot",
    "Delete an Integration Hook": "Удалить Integration Hook",
    "Fetch user profile": "Получить профиль пользователя",
    "Get Account reports": "Получить отчёты аккаунта",
    "Get Account reports summary": "Получить сводку отчётов аккаунта",
    "Get Contactable Inboxes": "Получить доступные inbox-очереди для контакта",
    "Get Conversation Counts": "Получить счётчики диалогов",
    "Get a automation rule details": "Получить детали правила автоматизации",
    "Get a custom attribute details": "Получить детали кастомного атрибута",
    "Get a custom filter details": "Получить детали пользовательского фильтра",
    "Get a scheduling appointment": "Получить запись расписания",
    "Get a scheduling resource": "Получить ресурс расписания",
    "Get a scheduling service": "Получить услугу расписания",
    "Get a team details": "Получить детали команды",
    "Get account details": "Получить детали аккаунта",
    "Get an agent bot details": "Получить детали agent bot",
    "Get an inbox": "Получить inbox",
    "Get conversation statistics grouped by agent": "Получить статистику диалогов по агентам",
    "Get conversation statistics grouped by channel type": "Получить статистику диалогов по типам каналов",
    "Get conversation statistics grouped by inbox": "Получить статистику диалогов по inbox-очередям",
    "Get conversation statistics grouped by team": "Получить статистику диалогов по командам",
    "Get first response time distribution by channel": "Получить распределение времени первого ответа по каналам",
    "Get inbox-label matrix report": "Получить матрицу inbox-очередей и меток",
    "Get messages": "Получить сообщения",
    "Get outgoing messages count grouped by entity": "Получить количество исходящих сообщений по сущностям",
    "Get scheduling calendar payload": "Получить payload календаря расписания",
    "Get weekly break rules for a resource": "Получить недельные правила перерывов для ресурса",
    "Get weekly work rules for a resource": "Получить недельные правила работы для ресурса",
    "List Agents in Account": "Список агентов в аккаунте",
    "List Agents in Inbox": "Список агентов в inbox-очереди",
    "List Agents in Team": "Список агентов в команде",
    "List Audit Logs in Account": "Список audit logs аккаунта",
    "List Contacts": "Список контактов",
    "List Labels": "Список меток",
    "List all AgentBots": "Список всех AgentBots",
    "List all Canned Responses in an Account": "Список всех шаблонов ответов в аккаунте",
    "List all automation rules in an account": "Список всех правил автоматизации в аккаунте",
    "List all custom attributes in an account": "Список всех кастомных атрибутов в аккаунте",
    "List all custom filters": "Список всех пользовательских фильтров",
    "List all inboxes": "Список всех inbox-очередей",
    "List all portals in an account": "Список всех порталов в аккаунте",
    "List all teams": "Список всех команд",
    "List all the Integrations": "Список всех интеграций",
    "List all webhooks": "Список всех webhook-ов",
    "List appointments": "Список записей",
    "List holidays": "Список праздничных дней",
    "List payment journal entries": "Список проводок журнала оплат",
    "List resource expenses and payouts": "Список расходов и выплат по ресурсам",
    "List scheduling resources": "Список ресурсов расписания",
    "List scheduling services and per-resource prices": "Список услуг расписания и цен по ресурсам",
    "List time off entries": "Список записей об отсутствии",
    "List workday overrides": "Список переопределений рабочего дня",
    "Mark a single resource expense as paid": "Отметить расход ресурса как оплаченный",
    "Merge Contacts": "Объединить контакты",
    "Pay all filtered unpaid expenses": "Оплатить все отфильтрованные неоплаченные расходы",
    "Record a payment on an appointment": "Зафиксировать оплату по записи",
    "Remove a Canned Response from Account": "Удалить шаблон ответа из аккаунта",
    "Remove a automation rule from account": "Удалить правило автоматизации из аккаунта",
    "Remove a custom attribute from account": "Удалить кастомный атрибут из аккаунта",
    "Remove an Agent from Account": "Удалить агента из аккаунта",
    "Remove an Agent from Inbox": "Удалить агента из inbox-очереди",
    "Remove an Agent from Team": "Удалить агента из команды",
    "Replace weekly break rules for a resource": "Заменить недельные правила перерывов для ресурса",
    "Replace weekly work rules for a resource": "Заменить недельные правила работы для ресурса",
    "Search Contacts": "Поиск контактов",
    "Search scheduling contacts": "Поиск scheduling-контактов",
    "Show Contact": "Показать контакт",
    "Show Inbox Agent Bot": "Показать agent bot inbox-очереди",
    "Toggle Priority": "Переключить приоритет",
    "Toggle Status": "Переключить статус",
    "Update Agent in Account": "Обновить агента в аккаунте",
    "Update Agents in Inbox": "Обновить агентов в inbox-очереди",
    "Update Agents in Team": "Обновить агентов в команде",
    "Update Canned Response in Account": "Обновить шаблон ответа в аккаунте",
    "Update Contact": "Обновить контакт",
    "Update Conversation": "Обновить диалог",
    "Update Custom Attributes": "Обновить кастомные атрибуты",
    "Update Inbox": "Обновить inbox",
    "Update a custom filter": "Обновить пользовательский фильтр",
    "Update a holiday": "Обновить праздничный день",
    "Update a portal": "Обновить портал",
    "Update a scheduling appointment": "Обновить запись расписания",
    "Update a scheduling contact": "Обновить scheduling-контакт",
    "Update a scheduling resource": "Обновить ресурс расписания",
    "Update a scheduling service": "Обновить услугу расписания",
    "Update a team": "Обновить команду",
    "Update a time off entry": "Обновить запись об отсутствии",
    "Update a webhook object": "Обновить объект webhook",
    "Update a workday override": "Обновить переопределение рабочего дня",
    "Update account": "Обновить аккаунт",
    "Update an Integration Hook": "Обновить Integration Hook",
    "Update an agent bot": "Обновить agent bot",
    "Update automation rule in Account": "Обновить правило автоматизации в аккаунте",
    "Update custom attribute in Account": "Обновить кастомный атрибут в аккаунте",
    "Create a contact": "Создать контакт",
    "Get a contact": "Получить контакт",
    "Update a contact": "Обновить контакт",
    "Create a conversation": "Создать диалог",
    "List all conversations": "Список всех диалогов",
    "Get a single conversation": "Получить один диалог",
    "Resolve a conversation": "Закрыть диалог",
    "Toggle typing status": "Переключить статус набора",
    "Update a message": "Обновить сообщение",
    "Update last seen": "Обновить last seen",
    "Create a message": "Создать сообщение",
    "List all messages": "Список всех сообщений",
    "Create a User": "Создать пользователя",
    "Create an Account": "Создать аккаунт",
    "Create an Account User": "Создать пользователя аккаунта",
    "Delete a User": "Удалить пользователя",
    "Delete an Account": "Удалить аккаунт",
    "Delete an Account User": "Удалить пользователя аккаунта",
    "Get User SSO Link": "Получить SSO-ссылку пользователя",
    "Get an account details": "Получить детали аккаунта",
    "Get an user details": "Получить детали пользователя",
    "List all Account Users": "Список всех пользователей аккаунта",
    "Update a user": "Обновить пользователя",
    "Update an account": "Обновить аккаунт",
    "Get CSAT survey page": "Получить страницу CSAT-опроса",
}


DESCRIPTION_EXACT = {
    "Create a contact": "Создать контакт / Create a contact",
    "Create a conversation": "Создать диалог / Create a conversation",
    "Create a message": "Создать сообщение / Create a message",
    "Get the details of a contact": "Получить детали контакта / Get the details of a contact",
    "List all conversations for the contact": "Получить список всех диалогов контакта / List all conversations for the contact",
    "List all messages in the conversation": "Получить список всех сообщений в диалоге / List all messages in the conversation",
    "Marks a conversation as resolved": "Пометить диалог как закрытый / Marks a conversation as resolved",
    "Retrieves the details of a specific conversation": "Получить детали конкретного диалога / Retrieves the details of a specific conversation",
    "Toggles the typing status in a conversation": "Переключить статус набора в диалоге / Toggles the typing status in a conversation",
    "Update a contact's attributes": "Обновить атрибуты контакта / Update a contact's attributes",
    "Update a message": "Обновить сообщение / Update a message",
    "Updates the last seen time of the contact in a conversation": "Обновить время последнего просмотра контакта в диалоге / Updates the last seen time of the contact in a conversation",
    "Create a User": "Создать пользователя / Create a User",
    "Create an Account": "Создать аккаунт / Create an Account",
    "Create an Account User": "Создать пользователя аккаунта / Create an Account User",
    "Create an agent bot": "Создать agent bot / Create an agent bot",
    "Delete a User": "Удалить пользователя / Delete a User",
    "Delete an Account": "Удалить аккаунт / Delete an Account",
    "Delete an Account User": "Удалить пользователя аккаунта / Delete an Account User",
    "Delete an AgentBot": "Удалить AgentBot / Delete an AgentBot",
    "Get the details of an account": "Получить детали аккаунта / Get the details of an account",
    "Get the details of an agent bot": "Получить детали agent bot / Get the details of an agent bot",
    "Get the details of an user": "Получить детали пользователя / Get the details of an user",
    "Get the sso link of a user": "Получить SSO-ссылку пользователя / Get the sso link of a user",
    "List all account users": "Получить список всех пользователей аккаунта / List all account users",
    "List all agent bots available": "Получить список всех доступных agent bots / List all agent bots available",
    "Update a user's attributes": "Обновить атрибуты пользователя / Update a user's attributes",
    "Update an account's attributes": "Обновить атрибуты аккаунта / Update an account's attributes",
    "Update an agent bot's attributes": "Обновить атрибуты agent bot / Update an agent bot's attributes",
    "You can redirect the client to this URL, instead of implementing the CSAT survey component yourself.": "Можно перенаправить клиента на этот URL вместо самостоятельной реализации CSAT-компонента. / You can redirect the client to this URL, instead of implementing the CSAT survey component yourself.",
}


def russian_only(text: str) -> str:
    return text.split(" / ", 1)[0]


def collapse_bilingual(text: str) -> str:
    if " / " not in text:
        return text
    left = text.split(" / ", 1)[0]
    if re.search(r"[А-Яа-яЁё]", left):
        return left
    return text


def localize_summary(text: str) -> str:
    if not text or re.search(r"[А-Яа-яЁё]", text):
        return collapse_bilingual(text)
    if text in SUMMARY_EXACT:
        return SUMMARY_EXACT[text]
    return text


def first_sentence(text: str) -> str:
    text = text.strip()
    if "\n\n" in text:
        text = text.split("\n\n", 1)[0]
    if ". " in text:
        return text.split(". ", 1)[0].strip() + "."
    return text


def localize_description(text: str) -> str:
    if not text or re.search(r"[А-Яа-яЁё]", text):
        return collapse_bilingual(text)
    if text in DESCRIPTION_EXACT:
        return russian_only(DESCRIPTION_EXACT[text])
    if text in SECURITY_DESCRIPTION_MAP:
        return russian_only(SECURITY_DESCRIPTION_MAP[text])
    sentence = first_sentence(text)
    ru = None
    if sentence in SUMMARY_EXACT:
        ru = SUMMARY_EXACT[sentence]
    elif sentence.startswith("Get the details of "):
        ru = "Получить детали объекта"
    elif sentence.startswith("List all "):
        ru = "Получить список записей"
    elif sentence.startswith("Create "):
        ru = "Создать объект"
    elif sentence.startswith("Update "):
        ru = "Обновить объект"
    elif sentence.startswith("Delete "):
        ru = "Удалить объект"
    elif sentence.startswith("Add "):
        ru = "Добавить объект"
    elif sentence.startswith("Remove "):
        ru = "Удалить объект"
    elif sentence.startswith("Search "):
        ru = "Выполнить поиск"
    elif sentence.startswith("Toggle "):
        ru = "Переключить состояние"
    elif sentence.startswith("Assign "):
        ru = "Назначить объект"
    elif sentence.startswith("Returns "):
        ru = "Возвращает данные"
    elif sentence.startswith("Requires "):
        ru = "Требуются соответствующие права и условия"
    elif sentence.startswith("Supports "):
        ru = "Поддерживается указанный режим работы"
    elif sentence.startswith("You can "):
        ru = "Можно использовать этот сценарий"
    if ru:
        return ru
    return text


def walk(node):
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if key == "summary" and isinstance(value, str):
                node[key] = localize_summary(value)
            elif key == "description" and isinstance(value, str):
                node[key] = localize_description(value)
            elif key == "title" and isinstance(value, str) and value == "Onelink":
                node[key] = INFO_TRANSLATIONS["title"]
            else:
                walk(value)
    elif isinstance(node, list):
        for item in node:
            walk(item)


def localize_tags(data: dict) -> None:
    for tag in data.get("tags", []):
        name = tag.get("name")
        lookup_name = name
        if lookup_name not in TAG_MAP and isinstance(lookup_name, str) and " / " in lookup_name:
            lookup_name = lookup_name.split(" / ", 1)[1].strip()
        if lookup_name in TAG_MAP:
            ru_name, ru_desc = TAG_MAP[lookup_name]
            tag["name"] = ru_name
            tag["description"] = russian_only(ru_desc)
        elif isinstance(name, str):
            tag["name"] = collapse_bilingual(name)
            if isinstance(tag.get("description"), str):
                tag["description"] = collapse_bilingual(tag["description"])


def localize_security(data: dict) -> None:
    schemes = data.get("components", {}).get("securitySchemes", {})
    for scheme in schemes.values():
        desc = scheme.get("description")
        if desc:
            scheme["description"] = localize_description(desc)


def process_file(path: Path) -> None:
    data = json.loads(path.read_text())
    data["info"]["title"] = INFO_TRANSLATIONS["title"]
    data["info"]["description"] = INFO_TRANSLATIONS["description"]
    localize_tags(data)
    localize_security(data)
    walk(data.get("paths", {}))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    for path in sorted(OPENAPI_ROOT.glob("*.json")):
        process_file(path)


if __name__ == "__main__":
    main()
