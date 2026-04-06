# Captain RubyLLM Audit And De-Legacy Plan

Date: 2026-04-06

## Goal

This audit compares the current `onelink` AI stack with the local RubyLLM ecosystem:

- `../ruby/ruby_llm`
- `../ruby/ruby-llm-docs`
- `../ruby/ruby_llm-schema`
- `../ruby/ruby_llm-instrumentation`

The target is not "keep every old behavior alive". The target is:

1. keep the good native RubyLLM-aligned runtime already present in Captain
2. remove legacy paths that only exist for historical compatibility
3. converge the whole AI stack on one logical contract for prompts, tools, schemas, moderation, and tracing
4. do this while the AI stack is still not used in production, so migrations can be opinionated

## Reference Materials For Comparison And Inspiration

The following local repositories were used as reference material for architectural comparison, implementation direction, and API-shape verification:

- `/Users/akhanbakhitov/Documents/zeroprompt/ruby/ruby_llm`
- `/Users/akhanbakhitov/Documents/zeroprompt/ruby/ruby-llm-docs`
- `/Users/akhanbakhitov/Documents/zeroprompt/ruby/ruby_llm-schema`
- `/Users/akhanbakhitov/Documents/zeroprompt/ruby/ruby_llm-instrumentation`

They are treated here as:

- inspiration for the native RubyLLM way of building the stack
- comparison material for finding drift and legacy in `onelink`
- reference for target contracts around chat, schemas, tools, moderation, and instrumentation

They are not treated as the sole source-of-truth for current `onelink` runtime behavior. Current behavior is always determined by `onelink` code first.

## Source Material Reviewed

### Onelink

- `docs/platform/captain-ai.mdx`
- `docs/internal/captain-runtime.mdx`
- `config/llm.yml`
- `config/agents/tools.yml`
- `lib/llm/config.rb`
- `lib/llm/models.rb`
- `lib/llm/api_client.rb`
- `lib/llm/chat_client.rb`
- `lib/llm/chat_request_runner.rb`
- `lib/llm/moderation_service.rb`
- `lib/llm/runtime_policy.rb`
- `lib/integrations/llm_instrumentation.rb`
- `lib/integrations/llm_instrumentation_spans.rb`
- `enterprise/app/models/captain/assistant.rb`
- `enterprise/app/models/captain/scenario.rb`
- `enterprise/app/models/captain/custom_tool.rb`
- `enterprise/app/models/concerns/agentable.rb`
- `enterprise/app/helpers/captain/chat_helper.rb`
- `enterprise/app/services/llm/base_ai_service.rb`
- `enterprise/app/services/captain/assistant/agent_runner_service.rb`
- `enterprise/app/services/captain/copilot/chat_service.rb`
- `enterprise/app/services/captain/llm/system_prompts_service.rb`
- `enterprise/app/services/captain/llm/contact_attributes_service.rb`
- `enterprise/app/services/captain/llm/contact_notes_service.rb`
- `enterprise/app/services/captain/llm/conversation_faq_service.rb`
- `enterprise/app/services/captain/llm/faq_generator_service.rb`
- `enterprise/app/services/captain/llm/paginated_faq_generator_service.rb`
- `enterprise/app/services/captain/onboarding/website_analyzer_service.rb`
- `enterprise/app/services/captain/tools/copilot/custom_http_tool.rb`
- `enterprise/lib/captain/runtime/*`
- `enterprise/lib/captain/prompts/*`
- `enterprise/lib/captain/context_fields.rb`
- `enterprise/lib/captain/tool_access.rb`
- `enterprise/lib/captain/tool_registry.rb`
- `enterprise/lib/captain/response_schema.rb`
- `enterprise/lib/captain/conversation_completion_schema.rb`

### RubyLLM

- `ruby-llm-docs/_introduction/configuration.md`
- `ruby-llm-docs/_core_features/chat.md`
- `ruby-llm-docs/_core_features/tools.md`
- `ruby-llm-docs/_core_features/agents.md`
- `ruby-llm-docs/_core_features/moderation.md`
- `ruby_llm-schema/README.md`
- `ruby_llm-instrumentation/README.md`

