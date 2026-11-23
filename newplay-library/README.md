# NewPlay resource library

Cloudflare Worker with a static multilingual catalog, search, previews and individual downloads. This is not the NewPlay marketing-site frontend.

```sh
npm test
```

Tests use the bundled published-catalog snapshot and relative-path fixture. They do not need production credentials, private operation caches or actual R2 documents. The public static catalog/thumbnail snapshot does not bundle the production document objects.

Private production catalog-generation and synchronization tooling is intentionally excluded. Rebuilding requires separately supplied authorized tooling and approved source materials; do not synchronize an empty archive against production. Font and Figma page implementation checks live at the repository root.

For a separately authorized deployment, copy `wrangler.example.jsonc` to the ignored `wrangler.jsonc`, set your own account, routes and R2 bucket, then use your own Cloudflare authorization. No production account configuration is included. Deployment and synchronization require explicit authorization and are not part of installation.
