# Gitea — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days,
idiom after 90 (`cobot-memory knowledge --stale expert-gitea`).

## Releases and tools

- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/releases/tag/v28.3.0] Gitea 28.3.0 (2026-11-01) is the latest stable; 28.0.0 shipped 2026-09-29, 1.27.3 on 2026-08-29.
- [verified 2026-11-10 · src: https://blog.gitea.com/release-of-28.0.0/] Gitea dropped the historical `1.` prefix: 28.0.0 follows 1.27.
- [verified 2026-11-10 · src: https://gitea.com/gitea/runner] The Actions runner moved from gitea/act_runner to gitea/runner; latest 5.4.1 (2026-11-05).
- [verified 2026-11-10 · src: https://gitea.com/api/v1/repos/gitea/tea] tea 0.16.0 (2026-09-10) is the last release; the repository was archived on 2026-10-29.
- [verified 2026-11-10 · src: https://blog.gitea.com/release-of-gitea-cli-1.0.0/] No more tea releases, fixes or security updates; its successor is gt (gitea.com/gitea/cli) for Gitea 28 and later; gt 1.2.0 (2026-11-09).
- [verified 2026-11-10 · src: https://gitea.com/gitea/cli/src/branch/main/skills/gt/SKILL.md] gt ships an official agent skill (`skills/gt`).
- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/pull/39052] OIDC workload identity for Actions merged 2026-10-18 for 29.0.0: not in 28.3.0.

## Contributing

- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/go.mod] go-gitea/gitea builds with Go 1.27 (toolchain go1.27.3); [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/package.json] Node 22.18 or newer, pnpm 12.17 or newer; the frontend is Vue 3.5, Vite 8, TypeScript 6.
- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/Makefile] No `make test`: `test-backend`, `test-frontend`, `test-integration`, `test-migration`; `generate-swagger`, `swagger-check`, `lint-swagger`.