## Executive Summary

The Captain AI stack is already partly modernized and partly legacy.

The strongest part of the stack is the live Captain runtime:

- account-scoped provider isolation is built on `RubyLLM.context`
- the main assistant runtime is built on RubyLLM chat/tool/schema primitives
- prompt layering is file-backed and coherent
- field access and tool access are explicit
- the main assistant response path already uses `RubyLLM::Schema`

The weakest parts are not the core runtime. They are the outer helper paths:

- helper services still use `response_format: { type: 'json_object' }`
- JSON cleanup is still done manually with `sanitize_json_response`
- tool contracts are split between old `param`, custom JSONB schemas, and runtime wrappers
- tracing is custom and powerful, but not aligned with standard `ruby_llm-instrumentation`
- model availability and capability validation is still too manual
- moderation is built on RubyLLM but remains product-level on/off instead of policy-driven
- old compatibility layers still exist for assistant instructions and tool configuration

Because this AI stack is not used in production yet, the right move is not to preserve legacy forever. The right move is to remove it in phases and converge the stack.

## Current Architecture Map

### Native RubyLLM-Aligned Paths To Keep

1. `lib/llm/config.rb`
   Uses scoped provider overrides through `RubyLLM.context` rather than leaking credentials into a global mutable config.

2. `lib/llm/chat_request_runner.rb`
   Centralizes:
   - chat creation
   - system instructions
   - schema attachment
   - tool attachment
   - history restoration

3. `enterprise/lib/captain/runtime/*`
   The new Captain runtime is product-native orchestration built on top of RubyLLM primitives instead of bypassing them.

4. `enterprise/lib/captain/response_schema.rb`
   `enterprise/lib/captain/conversation_completion_schema.rb`
   These are the correct direction: explicit structured outputs using `RubyLLM::Schema`.

5. `enterprise/lib/captain/prompts/*`
   File-backed prompt registry plus snippets is the right long-term shape.

6. `enterprise/lib/captain/context_fields.rb`
   `enterprise/lib/captain/tool_access.rb`
   Access control is explicit and assistant-scoped. This is good product architecture.

### Legacy Or Transitional Paths To Retire

1. JSON mode helper services:
   - `enterprise/app/services/captain/llm/contact_attributes_service.rb`
   - `enterprise/app/services/captain/llm/contact_notes_service.rb`
   - `enterprise/app/services/captain/llm/conversation_faq_service.rb`
   - `enterprise/app/services/captain/llm/faq_generator_service.rb`
   - `enterprise/app/services/captain/llm/paginated_faq_generator_service.rb`
   - `enterprise/app/services/captain/onboarding/website_analyzer_service.rb`

2. Manual JSON cleanup:
   - `enterprise/app/services/llm/base_ai_service.rb`

3. Split tool contract layer:
   - old `param` declarations across tool classes
   - custom tool `param_schema` JSONB in `enterprise/app/models/captain/custom_tool.rb`
   - manual `RubyLLM::Parameter` assembly in `enterprise/app/services/captain/tools/copilot/custom_http_tool.rb`

4. Historical duplicate tool metadata source:
   - removed `config/agents/tools.yml`
   - `enterprise/lib/captain/tool_registry.rb`

5. Legacy assistant instruction compatibility:
   - `enterprise/app/models/captain/assistant.rb`
   - `legacy_system_instruction`
   - old config keys `instructions` and `copilot_instructions`

6. Split runtime path between:
   - new Captain v2 runtime
   - helper-based `Captain::ChatHelper` path for copilot and related flows

7. Custom-only tracing stack:
   - `lib/integrations/llm_instrumentation.rb`
   - `lib/integrations/llm_instrumentation_spans.rb`
   - `enterprise/lib/captain/runtime/instrumentation.rb`
   without leveraging `ruby_llm-instrumentation`

## Detailed Findings By Layer

## 1. Provider And Context Configuration

### Current State

`lib/llm/config.rb` is one of the best parts of the stack.

What it already does right:

