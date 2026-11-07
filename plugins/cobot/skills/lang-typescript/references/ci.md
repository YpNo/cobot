# TypeScript — minimal CI job

One job: pnpm, frozen install, type check, lint, vitest with the 85 % coverage gate, audit.

- [verified 2026-11-07 · src: https://api.github.com/repos/actions/setup-node/git/ref/tags/v7.1.0] actions/setup-node v7.1.0 = `949feb2413d6458794dcd2491c4babbbce0c15c1`
- [verified 2026-11-07 · src: https://api.github.com/repos/pnpm/action-setup/git/tags/9bbca1e9dc2902adb87e8780fe5c98796985a62d] pnpm/action-setup v6.1.1 = `73e46992e05b19abd31f2f3c20e0e7370d762115` (annotated tag dereferenced)
- [verified 2026-11-07 · src: https://github.com/actions/setup-node/blob/main/docs/advanced-usage.md] setup-node's pnpm caching example runs `pnpm/action-setup` before `actions/setup-node` with `cache: pnpm` (pnpm >= 6.10.0).
- [verified 2026-11-06 · src: https://github.com/actions/checkout/releases/tag/v7.0.1] actions/checkout v7.0.1 = `3d3c42e5aac5ba805825da76410c181273ba90b1`

SHAs resolved with `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` (annotated tags dereferenced).

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  typescript:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: pnpm/action-setup@73e46992e05b19abd31f2f3c20e0e7370d762115 # v6.1.1
        # reads packageManager from package.json; add `version:` only when it is absent
      - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0
        with:
          node-version-file: package.json   # engines.node; or .nvmrc
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm run typecheck
      - run: pnpm run lint
      - run: pnpm exec vitest run --coverage --coverage.thresholds.lines=85
      - run: pnpm audit --audit-level=high
```

Notes

- Call the repository's scripts, not re-typed flags, so CI and local runs stay identical.
- Changed-area tests on a PR: `pnpm exec vitest run --changed origin/main` (needs
  `fetch-depth: 0`); the merge run executes the full suite.
- A library that publishes to npm adds a release job with `id-token: write` and
  `npm publish --provenance` (or trusted publishing); the gate denies `npm publish` locally.
- Playwright: a separate job with `pnpm exec playwright install --with-deps chromium`, only for
  the critical journeys, with `timeout-minutes` and artifacts on failure.
