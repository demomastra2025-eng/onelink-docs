# One Link Cloud Docs Agent Notes

## Scope

- This repository is the source of truth for documentation content.
- In the main app repository, it is mounted as the `docs/` git submodule.
- Public Mintlify navigation must expose only client-facing product documentation.
- Internal implementation notes must stay outside Mintlify navigation, currently under `internal/`.

## Editing Rules

- Keep client-facing pages focused on product behavior, entities, workflows, integrations, and API usage.
- Keep implementation details, repo ownership, and runtime file references in `internal/`.
- Public docs should use Russian as the primary reading layer.
- Use English in public docs only for product terms, API surface names, code identifiers, or where the technical term is clearer than a forced translation.
- Internal docs remain English-only unless there is a specific reason to localize them.
- Update `docs.json` when public navigation changes.
- Prefer updating existing source pages over creating overlapping docs.
- Do not describe the product as a set of separate industry runtimes.
- Do not surface legacy upstream branding in public documentation.

## Read Order

Use this order when the task is public-product-facing:

1. `docs.json`
2. `introduction.mdx`
3. `getting-started/quick-start.mdx`
4. `getting-started/workspace-setup.mdx`
5. `platform/overview.mdx`
6. the relevant page under `user-guide/`, `integrators/`, or `reference/`

Use this order when the task is internal:

1. `internal/index.mdx`
2. `internal/architecture-overview.mdx`
3. the relevant page under `internal/`
4. `internal/runtime-flows.mdx`
5. `internal/entity-reference.mdx`

## OpenAPI Sync

- From `onelink/docs`, run `./scripts/sync-openapi-from-onelink.sh`.
- From a standalone sibling clone, run `./scripts/sync-openapi-from-onelink.sh ../onelink`.
- After syncing fresh OpenAPI files, rerun `python3 ./scripts/localize_openapi_ru.py` so public API descriptions stay Russian-first.

## Public Localization

- `python3 ./scripts/localize_public_docs_ru.py` keeps public navigation, frontmatter, and page shell aligned with the Russian-first structure.
- `python3 ./scripts/localize_openapi_ru.py` keeps OpenAPI descriptions Russian-first.
- `python3 ./scripts/translate_public_docs_ru.py` is an optional helper for machine draft translation of public page bodies; it requires `deep-translator` in the Python environment and should be followed by spot-checking key pages.

## Commit Flow

1. Commit and push the content change in `onelink-docs`.
2. Return to the main `onelink` repository.
3. Commit the updated `docs` submodule pointer there if the parent repo needs to reference the new docs commit.

## Preview

- Run `mint dev` from this repository root to preview the docs locally.
