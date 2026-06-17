---
title: OneLink Meta Graph API v25 Upgrade Plan
description: Internal upgrade plan for moving OneLink Facebook, Instagram, and WhatsApp Cloud integrations to Meta Graph/API v25.0.
---

# OneLink Meta Graph/API v25.0 Upgrade Plan

## 1. Direct verdict

OneLink is **not fully on Meta Graph/API v25.0 yet**.

Official Meta documentation confirms that the latest Graph API version is `v25.0`, introduced on **2026-02-18**. The current OneLink codebase still defaults or hardcodes older Meta API versions in several provider paths:

- Facebook default: `v18.0`
- WhatsApp Cloud default: `v22.0`
- Instagram default/hardcoded endpoints: `v22.0`

The project can be upgraded to v25.0, but the version switch must be gated by code fixes and provider-specific tests. The highest-risk blockers are not the endpoint paths themselves; they are payload/status contract differences and hardcoded version fallbacks.

Related internal reference: [`upstream-chatwoot-4-15-adoption-plan.md`](./upstream-chatwoot-4-15-adoption-plan.md), especially the P0 Meta adoption items and the official Meta documentation gate.

## 2. Official Meta documentation baseline

Use only official Meta documentation for the v25 decision gate:

- Graph API changelog: `https://developers.facebook.com/docs/graph-api/changelog`
  - Latest Graph API version is `v25.0`.
- Graph API versions table: `https://developers.facebook.com/docs/graph-api/changelog/versions/`
  - `v25.0`: introduced 2026-02-18, available until `TBD`.
  - `v18.0`: introduced 2023-09-12, available until 2026-01-26.
- Graph API v25.0 changelog: `https://developers.facebook.com/docs/graph-api/changelog/version25.0/`
  - `metadata=1` node metadata behavior is deprecated in v25.0+ and applies to all versions from 2026-05-19.
  - Webhooks mTLS certificate trust store changed to Meta-owned CA.
  - Insights metric deprecations are mostly Page/Post/Video/Story Insights and Marketing API related.
- v25.0 release blog: `https://developers.facebook.com/blog/post/2026/02/18/introducing-graph-api-v25-and-marketing-api-v25/`
  - Confirms v25.0 release date and Webhooks mTLS CA transition.
- WhatsApp status webhook reference: `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/status/`
  - Status values include `sent`, `delivered`, `read`, `failed`, and `played`.
  - `played` is sent when a voice message is played by the WhatsApp user.
- WhatsApp unsupported messages webhook reference: `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/unsupported/`
  - Unsupported message payload includes `type: "unsupported"` plus `unsupported.type`.
  - Example values include `button`, `edit`, `errors`, `gif`, `group_invite`, `hsm`, `image`, `interactive`, `keep_in_chat`, `link_preview`, `list`, `location`, `media_placeholder`, `order`, `pin`, `poll_creation`, `poll_update`, `product`, `reaction`.
- WhatsApp interactive reply buttons: `https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/interactive-reply-buttons-messages/`
  - Request syntax uses `interactive.action` as an object with `buttons` array.
- WhatsApp interactive list messages: `https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/interactive-list-messages/`
  - Request syntax uses `interactive.action` as an object with `button` and `sections`.
- WhatsApp `smb_message_echoes`: `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/smb_message_echoes/`
  - This webhook is for messages sent via WhatsApp Business App or linked devices by customers onboarded to Cloud API via a solution provider.
- WhatsApp Cloud API Calling: `https://developers.facebook.com/documentation/business-messaging/whatsapp/calling/`
  - Default signaling uses Graph APIs + Webhooks.
  - The app should be subscribed to the WABA and calling should be enabled for the business phone number.
- WhatsApp Embedded Signup overview: `https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/overview/`
  - Embedded Signup v2 is deprecated on 2026-10-15.
  - Meta says to migrate to Embedded Signup v4 before that date.
  - Cloud API flow requires `whatsapp_business_management` and `whatsapp_business_messaging` permissions.

## 3. Current OneLink code evidence

### 3.1 Config defaults and dashboard exposure

- `config/installation_config.yml`
  - `FACEBOOK_API_VERSION` default is `v18.0`.
  - `WHATSAPP_API_VERSION` default is `v22.0`.
  - `INSTAGRAM_API_VERSION` default is `v22.0` and currently `locked: true`.