- initializes RubyLLM once
- applies provider API keys and API bases in a controlled way
- resolves per-feature model selection
- supports installation-level and account-level overrides
- creates scoped contexts through `Llm::ApiClient.context`

### Comparison With RubyLLM

This matches the RubyLLM docs well. RubyLLM wants provider configuration to be explicit and context-scoped where isolation matters. Onelink is already doing that.

### Verdict

Keep this layer. Improve validation around it, do not rewrite it from scratch.

### Needed Change

Add a stricter validation layer around `config/llm.yml` and actual registry availability from `RubyLLM.models`.

### Why

Today the stack can still offer models that are:

- listed in `config/llm.yml`
- not actually accessible to the active provider credentials
- or not aligned with provider capabilities

This is a runtime reliability issue, not a UI issue.

## 2. Prompt System

### Current State

Prompt construction is mostly coherent:

- file-backed Liquid prompts
- shared snippets
- assistant prompt
- scenario prompt
- copilot/system prompt helpers
- preview service

Relevant files:

- `enterprise/lib/captain/prompts/assistant.liquid`
- `enterprise/lib/captain/prompts/scenario.liquid`
- `enterprise/lib/captain/prompts/llm/copilot_response_generator.liquid`
- `enterprise/lib/captain/prompts/llm/assistant_response_generator.liquid`
- `enterprise/app/services/captain/assistant/prompt_preview_service.rb`

### Good Parts

- optional blocks are guarded with Liquid conditionals
- empty optional sections are omitted cleanly
- glossary and runtime context are explicit
- global system prompt layer now exists and is separated from per-assistant instruction

### Legacy Parts

`Captain::Assistant#system_instruction` still merges:

- `description`
- `legacy_system_instruction`

and `legacy_system_instruction` still reads old config keys:

- `instructions`
- `copilot_instructions`

This is a migration shim. It should not remain the long-term contract.

### Needed Change

Define exactly one source-of-truth field for assistant instruction and one optional global installation layer per runtime type:

- global AI agent system prompt
- global AI assistant system prompt
- assistant instruction

Everything else should be removed after migration.

### Verdict

Prompt architecture is good.
Prompt data model still contains legacy.

## 3. Structured Output

### Current State

The main assistant runtime already uses structured output correctly:

- `enterprise/lib/captain/response_schema.rb`
- `enterprise/lib/captain/conversation_completion_schema.rb`

But many helper services still rely on JSON mode and post-processing:

- `with_params(response_format: { type: 'json_object' })`
- `sanitize_json_response`
- `JSON.parse`

### Comparison With RubyLLM

RubyLLM docs and `ruby_llm-schema` clearly push toward schema-driven output.
That is the native path.

### Why The Current Helper Pattern Is Legacy

JSON mode plus cleanup means the application still has to defend against:

- fenced JSON
- malformed content
- provider formatting drift
- extra prose around payloads

That is exactly what `with_schema` is supposed to remove.

### Mandatory Refactor

Move every helper service that expects structured data to its own schema class.

Priority targets:

1. `contact_attributes_service`
2. `contact_notes_service`
3. `conversation_faq_service`
4. `faq_generator_service`
5. `paginated_faq_generator_service`
6. `website_analyzer_service`

### End State

- every structured helper uses `with_schema`
- every response is parsed through schema output
- `sanitize_json_response` is deleted

## 4. Tool Contracts

### Current State

The product concept is good:

- built-in tools
- custom tools
- per-scope tool access
- policy checks
- assistant scope vs agent scope

But the contract format is fragmented.

#### Built-In Tools

Most built-in tools still use old `param` declarations.

#### Custom Tools

Custom tools store `param_schema` as JSONB and later rebuild runtime params manually:

- `enterprise/app/models/captain/custom_tool.rb`
- `enterprise/app/services/captain/tools/copilot/custom_http_tool.rb`

#### Registry

There is a modern runtime metadata registry:

- `enterprise/lib/captain/tool_registry.rb`

The older YAML metadata file has now been removed, and the registry is the runtime source of truth.

### Comparison With RubyLLM

RubyLLM now prefers:

