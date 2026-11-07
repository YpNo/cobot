# TypeScript and Node — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale lang-typescript`).

## Runtimes

- [verified 2026-11-07 · src: https://endoflife.date/api/nodejs.json] Node 26 "Lithium" is the newest LTS (LTS since 2026-10-28), latest 26.13.0, end of life 2029-04-30.
- [verified 2026-11-07 · src: https://raw.githubusercontent.com/nodejs/Release/main/schedule.json] Node 24 "Krypton" entered maintenance on 2026-10-20 (latest 24.22.2, end of life 2028-04-30); Node 22 "Jod" is maintenance LTS (22.23.4, end of life 2027-04-30).
- [verified 2026-11-07 · src: https://endoflife.date/api/nodejs.json] Node 25 (25.9.0) is end of life since 2026-06-01 and Node 20 since 2026-04-30.
- [verified 2026-11-07 · src: https://nodejs.org/dist/index.json] No Current line ships today: the newest entry is v27.0.0-alpha.0.0.0 (2026-10-29); the schedule starts Node 27 on 2027-04-22.
- [verified 2026-11-07 · src: https://nodejs.org/api/typescript.html] Type stripping is on by default since 23.6.0 and 22.18.0, lost its warning in 24.3.0, became Stable in 25.2.0 and 24.12.0; 26.0.0 removed `--experimental-transform-types`; opt out with `--no-strip-types`.
- [verified 2026-11-07 · src: https://github.com/nodejs/corepack#readme] Corepack ships with Node 14.19.0 up to but not including 25.0.0; on Node 25 and later install it with `npm install -g corepack`.
- [verified 2026-11-07 · src: https://api.github.com/repos/oven-sh/bun/releases/latest] Bun 1.4.4 (2026-10-22); Deno v2.9.8 (2026-10-21, its own release page).

## TypeScript

- [verified 2026-11-07 · src: https://registry.npmjs.org/typescript/latest] `typescript` 7.0.2 is latest on npm.
- [verified 2026-11-07 · src: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] TypeScript 7.0 (Go-native compiler) shipped 2026-07-08 for production; `npm install -D typescript` gives the native `tsc`; TS 6 remains as `@typescript/typescript6`; 7.0 has no JS API (7.1 beta on 2026-10-20 is next).
- [verified 2026-11-07 · src: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] TS 7 defaults: `strict: true`, `module: esnext`, `noUncheckedSideEffectImports: true`; `baseUrl`, `moduleResolution: node/node10/classic`, `target: es5`, AMD, UMD and SystemJS are hard errors.
- [verified 2026-11-07 · src: https://www.typescriptlang.org/tsconfig/] The tsconfig reference marks `strict`, `exactOptionalPropertyTypes` and `skipLibCheck` as Recommended; `noUncheckedIndexedAccess` and `verbatimModuleSyntax` carry no such label (the latter deprecates `importsNotUsedAsValues` and `preserveValueImports` and implies `isolatedModules`).
- [verified 2026-11-07 · src: https://www.typescriptlang.org/docs/handbook/modules/reference.html] `module: nodenext` is the correct option for code that runs on Node; `module: esnext` or `preserve` with `moduleResolution: bundler` for bundlers, Bun and tsx (`bundler` must pair with `esnext` or `preserve`).

## Package managers and supply chain

- [verified 2026-11-07 · src: https://registry.npmjs.org/pnpm/latest] pnpm 12.18.0; npm 12.2.2 (its registry entry).
- [verified 2026-11-07 · src: https://api.github.com/repos/pnpm/pnpm/releases/tags/v10.16.0] `minimumReleaseAge` (minutes) arrived in pnpm 10.16.0 (2025-09-12); the current settings page lists its default as 1440.
- [verified 2026-11-07 · src: https://docs.npmjs.com/cli/v12/commands/npm-install] npm `ignore-scripts` (default false) stops install scripts; npm 12 also documents `min-release-age` (days) and `before` (date) install filters.
- [verified 2026-11-07 · src: https://docs.npmjs.com/cli/v12/commands/npm-audit] `npm audit signatures` verifies registry signatures and provenance attestations of installed packages.
- [verified 2026-11-07 · src: https://docs.npmjs.com/cli/v12/configuring-npm/package-lock-json] `lockfileVersion: 3` is used by npm 9 and above, readable from npm 7.
- [verified 2026-11-07 · src: https://docs.npmjs.com/trusted-publishers] Trusted publishing (OIDC) supports GitHub Actions, GitLab CI/CD and CircleCI cloud runners, needs npm 11.5.1+ and Node 22.14.0+, and generates provenance for public packages from public repositories.
- [verified 2026-11-07 · src: https://docs.npmjs.com/generating-provenance-statements] `npm publish --provenance` needs npm 9.5.0+, a cloud-hosted GitHub Actions or GitLab runner, `id-token: write` and a matching public `repository` field.

## Test, lint, build

- [verified 2026-11-07 · src: https://registry.npmjs.org/vitest/latest] vitest 5.1.0; `coverage.provider` defaults to `v8` and `coverage.thresholds.{lines,functions,branches,statements}` work in config and as `--coverage.thresholds.lines=<n>` (source: <https://vitest.dev/config/coverage>).
- [verified 2026-11-07 · src: https://registry.npmjs.org/@playwright/test/latest] `@playwright/test` 1.65.0.
- [verified 2026-11-07 · src: https://registry.npmjs.org/@biomejs/biome/latest] `@biomejs/biome` 2.6.6.
- [verified 2026-11-07 · src: https://api.github.com/repos/oxc-project/oxc/releases?per_page=6] oxlint 1.92.0 and oxfmt 0.77.0 (2026-11-06); oxfmt is still beta (source: <https://oxc.rs/blog/2026-02-24-oxfmt-beta>).
- [verified 2026-11-07 · src: https://registry.npmjs.org/eslint/latest] eslint 10.14.0; flat config is the default and eslintrc deprecated since 9.0.0; prettier 3.9.10.
- [verified 2026-11-07 · src: https://registry.npmjs.org/vite/latest] vite 8.3.6; tsx 4.23.15; esbuild 0.28.2 (their registry entries).

## Frameworks (versions only; the framework skills carry the idiom)

- [verified 2026-11-07 · src: https://registry.npmjs.org/react/latest] react 19.3.1; react-router 8.5.1 (2026-10-27, GitHub release); next 16.4.5; vue 3.5.45.