- `app/controllers/dashboard_controller.rb`
  - `FACEBOOK_API_VERSION` fallback is `v18.0`.
  - `WHATSAPP_API_VERSION` fallback is `v22.0`.
- `app/views/layouts/vueapp.html.erb`
  - Exposes `fbApiVersion` and `whatsappApiVersion` to the dashboard frontend.
- `app/javascript/dashboard/routes/dashboard/settings/inbox/channels/whatsapp/utils.js`
  - Facebook SDK initialization fallback is `v22.0`.
  - WhatsApp Embedded Signup SDK setup fallback is `v22.0`.

### 3.2 Facebook Messenger/Page

- `app/controllers/dashboard_controller.rb`
  - Facebook Graph default is `v18.0`; official Meta versions table says v18.0 ended 2026-01-26.
- `app/services/meta/authorization_health_check_service.rb`
  - Facebook Page health check uses `GlobalConfigService.load('FACEBOOK_API_VERSION', 'v18.0')`.
- `app/javascript/dashboard/routes/dashboard/settings/inbox/channels/Facebook.vue`
  - Uses `window.chatwootConfig.fbApiVersion` for SDK init.
- `app/javascript/dashboard/routes/dashboard/settings/inbox/facebook/Reauthorize.vue`
  - Uses `window.chatwootConfig.fbApiVersion` for SDK init.

Facebook v25 upgrade must also incorporate the separate Meta policy fixes already documented in the upstream adoption plan: Messenger-only OAuth scope split and `MESSAGE_TAG`/`ACCOUNT_UPDATE` removal for normal replies.

### 3.3 Instagram

- `app/controllers/concerns/instagram_concern.rb`
  - `fetch_instagram_user_details` hardcodes `https://graph.instagram.com/v22.0/me`.
- `app/models/channel/instagram.rb`
  - `subscribe` hardcodes `https://graph.instagram.com/v22.0/#{instagram_id}/subscribed_apps`.
  - `unsubscribe` hardcodes the same v22.0 endpoint.
- `app/services/instagram/send_on_instagram_service.rb`
  - Direct Instagram send hardcodes `https://graph.instagram.com/v22.0/#{instagram_id}/messages`.
- `app/services/instagram/message_text.rb`
  - Uses `GlobalConfigService.load('INSTAGRAM_API_VERSION', 'v22.0')`.
- `app/builders/messages/instagram/message_builder.rb`
  - Uses `GlobalConfigService.load('INSTAGRAM_API_VERSION', 'v22.0')`.
- `app/services/meta/authorization_health_check_service.rb`
  - Instagram health check uses `GlobalConfigService.load('INSTAGRAM_API_VERSION', 'v22.0')`.

Instagram cannot be called v25-ready while these direct `v22.0` literals remain.

### 3.4 WhatsApp Cloud / Embedded Signup

- `app/services/whatsapp/facebook_api_client.rb`
  - Uses `GlobalConfigService.load('WHATSAPP_API_VERSION', 'v22.0')`.
  - Calls `/oauth/access_token`, `/{waba_id}/phone_numbers`, `/debug_token`, `/{phone_number_id}/register`, `/{waba_id}/subscribed_apps`.
  - `WEBHOOK_DEFAULT_FIELDS = %w[messages smb_message_echoes calls]` subscribes `calls` for every Cloud setup today.
- `app/services/whatsapp/providers/whatsapp_cloud_service.rb`
  - Uses `GlobalConfigService.load('WHATSAPP_API_VERSION', 'v22.0')`.
  - Calls `/{phone_number_id}/messages`, `/{waba_id}/message_templates`, `/{media_id}`.
  - Current interactive payload builder receives `action` as a JSON string from `Whatsapp::Providers::BaseService`.
- `app/services/whatsapp/providers/base_service.rb`
  - `create_button_payload` and `create_list_payload` call `JSON.generate(json_hash)` before assigning it to `interactive.action`.
  - Official v25 WhatsApp docs show `interactive.action` as a JSON object, not an encoded string.
- `app/services/whatsapp/health_service.rb`
  - Uses `v22.0` fallback and reads health fields such as `messaging_limit_tier`.
- `enterprise/app/services/whatsapp/providers/whatsapp_cloud_call_methods.rb`
  - `WHATSAPP_CALLING_API_VERSION_FALLBACK = 'v22.0'`.
  - Uses `/{phone_number_id}/messages` for `call_permission_request` and `/{phone_number_id}/calls` for calling actions.
