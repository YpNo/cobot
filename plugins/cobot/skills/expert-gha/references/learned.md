# expert-gha — learned lines

Promoted by `cobot-memory learn --promote`; move a line to its topical file at review.
Format: `- [status YYYY-MM-DD · src: <url or exp: command>] claim`.

- [verified 2026-11-07 · src: https://docs.github.com/en/actions/concepts/security/secrets] GitHub states automatic redaction 'is not guaranteed' because a secret can be transformed in many ways, and the runner can only redact secrets used within the current job.
- [verified 2026-11-07 · src: https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference] In the Dependabot options reference only `groups.dependency-type` is restricted by ecosystem (bundler, composer, mix, maven, npm, pip); `patterns`, `exclude-patterns`, `update-types` and `applies-to` (version-updates default, or security-updates) carry no ecosystem restriction. `dependency-type` is therefore unusable for github-actions groups.
- [verified 2026-11-15 · src: exp: zizmor --offline --persona pedantic .github/workflows/ci.yml] zizmor v1.32.0 in the auditor and pedantic personas reports only anonymous-definition (info) for unnamed jobs; since zizmor-action defaults to `version: latest`, set its `version:` input to the CLI version the local audit ran, so CI and local audits agree.
- [verified 2026-11-15 · src: exp: a GitHub Actions run on ubuntu-24.04, step log of `rustup toolchain install`] On the ubuntu-24.04 image, `rustup toolchain install` with no arguments reads rust-toolchain.toml (channel and components): a `channel = "stable"` file installed the newest stable (1.100.0) with its listed components (llvm-tools present for cargo-llvm-cov). A floating channel therefore moves with each Rust release; pin it to keep CI and the local proof on one toolchain.
