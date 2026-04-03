## One Link Cloud Docs

This repository is the documentation source for One Link Cloud.

## Documentation Structure

The docs are now intentionally split into two contours:

- public product documentation for clients and partners
- internal implementation documentation for the One Link team

### Public Contour

The public contour is the only part exposed through Mintlify navigation in `docs.json`.

Reading model:

- Russian is the primary language for the public contour
- English should remain only in product terms, API surface names, code identifiers, and other technical names where translation would reduce clarity
- internal docs stay English-only

It covers:

- introduction and getting started
- workspace setup and access model
- communication, CRM, scheduling, and Captain
- automations, integrations, reports, and knowledge base
- integrator guides and API model
- glossary and FAQ

### Internal Contour

Internal documentation lives under `internal/` and is intentionally excluded from Mintlify navigation.

It is meant for:

- runtime architecture notes
- model and file-path references
- internal flows
- implementation guidance
- backend and frontend architecture
- database and runtime subsystem documentation
- testing, tooling, and engineering principles

## Editing Rule

When updating documentation:

- keep client-facing pages focused on product behavior and operational logic
- keep implementation and repo details in `internal/`
- do not describe One Link Cloud as a set of separate industry runtimes
- do not surface legacy upstream branding in public docs

## Local Preview

Install the [Mintlify CLI](https://www.npmjs.com/package/mint):

```bash
npm i -g mint
```

Run the preview server from the repository root:

```bash
mint dev
```

## API Reference

The API reference in `docs.json` uses the OpenAPI files stored in [`openapi/`](./openapi).

To refresh those files from the main One Link application repository, run:

```bash
./scripts/sync-openapi-from-onelink.sh
```

Then reapply the public Russian-first localization layer:

```bash
python3 ./scripts/localize_openapi_ru.py
python3 ./scripts/localize_public_docs_ru.py
```

If a broad machine draft translation of public page bodies is needed, run the optional helper below from an environment where `deep-translator` is installed and then spot-check the key public pages:

```bash
python3 ./scripts/translate_public_docs_ru.py
```
