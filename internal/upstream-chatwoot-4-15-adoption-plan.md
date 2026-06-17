# Upstream Chatwoot v4.14.2/v4.15.0 deep adoption audit for OneLink

Date: `2026-06-17T15:01:55+02:00`

> Scope: local evidence-backed adoption plan from `/root/crafty/example/chatwoot` into `/root/crafty/onelink/chatwoot`. This document changes documentation only; application code is not modified by this audit.

## 0. What changed in this deeper pass

- Re-read the local reference checkout, not GitHub-only summaries.
- Expanded the plan from a release map into an implementation-quality decision matrix.
- Added concrete upstream commit ids, local OneLink file status, bug/UX rationale, adoption nuance, risks, and verification per item.
- Split Meta inbox/channel setup from generic UI and from OneLink custom WhatsApp Web/telephony paths.
- Marked dangerous wholesale-copy areas explicitly so the next branch does not overwrite OneLink custom runtime.

## 1. Local source snapshots

### Reference upstream checkout
- Path: `/root/crafty/example/chatwoot`
- Branch: `master`
- HEAD: `3fc1f177577193661f5a458c8566007d7fc3a318`
- Tags used: `v4.14.1`, `v4.14.2`, `v4.15.0`
- Git status:
  `## master...origin/master
   M app/javascript/dashboard/components-next/sidebar/SidebarGroupLeaf.vue`
- Note: the dirty `SidebarGroupLeaf.vue` tweak in reference is local and is not treated as upstream release evidence.

### OneLink checkout
- Path: `/root/crafty/onelink/chatwoot`
- Branch: `dev/content-postiz-native-module`
- HEAD: `acaede9ce4688f2b3d0b789d5d02bf55afc1e1c0`
- Parent repo status:
  `## dev/content-postiz-native-module...origin/dev/content-postiz-native-module [ahead 1]
   ? docs`
- Docs submodule status:
  `## feature/workspace-20260327...origin/feature/workspace-20260327
  ?? internal/upstream-chatwoot-4-15-adoption-plan.md`

### Release range

- Non-merge commits: `91` total — `54` in `v4.14.1..v4.14.2`, `37` in `v4.14.2..v4.15.0`.
- Changed-path status versus current OneLink: `{'diverged': 850, 'missing_in_onelink': 150, 'missing_both': 2, 'onelink_only_or_deleted_upstream': 4}`.
- Interpretation: this is not a safe merge range. Most paths are `diverged`; correct adoption is selective `TAKE`/`ADAPT`, not blanket merge/cherry-pick.

### Implementer reference index

Use this index before closing any adoption case, so the next developer can reproduce the evidence instead of trusting this document blindly.

- Upstream source repo: `https://github.com/chatwoot/chatwoot`
- Local upstream/reference checkout: `/root/crafty/example/chatwoot`
- Local OneLink checkout: `/root/crafty/onelink/chatwoot`
- Upstream compare URLs:
  - `https://github.com/chatwoot/chatwoot/compare/v4.14.1...v4.14.2`
  - `https://github.com/chatwoot/chatwoot/compare/v4.14.2...v4.15.0`
- Upstream commit URL template: `https://github.com/chatwoot/chatwoot/commit/<commit-sha>`
- Local upstream commit inspection:
  - `git -C /root/crafty/example/chatwoot show --stat --name-status <commit-sha>`
  - `git -C /root/crafty/example/chatwoot show <commit-sha> -- <path>`
- Local OneLink comparison:
  - `git -C /root/crafty/onelink/chatwoot status --short --branch --untracked-files=all`
  - `git -C /root/crafty/onelink/chatwoot diff -- <path>`
  - `git -C /root/crafty/onelink/chatwoot grep -n "<symbol-or-endpoint>" -- app enterprise config spec`
- Meta-specific reference gate: section `5.4 Official Meta documentation revalidation gate` in this document.
- Dedicated Meta v25 upgrade plan: [`onelink-meta-graph-api-v25-upgrade-plan.md`](./onelink-meta-graph-api-v25-upgrade-plan.md).

Adoption case closure requirements:

1. Link or cite the upstream commit SHA and, when useful, the GitHub commit URL.
2. For Facebook/Instagram/WhatsApp, cite the official Meta documentation URL used for the decision.
3. Cite the OneLink files changed or intentionally not changed.
4. Add targeted regression specs or a documented reason why live provider proof is required instead.
5. Mark the item as `TAKE`, `ADAPT`, `PRESENT`, `DEFER`, or `SKIP` with the reason preserved in the implementation PR/commit message.

## 2. Decision legend and priority

- `P0`: security, data-loss, provider-connectivity, or silent-message-drop fixes; should be first backend/integration branch.
- `P1`: operator UX and reliability modules with coherent backend/frontend slices.
- `P2`: larger architecture/performance/auth/tooling changes; take only with a dedicated design branch.
- `TAKE`: can be ported almost directly, still with OneLink tests.
- `ADAPT`: upstream idea/fix is correct, but OneLink code has custom overlays; hand-merge.
- `PRESENT`: OneLink already has equivalent or stronger behavior.
- `DEFER`: useful but not first wave or needs runtime/product proof.
- `SKIP`: do not adopt directly.

## 3. Executive answer: what to take

### 3.1 P0 bugfix/security/integration fixes to take first

#### P0 / ADAPT: Meta WhatsApp Embedded Signup: remove obsolete WABA granular-scope hard fail

