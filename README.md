## Onelink Docs

This repository is the standalone Mintlify documentation site for Onelink.

It contains:

- Onelink platform and architecture documentation
- inherited operational and deployment guides from Chatwoot where still applicable
- API and contributor documentation for the fork
- repository and workflow guidance for human analysts and AI agents working across app code, docs, and deployment surfaces

### Repository Layout

This repository is the source of truth for the documentation content.

It is used in two ways:

- as its own Git repository: `demomastra2025-eng/onelink-docs`
- as the `docs/` submodule inside the main Onelink app repository

When you open the `docs/` directory inside the main Onelink repository, you are already working inside this separate docs repository.

### Editing Content

You can edit the docs in two ways:

- locally in Git by changing the `mdx` files and `docs.json`
- in the Mintlify web editor after this repository is connected through the Mintlify GitHub app

The web editor is still Git-backed. Changes are saved to branches or pull requests in this repository.

If the docs were edited in Mintlify, pull the latest changes in the `docs/` repository before assuming the local files are current.

### Recommended Reading Order

For structural or project-wide work, start with:

1. `platform/current-architecture.mdx`
2. `platform/repository-map.mdx`
3. `contributing-guide/project-operations.mdx`
4. `contributing-guide/ai-agent-operating-model.mdx`
5. `contributing-guide/skill-map.mdx`

Then move to the surface-specific implementation guide under `contributing-guide/` or `self-hosted/`.

### Local Preview

Install the [Mintlify CLI](https://www.npmjs.com/package/mint):

```bash
npm i -g mint
```

Run the preview server from the repository root:

```bash
mint dev
```

If you want a shared dev instance on a server IP, run the preview on that host and expose it with your reverse proxy or a published port.

### API Reference

The API reference in `docs.json` uses the OpenAPI files stored in [`openapi/`](./openapi).

To refresh those files from the main Onelink app repository, run:

```bash
./scripts/sync-openapi-from-onelink.sh
```

If you are running this repository as a standalone sibling checkout instead of as `onelink/docs`, you can also pass the app path explicitly:

```bash
./scripts/sync-openapi-from-onelink.sh ../onelink
```

### Commit Flow

When docs change, the normal flow is:

1. Commit and push the content change in this repository.
2. In the main `onelink` repository, commit the updated `docs` submodule pointer.

If a task changes both product code and docs, keep the docs commit in `onelink-docs` and the product code commit in `onelink`.

### Production Domain

Connect this repository in Mintlify and configure the production domain as `docs.one-link.kz`.

Use local preview or a temporary dev server for pre-production checks. Mintlify production hosting should stay on the domain, not on a raw IP.