- `app/javascript/dashboard/routes/dashboard/settings/inbox/channels/whatsapp/utils.js`
  - Embedded Signup login uses `config_id`, `response_type: 'code'`, and `override_default_response_type: true`.
  - It also sends `extras.featureType = 'whatsapp_business_app_onboarding'` and `sessionInfoVersion = '3'`, which must be reviewed for Embedded Signup v4.

### 3.5 WhatsApp inbound/status parsing

- `app/services/whatsapp/incoming_message_base_service.rb`
  - `update_message_with_status` assigns `message.status = status[:status]` directly.
  - `update_campaign_delivery_with_status` passes `status[:status]` directly to `CampaignDelivery#mark_status!`.
- `app/models/message.rb`
  - `enum status: { sent: 0, delivered: 1, read: 2, failed: 3 }`.
- `app/models/campaign_delivery.rb`
  - Status enum includes `pending`, `submitted`, `sent`, `delivered`, `read`, `failed`, `skipped`; no `played`.

Because official WhatsApp status webhooks include `played`, switching to v25 without normalization can raise enum errors or fail status processing for voice messages.

### 3.6 Unsupported message classification

- `app/services/whatsapp/incoming_message_service_helpers.rb`
  - Detects `message[:type] == 'unsupported'`.
  - Stores `is_unsupported`, `whatsapp_error_code`, and `whatsapp_error_title`.
  - Does not persist `message[:unsupported][:type]`.

Official docs now expose `unsupported.type`, so v25 readiness should preserve it in `content_attributes`, e.g. `whatsapp_unsupported_type`.

### 3.7 Coexistence / Business App + Cloud API

- `app/jobs/webhooks/whatsapp_events_job.rb`
  - Detects `field == 'smb_message_echoes'`.
  - Routes `message_echoes` through `Whatsapp::IncomingMessageWhatsappCloudService` with `outgoing_echo: true`.
- `app/services/whatsapp/contact_identity_resolver.rb` and specs support `from_user_id` / `from_parent_user_id` BSUID fields.
- No project code was found for `smb_app_data` / `smb_app_state_sync` history sync APIs.

Verdict: OneLink has partial coexistence handling for new Business App echo messages, but not full Business App data/history synchronization.

### 3.8 v25 changelog items not currently used by OneLink

Search evidence in the current codebase:

- No `metadata=1` usage found.
- No Page/Post/Video/Story Insights metric usage found for the v25/v26 metric deprecation list.
- No application-level Meta webhook mTLS verification found; OneLink currently uses `X-Hub-Signature-256` HMAC verification in `MetaTokenVerifyConcern`. If production enables Meta webhook mTLS at the edge, the gateway trust store must be checked separately.

## 4. Upgrade strategy

Do not switch production config to v25.0 first. Make the code accept v25 payloads first, then switch DEV, then production.

### Phase 0 — read-only runtime inventory

1. Read current `InstallationConfig` values for:
   - `FACEBOOK_API_VERSION`
   - `INSTAGRAM_API_VERSION`
   - `WHATSAPP_API_VERSION`
2. Count active channels by provider:
   - `Channel::FacebookPage`
   - `Channel::Instagram`
   - `Channel::Whatsapp.where(provider: 'whatsapp_cloud')`
3. For WhatsApp Cloud, summarize without secrets:
   - number of channels with `phone_number_id`
   - number with `business_account_id`
   - number with token health metadata
   - number with `provider_config['source'] == 'embedded_signup'`
4. Do not print access tokens, app secrets, page IDs, WABA IDs, phone IDs, or user IDs in public reports.

### Phase 1 — remove hardcoded older versions

1. Introduce provider-level version helpers or constants:
   - `Meta::ApiVersion.facebook`
   - `Meta::ApiVersion.instagram`
   - `Meta::ApiVersion.whatsapp`
   - or equivalent existing-service helpers, if preferred.
2. Update fallbacks to `v25.0` only after Phase 2 blockers are fixed.
3. Replace hardcoded Instagram `v22.0` endpoints with `INSTAGRAM_API_VERSION`:
   - `InstagramConcern#fetch_instagram_user_details`
   - `Channel::Instagram#subscribe`
   - `Channel::Instagram#unsubscribe`
   - `Instagram::SendOnInstagramService#send_message`
