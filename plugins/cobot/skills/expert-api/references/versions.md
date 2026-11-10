# APIs and web protocols — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale expert-api`).

## Specifications and tools

- [verified 2026-11-10 · src: https://github.com/OAI/OpenAPI-Specification/releases/tag/3.2.1] OpenAPI 3.2.1 (2026-09-10) is the latest, a clarification patch; 3.2.0 (2025-09-19); 3.1.x is the previous minor line.
- [verified 2026-11-10 · src: https://github.com/OAI/OpenAPI-Specification/releases/tag/3.2.0] OAS 3.2 adds hierarchical tags, the `query` method and `additionalOperations`, `$self`, sequential media types (SSE, jsonl, json-seq) with `itemSchema`, `in: querystring`, better multipart.
- [verified 2026-11-10 · src: https://spec.openapis.org/oas/v3.2.0.html] OAS 3.2 adds `oauth2MetadataUrl`, the `deviceAuthorization` flow, `deprecated` on security schemes, `discriminator.defaultMapping`, and deprecates the schema keyword `example` for `examples`.
- [verified 2026-11-10 · src: https://github.com/OAI/Overlay-Specification/releases/tag/1.2.0] Overlay 1.2.0 (2026-09-22); [verified 2026-11-10 · src: https://github.com/OAI/Arazzo-Specification/releases/tag/1.1.0] Arazzo 1.1.0 (2026-05-18).
- [verified 2026-11-10 · src: https://github.com/stoplightio/spectral/releases/tag/v6.17.1] Spectral CLI 6.17.1 (2026-11-06); its `oas` ruleset covers 2.0 to 3.2.
- [verified 2026-11-10 · src: https://github.com/Redocly/redocly-cli/releases] @redocly/cli 2.77.0 (2026-11-09), ESM-only, Node 22.12 or newer; supports OAS 2.0 to 3.2, AsyncAPI, Arazzo, Overlay.
- [verified 2026-11-10 · src: https://github.com/OpenAPITools/openapi-generator/releases/tag/v7.27.0] openapi-generator 7.27.0 (2026-11-02); its README still claims 2.0 and 3.0 only, so 3.1 support is partial and 3.2 absent (inference).
- [verified 2026-11-10 · src: https://spec.openapis.org/oas/v2.0.html] Swagger 2.0 carries no deprecation notice but lists 3.0.0 to 3.2.1 as newer: treat it as frozen.

## Standards status

- [verified 2026-11-10 · src: https://datatracker.ietf.org/doc/draft-ietf-httpbis-safe-method-w-body/] QUERY is RFC 10008 (June 2026): safe, idempotent, with a body.
- [verified 2026-11-10 · src: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/] `Idempotency-Key` is draft-08 (2026-10-22), not an RFC.
- [verified 2026-11-10 · src: https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/] `RateLimit` and `RateLimit-Policy` are draft-11 (2026-05-23).
- [verified 2026-11-10 · src: https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/] OAuth 2.1 is draft-17 (2026-10-31): PKCE required, implicit and password grants removed, exact redirect URIs, no bearer token in query strings.
