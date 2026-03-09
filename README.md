## Onelink Docs

This repository is the standalone Mintlify documentation site for Onelink.

It contains:

- Onelink platform and architecture documentation
- inherited operational and deployment guides from Chatwoot where still applicable
- API and contributor documentation for the fork

### Editing Content

You can edit the docs in two ways:

- locally in Git by changing the `mdx` files and `docs.json`
- in the Mintlify web editor after this repository is connected through the Mintlify GitHub app

The web editor is still Git-backed. Changes are saved to branches or pull requests in this repository.

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
./scripts/sync-openapi-from-onelink.sh ../onelink
```

### Production Domain

Connect this repository in Mintlify and configure the production domain as `docs.one-link.kz`.

Use local preview or a temporary dev server for pre-production checks. Mintlify production hosting should stay on the domain, not on a raw IP.