- `params do ... end` for structured tool inputs
- one schema-like contract per tool

The current Onelink tool layer still mixes:

- old `param`
- manual JSONB param schema
- registry metadata
- wrapper-generated RubyLLM params

### Mandatory Refactor

1. Make `enterprise/lib/captain/tool_registry.rb` the only source-of-truth for runtime tool metadata.
2. Keep `enterprise/lib/captain/tool_registry.rb` as the only runtime metadata source.
3. Standardize tool inputs:
   - use `params do` for built-in tools that need structured or nested inputs
   - keep `param` only for trivially flat tools if desired, but make that an explicit short-term exception
4. Replace ad hoc custom tool parameter reconstruction with a schema-backed adapter layer.

### Better Long-Term Model

Each tool should have one canonical contract with:

- id
- title
- description
- scope support
- permission/risk metadata
- input schema
- output expectations

That contract should feed:

- runtime
- UI metadata
- preview/help text
- tests

## 5. Runtime Split: Assistant V2 vs Helper-Based Flows

### Current State

There are two broad execution styles:

#### New Native Captain Runtime

- `Captain::Assistant::AgentRunnerService`
- `Captain::Runtime::Runner`
- `Captain::Runtime::Agent`

This is the strongest path in the stack.

#### Helper-Based Chat Flow

- `Captain::ChatHelper`
- `Llm::ChatRequestRunner`
- `Captain::Copilot::ChatService`

This path still works, but it is not fully converged with the newer runtime.

### Problem

Two runtime styles means:

- two mental models
- two tracing styles
- two moderation injection points
- higher risk of drift in prompt/tool history handling

### Recommended Direction

Do not rip out the helper path immediately.
Converge it deliberately:

1. make the request contract identical
2. normalize structured output
3. normalize instrumentation
4. then decide whether copilot should remain helper-based or move behind the same Captain runtime abstractions

### Verdict

Keep both short-term.
Do not accept permanent divergence.

## 6. Moderation

### Current State

`lib/llm/moderation_service.rb` correctly uses `RubyLLM.moderate` through `Llm::ApiClient.moderate`.

This is good.

But product policy is still simplistic:

- moderation is basically on/off
- provider path is effectively OpenAI-only
- flagged content becomes block behavior
- category scores are not used

### Comparison With RubyLLM

RubyLLM moderation already exposes:

- `flagged?`
- `categories`
- `flagged_categories`
- `category_scores`

The framework supports a more precise policy than Onelink currently uses.

### Needed Change

Introduce a product policy object that maps moderation results to actions.

Examples:

- `self-harm` or `sexual/minors` -> block
- `harassment` medium score -> warn or handoff
- mild violence score -> allow and log

Also split policy by:

- runtime type: `assistant` vs `copilot`
- stage: `input` vs `output`

### Verdict

Keep moderation on RubyLLM.
Replace simplistic product policy.

## 7. Instrumentation And Observability

### Current State

Onelink has a substantial custom observability layer:

- OpenTelemetry
- Langfuse attributes
- custom session spans
- tool spans
- moderation spans

This is not weak. It is actually fairly advanced.

### Problem

It is product-specific instead of building on top of the standard RubyLLM event surface.

RubyLLM instrumentation already emits stable events:

- `complete_chat.ruby_llm`
- `execute_tool.ruby_llm`
- `embed_text.ruby_llm`
- `moderate_text.ruby_llm`
- `transcribe_audio.ruby_llm`

### Recommended Direction

Do not delete current tracing.
Wrap or bridge it through standard RubyLLM instrumentation so the base event model is consistent with the framework.

### End State

- RubyLLM standard notifications are always available
- Onelink enriches them with tenant, assistant, conversation, and Langfuse metadata
- custom spans become additive, not foundational

## 8. Model Registry And Capability Validation

### Current State

`config/llm.yml` is the product-facing model registry.
`lib/llm/models.rb` partially consults `RubyLLM.models`.

This is a reasonable start but not strict enough.

### Risk

The product can still expose models that are:

- listed in product config
- not actually accessible
- missing required capabilities
- not appropriate for a given feature

### Needed Change

