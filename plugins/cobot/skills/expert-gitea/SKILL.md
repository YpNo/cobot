---
name: expert-gitea
description: >-
  Gitea: how it works, how it differs from GitHub and GitLab (Actions compatibility and gaps,
  packages, mirrors, protection, webhooks, AGit flow, OIDC), its API and token scopes, the gt CLI
  (tea is archived) under the gate, and contributing to go-gitea/gitea. Use on .gitea/, a
  gitea.com remote or forge: gitea, and for Gitea contributions.
paths:
  - ".gitea/**"
user-invocable: false
---

# expert-gitea

CONTEXT.md and the governance file override it; in a contribution, go-gitea/gitea's own
CONTRIBUTING.md wins (onboard the clone with `/cobot:onboard --foreign` so its rules land in
Constraints). Versions and dated facts: `references/versions.md`. Pipelines in general:
`expert-cicd`; the GitHub Actions idiom Gitea reuses: `expert-gha`.

## What Gitea is

- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/README.md] One Go binary bundling Git hosting, review, issues, kanban, wiki, a package registry and Actions that reuse GitHub Actions; MIT; gitea.com is a free hosted instance with limits, Gitea Cloud offers dedicated ones.
- [verified 2026-11-10 · src: https://gitea.com/gitea/docs/src/branch/main/docs/installation/database-preparation.md] Databases: PostgreSQL 12+, MySQL 8.0+, MariaDB 10.4+, SQLite built in, MSSQL 2012 SP4+.
- [verified 2026-11-10 · src: https://gitea.com/gitea/docs/src/branch/main/docs/index.md] Gitea began as a fork of Gogs; Forgejo is a community fork of Gitea since late 2022 (reported).

## Against GitHub and GitLab

- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/v28.3.0/custom/conf/app.example.ini] Workflows: `WORKFLOW_DIRS = .gitea/workflows,.github/workflows`; only the first that exists is used, so a `.gitea/workflows` folder hides `.github/workflows`.
- [verified 2026-11-10 · src: https://docs.gitea.com/usage/actions/comparison] Actions differences: context availability is not checked; `jobs.<id>.environment` is ignored (no approval gate); problem matchers and annotations are ignored; `GITEA_TOKEN` cannot publish packages; additions are absolute `uses:` URLs, `self:` and `builtin:`, Go actions, `@daily` schedules.
- [verified 2026-11-10 · src: https://docs.gitea.com/usage/actions/comparison] Unsupported token scopes in 28.x: `id-token`, `statuses`, `checks`, `deployments`, `pages`; Gitea adds `code`, `releases`, `wiki`, `projects`. So no keyless cloud auth or keyless signing from Actions until 29.0 (OIDC merged for 29.0.0).
- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/tree/v28.3.0/services/actions] Reusable workflows (up to 10 deep) and `concurrency` work in 28.3; since 28.0 a public repository cannot call a private reusable workflow.
- [verified 2026-11-10 · src: https://gitea.com/gitea/docs/src/branch/main/docs/usage/packages/overview.md] Package registry: Alpine, Arch, Cargo, Chef, Composer, Conan, Conda, Container (OCI), CRAN, Debian, Generic, Go, Helm, Maven, npm, NuGet, Pub, PyPI, RPM, RubyGems, Swift, Terraform state and modules, Vagrant.
- [verified 2026-11-10 · src: https://gitea.com/gitea/docs/src/branch/main/docs/usage/repository/repo-mirror.md] Pull mirrors are set up only at repository creation; push mirrors force-push and can sync on every push.
- [verified 2026-11-10 · src: https://gitea.com/gitea/docs/src/branch/main/docs/usage/access-control/protected-branches.md] Branch protection: glob patterns (first match wins), push, force-push and merge allowlists, required approvals with stale handling, CODEOWNERS, protected file patterns, required checks by glob (`actions/test-*`).
- [verified 2026-11-10 · src: https://gitea.com/gitea/docs/src/branch/main/docs/usage/issues-prs/agit.md] AGit flow opens a PR without a fork: `git push origin HEAD:refs/for/main -o topic=<name>` (server Git 2.29+).
- [verified 2026-11-10 · src: https://gitea.com/gitea/docs/src/branch/main/docs/usage/repository/webhooks.md] Webhooks at repository, organisation, user and system scope; Gitea, Gogs, Slack, Discord, Teams, Matrix and more.
- [verified 2026-11-10 · src: https://gitea.com/gitea/docs/src/branch/main/docs/development/oauth2-provider.md] Gitea is an OAuth2 and OIDC provider (`/.well-known/openid-configuration`), granular scopes since 1.23.
- [verified 2026-11-10 · src: https://blog.gitea.com/release-of-28.0.0/] 28.0 added audit logging, bot accounts, HTTPS deploy tokens, user impersonation and code-owner approval rules.

## API and CLI

- [verified 2026-11-10 · src: https://gitea.com/gitea/docs/src/branch/main/docs/development/api-usage.md] Swagger UI at `/api/swagger`, spec at `/swagger.v1.json`; `Authorization: token …`; scopes `read:` or `write:` on activitypub, admin, commitstatus, issue, misc, notification, organization, package, repository, user. Ask for the narrowest.
- [verified 2026-11-10 · src: https://gitea.com/gitea/cli/src/branch/main/docs/migrating-from-tea.md] Use gt: singular resources (`gt pr`, `gt issue`, `gt release`, `gt repo`), `list` answers to `ls` and `delete` to `rm`, `--json` with `--jq`; `tea pulls approve` is `gt pr review --approve`; log in with `gt auth login`.
- Under the gate (aliases rewritten first): `gt release create|publish`, `gt repo delete`,
  `gt api -X DELETE`, a PR text with an attribution line are never run; PR, issue, comment,
  review, merge, repository and `api` writes ask; lists and views are silent. The same for `tea`.
- `gt` also names Graphite's stacking CLI: check `gt --version` before trusting a command.
- [verified 2026-11-10 · src: https://gitea.com/gitea/tea/src/branch/main/modules/config/config.go] tea kept tokens in `$XDG_CONFIG_HOME/tea/config.yml` (or `~/.tea/tea.yml`); read neither.

## Contributing to go-gitea/gitea

- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/CONTRIBUTING.md] Issues and PRs on GitHub go-gitea/gitea; docs PRs at gitea.com/gitea/docs; security reports to `security@gitea.io`; a significant feature needs a proposal first.
- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/CONTRIBUTING.md] PR titles are Conventional Commits (`type(scope)!: subject`; types include `enhance`), squash-merged; the first comment is the summary; screenshots for UI changes; a `## :warning: BREAKING :warning:` section; one `Fixes #N` per line; no rebase once review started.
- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/CONTRIBUTING.md] AI-assisted contributions must be disclosed, reviewed, tested and understood; undisclosed or low-quality AI content may be closed. Opening a PR is the DCO sign-off; no CLA.
- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/CONTRIBUTING.md] Run `make fmt`, then `make lint` (or `lint-backend`, `lint-frontend`) and the matching tests; translations only through Crowdin (edit `options/locale/locale_en-US.json` alone); new files carry the Gitea copyright and `SPDX-License-Identifier: MIT` header.
- [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/docs/community-governance.md] Two maintainer approvals, giteabot labels, a milestone before merge, the merge queue; [verified 2026-11-10 · src: https://github.com/go-gitea/gitea/blob/main/docs/release-management.md] backports through `backport/<version>` labels, fixes only.

## Do not

- Do not write `environment:` approval gates, keyless cosign or `id-token` jobs for Gitea 28:
  they are ignored or unsupported; say so instead.
- Do not install or update tea; propose gt.
- Do not open a go-gitea PR without the AI disclosure its CONTRIBUTING.md requires.