4. Replace `WHATSAPP_CALLING_API_VERSION_FALLBACK = 'v22.0'` with the same WhatsApp API version helper.
5. Update tests to use a variable `api_version` fixture instead of hardcoded `v22.0` expectations where the behavior is version-independent.

### Phase 2 — WhatsApp pre-switch blockers

1. **Status normalization**
   - Add a WhatsApp status normalizer.
   - Lowest-risk behavior: map provider `played` to local `read` for `Message` and `CampaignDelivery` unless product needs a distinct `played` state.
   - Preserve raw provider status in metadata/content attributes if needed for audit.
2. **Unsupported message metadata**
   - Store `message.dig(:unsupported, :type)` as `content_attributes[:whatsapp_unsupported_type]`.
   - Add specs for an unsupported payload with `unsupported.type = 'poll_creation'` or similar.
3. **Interactive action object**
   - Change `Whatsapp::Providers::BaseService#create_button_payload` and `create_list_payload` so `interactive.action` is a Ruby hash/object, not a JSON string.
   - Verify both Cloud and 360dialog paths still serialize correctly.
4. **Webhook field gating**
   - Keep `messages` always.
   - Add `smb_message_echoes` only when the channel/setup is explicitly Coexistence/Business App enabled or when OneLink intentionally keeps partial coexistence for all embedded-signup channels.
   - Add `calls` only when WhatsApp Cloud Calling is enabled for that channel/account and approved by feature flags.
5. **Template pagination hardening**
   - Handle Meta error `131059` for invalid/stale template pagination cursor by retrying without stale cursor if OneLink follows `paging.next` across runs.
6. **Health fields**
   - Add optional `whatsapp_business_manager_messaging_limit` to health formatting if Meta returns it, while keeping old `messaging_limit_tier` for compatibility.

### Phase 3 — Embedded Signup v4 path

1. Review official Embedded Signup v4 docs before code changes.
2. Ensure the frontend remains on the official code flow:
   - `config_id`
   - `response_type: 'code'`
   - `override_default_response_type: true`
3. Re-check whether v4 still requires or rejects current extras:
   - `featureType: 'whatsapp_business_app_onboarding'`
   - `sessionInfoVersion: '3'`
4. Keep backend functional validation strict:
   - exact selected `phone_number_id`
   - WABA phone-number access
   - token inspection diagnostics
   - strict webhook setup
5. Do not resurrect brittle `debug_token.granular_scopes[target_ids]` as a blocking check. Use real Graph access checks instead.

### Phase 4 — Facebook and Instagram v25 readiness

1. Facebook:
   - Set default `FACEBOOK_API_VERSION` to `v25.0` only after Messenger scope and Send API policy fixes are merged.
   - Keep Messenger-only setup free from Instagram scopes unless the flow is explicitly Instagram-linked.
   - Remove default `ACCOUNT_UPDATE` tagging for normal replies; use standard response behavior and `HUMAN_AGENT` only when approved.
2. Instagram:
   - Replace all hardcoded `v22.0` endpoints.
   - Keep required scopes and webhook fields aligned with official Instagram Messaging docs.
   - Keep `messages`, `message_reactions`, and `messaging_seen` subscriptions; add `messaging_postbacks`, `messaging_referral`, or `standby` only when the parser/runtime supports them.
3. Health checks:
   - Verify Facebook/Instagram/WhatsApp health checks use the configured v25 version and fail safely on provider auth errors.

### Phase 5 — DEV switch and provider smoke

In DEV only, set:

- `FACEBOOK_API_VERSION = v25.0`
- `INSTAGRAM_API_VERSION = v25.0`
- `WHATSAPP_API_VERSION = v25.0`

Then verify:

1. Facebook Messenger:
   - connect/reauthorize page flow
   - page subscription
   - inbound webhook signature
   - outbound text reply within 24-hour window
2. Instagram:
   - OAuth/long-lived token exchange
   - user details fetch
   - subscribe/unsubscribe
   - inbound message webhook
   - outbound message
3. WhatsApp Cloud:
   - Embedded Signup / reauthorization
   - `GET /{phone_number_id}` health
   - `GET /{waba_id}/message_templates`
   - `POST /{phone_number_id}/messages` text
   - media send/download URL lookup
   - template send
   - interactive button/list send
   - status webhooks: `sent`, `delivered`, `read`, `failed`, `played`
   - unsupported message webhook with `unsupported.type`
   - `smb_message_echoes` if coexistence is enabled
   - calls only if WhatsApp Cloud Calling is in scope

