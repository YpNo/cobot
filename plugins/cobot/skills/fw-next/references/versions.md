# Next.js — versions and facts

Format: `- [status YYYY-MM-DD · src: <url>] claim`. Every line is **reported**: read on the primary
source, not yet exercised on a repository (owner's choice, 2026-11-10; no local Next.js project).
Promote a line to verified once a repository proves it.

## Versions

- [reported 2026-11-10 · src: https://github.com/vercel/next.js/releases/tag/v16.4.6] next 16.4.6 (2026-11-09) on the Active LTS line; 15.5.29 is Maintenance LTS.
- [reported 2026-11-10 · src: https://github.com/vercel/next.js/blob/v16.4.6/packages/next/package.json] React peer `^18.2.0 || ^19.0.0`; 16.4 ships React 19.3; Node `>=20.9.0`; TypeScript 5.1 or newer.
- [reported 2026-11-10 · src: https://nextjs.org/blog/next-16] Turbopack is the default for `next dev` and `next build` since 16.0 (`--webpack` opts out).
- [reported 2026-11-10 · src: https://nextjs.org/blog/november-2026-security-release] The November 2026 security release fixes 16.4.5 and 15.5.29 (GHSA-mfr8-8qww-v76h high, cross-tenant leak with `unstable_cache` and `use cache`, plus five medium); require at least those.
- [reported 2026-11-10 · src: https://nextjs.org/blog/nextjs-security-update-october-14-2026] The October 14 update fixes 16.4.1 and 15.5.28: GHSA-673q-mjm6-r5xr (critical, RCE through `use cache`), GHSA-2464-fhr4-w9xw (critical, RCE through sharp on SVG; sharp 0.35.5 or newer).
