---
name: lang-typescript
description: >-
  Senior TypeScript: verified Node, TypeScript and tools, the exact pnpm, tsc, vitest and lint
  commands, strict tsconfig, ESM idiom, test, supply-chain and runtime security rules. Use on *.ts,
  *.tsx, package.json, tsconfig*.json and lockfiles, in typescript-builder, and before writing,
  reviewing or testing TypeScript or touching Node CI.
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/package.json"
  - "**/tsconfig*.json"
  - "**/pnpm-lock.yaml"
  - "**/package-lock.json"
user-invocable: false
---

# lang-typescript

CONTEXT.md and the governance file it names override this skill: the project's coverage tool and
threshold, error-handling rules and shape win over the defaults below.

Versions, dates and sources: `references/versions.md`. Re-verify a line the brief flags stale
(versions after 30 days, idiom after 90) before relying on it; never "upgrade" a repo as a side
effect — report the gap.

## Toolchain and commands

- [verified 2026-11-07 · src: https://endoflife.date/api/nodejs.json] Node 26 is the active LTS (26.13.0); 24 (24.22.2) and 22 (22.23.4) are maintenance LTS; 25, 20 and older are end of life.
- [verified 2026-11-07 · src: https://registry.npmjs.org/typescript/latest] TypeScript 7.0.2 is current: the Go-native `tsc`, production since 2026-07-08; TypeScript 6 stays available as `@typescript/typescript6`.
- [verified 2026-11-07 · src: https://registry.npmjs.org/pnpm/latest] pnpm 12.18.0; Node 25+ no longer bundles Corepack (`npm install -g corepack`, or install pnpm itself).
- Repo pins win: `engines.node` and `packageManager` in `package.json`, `.nvmrc` or `mise.toml`.

| step | command |
|---|---|
| install | `pnpm install --frozen-lockfile` (npm: `npm ci`); never a bare install in CI |
| type check | `pnpm exec tsc --noEmit` (`tsc -b` for project references) |
| lint | `pnpm exec biome check .` **or** `pnpm exec oxlint` — one linter per repo, the one the repo has |
| format | `pnpm exec biome format .` or `pnpm exec oxfmt --check` (oxfmt is beta) or `prettier --check .` |
| test (focused) | `pnpm exec vitest run path/to/file.test.ts -t "name"` |
| test (all) | `pnpm exec vitest run` |
| coverage | `pnpm exec vitest run --coverage --coverage.thresholds.lines=85` (provider v8 by default) |
| audit | `pnpm audit --audit-level=high` (npm: `npm audit`, `npm audit signatures`) |
| outdated | `pnpm outdated` ; `cobot-deps check` reports what is behind |
| build | `pnpm exec tsc -p tsconfig.build.json` for libraries; `vite build` for apps |
| e2e | `pnpm exec playwright test` (critical journeys only) |

- Lock rule: `pnpm-lock.yaml` (or `package-lock.json` v3) committed; CI installs frozen.
- Scripts in `package.json` wrap these commands so local and CI run the same thing; CI calls
  the scripts (`pnpm run lint`), not re-typed flags.
- Node runs `.ts` files directly (type stripping stable since 24.12 and 25.2, default on): a
  script no longer needs `tsx` unless it uses enums or namespaces.

## tsconfig

```jsonc
{
  "compilerOptions": {
    "strict": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,      // team policy, not a TS default: arrays index to T | undefined
    "noUncheckedSideEffectImports": true,
    "verbatimModuleSyntax": true,          // `import type` is explicit; isolatedModules follows
    "module": "nodenext",                  // code that runs on Node; "esnext" + "moduleResolution": "bundler" for Vite, Bun, tsx
    "target": "es2024",
    "skipLibCheck": true,
    "noEmit": true                         // the bundler or `tsc -p tsconfig.build.json` emits
  }
}
```

- TypeScript 7 defaults `strict`, `module: esnext` and `noUncheckedSideEffectImports` to on and
  rejects `baseUrl`, `moduleResolution: node10`, `target: es5`, AMD, UMD and SystemJS: migrate
  with path aliases through the bundler and `nodenext`/`bundler` resolution.
- `"type": "module"` in `package.json`; `.cjs` only for a config file a tool still requires.

## Idiom

- Types at the boundary, inference inside: annotate exported functions and public object
  shapes; let locals infer. `unknown` at every input (`JSON.parse`, request bodies, env), then
  narrow with a schema (`valibot`, `zod`, `arktype`) or type guards. `any` needs a comment.
- Model with discriminated unions and `satisfies`; `as const` for literal tables; avoid `enum`
  (not erasable, breaks type stripping) in favour of union literals or `as const` objects.
- Errors: throw `Error` subclasses with a `cause`; return `Result`-style unions only where the
  caller always branches; never throw strings; `catch (error: unknown)` and narrow.
- Async: `async`/`await` everywhere; `Promise.all` for independent work, `Promise.allSettled`
  when partial failure is expected; `AbortSignal` through to fetch and timers; no floating
  promises (the linter rule is on).
- Modules: ESM only, named exports, one module per concern, no barrel files that re-export
  everything (tree-shaking and cycles). Import Node built-ins with the `node:` prefix.
- Immutability by default: `readonly` properties and arrays in public types, `structuredClone`
  over hand-rolled deep copies.
- Dependency injection through function parameters or a small factory; no global singletons
  except the logger.

## Project shape

```text
package.json  pnpm-lock.yaml  tsconfig.json  tsconfig.build.json  biome.json (or .oxlintrc.json)
src/<feature>/<module>.ts   src/<feature>/<module>.test.ts   src/index.ts (public surface)
tests/e2e/  (playwright)   vitest.config.ts
```

- Tests beside the module they test, named `<module>.test.ts`; e2e apart.
- One `package.json` per repository unless a `pnpm-workspace.yaml` declares packages.
- Mixed repos (headplane: Go backend and a React Router app) keep each stack's commands in its
  own `package.json` scripts and Makefile targets; the TypeScript builder touches only the
  TypeScript files of a task.

## Tests

- vitest: `describe`/`it`, `expect` matchers, `vi.fn()` for fakes at the boundary, `vi.useFakeTimers()`
  for time, `--project` for unit versus integration suites. No snapshot tests for logic.
- Names read as sentences: `it("rejects an expired token")`; one behaviour per test.
- Fakes over mocks of your own modules: inject the port; mock only the process boundary
  (fetch, fs, clock, env). `msw` for HTTP when a real client is under test.
- Coverage floor 85 % lines on `src/`, enforced in `vitest.config.ts` (`coverage.thresholds`).
- Type tests for public generics: `expectTypeOf` in `*.test-d.ts`.

## Security

- Inputs: validate every external payload with a schema before use; never trust `req.body`,
  query strings, env or `JSON.parse` output as typed.
- Injection: parameterised queries (drizzle, kysely, the driver's placeholders), never string
  concatenation; `execFile` with an argv array, never `exec` with user data; `path.resolve`
  then a prefix check for file paths; no `eval`, `new Function`, `vm` on input.
- Web: set security headers (helmet or the framework's), `SameSite` cookies, CSRF tokens for
  state-changing forms, output encoding by the template engine, a strict CSP.
- Secrets from env or a manager, never in the bundle: anything imported by client code is
  public; use the framework's server-only boundary.
- Supply chain: install with scripts off where possible (`npm_config_ignore_scripts=true` for
  tooling), `pnpm` `minimumReleaseAge` (default 1440 minutes) or npm `min-release-age` to skip
  fresh releases, `npm audit signatures` for provenance, trusted publishing with OIDC when the
  repo publishes.
- Dependencies: every new package is a spec decision (decision 22); prefer the platform
  (`fetch`, `URL`, `crypto.randomUUID`, `node:test` is not used here but exists) over a
  micro-package.

## CI

`references/ci.md`: one job with `pnpm/action-setup` then `actions/setup-node` (`cache: pnpm`),
`pnpm install --frozen-lockfile`, type check, lint, vitest with coverage, audit; SHAs dated there.

## Pitfalls

1. `moduleResolution: bundler` with `module: nodenext` (or the reverse): the pair must match
   the runtime.
2. `import { X }` of a type without `type`: fails under `verbatimModuleSyntax` and in strip-types
   Node.
3. `enum` and `namespace` in code run by Node directly: not erasable, needs a transform.
4. Floating promises in event handlers and `forEach(async …)`: use `for … of` with `await`.
5. `process.env.X!`: non-null assertions on env; read env once into a validated config object.
6. `tsc` on a Vite app without `noEmit`: emits beside sources.
7. `npm install` in CI without a lockfile check: drifts silently; use `npm ci` or
   `pnpm install --frozen-lockfile`.

## Do not

- Do not add a dependency the spec does not name; do not run two linters or two formatters.
- Do not loosen `strict` or add `// @ts-ignore` without an issue reference; prefer
  `// @ts-expect-error` with a reason when a workaround is unavoidable.
- Do not bump Node or TypeScript majors as a side effect of a task; report the gap.
