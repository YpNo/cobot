# Actions — pinned versions

Latest stable release per action, resolved through the GitHub API on the check date
(`gh api repos/<r>/releases/latest`, then `gh api repos/<r>/commits/<tag> --jq .sha`).
Pin as `uses: <owner>/<repo>@<sha> # <tag>`. Re-resolve before relying on a row older than 90 days.

| action | tag | commit SHA | released | source |
|---|---|---|---|---|
| actions/checkout | v7.0.1 | 3d3c42e5aac5ba805825da76410c181273ba90b1 | 2026-07-20 | github.com/actions/checkout/releases |
| actions/setup-python | v7.1.0 | 6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 | 2026-10-22 | github.com/actions/setup-python/releases |
| actions/setup-go | v7.0.0 | b7ad1dad31e06c5925ef5d2fc7ad053ef454303e | 2026-07-16 | github.com/actions/setup-go/releases |
| actions/setup-node | v7.1.0 | 949feb2413d6458794dcd2491c4babbbce0c15c1 | 2026-10-08 | github.com/actions/setup-node/releases |
| actions/cache | v6.1.0 | 55cc8345863c7cc4c66a329aec7e433d2d1c52a9 | 2026-06-26 | github.com/actions/cache/releases |
| actions/upload-artifact | v7.0.2 | cf430e030ddbb5b0abf93d22962f4752f3646cd9 | 2026-10-07 | github.com/actions/upload-artifact/releases |
| actions/download-artifact | v8.0.2 | 9000827ccba6bdab643e8b6fd33ac0654aef8333 | 2026-10-07 | github.com/actions/download-artifact/releases |
| actions/attest | v4.2.2 | 1e69f48acb82d1966a394da916b4c1698aa569d6 | 2026-08-04 | github.com/actions/attest/releases |
| actions/attest-build-provenance | v4.2.2 | 4d101475d8b20a2381f78447822ac1eab6504dd8 | 2026-08-06 | github.com/actions/attest-build-provenance/releases |
| zizmorcore/zizmor-action | v0.8.1 | 45d7276c9ca790aabd705e31ca99c6185c3e76dd | 2026-11-03 | github.com/zizmorcore/zizmor-action/releases |
| DavidAnson/markdownlint-cli2-action | v25.0.0 | 696eb3f2509270d7b882d2aa68347bc676e7af34 | 2026-10-25 | github.com/DavidAnson/markdownlint-cli2-action/releases |
| Swatinem/rust-cache | v2.9.3 | d1527c8f67ef9af357290475d4af4b0fab8f12e0 | 2026-10-20 | github.com/Swatinem/rust-cache/releases |
| EmbarkStudios/cargo-deny-action | v2.1.1 | 3c6349835b2b7b196a839186cb8b78e02f7b5f25 | 2026-07-13 | github.com/EmbarkStudios/cargo-deny-action/releases |
| taiki-e/install-action | v2.90.1 | c509219cf42fba86913069efd0ade2458c59337b | 2026-11-04 | github.com/taiki-e/install-action/releases |
| golangci/golangci-lint-action | v9.3.0 | ba0d7d2ec06a0ea1cb5fa41b2e4a3ab91d21278a | 2026-06-29 | github.com/golangci/golangci-lint-action/releases |
| astral-sh/setup-uv | v10.3.3 | 68559e99cc807c1eb7e9238fd43a15bba460eec2 | 2026-10-28 | github.com/astral-sh/setup-uv/releases |
| hashicorp/setup-terraform | v4.0.1 | dfe3c3f87815947d99a8997f908cb6525fc44e9e | 2026-05-12 | github.com/hashicorp/setup-terraform/releases |
| google-github-actions/auth | v3.0.0 | 7c6bc770dae815cd3e89ee6cdf493a5fab2cc093 | 2025-08-28 | github.com/google-github-actions/auth/releases |
| step-security/harden-runner | v2.22.3 | 46b06cea07f9e64621fdf066ba77ac6915163d43 | 2026-10-27 | github.com/step-security/harden-runner/releases |
| docker/setup-buildx-action | v4.4.1 | f87e5991a6d7451dcb8d9637bfbc97413f497069 | 2026-09-16 | github.com/docker/setup-buildx-action/releases |
| docker/login-action | v4.8.0 | 8aa5831fb8d48d8f76594c7ddde61ae58019f550 | 2026-11-05 | github.com/docker/login-action/releases |
| docker/build-push-action | v7.4.0 | c3c9e263c25d99ce0380d002d59b67737d91b0dc | 2026-09-15 | github.com/docker/build-push-action/releases |
| sigstore/cosign-installer | v4.1.3 | 756fe2d284c7292c4e9b62c8a28f1e5629c59532 | 2026-11-04 | github.com/sigstore/cosign-installer/releases |
| softprops/action-gh-release | v3.0.4 | 8a0cd651e5b2365bd640854a3fa5dfc70e4875f3 | 2026-11-05 | github.com/softprops/action-gh-release/releases |
| rhysd/actionlint (binary, not an action) | v1.7.12 | 914e7df21a07ef503a81201c76d2b11c789d3fca | 2026-03-30 | github.com/rhysd/actionlint/releases |

