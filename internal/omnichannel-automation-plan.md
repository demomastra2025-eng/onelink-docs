---
title: Omnichannel Automation And Outbound Plan
description: Internal runtime note for how broadcasts, personal sends, stages, and automation fit together in the current outbound model.
---

# Omnichannel Automation And Outbound Plan

## Goal

Document the current outbound architecture after the shift from a standalone `touches` workspace to one shared campaigns surface with:

- mass broadcasts
- personal sends
- reusable stages
- shared templates
- automation-triggered outbound actions

The point of this page is not to preserve the old rel1 language.

The point is to describe the product and runtime shape that now exists in code.

## Current Product Shape

The current product entrypoint is:

- `Кампании` in the main navigation
- `Рассылки` as the outbound subsection

Inside the outbound surface, the product is split into:

- `Массовые`
  - audience-based outbound campaigns
- `Персональные`
  - one scheduled outbound message for one contact and one channel target
- `Этапы рассылок`
  - reusable multi-step personal outbound definitions
- `Шаблоны`
  - reusable authoring assets used from the same outbound surface

The old standalone `Касания` workspace is no longer the primary user-facing model.

## Runtime Mapping

The user-facing product terms map to the current backend entities like this:

- mass outbound campaign
  - `Campaign`
  - `CampaignRun`
  - `CampaignDelivery`
- personal outbound send
  - `Reminder`
- outbound stage set
  - `ReminderGroup`

This split is intentional:

- `Campaign` handles one content definition applied to an audience fanout
- `Reminder` handles one scheduled outbound action for one resolved target
- `ReminderGroup` stores reusable staged personal outbound sequences

## Why These Are Not One Table

Mass and personal outbound are related, but they should not be collapsed into the same persistence model.

They solve different runtime problems:

- mass outbound needs audience resolution, per-contact delivery rows, retries, resumability, and aggregate analytics
- personal outbound needs exact routing, relative timing, repeat rules, auto-cancel on reply, and entity-scoped execution

The right unification point is shared outbound UX and shared delivery conventions, not forced table-level identity.

## Personal Sends

### Product Behavior

A personal send is one scheduled outbound action for one contact through one selected inbox target.

The current UI supports:

- manual creation from the campaigns surface
- manual creation from the conversation side panel as `Создать отложенное сообщение`
- editing
- deletion before completion
- analytics dialog
- free-text or channel-template authoring
- AI-authored mode where an AI agent writes the message at execution time

### Runtime Behavior

A personal send stays as a scheduled outbound item until execution time.

At execution:

1. target resolution runs for the selected contact and inbox
2. a conversation is reused or created when allowed
3. a normal outgoing `Message` is materialized
4. the regular send pipeline takes over

Relevant files:

- `app/models/reminder.rb`
- `app/services/reminders/create_service.rb`
- `app/services/reminders/execute_service.rb`
- `app/services/reminders/conversation_resolver.rb`
- `app/services/outbound/contact_inbox_resolver.rb`
- `app/jobs/reminders/process_pending_reminders_job.rb`
- `app/jobs/reminders/execute_reminder_job.rb`

## Stages

`Этапы рассылок` are reusable grouped definitions for personal sends.

They are implemented through `ReminderGroup` and are used for:

- manual stage application
- automation-triggered stage materialization
- future default outbound flows per entity type

Important behavior:

- a stage group expands into concrete `Reminder` records
- changing the group later does not rewrite already-created reminders
- the stage layer is reusable content and timing logic, not the trigger engine

Relevant files:

- `app/models/reminder_group.rb`
- `app/services/reminders/apply_group_service.rb`
- `app/javascript/dashboard/components-next/Outbound/TouchPlanEditorDrawer.vue`
- `app/javascript/dashboard/routes/dashboard/campaigns/pages/OutboundTouchPlansPage.vue`

## Automation Contract

Automation remains the trigger and conditions layer.

Outbound remains the action and delivery layer.

The current automation actions are:

- `create_touch`
- `apply_touch_plan`

Even though the code still uses `touch` terminology internally, these actions now feed the same personal outbound runtime as the campaigns surface.

That means:

- no separate outbound engine for automation
- no separate execution semantics for automation-created personal sends
- one shared service layer for manual and automation-triggered items

Relevant files:

- `app/services/automation_rules/touch_action_service.rb`
- `enterprise/app/services/captain/tools/copilot/create_touch_service.rb`
- `enterprise/lib/captain/tools/create_touch_tool.rb`

## Timing Model

Personal sends currently support:

- absolute scheduling
- relative scheduling
- recurring absolute schedules

Conversation-aware relative anchors now include:

- conversation creation
- last activity
- last incoming message
- last outgoing message
- waiting for reply

The runtime also supports:

- auto-cancel on incoming reply for the same target
- timing sync when conversation activity changes
- recurrence materialization for absolute schedules

Relevant files:

- `app/services/reminders/recurrence_service.rb`
- `app/services/reminders/sync_conversation_timing_service.rb`
- `app/models/message.rb`
- `app/javascript/dashboard/components-next/Outbound/touchAnchors.js`

## Channel And Routing Model

The product goal is channel-aware outbound behavior without duplicating one-off logic for each surface.

Current routing rules are:

- mass campaigns resolve an eligible target from audience and inbox context
- personal sends store the chosen contact and inbox target
- execution resolves or reuses the correct delivery path at send time
- channel-specific send behavior stays in the normal message send stack

This is why personal sends and mass campaigns now share more of the outbound target resolution path.

## Current UI Surfaces

Relevant routes and page-level files:

- `app/javascript/dashboard/routes/dashboard/campaigns/campaigns.routes.js`
- `app/javascript/dashboard/routes/dashboard/campaigns/pages/OutboundCampaignsPage.vue`
- `app/javascript/dashboard/routes/dashboard/campaigns/pages/OutboundTouchPlansPage.vue`
- `app/javascript/dashboard/routes/dashboard/campaigns/pages/OutboundTemplatesPage.vue`

Key components:

- `app/javascript/dashboard/components-next/Campaigns/Pages/CampaignPage/OutboundCampaign/OutboundCampaignDialog.vue`
- `app/javascript/dashboard/components-next/Outbound/TouchEditorDrawer.vue`
- `app/javascript/dashboard/components-next/Outbound/TouchAnalyticsDialog.vue`
- `app/javascript/dashboard/components-next/Outbound/TouchCard.vue`

## Implementation Status

The current codebase iteration already includes:

- one campaigns surface that can switch between mass and personal modes
- personal send creation, editing, deletion, and analytics
- separate stages page
- conversation-side delayed message creation using the same core editor
- automation actions for personal sends and stages
- AI-authored personal sends
- channel-aware target resolution shared more closely across outbound paths

## Remaining Risk Before Production

The main remaining release risk is no longer architecture confusion.

The main risk is release hygiene:

- keeping docs and product code committed coherently across the parent repo and the `docs` submodule
- making sure the final GitHub push includes the docs submodule update
- keeping verification scoped but real before the production deploy

This page should be updated whenever the user-facing outbound terminology changes again or when automation and outbound are unified further at the domain layer.