Add a hard audit command or boot-time verifier that checks:

- every configured model exists in `RubyLLM.models` unless explicitly allowed as custom
- provider matches
- declared capabilities are compatible with RubyLLM registry capabilities
- feature defaults are valid
- moderation model is available

### Verdict

Keep product-owned model curation.
Add hard validation against RubyLLM registry.

## What Must Change In Existing Code

These are not optional cleanups. These are the core de-legacy tasks.

1. Replace JSON-mode helper services with schema-driven output.
2. Delete `sanitize_json_response` after all structured helpers are migrated.
3. Retire legacy assistant instruction keys:
   - `config.instructions`
   - `config.copilot_instructions`
4. Move to one source-of-truth assistant instruction field.
5. Remove any remaining references to the deleted YAML-era tool metadata path.
6. Standardize tool contracts around one schema-driven contract.
7. Add strict model registry verification against `RubyLLM.models`.
8. Bridge tracing through `ruby_llm-instrumentation`.
9. Replace simple moderation on/off policy with category-aware policy.

## What Should Be Added

These are additive improvements that make the stack complete rather than merely less legacy.

1. Schema classes for every structured helper task.
2. A unified tool contract object that feeds runtime and UI.
3. A model-audit rake task or boot validator.
4. A moderation policy object with score thresholds and per-stage actions.
5. Standard ActiveSupport instrumentation subscriptions for all LLM calls.
6. End-to-end smoke coverage for:
   - external AI agent
   - internal AI assistant
   - scenario handoff
   - custom HTTP tool
   - moderation enabled
   - provider switch
   - structured helper services
7. Contract tests for every tool schema and every structured output schema.

## MVP Plan

The MVP is the smallest reasonable plan that removes the highest-risk legacy and locks the stack onto the native RubyLLM direction.

### MVP Scope

1. Freeze the target contract.
2. Migrate all structured helper services off JSON mode.
3. Clean up the assistant instruction contract.
4. Add hard model registry verification.
5. Remove only the legacy code that becomes dead immediately after those migrations.

### MVP Includes

#### Phase 1: Freeze The Native Contract

##### Goal

Agree on the long-term contract before refactoring implementation.

##### Decisions

- one assistant instruction field
- one global agent system prompt field
- one global AI assistant system prompt field
- one tool metadata source
- one preferred structured-output approach: `RubyLLM::Schema`

##### Deliverables

- architecture note
- field contract note
- deprecation list

##### Acceptance Criteria

- no new feature is allowed to use JSON mode for structured output
- no new tool metadata is added outside the registry

#### Phase 2: Migrate Structured Helper Services

##### Goal

Remove JSON mode from all structured helper tasks.

##### Work

- create schema classes for each helper
- swap `response_format: { type: 'json_object' }` for `with_schema`
- remove manual cleanup/parsing

##### Acceptance Criteria

- `sanitize_json_response` has zero callers
- helpers return parsed structured data directly

#### Phase 3: Clean Up The Instruction Contract

##### Goal

Remove prompt-field ambiguity before the stack goes live.

##### Work

- keep one assistant instruction source-of-truth
- migrate any remaining values from legacy keys into the canonical field
- stop reading `config.instructions`
- stop reading `config.copilot_instructions`

##### Acceptance Criteria

- no runtime prompt depends on legacy instruction keys
- prompt preview and runtime use the same canonical instruction field

#### Phase 4: Add Hard Model Registry Verification

##### Goal

Stop invalid or inaccessible model configuration from reaching runtime.

##### Work

- add a verifier for `config/llm.yml` against `RubyLLM.models`
- validate feature defaults
- validate provider/model capability assumptions
- validate moderation model availability

##### Acceptance Criteria

- invalid model config fails audit early
- feature defaults cannot point to unsupported models silently

### MVP Outcome

After MVP, the stack should be:

- schema-first for structured tasks
- free of JSON cleanup glue
- consistent in assistant instruction handling
- much safer around model configuration

This is the smallest version that is reasonable to ship toward real usage.

## Full Plan