### Phase 6 — production cutover gate

Do not change production version config until all of these are true:

- targeted specs pass for changed services and webhook parsers;
- DEV live provider smoke passes for every enabled Meta channel type;
- active production Meta app permissions are confirmed;
- production webhook HMAC/app secret state is verified read-only;
- if Meta webhook mTLS is enabled at the edge, gateway trust store is confirmed for `meta-outbound-api-ca-2025-12.pem`;
- rollback plan is documented: reset `FACEBOOK_API_VERSION`, `INSTAGRAM_API_VERSION`, `WHATSAPP_API_VERSION` to previous values without code rollback if the failure is provider-version-specific.

## 5. Suggested implementation order

1. WhatsApp status normalization for `played`.
2. WhatsApp unsupported type persistence.
3. WhatsApp interactive `action` object fix.
4. WhatsApp webhook field gating for `calls` and coexistence.
5. Replace Instagram hardcoded `v22.0` endpoints.
6. Centralize Meta version fallbacks and move defaults to `v25.0`.
7. Facebook Messenger policy/scope fixes from the upstream adoption plan.
8. Embedded Signup v4 review and frontend adjustment if required.
9. DEV v25 config switch and provider smoke.
10. Production read-only probes, then explicit production config switch by approved deploy/change window.

## 6. Targeted verification pack

### Ruby syntax

- `app/services/whatsapp/incoming_message_base_service.rb`
- `app/services/whatsapp/incoming_message_service_helpers.rb`
- `app/services/whatsapp/providers/base_service.rb`
- `app/services/whatsapp/providers/whatsapp_cloud_service.rb`
- `app/services/whatsapp/facebook_api_client.rb`
- `app/services/whatsapp/health_service.rb`
- `enterprise/app/services/whatsapp/providers/whatsapp_cloud_call_methods.rb`
- `app/controllers/concerns/instagram_concern.rb`
- `app/models/channel/instagram.rb`
- `app/services/instagram/send_on_instagram_service.rb`
- `app/services/meta/authorization_health_check_service.rb`

### RSpec

- `spec/services/whatsapp/incoming_message_service_spec.rb`
- `spec/services/whatsapp/incoming_message_whatsapp_cloud_service_spec.rb`
- `spec/services/whatsapp/providers/whatsapp_cloud_service_spec.rb`
- `spec/services/whatsapp/facebook_api_client_spec.rb`
- `spec/services/whatsapp/health_service_spec.rb`
- `spec/services/meta/authorization_health_check_service_spec.rb`
- `spec/controllers/instagram/callbacks_controller_spec.rb`
- `spec/controllers/concerns/instagram_concern_spec.rb`
- `spec/models/channel/whatsapp_spec.rb`
- WhatsApp Calling specs only if `calls` path is touched.

### Frontend/unit checks

- `app/javascript/dashboard/routes/dashboard/settings/inbox/channels/whatsapp/utils.js`
- WhatsApp Embedded Signup component/specs if v4 frontend changes are made.
- Facebook scope helper/component specs if Messenger scope split is carried in the same branch.

Use `pnpm exec eslint <changed files>` for targeted lint; avoid package-script expansion for narrow checks.

## 7. Out of scope for this upgrade

- Marketing API campaign/reporting migration, unless OneLink later adds Meta Ads reporting.
- Page/Post/Story Insights migration, because no matching metrics usage was found in the current OneLink codebase.
- Full WhatsApp Business App history sync, unless product explicitly wants full Coexistence beyond `smb_message_echoes`.
- Production config mutation, deploy, restart, or Meta app setting changes. Those require explicit approval and live state checks.

## 8. Rollback plan

If DEV or production v25 switch exposes provider-specific failures:

1. Keep the code fixes; they are backwards-compatible defensive parsing/serialization improvements.
2. Roll back only config values:
   - `FACEBOOK_API_VERSION`
   - `INSTAGRAM_API_VERSION`
   - `WHATSAPP_API_VERSION`
3. Preserve logs and sanitized provider error codes for RCA.
4. Do not delete/recreate channels as rollback; use reauthorization only when Meta returns real auth/token failures.
