---
name: fw-react
description: >-
  Senior React 19 on lang-typescript: components and hooks rules, the React Compiler, effects you
  do not need, forms and Actions, React Router 8 loaders and actions, TanStack Query, Testing
  Library with Vitest, XSS sinks. Use on *.tsx, *.jsx, a package.json with react, in
  typescript-builder when the brief names it, before writing or reviewing React.
paths:
  - "**/*.tsx"
  - "**/*.jsx"
user-invocable: false
---

# fw-react

Thin on purpose: TypeScript, Node, pnpm, Vitest and lint ground is `lang-typescript`; this skill
holds only what React changes. CONTEXT.md and the governance file override it; UI quality
(contrast, focus, tokens) is `expert-ui`. Versions: `references/versions.md`; re-verify a line
the brief flags stale. Next.js is `fw-next`.

## React 19

- [verified 2026-11-10 · src: https://react.dev/reference/react/forwardRef] `ref` is a plain prop; write no new `forwardRef` (slated for deprecation).
- [verified 2026-11-10 · src: https://react.dev/blog/2024/12/05/react-19] `<Ctx value={v}>` instead of `<Ctx.Provider>`; `<title>`, `<meta>` and `<link>` in components hoist to `<head>`; a ref callback may return a cleanup, so give it a block body.
- [verified 2026-11-10 · src: https://react.dev/blog/2024/12/05/react-19] Forms: an async function as `<form action>`; `useActionState(fn, init)` gives `[state, action, isPending]`; `useOptimistic`; `useFormStatus` from `react-dom`; `useFormState` is deprecated.
- [verified 2026-11-10 · src: https://react.dev/blog/2024/12/05/react-19] `use(promise)` may run conditionally but never on a promise created during render: take it from a loader or a cache.
- [verified 2026-11-10 · src: https://github.com/react/react/releases/tag/v19.3.0] 19.3 warns in development about a conditional `use()` that looks unblocked; `<ViewTransition>` and Fragment refs are stable.

## Compiler and memoisation

- [verified 2026-11-10 · src: https://react.dev/learn/react-compiler/introduction] With the Compiler, new code relies on automatic memoisation; keep `useMemo` and `useCallback` for precise control (stable effect dependencies); do not strip existing memoisation without tests.
- [verified 2026-11-10 · src: https://react.dev/learn/react-compiler/installation] `@vitejs/plugin-react` 6 dropped the inline `babel` option: `reactCompilerPreset()` through `@rolldown/plugin-babel`; lint with eslint-plugin-react-hooks `recommended-latest`.

## Effects and state

- [verified 2026-11-10 · src: https://react.dev/learn/you-might-not-need-an-effect] Derive values during render, not with an effect and a setter; reset state with `key`; interaction logic stays in the event handler; a fetch in an effect needs an `ignore` cleanup.
- [verified 2026-11-10 · src: https://react.dev/reference/react/StrictMode] StrictMode double-invokes bodies, initialisers and effect and ref setup with cleanup in development, during hydration too since 19.3: write symmetric cleanups; never silence a double fetch with a ref.
- Hooks at the top level of components and hooks only; stable, unique `key` values from the data,
  never the index for lists that reorder.

## Data and routing

- [verified 2026-11-10 · src: https://reactrouter.com/explanation/type-safety] React Router framework mode: type routes with `import type { Route } from "./+types/<file>"`; read in `loader` or `clientLoader`, write in `action`, never in effects.
- [verified 2026-11-10 · src: https://tanstack.com/query/latest/docs/framework/react/guides/query-options] TanStack Query: `queryOptions()` factories shared by `useQuery`, `useSuspenseQuery` and `setQueryData(opts.queryKey)` keep keys typed.
- Error boundaries per route; Suspense boundaries where data streams; one source of truth for
  server state (the loader or the query cache), never a copy in `useState`.

## Tests and commands

- [verified 2026-11-10 · src: https://testing-library.com/docs/queries/about/] Query by role first, test ids last; `screen`; `findBy` for what appears later, `queryBy` to assert absence.
- [verified 2026-11-10 · src: https://testing-library.com/docs/user-event/intro] `const user = userEvent.setup()` before render, then `await user.click(…)`; prefer it to `fireEvent`.
- [verified 2026-11-10 · src: https://vitest.dev/guide/browser/] Browser mode: `test.browser` with the `playwright()` provider from `@vitest/browser-playwright`, `vitest-browser-react`, `await expect.element(…)`; jsdom or happy-dom stay fine for unit tests.
- [verified 2026-11-10 · src: https://reactrouter.com/how-to/route-module-type-safety] Type check `react-router typegen && tsc`: **typegen writes** `.react-router/types/` (gitignored, in `include` and `rootDirs`). Name it before running it.
- Read-only: the repository's linter (`eslint .` or `oxlint`; headplane uses oxlint), `vitest run`.
  Writing: `--fix`, `-u`, `--coverage`, `vite build`,
  `react-router build`, `tsc -b` (`.tsbuildinfo`).

## Security

- [verified 2026-11-10 · src: https://react.dev/reference/react-dom/components/common] `dangerouslySetInnerHTML` only with trusted, sanitised HTML, built next to the sanitiser.
- [verified 2026-11-10 · src: https://react.dev/blog/2026/09/09/react-19-3] React 19.3 passes `TrustedHTML` through, so a CSP with `require-trusted-types-for 'script'` is viable.
- [verified 2026-11-10 · src: https://github.com/react/react/blob/main/CHANGELOG.md] `javascript:` URLs are only deprecated: allowlist `http:`, `https:`, `mailto:` on user-supplied `href`, `src`, `action`.
- [verified 2026-11-10 · src: https://vite.dev/guide/env-and-mode] Every `VITE_*` variable is inlined in the client bundle: no secrets, no wider `envPrefix`.
- [verified 2026-11-10 · src: https://github.com/react/react/releases/tag/v19.3.1] Security patches ship in lockstep across 19.0–19.3: stay on the latest patch of your minor, lockfile committed.

## Do not

- Do not add `forwardRef`, `Ctx.Provider` or `useFormState` to new code.
- Do not fetch in `useEffect` when a loader or a query exists.
- Do not run a command that writes (typegen, `--fix`, `-u`, builds) without naming it.
