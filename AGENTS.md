# Onelink Docs Agent Notes

## Scope

- This repository is the source of truth for documentation content.
- In the main app repository, it is mounted as the `docs/` git submodule.
- When an agent edits files under `onelink/docs`, the content change belongs to the `onelink-docs` repository first.

## Editing Rules

- Keep documentation changes in this repository unless the task truly changes product code.
- Update `docs.json` when you add, remove, or rename pages in navigation.
- Keep API reference files under `openapi/` in sync with the app repo when Swagger changes.
- Prefer editing existing pages over creating duplicate pages that say the same thing.

## OpenAPI Sync

- From `onelink/docs`, run `./scripts/sync-openapi-from-onelink.sh`.
- From a standalone sibling clone, run `./scripts/sync-openapi-from-onelink.sh ../onelink`.

## Commit Flow

1. Commit and push the content change in `onelink-docs`.
2. Return to the main `onelink` repository.
3. Commit the updated `docs` submodule pointer there if the parent repo needs to reference the new docs commit.

## Mintlify Edits

- Mintlify web editor writes back to this repository.
- If docs were changed in Mintlify, pull the latest `onelink-docs` changes locally before editing or before using the docs as a source of truth.

## Preview

- Run `mint dev` from this repository root to preview the docs locally.
