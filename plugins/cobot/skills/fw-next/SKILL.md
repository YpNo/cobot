---
name: fw-next
description: >-
  Senior Next.js 16 on fw-react: App Router, Server and Client Components, Server Actions as public
  endpoints, Cache Components and use cache, proxy.ts, async params, env exposure, recent
  advisories. Lines reported (no local repository yet). Use on next.config.*, app/ routes, a
  package.json with next, in typescript-builder when the brief names it.
paths:
  - "**/next.config.*"
  - "**/app/**/page.tsx"
  - "**/app/**/layout.tsx"
user-invocable: false
---

# fw-next

On top of `fw-react` and `lang-typescript`. **Every line is reported**: read on nextjs.org or the
release pages, not yet exercised on a repository; say so when a line drives a decision, and
promote it to verified once a project proves it. CONTEXT.md and the governance file override it.
Versions and advisories: `references/versions.md`.

## Rendering model

- [reported 2026-11-10 · src: https://nextjs.org/docs/pages] App Router is the default; Pages Router is supported, migration recommended.
- [reported 2026-11-10 · src: https://nextjs.org/docs/app/getting-started/server-and-client-components] Layouts and pages are Server Components; `'use client'` marks a module-graph boundary (everything it imports ships to the client); props crossing it are serialisable; pass Server Components into Client Components as `children`.
- [reported 2026-11-10 · src: https://nextjs.org/blog/next-16] `params` and `searchParams` are promises; `cookies()`, `headers()`, `draftMode()` are awaited; use `PageProps<'/route'>` and `LayoutProps`.
- [reported 2026-11-10 · src: https://nextjs.org/docs/app/getting-started/metadata-and-og-images] `metadata` or `generateMetadata` in Server Components only; file conventions `opengraph-image`, `icon`, `sitemap`, `robots`.

## Caching

- [reported 2026-11-10 · src: https://nextjs.org/blog/next-16-4] Cache Components is recommended from 16.4 (`cacheComponents: true`, with `partialPrefetching: true`), default in `create-next-app`, the default in Next 17.
- [reported 2026-11-10 · src: https://nextjs.org/docs/app/getting-started/caching] With Cache Components, caching is opt-in: `'use cache'` with `cacheLife` and `cacheTag`; runtime reads (`cookies`, `headers`, `params`, `searchParams`) sit behind `<Suspense>`; `Math.random()` and `Date.now()` need `connection()` or `'use cache'`.
- [reported 2026-11-10 · src: https://nextjs.org/docs/app/guides/caching-without-cache-components] Without it, `fetch` is not cached by default: `cache: 'force-cache'`, `next.revalidate`, `next.tags`, `unstable_cache`, segment config.
- [reported 2026-11-10 · src: https://nextjs.org/blog/next-16] `revalidateTag(tag, profile)` (one argument deprecated); `updateTag()` only in Server Actions; `refresh()` for uncached data.
- [reported 2026-11-10 · src: https://nextjs.org/blog/next-16-4] `export const ensureStatic = 'navigation' | 'prefetch' | 'shell'` fails the build when dynamic content leaks in.

## Routing, proxy, config

- [reported 2026-11-10 · src: https://nextjs.org/docs/app/getting-started/route-handlers] `route.ts` handlers never share a segment with `page`; type the context `RouteContext<'/x/[id]'>` and `await ctx.params`.
- [reported 2026-11-10 · src: https://nextjs.org/docs/app/api-reference/file-conventions/proxy] `middleware.ts` is deprecated for `proxy.ts` (exports `proxy`, Node.js runtime only); codemod `middleware-to-proxy`; matchers can skip Server Functions, so proxy is never the only auth check.
- [reported 2026-11-10 · src: https://nextjs.org/blog/next-16] `next/image`: `remotePatterns` (not `domains`), local IPs blocked, at most three redirects; `serverRuntimeConfig` and `publicRuntimeConfig` are removed; `next.config.ts` is supported.
- [reported 2026-11-10 · src: https://nextjs.org/docs/app/guides/static-exports] `output: 'export'` drops Server Actions, proxy, cookies, ISR, rewrites, redirects, headers and the default image loader.

## Security

- [reported 2026-11-10 · src: https://nextjs.org/docs/app/guides/data-security] Server Actions are public POST endpoints: each validates input and checks auth and ownership itself; return only what the UI needs; set `serverActions.allowedOrigins` behind proxies and `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` across instances.
- [reported 2026-11-10 · src: https://nextjs.org/docs/app/guides/data-security] `import 'server-only'` in data-access modules; a data access layer returning minimal DTOs and holding every `process.env` read; taint APIs are a second layer only.
- [reported 2026-11-10 · src: https://nextjs.org/docs/app/guides/environment-variables] `NEXT_PUBLIC_*` is inlined at build time; never a secret there; never commit `.env*`.

## Tests and commands

- [reported 2026-11-10 · src: https://nextjs.org/docs/app/getting-started/installation] `next dev`, `next build`, `next start`; `next lint` is removed in 16 (run `eslint` or `biome check`); `next build` no longer lints and fails on type errors; `next typegen` writes route types.
- [reported 2026-11-10 · src: https://nextjs.org/docs/app/guides/testing] Vitest or Jest for units, Playwright for end-to-end; async Server Components are better covered end to end, against `next build && next start`.

## Do not

- Do not trust proxy or a page check to protect a Server Action.
- Do not put a secret in `NEXT_PUBLIC_*` or read `process.env` outside the data access layer.
- Do not ship below 16.4.5 or 15.5.29.
