# React — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale fw-react`).

## Packages

- [verified 2026-11-10 · src: https://github.com/react/react/releases/tag/v19.3.1] react and react-dom 19.3.1 (2026-10-14); 19.2.9 patches the 19.2 line the same day; `facebook/react` now redirects to `react/react`.
- [verified 2026-11-10 · src: https://github.com/remix-run/react-router/releases/tag/react-router%408.5.1] react-router 8.5.1 (2026-10-27); 8.0.0 shipped 2026-06-17; 7.18.5 is still maintained.
- [verified 2026-11-10 · src: https://github.com/TanStack/query/releases/tag/release-2026-11-06-2304] @tanstack/react-query 5.107.1 (2026-11-06).
- [verified 2026-11-10 · src: https://github.com/testing-library/react-testing-library/releases/tag/v16.3.3] @testing-library/react 16.3.3 (2026-08-27); [verified 2026-11-10 · src: https://github.com/testing-library/user-event/releases] @testing-library/user-event 14.6.9 (2026-11-10).
- [verified 2026-11-10 · src: https://github.com/vitest-dev/vitest/releases/tag/v5.1.0] vitest 5.1.0 (2026-11-02), `--last-failed` new; [verified 2026-11-10 · src: https://github.com/vitejs/vite/releases/tag/v8.3.7] vite 8.3.7 (2026-11-09).
- [verified 2026-11-10 · src: https://github.com/react/react/releases/tag/eslint-plugin-react-hooks@7.1.1] eslint-plugin-react-hooks 7.1.1 (2026-04-17); 7.1.0 added ESLint 10.
- [reported 2026-11-10 · src: https://react.dev/learn/react-compiler/introduction] React Compiler is stable per react.dev; no GitHub release names a version.

## React Router 8 against 7

- [verified 2026-11-10 · src: https://github.com/remix-run/react-router/blob/main/CHANGELOG.md#v800] `react-router-dom` is gone (import from `react-router`, `RouterProvider` and `HydratedRouter` from `react-router/dom`); ESM-only; Node 22.22+, React 19.2.7+, Vite 7+; middleware always on, `context` is a `RouterContextProvider`; `meta` reads `loaderData`; `splitRouteModules` top-level, on by default.
- [verified 2026-11-10 · src: https://github.com/remix-run/react-router/blob/main/CHANGELOG.md#v850] 8.5 deprecates its own view-transition APIs for React's `<ViewTransition>`.