The current full plan takes the MVP foundation and finishes the highest-value convergence work first, without pulling in moderation policy expansion or instrumentation.

### Full Plan Scope

1. Everything in MVP.
2. Normalize the tool contract layer.
3. Converge runtime execution styles.
4. Remove all remaining compatibility shims.
5. Add stronger contract and smoke coverage.

### Full Plan Includes

#### Phase 5: Normalize Tool Contracts

##### Goal

Converge built-in and custom tools on one consistent runtime contract.

##### Work

- make `tool_registry.rb` the only runtime metadata source
- migrate important built-in tools to `params do`
- define a custom-tool schema adapter instead of raw JSONB-to-Parameter glue
- define contract tests for tool schemas

##### Acceptance Criteria

- `enterprise/lib/captain/tool_registry.rb` is the only runtime tool metadata source
- new tools use one standardized contract

#### Phase 6: Converge Runtime Paths

##### Goal

Reduce drift between assistant v2 runtime and helper-based copilot/runtime calls.

##### Work

- normalize request-building and tool wiring
- normalize moderation hooks
- normalize history restoration expectations
- decide whether copilot stays helper-based or moves behind the same runtime abstractions

##### Acceptance Criteria

- runtime hooks, tracing, and tool flow behave consistently across assistant and copilot

#### Phase 7: Remove Compatibility Shims

##### Goal

Delete code that exists only for historical compatibility.

##### Work

- remove legacy instruction fallback keys
- remove dead prompt paths
- remove obsolete tool config file if not needed
- remove JSON cleanup helpers
- remove any temporary adapters introduced during migration

##### Acceptance Criteria

- the AI stack no longer needs historical compatibility glue
- runtime behavior is described by one modern contract

#### Phase 8: Test And Smoke Hardening

##### Goal

Make the converged stack verifiable instead of only conceptually clean.

##### Work

- add contract tests for schemas and tools
- add smoke tests for assistant, copilot, scenarios, custom tools, moderation, and provider switching
- add regression checks for prompt assembly and tool access

##### Acceptance Criteria

- the main AI paths have repeatable automated coverage
- refactors stop depending on manual confidence

### Full Plan Outcome

After the full plan, the stack should be:

- native to RubyLLM concepts
- internally consistent across runtimes
- safer to operate
- easier to extend without reintroducing legacy

## Prioritization Summary

### MVP

- contract freeze
- structured helper migration
- instruction contract cleanup
- model registry verification

### Full Plan

- tool contract normalization
- runtime-path convergence
- compatibility cleanup
- docs and test hardening

## Deferred Work

These items are intentionally not part of the current full plan:

### Stage 2

- moderation policy expansion
- category-aware moderation behavior
- stage-specific moderation rules
- runtime-specific moderation rules

### Stage 3

- instrumentation convergence with `ruby_llm-instrumentation`
- broader observability cleanup beyond what is strictly needed for runtime correctness

They are useful, but they are not required to make the Captain AI stack native, reliable, and production-ready in its core behavior.

## Practical Implementation Notes

### Because The Stack Is Not Live In Production

Prefer these choices:

- rename fields if the new domain model is better
- remove legacy config keys instead of preserving them indefinitely
- migrate stored records once rather than carrying fallback code forever
- add stricter validation early rather than late

Avoid these choices:

- keeping two prompt-field models forever
- keeping both YAML and registry tool metadata forever
- keeping JSON-mode helpers "for now"

## Final Recommendation

Do not rewrite the whole AI stack.

Keep and strengthen what is already native:

- scoped config
- Captain runtime
- schema-driven main assistant flow
- prompt registry
- access-controlled fields and tools

Delete what is clearly legacy:

- JSON mode helper services
- manual JSON cleanup
- legacy instruction keys
- duplicate tool metadata sources
- unchecked model/config drift

Add what is missing for a production-grade architecture:

- schema-driven helper services everywhere
- unified tool contracts
- model capability audit
- moderation policy object
- RubyLLM-standard instrumentation bridge
- end-to-end smoke coverage

That path is the most native, the most reliable, and the lowest-risk long-term architecture for the Onelink Captain AI stack.