- [verified 2026-11-06 · src: exp: gh api repos/<r>/releases/latest + commits/<tag>] every row above.
- [verified 2026-11-06 · src: https://github.com/actions/attest-build-provenance/releases] attest-build-provenance v4 is a wrapper over actions/attest; new workflows use actions/attest.
- [verified 2026-11-06 · src: exp: gh api repos/google-github-actions/auth/commits] auth: latest release v3.0.0 (2025-08-28) but main has commits through 2026-07-29 — maintained, release cadence slow; re-check before pinning.
- [verified 2026-11-06 · src: exp: gh api repos/astral-sh/setup-uv/git/matching-refs/tags/v10] setup-uv publishes only full `vX.Y.Z` tags, no moving major tag — Dependabot still bumps the SHA.
- [verified 2026-11-06 · src: exp: gh api repos/dtolnay/rust-toolchain/releases/latest] dtolnay/rust-toolchain is selected by branch (`@stable`), last release v1 2022 — prefer `rustup` from `rust-toolchain.toml`; it is on the runner image.
- [verified 2026-11-06 · src: https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md] ubuntu-24.04 image ships Rustup 1.29.2, Rust 1.99.1, GitHub CLI 2.103.2.
- [verified 2026-11-06 · src: https://github.com/actions/runner-images] `ubuntu-latest` = ubuntu-24.04; ubuntu-26.04, `-arm` variants and `ubuntu-slim` are also offered.
- [verified 2026-11-06 · src: https://github.com/zizmorcore/zizmor/releases] zizmor CLI v1.32.0 (2026-11-02); zizmor-action defaults `version: latest`.
- [verified 2026-11-06 · src: https://github.com/cli/cli/releases] gh CLI v2.103.3 (2026-10-26).

## Built-in caching of setup actions (prefer over actions/cache)

- [verified 2026-11-06 · src: https://github.com/actions/setup-go/blob/main/action.yml] setup-go `cache` defaults to `true` (keyed on go.sum).
- [verified 2026-11-06 · src: https://github.com/actions/setup-node/blob/main/action.yml] setup-node `package-manager-cache` defaults to `true` when package.json `packageManager` names npm; else `cache: npm|yarn|pnpm`.
- [verified 2026-11-06 · src: https://github.com/actions/setup-python/blob/main/action.yml] setup-python `cache: pip|pipenv|poetry`, off by default.
- [verified 2026-11-06 · src: https://github.com/astral-sh/setup-uv/blob/main/action.yml] setup-uv `enable-cache: auto` skips caching on release, tag push, `pull_request_target` and `workflow_run`.
- [verified 2026-11-06 · src: https://github.com/hashicorp/setup-terraform/blob/main/action.yml] setup-terraform `terraform_wrapper` defaults to `true`; set `false` when parsing `terraform` output.
