# Vue — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale fw-vue`).

## Packages

- [verified 2026-11-10 · src: https://github.com/vuejs/core/releases] vue 3.5.45 is the latest stable (2026-11-05).
- [verified 2026-11-10 · src: https://github.com/vuejs/core/releases] Vue 3.6 is a prerelease: 3.6.0-rc.14 (2026-10-30); beta 1 on 2025-12-23 brought Vapor parity and reactivity on alien-signals.
- [verified 2026-11-10 · src: https://github.com/vuejs/core/blob/minor/CHANGELOG.md] Vapor Mode is feature-complete in 3.6 RC, opt-in with `<script setup vapor>` or `<template vapor>` and `vaporInteropPlugin`; no Options API, `globalProperties`, `getCurrentInstance()`, `v-memo`, or Suspense in Vapor-only apps.
- [verified 2026-11-10 · src: https://github.com/vuejs/pinia/releases/tag/v4.1.0] pinia 4.1.0 (2026-10-14); Pinia 4 (2026-07-14) is ESM-only and needs `@vue/devtools-api` 8 beside it.
- [verified 2026-11-10 · src: https://github.com/vuejs/router/releases/tag/v5.4.0] vue-router 5.4.0 (2026-10-07); its one breaking change touches only the experimental API.
- [verified 2026-11-10 · src: https://github.com/vuejs/test-utils/releases] @vue/test-utils 2.5.1 (2026-09-16).
- [verified 2026-11-10 · src: https://github.com/vuejs/language-tools/releases] vue-tsc 3.3.14 (2026-10-29), TypeScript 5.0 or newer.
- [verified 2026-11-10 · src: https://github.com/vitejs/vite-plugin-vue/releases] @vitejs/plugin-vue 6.0.10 (2026-10-10).
- [verified 2026-11-10 · src: https://github.com/vuejs/eslint-plugin-vue/releases] eslint-plugin-vue 10.12.1 (2026-11-09), ESLint 8.57, 9 or 10.
- [verified 2026-11-10 · src: https://github.com/vitejs/vite/releases] vite 8.3.7; [verified 2026-11-10 · src: https://github.com/vitest-dev/vitest/releases] vitest 5.1.0.

## Router

- [verified 2026-11-10 · src: https://router.vuejs.org/guide/migration/v4-to-v5.html] 4 → 5 has no breaking change without file-based routing; v5 absorbs unplugin-vue-router (`vue-router/vite`, `vue-router/auto-routes`, types in `src/route-map.d.ts`); v6 will be ESM-only.
- [verified 2026-11-10 · src: https://router.vuejs.org/data-loaders/] Data loaders are experimental (`vue-router/experimental`, `defineBasicLoader`, `DataLoaderPlugin` installed before the router).