- Upstream evidence: `f93f2067b` — f93f2067b fix(whatsapp): Drop obsolete WABA scope check broken by Meta embedded signup (#14697).
- Problem fixed upstream: Meta Embedded Signup no longer reliably exposes the old WABA target_ids granular scope in the way Chatwoot used to validate. A strict local WABA-scope validator rejects otherwise valid signup/reauth attempts.
- OneLink evidence: OneLink still calls `validate_token_access` in `Whatsapp::EmbeddedSignupService`; `Whatsapp::TokenValidationService` exists. OneLink additionally has `TokenInspectionService`, which can keep diagnostics without hard-failing creation.
- Adoption nuance: Remove the blocking WABA-scope validation from signup/reauth, but keep/route non-blocking token inspection metadata. Do not delete OneLink diagnostic health code wholesale.
- Risk/control: If removed incorrectly, truly wrong WABA/phone selections could pass farther; mitigate by exact `phone_number_id` and phone-info fetch validation, and by preserving account-scoped existing inbox reauth rules.
- Verification: Embedded signup service spec: successful create and reauth no longer instantiate TokenValidationService; exact phone_number_id required; token-inspection metadata recorded/sanitized; missing required WhatsApp permissions still surfaces through Graph/phone-info errors.
- Local file status:
  - `app/services/whatsapp/embedded_signup_service.rb` — `diverged`
  - `app/services/whatsapp/token_validation_service.rb` — `onelink_only_or_deleted_upstream`
  - `app/services/whatsapp/token_inspection_service.rb` — `onelink_only_or_deleted_upstream`

#### P0 / ADAPT: Facebook/Messenger OAuth scopes: do not request Instagram scopes in Messenger-only flow

- Upstream evidence: `c6a38e2fc` — c6a38e2fc fix: Keep Instagram scopes out of new Messenger OAuth flows (#14695).
- Problem fixed upstream: Messenger-only OAuth asks for Instagram permissions, increasing Meta review friction and causing connect/reauth failures for apps/users that should only connect Facebook Pages.
- OneLink evidence: OneLink hardcodes `instagram_basic,instagram_manage_messages` in both `Facebook.vue` and `facebook/Reauthorize.vue`; upstream composables are missing locally, but `facebookScopes.js` style helper can be added/adapted.
- Adoption nuance: Create/adjust `buildFacebookLoginScopes(includeInstagramScopes:)`; default Messenger flow excludes Instagram scopes; reauth includes Instagram scopes only for existing Instagram-linked inbox.
- Risk/control: If Instagram inbox creation depends on the shared Facebook flow, ensure its entrypoint passes `includeInstagramScopes: true`; otherwise Instagram messaging breaks.
- Verification: Frontend composable/helper specs; component spec or grep assertion for Facebook.vue/Reauthorize.vue; manual Meta app permission matrix notes.
- Local file status:
  - `app/javascript/dashboard/routes/dashboard/settings/inbox/channels/Facebook.vue` — `diverged`
  - `app/javascript/dashboard/routes/dashboard/settings/inbox/facebook/Reauthorize.vue` — `diverged`
  - `app/javascript/dashboard/helper/facebookScopes.js` — `missing_in_onelink`
  - `app/javascript/dashboard/composables/useFacebookPageConnect.js` — `missing_in_onelink`

#### P0 / TAKE/ADAPT: Facebook Messenger replies: stop force tagging with MESSAGE_TAG/ACCOUNT_UPDATE

- Upstream evidence: `d8656edc6` — d8656edc6 fix(facebook): Stop force tagging Messenger replies with MESSAGE_TAG/ACCOUNT_UPDATE (#14329).
- Problem fixed upstream: Messenger replies sent as `MESSAGE_TAG` with `ACCOUNT_UPDATE` fallback can violate Meta messaging policy and fail for apps without HUMAN_AGENT approval.
- OneLink evidence: OneLink `Facebook::SendOnFacebookService` still needs exact check during implementation; prior audit showed forced tag behavior.
- Adoption nuance: Send `messaging_type: RESPONSE` by default. Only use `MESSAGE_TAG`/`HUMAN_AGENT` when `ENABLE_MESSENGER_CHANNEL_HUMAN_AGENT` is explicitly enabled.
- Risk/control: Some long-window replies may stop using tag fallback; that is policy-correct but changes behavior. Document admin env knob.
- Verification: Service spec for env disabled/enabled; payload JSON assertion; outbound failure path remains captured.
- Local file status:
  - `app/services/facebook/send_on_facebook_service.rb` — `diverged`

#### P0 / ADAPT: WhatsApp webhook subscription: include calls only when voice/calling is enabled

- Upstream evidence: `e055cead3` — e055cead3 fix: only subscribe calls webhook field when voice calling enabled (#14718).
- Problem fixed upstream: Subscribing WABA `calls` field for every WhatsApp Cloud inbox can fail Meta webhook setup or request call permissions for inboxes that do not have voice enabled.
- OneLink evidence: OneLink `Whatsapp::FacebookApiClient::WEBHOOK_DEFAULT_FIELDS` still includes `calls`; channel creation sets `calling_enabled=true` if phone looks capable, so this can silently broaden subscriptions.
- Adoption nuance: Default fields: `messages`, `smb_message_echoes`. Append `calls` only when channel provider_config `calling_enabled` is true and OneLink `whatsapp_call` feature allows it. Keep OneLink voice/call gating, do not copy upstream `channel_voice` wholesale.
- Risk/control: If existing call-enabled inboxes rely on the previous blanket subscription, ensure re-register after enabling voice preserves calls; disable path should not leave stale UI state.
- Verification: FacebookApiClient/WebhookSetup specs for fields with/without calling_enabled; Channel::Whatsapp voice_enabled? specs; no change to WhatsApp Web/Evolution paths.
- Local file status:
  - `app/services/whatsapp/facebook_api_client.rb` — `diverged`
  - `app/services/whatsapp/webhook_setup_service.rb` — `diverged`
  - `app/models/channel/whatsapp.rb` — `diverged`

#### P0 / ADAPT: WhatsApp Cloud inbound media: preserve original filenames

- Upstream evidence: `c041fde3a` — c041fde3a fix: Preserve original filenames for WhatsApp cloud attachments (#14168).
- Problem fixed upstream: WhatsApp Cloud media downloaded through Graph can arrive with generic temp filenames, degrading operator UX and file-type handling.
- OneLink evidence: OneLink base attach path uses `attachment_file.original_filename`; Cloud service needs to set/override it from provider metadata before attach.
- Adoption nuance: Port filename preservation into current OneLink Cloud incoming service, respecting custom identity/dedup/unsupported-message code.
- Risk/control: Never trust filename for path; sanitize as display name only; keep ActiveStorage content-type detection.
- Verification: Incoming Cloud service spec: media payload filename appears in attachment; no regression for unsupported and dedup paths.
- Local file status:
  - `app/services/whatsapp/incoming_message_whatsapp_cloud_service.rb` — `diverged`
  - `app/services/whatsapp/incoming_message_base_service.rb` — `diverged`

#### P0 / ADAPT: WhatsApp location: truncate fallback_title to avoid silent message drops

- Upstream evidence: `7acbe8b3f` — 7acbe8b3f fix(whatsapp): truncate location fallback_title to 255 chars to avoid silent message drop (#14517).
- Problem fixed upstream: Long location names exceed attachment `fallback_title` DB limit and can drop messages silently.
- OneLink evidence: OneLink `location_params` uses `location_name` directly; no `.first(255)` found.
- Adoption nuance: Truncate location fallback_title to `ApplicationRecord::MAX_STRING_COLUMN_LENGTH` or 255 in current base service.
- Risk/control: Truncation must be deterministic and not mutate coordinates/external_url.
- Verification: Incoming WhatsApp location spec with >255 chars; message and attachment still created.
- Local file status:
  - `app/services/whatsapp/incoming_message_base_service.rb` — `diverged`

#### P0 / ADAPT: WhatsApp/Twilio CTWA referrals: persist referral metadata in message.content_attributes

- Upstream evidence: `de137e829` — de137e829 feat: Capture CTWA referral metadata for WhatsApp conversations (#14681).
- Problem fixed upstream: Click-to-WhatsApp Ads referral metadata is lost, so operators/Captain/CRM cannot see which ad/source produced the conversation.
- OneLink evidence: OneLink WhatsApp helpers already have `message_content_attributes`, but no referral/CTWA extraction; Twilio helper absent. This is especially relevant for lead attribution/MacroCRM.
- Adoption nuance: Merge referral attributes into `message.content_attributes[:referral]` for Cloud and Twilio WhatsApp. Keep outgoing echo exclusion and inbox-scoped source-id lookup.
- Risk/control: Referral payload may contain URLs/media; store metadata but do not auto-fetch media without SafeFetch policy. Avoid leaking tokens in logs.
- Verification: Cloud/Twilio incoming specs with referral/ctwa_clid; existing reply-to and unsupported metadata still present.
- Local file status:
  - `app/services/whatsapp/incoming_message_base_service.rb` — `diverged`
  - `app/services/whatsapp/incoming_message_service_helpers.rb` — `diverged`
  - `app/services/twilio/incoming_message_service.rb` — `diverged`

#### P0 / ADAPT: Integration hooks API: redact sensitive settings according to visible_properties

- Upstream evidence: `27404b4a2` — 27404b4a2 fix: redact sensitive integration secrets from API responses (#14147).
- Problem fixed upstream: Admin hook API can return full `resource.settings`, leaking integration credentials/secrets to the browser/API clients.
- OneLink evidence: OneLink `_hook.json.jbuilder` still returns `json.settings settings_payload`; config has `visible_properties` but model/view do not enforce it. OneLink also adds MacroCRM webhook metadata, Kaspi Pay metadata, and Medelement schedule fields.
- Adoption nuance: Implement `Integrations::App#visible_properties` and filter only safe settings. Keep OneLink metadata blocks, but audit metadata methods for secret leakage. Remove `openai.api_key` and `leadsquared.access_key` from visible_properties.
- Risk/control: UI edit forms may expect a masked value. Do not send real secret back; use placeholder/credential_configured flags if needed.
- Verification: Hook JSON/request specs for macrocrm/kaspi_pay/medelement/openai/leadsquared; admin vs non-admin; secret_settings never present.
- Local file status:
  - `app/models/integrations/app.rb` — `diverged`
  - `app/views/api/v1/models/_hook.json.jbuilder` — `diverged`
  - `config/integration/apps.yml` — `diverged`
  - `app/models/integrations/hook.rb` — `diverged`

#### P0 / TAKE: Session cookie: secure and httponly flags

- Upstream evidence: `95d6aecb5` — 95d6aecb5 chore: Add security flags to session cookie configuration (#14248).
- Problem fixed upstream: Session cookie lacks explicit security flags.
- OneLink evidence: OneLink session store uses key + `same_site: :lax`; missing `secure: ENV/force_ssl`, `httponly: true`.
- Adoption nuance: Add `secure: Rails.configuration.force_ssl`/FORCE_SSL-compatible flag and `httponly: true`, preserving key/same_site.
- Risk/control: Local HTTP dev must still work; secure should follow FORCE_SSL not unconditional true.
- Verification: Spec/config assertion for secure/httponly/same_site; boot smoke.
- Local file status:
  - `config/initializers/session_store.rb` — `diverged`

#### P0 / TAKE/ADAPT: Instagram webhook mutex exhaustion: process after lock retries instead of dropping

- Upstream evidence: `73ba0b26e` — 73ba0b26e fix(instagram): process webhook events after mutex retry exhaustion (#14647).
- Problem fixed upstream: Instagram webhook jobs can exhaust mutex retries and drop an event instead of processing after contention clears.
- OneLink evidence: OneLink uses MutexApplicationJob/InstagramEventsJob; needs diff check before patch because queue semantics can affect all providers.
- Adoption nuance: Add targeted retry-on-lock-conflict path for Instagram only, not a global behavior change unless specs prove safe.
- Risk/control: Duplicate processing if lock bypass is too broad; ensure idempotency by event/source ids.
- Verification: MutexApplicationJob spec for exhaustion fallback; InstagramEventsJob spec; no side effect for WhatsApp jobs.
- Local file status:
  - `app/jobs/mutex_application_job.rb` — `diverged`
  - `app/jobs/webhooks/instagram_events_job.rb` — `diverged`

#### P0 / TAKE: Contacts search/phone/name robustness: truncate inbound contact names

- Upstream evidence: `6d26e7930` — 6d26e7930 fix(contacts): truncate inbound contact names (IMAP sender display names) (#14631).
- Problem fixed upstream: Inbound display names from IMAP/providers can exceed string column max and fail contact/contact_inbox creation.
- OneLink evidence: OneLink builder is custom (`skip_runtime_events`, channel profile upsert); add only truncation helper, do not replace builder.
- Adoption nuance: Use `ApplicationRecord::MAX_STRING_COLUMN_LENGTH` and truncate generated contact name.
- Risk/control: Do not truncate identifiers/source_id; only display name.
- Verification: Builder spec long single/multi-part sender name; OneLink channel profile behavior still works.
- Local file status:
  - `app/builders/contact_inbox_with_contact_builder.rb` — `diverged`
  - `app/models/application_record.rb` — `diverged`

### 3.2 P1 UX/reliability improvements worth taking after P0

#### P1 / ADAPT: Facebook shared links: render as fallback link attachments, not broken downloadable media

- Upstream evidence: `3eed8905c`.
- User value/problem: Facebook shared links are page URLs, not downloadable media. Treating them as file/media causes broken attachments or download errors.
- OneLink evidence: OneLink backend already maps Facebook `share` to fallback-ish params in builder, but frontend has no `Fallback.vue` bubble and Message.vue does not render `ATTACHMENT_TYPES.FALLBACK` explicitly; current result likely degrades to text bubble or unsupported UX.
- Adoption nuance: Finish the UI half: add fallback bubble/link renderer and route fallback attachments to it. Keep OneLink reel/story custom handling.
- Risk/control: Do not change Instagram share/story media handling; upstream fix is Facebook-only.
- Verification: Builder spec for share -> fallback; Message.vue component spec/story for fallback attachment.
- Local file status:
  - `app/builders/messages/facebook/message_builder.rb` — `diverged`
  - `app/javascript/dashboard/components-next/message/Message.vue` — `diverged`
  - `app/javascript/dashboard/components-next/message/bubbles/Fallback.vue` — `missing_in_onelink`

#### P1 / ADAPT: Contact media tab: shared media/files on contact sidebar

- Upstream evidence: `35bef21f8`.
- User value/problem: Operators lack a contact-level media/files view, so finding previous files requires opening each conversation.
- OneLink evidence: Backend contact attachments controller exists and is more scoped than upstream includes; frontend store pieces are incomplete: no `SET_CONTACT_ATTACHMENTS` mutation type, no getter/action in current OneLink actions/getters/mutations; ContactMedia component missing.
- Adoption nuance: Adopt as coherent UX module: endpoint + store + ContactMedia tab + SharedAttachments components. Preserve OneLink contact channel_profile includes and permissions.
- Risk/control: Contact attachment endpoint can leak files across inaccessible conversations if permission filter is wrong; current controller uses `PermissionFilterService`, keep it.
- Verification: Request spec for only accessible account/conversations; frontend store/component tests; jump-to-message route using display_id vs DB id verified.
- Local file status:
  - `app/controllers/api/v1/accounts/contacts/attachments_controller.rb` — `diverged`
  - `app/javascript/dashboard/components-next/Contacts/ContactsSidebar/ContactMedia.vue` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/SharedAttachments/Media.vue` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/SharedAttachments/Files.vue` — `missing_in_onelink`
  - `app/javascript/dashboard/store/modules/contacts/actions.js` — `diverged`
  - `app/javascript/dashboard/store/modules/contacts/getters.js` — `diverged`
  - `app/javascript/dashboard/store/modules/contacts/mutations.js` — `diverged`
  - `app/javascript/dashboard/store/mutation-types.js` — `diverged`

#### P1 / ADAPT: Contacts native Company selector: use company_id instead of free-text companyName only

- Upstream evidence: `41a3ab6df`.
- User value/problem: Contacts still store company as free-text `additionalAttributes.companyName`, so CRM/company entity is disconnected from contact form UX.
- OneLink evidence: OneLink has `contacts.company_id`, Enterprise concern, CRM/Scheduling company usage, but lacks enterprise contacts controller override and `_contact.json` does not expose company_id. Contact form has KZ phone default that must remain.
- Adoption nuance: Use native `company_id` when companies feature is enabled; keep `additionalAttributes.companyName` as legacy display fallback/sync. Add CompanySelector and create dialog using existing `components-next` patterns.
- Risk/control: Blank company_id must clear association; cross-account company_id must be rejected; migration/backfill from companyName should be explicit, not automatic in the UI patch.
- Verification: Enterprise contacts controller spec, contact JSON exposes company_id, frontend payload update/create, KZ default country still present.
- Local file status:
  - `app/controllers/api/v1/accounts/contacts_controller.rb` — `diverged`
  - `enterprise/app/controllers/enterprise/api/v1/accounts/contacts_controller.rb` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/Companies/CompanySelector.vue` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/Contacts/ContactsForm/ContactsForm.vue` — `diverged`
  - `app/views/api/v1/models/_contact.json.jbuilder` — `diverged`
  - `enterprise/app/models/enterprise/concerns/contact.rb` — `diverged`

#### P1 / ADAPT: WhatsApp Cloud outgoing voice notes: OGG/Opus conversion + voice payload

- Upstream evidence: `37eed5de1`.
- User value/problem: WhatsApp Cloud supports voice-note style OGG/Opus messages, but browser recording defaults to webm/other formats that Cloud may reject or render as ordinary audio.
- OneLink evidence: OneLink has separate WhatsApp call subsystem; missing WootWriter OGG conversion utilities. Do not confuse voice notes with calls.
- Adoption nuance: Adopt only if product wants outgoing voice notes in official WhatsApp Cloud. Restrict OGG conversion to WhatsApp Cloud inboxes as follow-up commit `33f755052` does.
- Risk/control: Large frontend/audio blast radius; mobile browser recording differences; avoid changing WhatsApp Web/Evolution media path.
- Verification: Audio recorder unit tests, provider payload `voice: true`, content type conversion tests; manual browser smoke if implemented.
- Local file status:
  - `app/javascript/dashboard/components/widgets/WootWriter/AudioRecorder.vue` — `diverged`
  - `app/javascript/dashboard/components/widgets/WootWriter/utils/audioConversionUtils.js` — `missing_in_onelink`
  - `app/javascript/dashboard/components/widgets/WootWriter/utils/webmOpusToOgg.js` — `missing_in_onelink`
  - `app/services/whatsapp/providers/whatsapp_cloud_service.rb` — `diverged`

#### P1 / TAKE/ADAPT: Email/IMAP: prevent deleted conversations from syncing again

- Upstream evidence: `ee6382109`.
- User value/problem: Deleted IMAP conversations can be fetched again because provider source ids are not remembered as deleted.
- OneLink evidence: DeletedMessageTracker missing; net-imap old. If email inboxes are active, this is user-visible duplicate conversation bug.
- Adoption nuance: Take tracker + delete/fetch hooks if IMAP is used; otherwise defer.
- Risk/control: Redis key TTL/retention must be chosen; deleting by account/inbox/source id only, not global.
- Verification: Delete service stores marker; fetch skips marked source ids; account/inbox scoping.
- Local file status:
  - `app/services/imap/deleted_message_tracker.rb` — `missing_in_onelink`
  - `app/services/imap/base_fetch_email_service.rb` — `diverged`
  - `app/services/conversations/delete_service.rb` — `missing_in_onelink`
  - `lib/redis/redis_keys.rb` — `diverged`

#### P1 / TAKE/ADAPT: Email compatibility: IMAP/SMTP compatibility and null-byte sanitization

- Upstream evidence: `8e42307bd+d1c482cb6`.
- Local file status:
  - `app/services/imap/base_fetch_email_service.rb` — `diverged`
  - `app/mailboxes/imap/imap_mailbox.rb` — `diverged`
  - `app/mailboxes/mailbox_sanitizer.rb` — `missing_in_onelink`

#### P1 / ADAPT: Help Center public search and per-locale portal branding

- Upstream evidence: `ecd9c26c8+64c5aeebe+1713cabdf+dda25c0b5`.
- Local file status:
  - `app/controllers/public/api/v1/portals/search_controller.rb` — `missing_in_onelink`
  - `app/models/concerns/portal_config_schema.rb` — `missing_in_onelink`
  - `app/helpers/portal_helper.rb` — `diverged`
  - `db/migrate/20260610000000_add_icon_color_to_categories.rb` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/emoji-icon-picker/EmojiIconPicker.vue` — `missing_in_onelink`

### 3.3 P2 items to defer or avoid as direct copy

#### P2 / DEFER/ADAPT: Conversation unread Redis cache, filter counters, sidebar ordering and unread sort

- Upstream evidence: `4d3196b02+a901c87ab+4816e923b+d8a16278b+fe6368b42`.
- Why not P0: OneLink already has `Conversations::SidebarUnreadCountService`, `/sidebar_unread_counts`, ActionCable refresh, and sidebar badges. Upstream adds Redis stores, filter counters, sort preferences, and many permission/cache invalidation hooks. This can improve large-account UX, but it is an architecture/performance module, not a small bugfix.
- Adoption nuance: first measure high-volume accounts and compare OneLink current counts against upstream contract. If adopted, port as a coherent module including `AccountUser`, `InboxMember`, `Mention`, `CustomFilter`, `ActionCableListener`, and enterprise custom-role changes.
- Local file status:
  - `app/services/conversations/unread_counts/builder.rb` — `missing_in_onelink`
  - `app/services/conversations/unread_counts/store.rb` — `missing_in_onelink`
  - `app/services/conversations/unread_counts/filter_counter.rb` — `missing_in_onelink`
  - `app/javascript/dashboard/store/modules/conversationUnreadCounts.js` — `missing_in_onelink`
  - `app/javascript/dashboard/store/modules/sidebarSortPreferences.js` — `missing_in_onelink`
  - `app/finders/conversation_finder.rb` — `diverged`

#### P2 / DEFER/CONFLICT: Active sessions/login picker

- Upstream evidence: `92a1fb8ab+396631ad7`.
- Why not direct: OneLink already has custom active auth client/session replacement enforcement. Upstream introduces `UserSession` and login picker; direct copy can conflict with `active_auth_client_id` and ActionCable session replacement.
- Local file status:
  - `app/controllers/devise_overrides/sessions_controller.rb` — `diverged`
  - `app/controllers/concerns/active_auth_session_enforcer.rb` — `onelink_only_or_deleted_upstream`
  - `app/javascript/dashboard/components/auth/SessionLimitOverlay.vue` — `missing_in_onelink`
  - `db/migrate/20260611184600_create_user_sessions.rb` — `missing_in_onelink`

#### P2 / SKIP direct / ADAPT only: Captain HttpTool SafeFetch and Firecrawl v2

- Upstream evidence: `3dfb5061e+cd9192f7d`.
- Why not direct: OneLink Captain HTTP executor and Firecrawl service are richer than upstream. Only take ideas after mapping to OneLink runtime contracts, artifacts, retries, redacted errors, and access model.
- Local file status:
  - `enterprise/lib/captain/tools/http_tool.rb` — `diverged`
  - `enterprise/lib/captain/tools/http_request_executor.rb` — `onelink_only_or_deleted_upstream`
  - `enterprise/app/services/captain/tools/firecrawl_service.rb` — `diverged`

#### P2 / TAKE: Dependency/security bumps: puma, net-imap, selected OAuth deps

- Upstream evidence: `7718f2a62+006b52991+72a59e479`.
- Adoption nuance: puma/net-imap are good candidates, but dependency bumps must be isolated with boot/spec smoke. Vite 6 is a separate frontend toolchain migration, not part of backend P0.
- Local file status:
  - `Gemfile` — `diverged`
  - `Gemfile.lock` — `diverged`

## 4. Release buckets: what changed by surface

### Meta inboxes and channel setup — 35 matching commits
- `v4.14.2` `ed3059c1a` docs: Document API inbox webhook URL (#14593) — `swagger/definitions/index.yml`, `swagger/definitions/request/inbox/channels/create_api_channel_payload.yml`, `swagger/definitions/request/inbox/channels/create_email_channel_payload.yml`, `swagger/definitions/request/inbox/channels/create_line_channel_payload.yml`, `swagger/definitions/request/inbox/channels/create_sms_channel_payload.yml` …
- `v4.14.2` `f27bbef73` feat: show processing status for one-off campaigns (#14592) — `app/javascript/dashboard/components-next/Campaigns/CampaignCard/CampaignCard.vue`, `app/javascript/dashboard/i18n/locale/en/campaign.json`, `app/models/campaign.rb`, `app/services/sms/oneoff_sms_campaign_service.rb`, `app/services/twilio/oneoff_sms_campaign_service.rb` …
- `v4.14.2` `3eed8905c` fix(facebook): render shared links as fallback attachments (#14554) — `app/builders/messages/facebook/message_builder.rb`, `app/javascript/dashboard/components-next/message/Message.vue`, `app/javascript/dashboard/components-next/message/bubbles/Fallback.vue`, `spec/builders/messages/facebook/message_builder_spec.rb`
- `v4.14.2` `1f6203d55` feat(onboarding): honor return_to hint in TikTok OAuth callback (#14569) — `app/controllers/api/v1/accounts/tiktok/authorizations_controller.rb`, `app/controllers/tiktok/callbacks_controller.rb`, `app/helpers/tiktok/integration_helper.rb`, `config/routes.rb`
- `v4.14.2` `04ac9d378` fix: use UPN for `imap_login` on Microsoft OAuth callback (#14522) — `app/controllers/microsoft/callbacks_controller.rb`, `app/controllers/oauth_callback_controller.rb`, `spec/controllers/microsoft/callbacks_controller_spec.rb`
- `v4.14.2` `4c6a345d6` feat(onboarding): honor return hint in email OAuth callback (#14567) — `app/controllers/api/v1/accounts/oauth_authorization_controller.rb`, `app/controllers/oauth_callback_controller.rb`
- `v4.14.2` `95cb3a7ad` feat(onboarding): honor return_to hint in Instagram OAuth callback (#14568) — `app/controllers/api/v1/accounts/instagram/authorizations_controller.rb`, `app/controllers/instagram/callbacks_controller.rb`, `app/helpers/instagram/integration_helper.rb`
- `v4.14.2` `37eed5de1` feat(whatsapp): Add support for voice messages (#14606) — `app/builders/messages/message_builder.rb`, `app/javascript/dashboard/api/inbox/message.js`, `app/javascript/dashboard/api/specs/inbox/message.spec.js`, `app/javascript/dashboard/components/widgets/AttachmentsPreview.vue`, `app/javascript/dashboard/components/widgets/WootWriter/AudioRecorder.vue` …
- `v4.14.2` `36a05097f` fix(webhooks): strip trailing newlines from webhook message content (#14272) — `app/services/messages/webhook_content_normalizer.rb`, `spec/services/messages/webhook_content_normalizer_spec.rb`
- `v4.14.2` `b791d75b3` fix(microsoft): prevent OAuth admin consent loop (#13962) — `app/controllers/api/v1/accounts/microsoft/authorizations_controller.rb`, `spec/controllers/api/v1/accounts/microsoft/authorization_controller_spec.rb`
- `v4.14.2` `7acbe8b3f` fix(whatsapp): truncate location fallback_title to 255 chars to avoid silent message drop (#14517) — `app/services/whatsapp/incoming_message_base_service.rb`, `spec/services/whatsapp/incoming_message_service_spec.rb`
- `v4.14.2` `1beaa284c` feat: inline images in website and email channels (#14516) — `app/javascript/dashboard/components/widgets/WootWriter/Editor.vue`, `app/javascript/dashboard/constants/editor.js`, `app/javascript/dashboard/helper/editorHelper.js`, `app/javascript/dashboard/helper/specs/editorHelper.spec.js`, `app/javascript/dashboard/i18n/locale/en/conversation.json` …
- `v4.14.2` `0e87519ec` feat: add mute button for Twilio calls (#14637) — `app/javascript/dashboard/api/channel/voice/twilioVoiceClient.js`, `app/javascript/dashboard/components-next/call/FloatingCallWidget.vue`
- `v4.14.2` `94ddd9805` chore: update the voice call ringtone (#14636) — `app/javascript/dashboard/components-next/call/FloatingCallWidget.vue`, `public/audio/dashboard/ringtone.mp3`
- `v4.14.2` `ea910227a` feat: add Voice Calls feature card to settings showcase (#14635) — `app/helpers/super_admin/features.yml`, `app/views/super_admin/application/_icons.html.erb`
- `v4.14.2` `eaffad12e` feat(langfuse): propagate observation metadata for evals (#14634) — `enterprise/app/helpers/captain/chat_generation_recorder.rb`, `lib/captain/tool_instrumentation.rb`, `lib/integrations/llm_instrumentation.rb`, `lib/integrations/llm_instrumentation_completion_helpers.rb`, `lib/integrations/llm_instrumentation_constants.rb` …
- `v4.14.2` `64c5aeebe` feat(help-center): support per-locale portal title, name & header (#14642) — `app/controllers/api/v1/accounts/portals_controller.rb`, `app/controllers/public/api/v1/portals_controller.rb`, `app/javascript/dashboard/components-next/HelpCenter/LocaleCard/LocaleCard.vue`, `app/javascript/dashboard/components-next/HelpCenter/Pages/LocalePage/LocaleContentDialog.vue`, `app/javascript/dashboard/components-next/HelpCenter/Pages/LocalePage/LocaleList.vue` …
- `v4.14.2` `73ba0b26e` fix(instagram): process webhook events after mutex retry exhaustion (#14647) — `app/jobs/mutex_application_job.rb`, `app/jobs/webhooks/instagram_events_job.rb`, `spec/jobs/mutex_application_job_spec.rb`
- … 17 more commits in this bucket; see local git range for full list.

### Security/auth/integration secrets — 28 matching commits
- `v4.14.2` `ed3059c1a` docs: Document API inbox webhook URL (#14593) — `swagger/definitions/index.yml`, `swagger/definitions/request/inbox/channels/create_api_channel_payload.yml`, `swagger/definitions/request/inbox/channels/create_email_channel_payload.yml`, `swagger/definitions/request/inbox/channels/create_line_channel_payload.yml`, `swagger/definitions/request/inbox/channels/create_sms_channel_payload.yml` …
- `v4.14.2` `1f6203d55` feat(onboarding): honor return_to hint in TikTok OAuth callback (#14569) — `app/controllers/api/v1/accounts/tiktok/authorizations_controller.rb`, `app/controllers/tiktok/callbacks_controller.rb`, `app/helpers/tiktok/integration_helper.rb`, `config/routes.rb`
- `v4.14.2` `04ac9d378` fix: use UPN for `imap_login` on Microsoft OAuth callback (#14522) — `app/controllers/microsoft/callbacks_controller.rb`, `app/controllers/oauth_callback_controller.rb`, `spec/controllers/microsoft/callbacks_controller_spec.rb`
- `v4.14.2` `4c6a345d6` feat(onboarding): honor return hint in email OAuth callback (#14567) — `app/controllers/api/v1/accounts/oauth_authorization_controller.rb`, `app/controllers/oauth_callback_controller.rb`
- `v4.14.2` `95cb3a7ad` feat(onboarding): honor return_to hint in Instagram OAuth callback (#14568) — `app/controllers/api/v1/accounts/instagram/authorizations_controller.rb`, `app/controllers/instagram/callbacks_controller.rb`, `app/helpers/instagram/integration_helper.rb`
- `v4.14.2` `0a181b0ce` chore: Update translations (#14498) — `app/javascript/dashboard/i18n/locale/am/bulkActions.json`, `app/javascript/dashboard/i18n/locale/am/campaign.json`, `app/javascript/dashboard/i18n/locale/am/components.json`, `app/javascript/dashboard/i18n/locale/am/contact.json`, `app/javascript/dashboard/i18n/locale/am/conversation.json` …
- `v4.14.2` `36a05097f` fix(webhooks): strip trailing newlines from webhook message content (#14272) — `app/services/messages/webhook_content_normalizer.rb`, `spec/services/messages/webhook_content_normalizer_spec.rb`
- `v4.14.2` `b791d75b3` fix(microsoft): prevent OAuth admin consent loop (#13962) — `app/controllers/api/v1/accounts/microsoft/authorizations_controller.rb`, `spec/controllers/api/v1/accounts/microsoft/authorization_controller_spec.rb`
- `v4.14.2` `eaffad12e` feat(langfuse): propagate observation metadata for evals (#14634) — `enterprise/app/helpers/captain/chat_generation_recorder.rb`, `lib/captain/tool_instrumentation.rb`, `lib/integrations/llm_instrumentation.rb`, `lib/integrations/llm_instrumentation_completion_helpers.rb`, `lib/integrations/llm_instrumentation_constants.rb` …
- `v4.14.2` `f9385a31f` fix(api): allow agent bots to read conversations and manage labels (#14655) — `app/controllers/concerns/access_token_auth_helper.rb`
- `v4.14.2` `73ba0b26e` fix(instagram): process webhook events after mutex retry exhaustion (#14647) — `app/jobs/mutex_application_job.rb`, `app/jobs/webhooks/instagram_events_job.rb`, `spec/jobs/mutex_application_job_spec.rb`
- `v4.14.2` `7718f2a62` fix: update puma for security advisories (#14670) — `Gemfile`, `Gemfile.lock`
- `v4.14.2` `af1dfc21f` fix: include account data in webhook payloads (#12445) — `app/listeners/webhook_listener.rb`, `app/presenters/conversations/event_data_presenter.rb`, `app/presenters/inbox/event_data_presenter.rb`, `spec/listeners/agent_bot_listener_spec.rb`, `spec/listeners/webhook_listener_spec.rb` …
- `v4.14.2` `8a3b12929` fix: Disable re-oauth flow for manual whatsapp (#13599) — `app/jobs/webhooks/whatsapp_events_job.rb`, `app/views/api/v1/models/_inbox.json.jbuilder`, `spec/controllers/api/v1/accounts/inboxes_controller_spec.rb`, `spec/jobs/webhooks/whatsapp_events_job_spec.rb`
- `v4.14.2` `72a59e479` fix: update oauth dependencies (#14691) — `Gemfile.lock`, `app/services/base_refresh_oauth_token_service.rb`
- `v4.14.2` `3dfb5061e` refactor: route captain custom tool requests through SafeFetch (#14620) — `enterprise/app/controllers/api/v1/accounts/captain/custom_tools_controller.rb`, `enterprise/lib/captain/tools/http_tool.rb`
- `v4.14.2` `f93f2067b` fix(whatsapp): Drop obsolete WABA scope check broken by Meta embedded signup (#14697) — `app/services/whatsapp/embedded_signup_service.rb`, `app/services/whatsapp/token_validation_service.rb`, `spec/services/whatsapp/embedded_signup_service_spec.rb`, `spec/services/whatsapp/token_validation_service_spec.rb`
- `v4.14.2` `e6dfb91fc` refactor: use SafeFetch for website branding page fetch (#14693) — `app/services/website_branding_service.rb`
- … 10 more commits in this bucket; see local git range for full list.

### Conversation/sidebar/unread UX — 42 matching commits
- `v4.14.2` `a3ffb48a4` refactor(onboarding): use separate onboarding controller (#14507) — `app/controllers/api/v1/accounts/onboardings_controller.rb`, `app/controllers/api/v1/accounts_controller.rb`, `app/javascript/dashboard/api/onboarding.js`, `app/javascript/dashboard/composables/useAccount.js`, `app/javascript/dashboard/routes/dashboard/onboarding/Index.vue` …
- `v4.14.2` `1f6203d55` feat(onboarding): honor return_to hint in TikTok OAuth callback (#14569) — `app/controllers/api/v1/accounts/tiktok/authorizations_controller.rb`, `app/controllers/tiktok/callbacks_controller.rb`, `app/helpers/tiktok/integration_helper.rb`, `config/routes.rb`
- `v4.14.2` `4c6a345d6` feat(onboarding): honor return hint in email OAuth callback (#14567) — `app/controllers/api/v1/accounts/oauth_authorization_controller.rb`, `app/controllers/oauth_callback_controller.rb`
- `v4.14.2` `33dea8371` docs: document message attachment uploads (#14600) — `swagger/paths/application/conversation/messages/create.yml`, `swagger/swagger.json`, `swagger/tag_groups/application_swagger.json`
- `v4.14.2` `88e2661ca` feat(conversations): remove unread count feature flag (CW-7237) (#14610) — `app/controllers/api/v1/accounts/conversations/unread_counts_controller.rb`, `app/javascript/dashboard/components-next/sidebar/Sidebar.vue`, `app/javascript/dashboard/featureFlags.js`, `app/javascript/dashboard/helper/actionCable.js`, `app/javascript/dashboard/helper/specs/actionCable.spec.js` …
- `v4.14.2` `95cb3a7ad` feat(onboarding): honor return_to hint in Instagram OAuth callback (#14568) — `app/controllers/api/v1/accounts/instagram/authorizations_controller.rb`, `app/controllers/instagram/callbacks_controller.rb`, `app/helpers/instagram/integration_helper.rb`
- `v4.14.2` `37eed5de1` feat(whatsapp): Add support for voice messages (#14606) — `app/builders/messages/message_builder.rb`, `app/javascript/dashboard/api/inbox/message.js`, `app/javascript/dashboard/api/specs/inbox/message.spec.js`, `app/javascript/dashboard/components/widgets/AttachmentsPreview.vue`, `app/javascript/dashboard/components/widgets/WootWriter/AudioRecorder.vue` …
- `v4.14.2` `87df43bdd` revert: restore conversation unread count feature flag (#14623) — `app/controllers/api/v1/accounts/conversations/unread_counts_controller.rb`, `app/javascript/dashboard/components-next/sidebar/Sidebar.vue`, `app/javascript/dashboard/featureFlags.js`, `app/javascript/dashboard/helper/actionCable.js`, `app/javascript/dashboard/helper/specs/actionCable.spec.js` …
- `v4.14.2` `0a181b0ce` chore: Update translations (#14498) — `app/javascript/dashboard/i18n/locale/am/bulkActions.json`, `app/javascript/dashboard/i18n/locale/am/campaign.json`, `app/javascript/dashboard/i18n/locale/am/components.json`, `app/javascript/dashboard/i18n/locale/am/contact.json`, `app/javascript/dashboard/i18n/locale/am/conversation.json` …
- `v4.14.2` `b791d75b3` fix(microsoft): prevent OAuth admin consent loop (#13962) — `app/controllers/api/v1/accounts/microsoft/authorizations_controller.rb`, `spec/controllers/api/v1/accounts/microsoft/authorization_controller_spec.rb`
- `v4.14.2` `1beaa284c` feat: inline images in website and email channels (#14516) — `app/javascript/dashboard/components/widgets/WootWriter/Editor.vue`, `app/javascript/dashboard/constants/editor.js`, `app/javascript/dashboard/helper/editorHelper.js`, `app/javascript/dashboard/helper/specs/editorHelper.spec.js`, `app/javascript/dashboard/i18n/locale/en/conversation.json` …
- `v4.14.2` `8e42307bd` fix: improve email inbox IMAP and SMTP compatibility (#14589) — `app/mailers/conversation_reply_mailer_helper.rb`, `app/services/imap/base_fetch_email_service.rb`, `spec/mailers/conversation_reply_mailer_spec.rb`, `spec/services/imap/fetch_email_service_spec.rb`, `spec/services/imap/microsoft_fetch_email_service_spec.rb`
- `v4.14.2` `64c5aeebe` feat(help-center): support per-locale portal title, name & header (#14642) — `app/controllers/api/v1/accounts/portals_controller.rb`, `app/controllers/public/api/v1/portals_controller.rb`, `app/javascript/dashboard/components-next/HelpCenter/LocaleCard/LocaleCard.vue`, `app/javascript/dashboard/components-next/HelpCenter/Pages/LocalePage/LocaleContentDialog.vue`, `app/javascript/dashboard/components-next/HelpCenter/Pages/LocalePage/LocaleList.vue` …
- `v4.14.2` `ec43975f3` chore: use square avatars (#14656) — `app/javascript/dashboard/components-next/Companies/CompaniesCard/CompaniesCard.vue`, `app/javascript/dashboard/components-next/Companies/CompanyDetail/CompanyProfileCard.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsCard/ContactsCard.vue`, `app/javascript/dashboard/components-next/sidebar/SidebarProfileMenu.vue`, `app/javascript/dashboard/components/widgets/conversation/ConversationHeader.vue` …
- `v4.14.2` `f9385a31f` fix(api): allow agent bots to read conversations and manage labels (#14655) — `app/controllers/concerns/access_token_auth_helper.rb`
- `v4.14.2` `45f4b423a` fix: captain usage for BYOK OpenAI tasks (#14587) — `enterprise/app/services/captain/llm/translate_query_service.rb`, `enterprise/lib/captain/conversation_completion_service.rb`, `lib/captain/base_task_service.rb`, `lib/captain/csat_utility_analysis_service.rb`, `lib/captain/follow_up_service.rb` …
- `v4.14.2` `e919a2cef` feat: add contact filter for conversations (#14629) — `app/javascript/dashboard/components-next/NewConversation/helpers/composeConversationHelper.js`, `app/javascript/dashboard/components-next/filter/ConditionRow.vue`, `app/javascript/dashboard/components-next/filter/helper/filterHelper.js`, `app/javascript/dashboard/components-next/filter/helper/filterHelper.spec.js`, `app/javascript/dashboard/components-next/filter/inputs/SingleSelect.vue` …
- `v4.14.2` `d8656edc6` fix(facebook): Stop force tagging Messenger replies with MESSAGE_TAG/ACCOUNT_UPDATE (#14329) — `app/services/facebook/send_on_facebook_service.rb`, `spec/services/facebook/send_on_facebook_service_spec.rb`
- … 24 more commits in this bucket; see local git range for full list.

### Contacts/companies/media UX — 13 matching commits
- `v4.14.2` `1afcd36de` fix(contacts): align contact export permissions (#14601) — `app/javascript/dashboard/components-next/Contacts/ContactsHeader/components/ContactMoreActions.vue`, `app/policies/contact_policy.rb`, `enterprise/app/policies/enterprise/contact_policy.rb`, `spec/enterprise/policies/contact_policy_spec.rb`
- `v4.14.2` `3eed8905c` fix(facebook): render shared links as fallback attachments (#14554) — `app/builders/messages/facebook/message_builder.rb`, `app/javascript/dashboard/components-next/message/Message.vue`, `app/javascript/dashboard/components-next/message/bubbles/Fallback.vue`, `spec/builders/messages/facebook/message_builder_spec.rb`
- `v4.14.2` `33dea8371` docs: document message attachment uploads (#14600) — `swagger/paths/application/conversation/messages/create.yml`, `swagger/swagger.json`, `swagger/tag_groups/application_swagger.json`
- `v4.14.2` `37eed5de1` feat(whatsapp): Add support for voice messages (#14606) — `app/builders/messages/message_builder.rb`, `app/javascript/dashboard/api/inbox/message.js`, `app/javascript/dashboard/api/specs/inbox/message.spec.js`, `app/javascript/dashboard/components/widgets/AttachmentsPreview.vue`, `app/javascript/dashboard/components/widgets/WootWriter/AudioRecorder.vue` …
- `v4.14.2` `0a181b0ce` chore: Update translations (#14498) — `app/javascript/dashboard/i18n/locale/am/bulkActions.json`, `app/javascript/dashboard/i18n/locale/am/campaign.json`, `app/javascript/dashboard/i18n/locale/am/components.json`, `app/javascript/dashboard/i18n/locale/am/contact.json`, `app/javascript/dashboard/i18n/locale/am/conversation.json` …
- `v4.14.2` `ec43975f3` chore: use square avatars (#14656) — `app/javascript/dashboard/components-next/Companies/CompaniesCard/CompaniesCard.vue`, `app/javascript/dashboard/components-next/Companies/CompanyDetail/CompanyProfileCard.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsCard/ContactsCard.vue`, `app/javascript/dashboard/components-next/sidebar/SidebarProfileMenu.vue`, `app/javascript/dashboard/components/widgets/conversation/ConversationHeader.vue` …
- `v4.14.2` `9d808a18d` fix(drops): Resolve first_name for single-word contact and agent names (#13488) — `app/drops/contact_drop.rb`, `app/drops/user_drop.rb`, `spec/drops/contact_drop_spec.rb`, `spec/drops/user_drop_spec.rb`
- `v4.14.2` `e919a2cef` feat: add contact filter for conversations (#14629) — `app/javascript/dashboard/components-next/NewConversation/helpers/composeConversationHelper.js`, `app/javascript/dashboard/components-next/filter/ConditionRow.vue`, `app/javascript/dashboard/components-next/filter/helper/filterHelper.js`, `app/javascript/dashboard/components-next/filter/helper/filterHelper.spec.js`, `app/javascript/dashboard/components-next/filter/inputs/SingleSelect.vue` …
- `v4.15.0` `6d26e7930` fix(contacts): truncate inbound contact names (IMAP sender display names) (#14631) — `app/builders/contact_inbox_with_contact_builder.rb`, `app/models/application_record.rb`, `spec/builders/contact_inbox_with_contact_builder_spec.rb`
- `v4.15.0` `c041fde3a` fix: Preserve original filenames for WhatsApp cloud attachments (#14168) — `app/services/whatsapp/incoming_message_whatsapp_cloud_service.rb`, `spec/services/whatsapp/incoming_message_whatsapp_cloud_service_spec.rb`
- `v4.15.0` `e5c140158` fix(new-conversation): stop writing literal "undefined" as mail_subject (#14383) — `app/javascript/dashboard/store/modules/contactConversations.js`, `app/javascript/dashboard/store/modules/specs/contactConversations/actions.spec.js`
- `v4.15.0` `35bef21f8` feat: add media view for contacts (#14393) — `app/javascript/dashboard/api/contacts.js`, `app/javascript/dashboard/components-next/Contacts/ContactsDetailsLayout.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsSidebar/ContactCustomAttributes.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsSidebar/ContactHistory.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsSidebar/ContactMedia.vue` …
- `v4.15.0` `41a3ab6df` feat(companies): add contact company selector (#14496) — `app/controllers/api/v1/accounts/contacts_controller.rb`, `app/javascript/dashboard/components-next/Companies/CompanyCreateDialog.vue`, `app/javascript/dashboard/components-next/Companies/CompanySelector.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsCard/ContactsCard.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsForm/ContactsForm.vue` …

### Help Center/public portal UX — 29 matching commits
- `v4.14.2` `f27bbef73` feat: show processing status for one-off campaigns (#14592) — `app/javascript/dashboard/components-next/Campaigns/CampaignCard/CampaignCard.vue`, `app/javascript/dashboard/i18n/locale/en/campaign.json`, `app/models/campaign.rb`, `app/services/sms/oneoff_sms_campaign_service.rb`, `app/services/twilio/oneoff_sms_campaign_service.rb` …
- `v4.14.2` `88e2661ca` feat(conversations): remove unread count feature flag (CW-7237) (#14610) — `app/controllers/api/v1/accounts/conversations/unread_counts_controller.rb`, `app/javascript/dashboard/components-next/sidebar/Sidebar.vue`, `app/javascript/dashboard/featureFlags.js`, `app/javascript/dashboard/helper/actionCable.js`, `app/javascript/dashboard/helper/specs/actionCable.spec.js` …
- `v4.14.2` `ecd9c26c8` feat: Implemented search results page functionality  (#11086) — `app/controllers/public/api/v1/portals/search_controller.rb`, `app/helpers/portal_helper.rb`, `app/javascript/entrypoints/portal.js`, `app/javascript/portal/application.scss`, `app/javascript/portal/components/PublicArticleSearch.vue` …
- `v4.14.2` `37eed5de1` feat(whatsapp): Add support for voice messages (#14606) — `app/builders/messages/message_builder.rb`, `app/javascript/dashboard/api/inbox/message.js`, `app/javascript/dashboard/api/specs/inbox/message.spec.js`, `app/javascript/dashboard/components/widgets/AttachmentsPreview.vue`, `app/javascript/dashboard/components/widgets/WootWriter/AudioRecorder.vue` …
- `v4.14.2` `28f87d2fc` fix(widget): translate zh_CN availability keys (#14288) — `app/javascript/widget/i18n/locale/zh_CN.json`
- `v4.14.2` `87df43bdd` revert: restore conversation unread count feature flag (#14623) — `app/controllers/api/v1/accounts/conversations/unread_counts_controller.rb`, `app/javascript/dashboard/components-next/sidebar/Sidebar.vue`, `app/javascript/dashboard/featureFlags.js`, `app/javascript/dashboard/helper/actionCable.js`, `app/javascript/dashboard/helper/specs/actionCable.spec.js` …
- `v4.14.2` `0a181b0ce` chore: Update translations (#14498) — `app/javascript/dashboard/i18n/locale/am/bulkActions.json`, `app/javascript/dashboard/i18n/locale/am/campaign.json`, `app/javascript/dashboard/i18n/locale/am/components.json`, `app/javascript/dashboard/i18n/locale/am/contact.json`, `app/javascript/dashboard/i18n/locale/am/conversation.json` …
- `v4.14.2` `0d59fb445` fix: validate portal color format (#14632) — `app/models/portal.rb`
- `v4.14.2` `1beaa284c` feat: inline images in website and email channels (#14516) — `app/javascript/dashboard/components/widgets/WootWriter/Editor.vue`, `app/javascript/dashboard/constants/editor.js`, `app/javascript/dashboard/helper/editorHelper.js`, `app/javascript/dashboard/helper/specs/editorHelper.spec.js`, `app/javascript/dashboard/i18n/locale/en/conversation.json` …
- `v4.14.2` `de8939103` fix: use hang-up handset icon for reject/end call button (#14640) — `app/javascript/dashboard/components-next/call/CallCard.vue`
- `v4.14.2` `ea910227a` feat: add Voice Calls feature card to settings showcase (#14635) — `app/helpers/super_admin/features.yml`, `app/views/super_admin/application/_icons.html.erb`
- `v4.14.2` `18ef019cd` fix: improve article editor typography & nested lists (#14572) — `app/javascript/dashboard/components/widgets/WootWriter/Editor.vue`
- `v4.14.2` `64c5aeebe` feat(help-center): support per-locale portal title, name & header (#14642) — `app/controllers/api/v1/accounts/portals_controller.rb`, `app/controllers/public/api/v1/portals_controller.rb`, `app/javascript/dashboard/components-next/HelpCenter/LocaleCard/LocaleCard.vue`, `app/javascript/dashboard/components-next/HelpCenter/Pages/LocalePage/LocaleContentDialog.vue`, `app/javascript/dashboard/components-next/HelpCenter/Pages/LocalePage/LocaleList.vue` …
- `v4.14.2` `e919a2cef` feat: add contact filter for conversations (#14629) — `app/javascript/dashboard/components-next/NewConversation/helpers/composeConversationHelper.js`, `app/javascript/dashboard/components-next/filter/ConditionRow.vue`, `app/javascript/dashboard/components-next/filter/helper/filterHelper.js`, `app/javascript/dashboard/components-next/filter/helper/filterHelper.spec.js`, `app/javascript/dashboard/components-next/filter/inputs/SingleSelect.vue` …
- `v4.14.2` `d9c07fe2e` feat: expose onboarding help center generation status (#14671) — `app/controllers/api/v1/accounts/onboardings_controller.rb`, `app/javascript/dashboard/api/onboarding.js`, `app/views/api/v1/models/_account.json.jbuilder`, `config/routes.rb`, `enterprise/app/controllers/enterprise/api/v1/accounts/onboardings_controller.rb` …
- `v4.15.0` `940428c10` fix: preserve markdown links with unsafe href characters in help center content (#14686) — `package.json`, `pnpm-lock.yaml`
- `v4.15.0` `8d5d02ea9` feat: add per-inbox toggle to disable incoming calls (#14645) — `app/javascript/dashboard/api/inboxes.js`, `app/javascript/dashboard/i18n/locale/en/inboxMgmt.json`, `app/javascript/dashboard/routes/dashboard/settings/inbox/settingsPage/VoiceConfigurationPage.vue`, `app/javascript/dashboard/routes/dashboard/settings/inbox/settingsPage/WhatsappCallingPage.vue`, `app/models/channel/twilio_sms.rb` …
- `v4.15.0` `92a1fb8ab` feat: manage active user sessions from profile (CW-7169) (#14556) — `app/controllers/api/v1/profile/sessions_controller.rb`, `app/controllers/application_controller.rb`, `app/controllers/concerns/track_session_activity.rb`, `app/controllers/devise_overrides/sessions_controller.rb`, `app/javascript/dashboard/api/auth.js` …
- … 11 more commits in this bucket; see local git range for full list.

### Email/IMAP reliability — 10 matching commits
- `v4.14.2` `ed3059c1a` docs: Document API inbox webhook URL (#14593) — `swagger/definitions/index.yml`, `swagger/definitions/request/inbox/channels/create_api_channel_payload.yml`, `swagger/definitions/request/inbox/channels/create_email_channel_payload.yml`, `swagger/definitions/request/inbox/channels/create_line_channel_payload.yml`, `swagger/definitions/request/inbox/channels/create_sms_channel_payload.yml` …
- `v4.14.2` `04ac9d378` fix: use UPN for `imap_login` on Microsoft OAuth callback (#14522) — `app/controllers/microsoft/callbacks_controller.rb`, `app/controllers/oauth_callback_controller.rb`, `spec/controllers/microsoft/callbacks_controller_spec.rb`
- `v4.14.2` `4c6a345d6` feat(onboarding): honor return hint in email OAuth callback (#14567) — `app/controllers/api/v1/accounts/oauth_authorization_controller.rb`, `app/controllers/oauth_callback_controller.rb`
- `v4.14.2` `1beaa284c` feat: inline images in website and email channels (#14516) — `app/javascript/dashboard/components/widgets/WootWriter/Editor.vue`, `app/javascript/dashboard/constants/editor.js`, `app/javascript/dashboard/helper/editorHelper.js`, `app/javascript/dashboard/helper/specs/editorHelper.spec.js`, `app/javascript/dashboard/i18n/locale/en/conversation.json` …
- `v4.14.2` `8e42307bd` fix: improve email inbox IMAP and SMTP compatibility (#14589) — `app/mailers/conversation_reply_mailer_helper.rb`, `app/services/imap/base_fetch_email_service.rb`, `spec/mailers/conversation_reply_mailer_spec.rb`, `spec/services/imap/fetch_email_service_spec.rb`, `spec/services/imap/microsoft_fetch_email_service_spec.rb`
- `v4.14.2` `d1c482cb6` fix(email): strip null bytes from inbound mailbox messages (#14546) — `app/mailboxes/imap/imap_mailbox.rb`, `app/mailboxes/mailbox_helper.rb`, `app/mailboxes/mailbox_sanitizer.rb`, `app/services/mailbox/conversation_finder_strategies/base_strategy.rb`, `app/services/mailbox/conversation_finder_strategies/in_reply_to_strategy.rb` …
- `v4.15.0` `6d26e7930` fix(contacts): truncate inbound contact names (IMAP sender display names) (#14631) — `app/builders/contact_inbox_with_contact_builder.rb`, `app/models/application_record.rb`, `spec/builders/contact_inbox_with_contact_builder_spec.rb`
- `v4.15.0` `006b52991` chore(deps): bump net-imap from 0.4.24 to 0.6.4.1 (#14688) — `Gemfile.lock`
- `v4.15.0` `ee6382109` feat: prevent deleted email conversations from syncing again (#14612) — `app/controllers/api/v1/accounts/conversations_controller.rb`, `app/services/conversations/delete_service.rb`, `app/services/imap/base_fetch_email_service.rb`, `app/services/imap/deleted_message_tracker.rb`, `lib/redis/redis_keys.rb` …
- `v4.15.0` `cf6ee1366` feat: scale email rate limits by agent count for paid plans (#13966) — `enterprise/app/models/enterprise/account/plan_usage_and_limits.rb`

### Editor/message rendering UX — 20 matching commits
- `v4.14.2` `3eed8905c` fix(facebook): render shared links as fallback attachments (#14554) — `app/builders/messages/facebook/message_builder.rb`, `app/javascript/dashboard/components-next/message/Message.vue`, `app/javascript/dashboard/components-next/message/bubbles/Fallback.vue`, `spec/builders/messages/facebook/message_builder_spec.rb`
- `v4.14.2` `33dea8371` docs: document message attachment uploads (#14600) — `swagger/paths/application/conversation/messages/create.yml`, `swagger/swagger.json`, `swagger/tag_groups/application_swagger.json`
- `v4.14.2` `37eed5de1` feat(whatsapp): Add support for voice messages (#14606) — `app/builders/messages/message_builder.rb`, `app/javascript/dashboard/api/inbox/message.js`, `app/javascript/dashboard/api/specs/inbox/message.spec.js`, `app/javascript/dashboard/components/widgets/AttachmentsPreview.vue`, `app/javascript/dashboard/components/widgets/WootWriter/AudioRecorder.vue` …
- `v4.14.2` `36a05097f` fix(webhooks): strip trailing newlines from webhook message content (#14272) — `app/services/messages/webhook_content_normalizer.rb`, `spec/services/messages/webhook_content_normalizer_spec.rb`
- `v4.14.2` `7acbe8b3f` fix(whatsapp): truncate location fallback_title to 255 chars to avoid silent message drop (#14517) — `app/services/whatsapp/incoming_message_base_service.rb`, `spec/services/whatsapp/incoming_message_service_spec.rb`
- `v4.14.2` `d028cc198` fix: prevent list marker overflow in messages (#14618) — `app/javascript/widget/assets/scss/woot.scss`, `tailwind.config.js`
- `v4.14.2` `1beaa284c` feat: inline images in website and email channels (#14516) — `app/javascript/dashboard/components/widgets/WootWriter/Editor.vue`, `app/javascript/dashboard/constants/editor.js`, `app/javascript/dashboard/helper/editorHelper.js`, `app/javascript/dashboard/helper/specs/editorHelper.spec.js`, `app/javascript/dashboard/i18n/locale/en/conversation.json` …
- `v4.14.2` `18ef019cd` fix: improve article editor typography & nested lists (#14572) — `app/javascript/dashboard/components/widgets/WootWriter/Editor.vue`
- `v4.14.2` `d8656edc6` fix(facebook): Stop force tagging Messenger replies with MESSAGE_TAG/ACCOUNT_UPDATE (#14329) — `app/services/facebook/send_on_facebook_service.rb`, `spec/services/facebook/send_on_facebook_service_spec.rb`
- `v4.14.2` `d1c482cb6` fix(email): strip null bytes from inbound mailbox messages (#14546) — `app/mailboxes/imap/imap_mailbox.rb`, `app/mailboxes/mailbox_helper.rb`, `app/mailboxes/mailbox_sanitizer.rb`, `app/services/mailbox/conversation_finder_strategies/base_strategy.rb`, `app/services/mailbox/conversation_finder_strategies/in_reply_to_strategy.rb` …
- `v4.14.2` `59d869d1e` feat: Ability to resize table column width (#14611) — `app/javascript/shared/helpers/MessageFormatter.js`, `app/javascript/shared/helpers/specs/MessageFormatter.spec.js`, `lib/custom_markdown_renderer.rb`, `package.json`, `pnpm-lock.yaml` …
- `v4.15.0` `c6e5657ee` fix(call): emit assignee activity message when agent answers a call (#14700) — `enterprise/app/services/whatsapp/call_service.rb`
- `v4.15.0` `940428c10` fix: preserve markdown links with unsafe href characters in help center content (#14686) — `package.json`, `pnpm-lock.yaml`
- `v4.15.0` `d0d275d96` fix: cannot resize pasted images (#14709) — `package.json`, `pnpm-lock.yaml`
- `v4.15.0` `c041fde3a` fix: Preserve original filenames for WhatsApp cloud attachments (#14168) — `app/services/whatsapp/incoming_message_whatsapp_cloud_service.rb`, `spec/services/whatsapp/incoming_message_whatsapp_cloud_service_spec.rb`
- `v4.15.0` `35bef21f8` feat: add media view for contacts (#14393) — `app/javascript/dashboard/api/contacts.js`, `app/javascript/dashboard/components-next/Contacts/ContactsDetailsLayout.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsSidebar/ContactCustomAttributes.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsSidebar/ContactHistory.vue`, `app/javascript/dashboard/components-next/Contacts/ContactsSidebar/ContactMedia.vue` …
- `v4.15.0` `ee6382109` feat: prevent deleted email conversations from syncing again (#14612) — `app/controllers/api/v1/accounts/conversations_controller.rb`, `app/services/conversations/delete_service.rb`, `app/services/imap/base_fetch_email_service.rb`, `app/services/imap/deleted_message_tracker.rb`, `lib/redis/redis_keys.rb` …
- `v4.15.0` `1713cabdf` feat: Add emoji & icon picker for Help Center categories (#14702) — `app/controllers/api/v1/accounts/categories_controller.rb`, `app/helpers/portal_helper.rb`, `app/javascript/dashboard/components-next/HelpCenter/ArticleCard/ArticleCard.vue`, `app/javascript/dashboard/components-next/HelpCenter/CategoryCard/CategoryCard.vue`, `app/javascript/dashboard/components-next/HelpCenter/Pages/ArticleEditorPage/ArticleEditorControls.vue` …
- … 2 more commits in this bucket; see local git range for full list.

### Captain/AI/API tooling — 7 matching commits
- `v4.14.2` `170b64d1f` chore: upgrade to vite 6 (#14363) — `Gemfile.lock`, `app/javascript/dashboard/composables/spec/index.spec.js`, `app/javascript/dashboard/composables/spec/useCaptain.spec.js`, `package.json`, `pnpm-lock.yaml` …
- `v4.14.2` `eaffad12e` feat(langfuse): propagate observation metadata for evals (#14634) — `enterprise/app/helpers/captain/chat_generation_recorder.rb`, `lib/captain/tool_instrumentation.rb`, `lib/integrations/llm_instrumentation.rb`, `lib/integrations/llm_instrumentation_completion_helpers.rb`, `lib/integrations/llm_instrumentation_constants.rb` …
- `v4.14.2` `cd9192f7d` chore(captain): update Firecrawl to use the v2 API (#14624) — `enterprise/app/services/captain/tools/firecrawl_service.rb`, `spec/enterprise/services/captain/tools/firecrawl_service_spec.rb`
- `v4.14.2` `f9385a31f` fix(api): allow agent bots to read conversations and manage labels (#14655) — `app/controllers/concerns/access_token_auth_helper.rb`
- `v4.14.2` `45f4b423a` fix: captain usage for BYOK OpenAI tasks (#14587) — `enterprise/app/services/captain/llm/translate_query_service.rb`, `enterprise/lib/captain/conversation_completion_service.rb`, `lib/captain/base_task_service.rb`, `lib/captain/csat_utility_analysis_service.rb`, `lib/captain/follow_up_service.rb` …
- `v4.14.2` `af1dfc21f` fix: include account data in webhook payloads (#12445) — `app/listeners/webhook_listener.rb`, `app/presenters/conversations/event_data_presenter.rb`, `app/presenters/inbox/event_data_presenter.rb`, `spec/listeners/agent_bot_listener_spec.rb`, `spec/listeners/webhook_listener_spec.rb` …
- `v4.14.2` `3dfb5061e` refactor: route captain custom tool requests through SafeFetch (#14620) — `enterprise/app/controllers/api/v1/accounts/captain/custom_tools_controller.rb`, `enterprise/lib/captain/tools/http_tool.rb`

### Other — 5 matching commits
- `v4.14.2` `9d591b8f4` feat: enable companies for Business cloud plans (#14598) — `enterprise/app/services/enterprise/billing/reconcile_plan_features_service.rb`
- `v4.14.2` `bec795f76` Bump version to 4.14.2 — `VERSION_CW`, `config/app.yml`, `package.json`
- `v4.15.0` `2663a8495` refactor(security): rename path_without_extensions in Rack::Attack (#14216) — `config/initializers/rack_attack.rb`
- `v4.15.0` `a58585369` chore: expose advanced_search flag in super_admin UI for self-hosted (#14750) — `config/features.yml`
- `v4.15.0` `124782938` Bump version to 4.15.0 — `VERSION_CW`, `config/app.yml`, `package.json`

## 5. Meta inbox integration plan in detail

### 5.1 Facebook Messenger

- **Take** Messenger send policy fix (`d8656edc6`): default `messaging_type: RESPONSE`; use `HUMAN_AGENT` tag only behind explicit env/config. This directly reduces failed sends and Meta policy risk.
- **Take/adapt** OAuth scope split (`c6a38e2fc`): Facebook Page setup must not ask Instagram scopes unless the flow is actually Instagram-linked. OneLink currently hardcodes Instagram scopes in `Facebook.vue` and `Reauthorize.vue`.
- **Adapt** shared-link fallback UI (`3eed8905c`): backend is partially ahead, but the user experience is incomplete without a fallback link bubble.
- **Do not mix** these with Instagram channel creation. Facebook Page connect, Instagram Business Login, and WhatsApp Embedded Signup need separate scope/config matrices.

### 5.2 Instagram

- **Take/adapt** mutex exhaustion handling (`73ba0b26e`): Instagram webhook events should not disappear after lock retries. Keep it job-specific and idempotent.
- **Scope nuance**: Instagram reauth may need Instagram scopes only when the inbox has Instagram linkage. Messenger-only reauth should not request them.
- **Verification**: event job lock-conflict spec, channel reauth scope helper spec, and a negative spec proving Messenger scope excludes `instagram_basic`/`instagram_manage_messages`.

### 5.3 WhatsApp Cloud / Embedded Signup

- **Take/adapt** obsolete WABA scope validator removal (`f93f2067b`): OneLink still hard-fails through `Whatsapp::TokenValidationService`; this can break valid Meta Embedded Signup/reauth. Preserve `TokenInspectionService` as non-blocking diagnostics.
- **Take/adapt** `calls` webhook subscription gating (`e055cead3`): OneLink currently includes `calls` by default in `WEBHOOK_DEFAULT_FIELDS`; upstream moved to conditional subscription. In OneLink this must be keyed to `whatsapp_call`/`calling_enabled`, not upstream `channel_voice` alone.
- **Take/adapt** Cloud media fixes: original filename (`c041fde3a`), location fallback truncation (`7acbe8b3f`), CTWA referral metadata (`de137e829`). These protect real lead attribution and silent-drop cases.
- **Defer/adapt** outgoing voice notes (`37eed5de1` + `33f755052`): useful UX, but separate from OneLink call/telephony voice. Restrict conversion to official WhatsApp Cloud inboxes.
- **Do not copy wholesale** `Channel::Whatsapp` from upstream because OneLink has custom `whatsapp_call`, media server callbacks, phone info, and reauthorization behavior.

### 5.4 Official Meta documentation revalidation gate

This subsection is mandatory before implementing any Facebook, Instagram, or WhatsApp adoption item. Upstream Chatwoot is useful evidence, but Meta channel behavior must be accepted only when it matches current official Meta documentation or a captured live Meta payload.

For the dedicated OneLink project upgrade path to Meta Graph/API v25.0, see [`onelink-meta-graph-api-v25-upgrade-plan.md`](./onelink-meta-graph-api-v25-upgrade-plan.md).

#### Official source registry used in this pass

- Facebook/Messenger permissions: `https://developers.facebook.com/docs/development/create-an-app/use-cases-permission-mapping/`
- Messenger/Instagram messaging policy: `https://developers.facebook.com/documentation/business-messaging/messenger-platform/policy`
- Messenger Send API reference: `https://developers.facebook.com/documentation/business-messaging/messenger-platform/reference/send-api/`
- Instagram Messaging overview: `https://developers.facebook.com/documentation/business-messaging/instagram-messaging/overview/`
- Instagram Platform overview: `https://developers.facebook.com/docs/instagram-platform/overview`
- Instagram Messaging webhooks: `https://developers.facebook.com/documentation/business-messaging/instagram-messaging/webhooks`
- WhatsApp Embedded Signup overview: `https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/overview/`
- WhatsApp Webhooks overview: `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview`
- WhatsApp incoming payload schema: `https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/webhooks/whatsapp-incoming-webhook-payload`
- WhatsApp messages webhook reference: `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages`
- WhatsApp `smb_message_echoes` reference: `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/smb_message_echoes/`
- WhatsApp Business App / Coexistence onboarding: `https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/onboarding-business-app-users/`
- WhatsApp history webhook reference: `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/history/`
- WhatsApp Cloud Calling overview: `https://developers.facebook.com/documentation/business-messaging/whatsapp/calling/`
- WhatsApp business-initiated calls: `https://developers.facebook.com/docs/whatsapp/cloud-api/calling/business-initiated-calls/`
- WhatsApp Media API: `https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/media/media-api`
- WhatsApp image/document/audio/video webhook refs:
  - `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/image/`
  - `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/document/`
  - `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/audio/`
  - `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/video/`
- WhatsApp audio/voice messages: `https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/audio-messages/`
- WhatsApp location request messages: `https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/location-request-messages`
- WhatsApp Click-to-WhatsApp ads: `https://developers.facebook.com/docs/marketing-api/ad-creative/messaging-ads/click-to-whatsapp/`
- WhatsApp CTWA welcome message sequences: `https://developers.facebook.com/documentation/business-messaging/whatsapp/ctwa/welcome-message-sequences/`

#### Meta-doc verdict matrix for upstream Meta-related items

1. **Facebook/Messenger OAuth scopes — `c6a38e2fc` — `TAKE/ADAPT`, docs-confirmed.**
   - Official permission mapping says Messenger use case requires Page/Messenger permissions and lists `instagram_basic` / `instagram_manage_messages` as optional, not required for Messenger-only setup.
   - OneLink currently hardcodes Instagram scopes in `Facebook.vue` and `facebook/Reauthorize.vue`.
   - Implementation rule: default Messenger setup must request only Page/Messenger scopes. Add Instagram scopes only when the flow is explicitly Instagram-linked, e.g. existing Facebook inbox has `instagram_id` or a dedicated Instagram setup path requests them.
   - Do not treat this as removal of Instagram support. It is scope separation.

2. **Facebook Messenger outbound `MESSAGE_TAG` / `ACCOUNT_UPDATE` — `d8656edc6` — `TAKE`, docs-confirmed.**
   - Official Messenger policy states standard messaging has a 24-hour response window and message tags are limited to approved use cases outside that window; misuse can restrict messaging ability.
   - OneLink currently sends normal text and attachment replies with `messaging_type: MESSAGE_TAG` and fallback `tag: ACCOUNT_UPDATE` when Human Agent is not enabled.
   - Implementation rule: default replies should use `messaging_type: RESPONSE` or omit tag per current Send API behavior; only attach `MESSAGE_TAG` + `HUMAN_AGENT` when the feature/permission is explicitly enabled.
   - This is provider-policy hardening, not a UX preference.

3. **Instagram webhook subscriptions/scopes — `REVIEW`, docs-confirmed baseline, not necessarily an upstream diff.**
   - Official Instagram Messaging docs require `instagram_basic`, `instagram_manage_messages`, and `pages_manage_metadata` for webhooks; overview also calls out Facebook Login for Business when Instagram is linked to a Facebook Page.
   - OneLink `Channel::Instagram#subscribe` currently subscribes `messages`, `message_reactions`, and `messaging_seen` through `graph.instagram.com`.
   - Official webhooks also list `messaging_postbacks`, `messaging_referral`, and `standby`. Do not add them blindly; add only if OneLink supports icebreakers/generic-template postbacks, referral links, or handover. If added, include inbound parser specs.
   - Keep Instagram setup separate from Facebook Messenger scope minimization.

4. **WhatsApp Embedded Signup WABA granular-scope hard fail — `f93f2067b` — `ADAPT`, docs-compatible but not a permission removal.**
   - Official Embedded Signup docs require `whatsapp_business_management` and `whatsapp_business_messaging` for the Cloud API flow and describe customer onboarding/token grant, but they do not require a local `debug_token.granular_scopes[target_ids]` hard check before using the WABA.
   - OneLink currently calls `Whatsapp::TokenValidationService` after exchanging the code and before channel creation. That validator hard-codes WABA target-id validation and can reject otherwise functional Embedded Signup tokens.
   - Implementation rule: remove the brittle blocking `debug_token` WABA-scope check, but keep functional Graph validation: exact `phone_number_id`, `PhoneInfoService`/`/{waba_id}/phone_numbers` access, webhook setup, and sanitized token-inspection diagnostics. Missing required Meta permissions must still fail through real Graph API calls.
   - Do not delete OneLink `TokenInspectionService` diagnostics wholesale.

5. **WhatsApp webhook fields: `messages`, `smb_message_echoes`, `calls` — `e055cead3` plus OneLink Coexistence nuance — `ADAPT`, docs-confirmed with conditions.**
   - Official WhatsApp Webhooks overview says `whatsapp_business_messaging` is required for `messages`; `whatsapp_business_management` is required for other webhook types.
   - Official Calling docs explicitly require subscribing to the `calls` webhook field for Cloud API Calling, unless using SIP-specific flow.
   - Official `smb_message_echoes` docs say this field is for WABAs onboarded to Cloud API via a solution provider where the business also uses the WhatsApp Business App or companion devices. Coexistence history sync additionally uses `history` webhooks.
   - OneLink currently has `WEBHOOK_DEFAULT_FIELDS = %w[messages smb_message_echoes calls]` for every WhatsApp Cloud setup.
   - Implementation rule: `calls` must be conditional on OneLink voice/calling being actually enabled and approved. `smb_message_echoes` must remain only if OneLink's official Cloud/Business App coexistence contract is active; otherwise it should be conditionally gated or at minimum kept with a documented app-permission expectation. Do not remove `smb_message_echoes` blindly because OneLink has partial coexistence support, but do not treat it as a universal WhatsApp field either.

6. **WhatsApp CTWA/referral metadata — `de137e829` — `TAKE/ADAPT`, docs-confirmed.**
   - Official WhatsApp incoming payload and image/document/audio/video webhook references include a `referral` object for messages originating from Click-to-WhatsApp ads.
   - Official fields include `source_url`, `source_id`, `source_type`, `body`, `headline`, `media_type`, `image_url`, `video_url`, `thumbnail_url`, `ctwa_clid`, and optional `welcome_message` data. The docs say `ctwa_clid` is omitted for messages not originating from CTWA ads.
   - OneLink currently does not merge `message[:referral]` into WhatsApp `message.content_attributes`.
   - Implementation rule: store referral metadata on the exact incoming message as `content_attributes[:referral]`, not as a global conversation truth. This preserves Meta semantics and gives MacroCRM/Captain/analytics a reliable lead-attribution source. For Twilio WhatsApp, normalize Twilio `Referral*` fields into the same shape only for WhatsApp channels.

7. **WhatsApp media filenames — `c041fde3a` — `ADAPT`, docs-confirmed only for document filename; type-aware implementation required.**
   - Official Media API returns metadata such as `mime_type`, `sha256`, `file_size`, `id`, and temporary `url`.
   - Official document webhook reference includes `document.filename`.
   - Official image/audio/video webhook references include `caption`, `mime_type`, `sha256`, `id`, `url`, but not a general `filename` field.
   - Implementation rule: preserve `document.filename` when present. For image/audio/video, derive safe display filenames from media id/MIME/caption only if needed; do not assume Meta provides original filenames. Sanitize filenames and never use them as paths.

8. **WhatsApp location fallback truncation — `7acbe8b3f` — `TAKE`, defensive and docs-compatible.**
   - Official location webhook payload can contain optional `name` and `address`; docs do not guarantee their length.
   - OneLink currently concatenates `name, address` into `fallback_title` without truncation.
   - Implementation rule: truncate to `ApplicationRecord::MAX_STRING_COLUMN_LENGTH` / attachment column limit. This is a database safety guard, not a Meta business-rule change.

9. **WhatsApp Cloud voice notes — `37eed5de1` and related frontend audio conversion — `ADAPT`, docs-confirmed but separate from Calling API.**
   - Official WhatsApp audio messages docs distinguish voice messages from basic audio. Voice messages require `.ogg` encoded with OPUS and can be sent with `audio.voice: true`.
   - This is not the same feature as WhatsApp Cloud Calling / `calls` webhook.
   - Implementation rule: only convert/send `.ogg` OPUS with `voice: true` for official WhatsApp Cloud audio-message flow. Do not route this through OneLink telephony/call subsystem and do not affect WhatsApp Web/Evolution media behavior.

10. **Instagram/Messenger/WhatsApp referral surfaces — `DEFER UI`, docs-confirmed cross-channel need.**
    - Instagram docs also define ad/product/referral payloads for Instagram Messaging. Messenger has separate referral/postback mechanics.
    - Upstream WhatsApp stores CTWA referral but defers UI. OneLink should do the same unless product asks for a cross-channel ad-attribution UI.
    - Implementation rule: store provider-native attribution now; design one UI surface later across WhatsApp, Instagram, Messenger, TikTok instead of a WhatsApp-only sidebar block.

#### Implementation gate for Meta code changes

Before any Meta-related code patch, require all of the following:

1. Identify exact provider and channel type: `Channel::Whatsapp` official Cloud vs WhatsApp Web/Evolution, `Channel::FacebookPage`, or `Channel::Instagram`.
2. Link the change to one official Meta URL above and one upstream commit/diff.
3. State whether the Meta docs **confirm**, **confirm with conditions**, or **do not confirm** the upstream behavior.
4. Add provider-specific regression specs; do not rely on broad channel tests.
5. For ambiguous payload fields, require a sanitized live/raw webhook fixture before implementing business logic.
6. Never print or persist tokens, app secrets, user IDs, page IDs, phone IDs, or WABA IDs in docs/logs beyond sanitized presence/state.

## 6. UI/UX improvements to improve operator experience

### 6.1 High-confidence UX improvements

1. **Contact media/files tab** (`35bef21f8`) — real operator value: find all media for a contact without opening every conversation. Needs backend permission filter and frontend store completion.
2. **Company selector in contact form** (`41a3ab6df`) — aligns UX with native `Company` entity instead of free-text company strings. Important for CRM/Scheduling data quality.
3. **Facebook shared-link fallback bubble** (`3eed8905c`) — avoids broken-looking media bubbles for shared posts/links.
4. **Help Center search/per-locale branding/icon picker** (`ecd9c26c8`, `64c5aeebe`, `1713cabdf`, `dda25c0b5`) — useful if public help center is active. Preserve OneLink `ru` default and branding rules.
5. **Inline image/editor fixes** (`1beaa284c`, `18ef019cd`, `d0d275d96`) — improves composer/editor quality, but WootWriter is broad and should be reviewed by frontend owner.

### 6.2 UX improvements to defer until measured

- **Conversation unread Redis cache/filter counters/sidebar ordering** — valuable for large accounts, but touches many models/listeners/enterprise permissions. First compare current `SidebarUnreadCountService` accuracy and performance on high-volume accounts.
- **Active sessions login picker** — good product UX, but conflicts with OneLink active-auth model. Needs design before adoption.
- **Onboarding website-branding/OAuth return hints** — useful but not first wave unless onboarding funnel is actively used.

## 7. Backend/security fixes beyond Meta

- **Integration secrets redaction** is the most urgent non-Meta security fix. OneLink has visible_properties config but the view does not enforce it; this is a classic “we had the field but not the guard” bug. Tiny fix, high risk reduction. Да, я тоже нервно моргнул, потому что это ровно тот вид багов, который выглядит как UI convenience until it leaks a token.
- **Session cookie flags** are tiny and should be taken early.
- **Email deleted tracker / IMAP compatibility** should be promoted to P0 if production uses IMAP inboxes. If not, keep P1.
- **Webhook content newline normalizer** (`36a05097f`) is low-risk if OneLink still has raw webhook message content issues; check before implementation.
- **Agent bot conversation/label access** (`f9385a31f`) appears likely present/equivalent in OneLink Captain/access model; verify only if bot API failures appear.

## 8. Explicit no-wholesale-copy list

- `app/models/channel/whatsapp.rb` — OneLink voice/call/media-server behavior diverges.
- `app/services/whatsapp/*` as whole files — hand-merge specific methods; preserve identity resolver, inbox-scoped dedup, unsupported placeholders, and reauth behavior.
- `app/controllers/devise_overrides/sessions_controller.rb` and auth concerns — OneLink active-auth differs.
- `enterprise/lib/captain/tools/http_tool.rb` and Firecrawl service — OneLink Captain executor/runtime is more advanced.
- Bulk `app/javascript/dashboard/i18n/locale/**` — add only keys for adopted UI in `en`, `ru`, `kk` as needed.
- Full unread Redis module without design — it is not a patch; it is a runtime cache architecture change.
- Reference dirty `SidebarGroupLeaf.vue` local tweak — not release evidence.

## 9. Suggested implementation waves

### Wave 1: narrow backend/integration branch

1. Integration secret redaction.
2. Session cookie flags.
3. Facebook Messenger send policy.
4. Facebook/Messenger OAuth scope split.
5. WhatsApp Embedded Signup WABA validator hard-fail removal, preserving diagnostics.
6. WhatsApp webhook `calls` field gating.
7. WhatsApp media filename + location truncation + CTWA referral metadata.
8. Instagram mutex exhaustion handling.
9. Contact inbound name truncation.

Wave 1 verification:

- Ruby syntax for touched services/controllers/jobs.
- Targeted RSpec: integrations hook JSON, session store spec, Facebook send service, WhatsApp embedded signup, webhook setup/client, incoming WhatsApp Cloud service, Instagram events/mutex, contact builder.
- Targeted frontend tests/lint for scope helper if OAuth scope split touches Vue/JS.

### Wave 2: operator UX branch

1. Contact media/files tab with backend permission specs.
2. Company selector in contact form with enterprise controller and contact JSON support.
3. Facebook fallback attachment bubble.
4. Optional WhatsApp voice-note UX if product wants official Cloud voice notes.

Wave 2 verification:

- Contact attachments request specs, company association specs, frontend store/component tests, targeted ESLint.
- Manual UI smoke for contact sidebar/form if implemented.

### Wave 3: architecture/performance branch

1. Unread Redis cache/filter counters/sidebar ordering, only after performance/accuracy measurement.
2. Help Center module if public Help Center is active.
3. Active sessions if OneLink auth design is reconciled.
4. Vite 6/toolchain upgrade as a separate frontend infra migration.

## 10. Open questions before code implementation

1. Are production IMAP/email inboxes actively used? If yes, promote deleted-message tracker and net-imap bump.
2. Do we want official WhatsApp Cloud outgoing voice notes now, or only call/telephony voice?
3. Should contact `company_id` become the source of truth with legacy `additionalAttributes.companyName` fallback?
4. Is public Help Center active for customers?
5. Are sidebar unread counts slow/wrong on account 8 or other high-volume workspaces? Measure before taking Redis cache module.
6. Which Meta app permissions are currently approved in production? This decides exact Facebook/Instagram scope defaults.

## 11. Next concrete action

Create a small Wave 1 branch and implement P0 items path-by-path. For Facebook/Instagram/WhatsApp items, first pass the Meta official-doc gate in section 5.4: each patch must cite the official Meta URL, the upstream commit, OneLink file evidence, and provider-specific regression specs. Do not merge `v4.15.0` wholesale. After each P0 item, run its targeted spec before moving to the next item; this keeps provider/API regressions localized.

## Appendix A. High-signal local file status

### Meta WhatsApp Embedded Signup: remove obsolete WABA granular-scope hard fail
  - `app/services/whatsapp/embedded_signup_service.rb` — `diverged`
  - `app/services/whatsapp/token_validation_service.rb` — `onelink_only_or_deleted_upstream`
  - `app/services/whatsapp/token_inspection_service.rb` — `onelink_only_or_deleted_upstream`

### Facebook/Messenger OAuth scopes: do not request Instagram scopes in Messenger-only flow
  - `app/javascript/dashboard/routes/dashboard/settings/inbox/channels/Facebook.vue` — `diverged`
  - `app/javascript/dashboard/routes/dashboard/settings/inbox/facebook/Reauthorize.vue` — `diverged`
  - `app/javascript/dashboard/helper/facebookScopes.js` — `missing_in_onelink`
  - `app/javascript/dashboard/composables/useFacebookPageConnect.js` — `missing_in_onelink`

### Facebook Messenger replies: stop force tagging with MESSAGE_TAG/ACCOUNT_UPDATE
  - `app/services/facebook/send_on_facebook_service.rb` — `diverged`

### WhatsApp webhook subscription: include calls only when voice/calling is enabled
  - `app/services/whatsapp/facebook_api_client.rb` — `diverged`
  - `app/services/whatsapp/webhook_setup_service.rb` — `diverged`
  - `app/models/channel/whatsapp.rb` — `diverged`

### WhatsApp Cloud inbound media: preserve original filenames
  - `app/services/whatsapp/incoming_message_whatsapp_cloud_service.rb` — `diverged`
  - `app/services/whatsapp/incoming_message_base_service.rb` — `diverged`

### WhatsApp location: truncate fallback_title to avoid silent message drops
  - `app/services/whatsapp/incoming_message_base_service.rb` — `diverged`

### WhatsApp/Twilio CTWA referrals: persist referral metadata in message.content_attributes
  - `app/services/whatsapp/incoming_message_base_service.rb` — `diverged`
  - `app/services/whatsapp/incoming_message_service_helpers.rb` — `diverged`
  - `app/services/twilio/incoming_message_service.rb` — `diverged`

### Integration hooks API: redact sensitive settings according to visible_properties
  - `app/models/integrations/app.rb` — `diverged`
  - `app/views/api/v1/models/_hook.json.jbuilder` — `diverged`
  - `config/integration/apps.yml` — `diverged`
  - `app/models/integrations/hook.rb` — `diverged`

### Session cookie: secure and httponly flags
  - `config/initializers/session_store.rb` — `diverged`

### Instagram webhook mutex exhaustion: process after lock retries instead of dropping
  - `app/jobs/mutex_application_job.rb` — `diverged`
  - `app/jobs/webhooks/instagram_events_job.rb` — `diverged`

### Contacts search/phone/name robustness: truncate inbound contact names
  - `app/builders/contact_inbox_with_contact_builder.rb` — `diverged`
  - `app/models/application_record.rb` — `diverged`

### Facebook shared links: render as fallback link attachments, not broken downloadable media
  - `app/builders/messages/facebook/message_builder.rb` — `diverged`
  - `app/javascript/dashboard/components-next/message/Message.vue` — `diverged`
  - `app/javascript/dashboard/components-next/message/bubbles/Fallback.vue` — `missing_in_onelink`

### Contact media tab: shared media/files on contact sidebar
  - `app/controllers/api/v1/accounts/contacts/attachments_controller.rb` — `diverged`
  - `app/javascript/dashboard/components-next/Contacts/ContactsSidebar/ContactMedia.vue` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/SharedAttachments/Media.vue` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/SharedAttachments/Files.vue` — `missing_in_onelink`
  - `app/javascript/dashboard/store/modules/contacts/actions.js` — `diverged`
  - `app/javascript/dashboard/store/modules/contacts/getters.js` — `diverged`
  - `app/javascript/dashboard/store/modules/contacts/mutations.js` — `diverged`
  - `app/javascript/dashboard/store/mutation-types.js` — `diverged`

### Contacts native Company selector: use company_id instead of free-text companyName only
  - `app/controllers/api/v1/accounts/contacts_controller.rb` — `diverged`
  - `enterprise/app/controllers/enterprise/api/v1/accounts/contacts_controller.rb` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/Companies/CompanySelector.vue` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/Contacts/ContactsForm/ContactsForm.vue` — `diverged`
  - `app/views/api/v1/models/_contact.json.jbuilder` — `diverged`
  - `enterprise/app/models/enterprise/concerns/contact.rb` — `diverged`

### WhatsApp Cloud outgoing voice notes: OGG/Opus conversion + voice payload
  - `app/javascript/dashboard/components/widgets/WootWriter/AudioRecorder.vue` — `diverged`
  - `app/javascript/dashboard/components/widgets/WootWriter/utils/audioConversionUtils.js` — `missing_in_onelink`
  - `app/javascript/dashboard/components/widgets/WootWriter/utils/webmOpusToOgg.js` — `missing_in_onelink`
  - `app/services/whatsapp/providers/whatsapp_cloud_service.rb` — `diverged`

### Email/IMAP: prevent deleted conversations from syncing again
  - `app/services/imap/deleted_message_tracker.rb` — `missing_in_onelink`
  - `app/services/imap/base_fetch_email_service.rb` — `diverged`
  - `app/services/conversations/delete_service.rb` — `missing_in_onelink`
  - `lib/redis/redis_keys.rb` — `diverged`

### Email compatibility: IMAP/SMTP compatibility and null-byte sanitization
  - `app/services/imap/base_fetch_email_service.rb` — `diverged`
  - `app/mailboxes/imap/imap_mailbox.rb` — `diverged`
  - `app/mailboxes/mailbox_sanitizer.rb` — `missing_in_onelink`

### Help Center public search and per-locale portal branding
  - `app/controllers/public/api/v1/portals/search_controller.rb` — `missing_in_onelink`
  - `app/models/concerns/portal_config_schema.rb` — `missing_in_onelink`
  - `app/helpers/portal_helper.rb` — `diverged`
  - `db/migrate/20260610000000_add_icon_color_to_categories.rb` — `missing_in_onelink`
  - `app/javascript/dashboard/components-next/emoji-icon-picker/EmojiIconPicker.vue` — `missing_in_onelink`

### Conversation unread Redis cache, filter counters, sidebar ordering and unread sort
  - `app/services/conversations/unread_counts/builder.rb` — `missing_in_onelink`
  - `app/services/conversations/unread_counts/store.rb` — `missing_in_onelink`
  - `app/services/conversations/unread_counts/filter_counter.rb` — `missing_in_onelink`
  - `app/javascript/dashboard/store/modules/conversationUnreadCounts.js` — `missing_in_onelink`
  - `app/javascript/dashboard/store/modules/sidebarSortPreferences.js` — `missing_in_onelink`
  - `app/finders/conversation_finder.rb` — `diverged`

### Active sessions/login picker
  - `app/controllers/devise_overrides/sessions_controller.rb` — `diverged`
  - `app/controllers/concerns/active_auth_session_enforcer.rb` — `onelink_only_or_deleted_upstream`
  - `app/javascript/dashboard/components/auth/SessionLimitOverlay.vue` — `missing_in_onelink`
  - `db/migrate/20260611184600_create_user_sessions.rb` — `missing_in_onelink`

### Captain HttpTool SafeFetch and Firecrawl v2
  - `enterprise/lib/captain/tools/http_tool.rb` — `diverged`
  - `enterprise/lib/captain/tools/http_request_executor.rb` — `onelink_only_or_deleted_upstream`
  - `enterprise/app/services/captain/tools/firecrawl_service.rb` — `diverged`

### Dependency/security bumps: puma, net-imap, selected OAuth deps
  - `Gemfile` — `diverged`
  - `Gemfile.lock` — `diverged`
