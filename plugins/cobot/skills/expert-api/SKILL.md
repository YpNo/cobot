---
name: expert-api
description: >-
  APIs and web protocols, design-first: OpenAPI 3.1 and 3.2, HTTP semantics, status codes,
  problem details, pagination, idempotency, versioning and deprecation, auth (OAuth 2.x, OIDC),
  webhooks, SSE, WebSocket and gRPC choices, Spectral and Redocly linting. Use on openapi and
  swagger files, *.proto, and when designing or reviewing an HTTP API.
paths:
  - "**/*openapi*.json"
  - "**/*openapi*.y*ml"
  - "**/swagger*.json"
  - "**/*.proto"
user-invocable: false
---

# expert-api

CONTEXT.md and the governance file override it; the host project's API conventions always win
in a contribution. Versions and standards status: `references/versions.md`. Audit:
`/cobot:consult api`.

## Design-first

1. The OpenAPI document is the contract: written or changed before the handler, reviewed in the
   same PR, linted in CI (Spectral or Redocly, one of them). A generated document (go-swagger,
   springdoc, FastAPI) is fixed at its source annotations, never by hand.
2. [verified 2026-11-10 · src: https://spec.openapis.org/oas/v3.2.0.html] Schemas in 3.1 and 3.2 are JSON Schema 2020-12 plus the OAS vocabulary; `nullable: true` exists only in 3.0.x, use `type: [string, "null"]`.
3. [verified 2026-11-10 · src: https://spec.openapis.org/oas/v3.2.0.html] A discriminator only with `oneOf`, `anyOf` or `allOf`; with `oneOf` or `anyOf` list every schema; an optional discriminating property needs `defaultMapping`.
4. Every operation: a unique `operationId`, a summary, its success response and its error
   responses (4xx typed, not only `default`), its security; arrays bounded (`maxItems`), objects
   closed where the contract is closed (`additionalProperties: false`): linters do not check
   those two.

## HTTP semantics

- [verified 2026-11-10 · src: https://www.rfc-editor.org/rfc/rfc9110.html] GET, HEAD, OPTIONS, TRACE are safe; those plus PUT and DELETE are idempotent; POST and PATCH are neither. QUERY (RFC 10008) for complex searches with a body.
- [verified 2026-11-10 · src: https://www.rfc-editor.org/rfc/rfc9110.html] Precise codes: 409 conflict, 412 failed precondition, 422 unprocessable content, 429 with rate limits; ETag with `If-Match` for optimistic concurrency (412), `If-None-Match` for caching (304).
- [verified 2026-11-10 · src: https://www.rfc-editor.org/rfc/rfc9457.html] Errors as `application/problem+json` (RFC 9457, obsoletes 7807): `type`, `title`, `status`, `detail`, `instance`, extensions allowed.
- Pagination through `Link` with `rel=next` and `prev` (RFC 8288), opaque cursors for large or
  changing collections, a capped page size.
- `Idempotency-Key` on retried POSTs (draft); never reuse a key with a different payload.
- [verified 2026-11-10 · src: https://www.rfc-editor.org/rfc/rfc9745.html] Deprecation as a structured date (`@<epoch>`) with `rel="deprecation"`, `Sunset` (RFC 8594) no earlier than it; version in the path or a media type, one scheme per API.

## Auth

- [verified 2026-11-10 · src: https://spec.openapis.org/oas/v3.2.0.html] Security scheme types: `apiKey`, `http`, `mutualTLS`, `oauth2`, `openIdConnect`; TLS for every OAuth URL.
- Follow OAuth 2.1's direction (draft): authorization code with PKCE, no implicit or password
  grant, exact redirect URIs, never a token in a query string. Scopes per operation.

## Protocol choice

- REST with OpenAPI for public and browser clients; gRPC (Protobuf) for internal service calls
  and streaming between services; GraphQL for client-shaped aggregation when a team owns it.
- [verified 2026-11-10 · src: https://github.com/OAI/OpenAPI-Specification/releases/tag/3.2.0] SSE for one-way server push (describable in OAS 3.2 with `itemSchema`); WebSocket only for two-way traffic; `webhooks` (3.1+) for calls the API makes to clients.
- HTTP/2 and HTTP/3 change transport, not semantics: the design is the same.

## Lint commands

- `spectral lint <file>` with the repository's `.spectral.yaml`, or `redocly lint <file>`; both
  read-only. `redocly bundle` and code generators write files: name them before running.

## Do not

- Do not edit a generated document; change the annotations and regenerate.
- Do not report 3.1-only features missing from a 3.0 document as defects.
- Do not add a second linter beside the one the repository uses.
