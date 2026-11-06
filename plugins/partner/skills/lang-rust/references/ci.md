# Rust — minimal CI job

One job: fmt, clippy, tests with the 85 % coverage gate, cargo-deny. Uses the runner's
preinstalled `rustup` instead of a toolchain action (one less third-party dependency).

- [verified 2026-11-06 · src: https://github.com/actions/checkout/releases/tag/v7.0.1] actions/checkout v7.0.1 = `3d3c42e5aac5ba805825da76410c181273ba90b1`
- [verified 2026-11-06 · src: https://github.com/Swatinem/rust-cache/releases/tag/v2.9.3] Swatinem/rust-cache v2.9.3 = `d1527c8f67ef9af357290475d4af4b0fab8f12e0`
- [verified 2026-11-06 · src: https://github.com/taiki-e/install-action/releases/tag/v2.90.1] taiki-e/install-action v2.90.1 = `c509219cf42fba86913069efd0ade2458c59337b`
- [verified 2026-11-06 · src: https://github.com/EmbarkStudios/cargo-deny-action/releases/tag/v2.1.1] EmbarkStudios/cargo-deny-action v2.1.1 = `3c6349835b2b7b196a839186cb8b78e02f7b5f25` (bundles cargo-deny 0.20.2; default `command: check`)
- [verified 2026-11-06 · src: https://github.com/actions/runner-images] `ubuntu-24.04` = `ubuntu-latest`; ships rustup 1.29.2 and Rust 1.99.1.

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
  rust:
    runs-on: ubuntu-24.04
    env:
      CARGO_TERM_COLOR: always
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - name: Toolchain
        # honours rust-toolchain.toml when present
        run: |
          rustup toolchain install stable --profile minimal -c rustfmt,clippy,llvm-tools-preview
          rustup default stable
      - uses: Swatinem/rust-cache@d1527c8f67ef9af357290475d4af4b0fab8f12e0 # v2.9.3
      - uses: taiki-e/install-action@c509219cf42fba86913069efd0ade2458c59337b # v2.90.1
        with:
          tool: cargo-llvm-cov
      - run: cargo fmt --all --check
      - run: cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
      - run: cargo llvm-cov --workspace --all-features --locked --fail-under-lines 85
      - run: cargo test --workspace --doc --locked
      - uses: EmbarkStudios/cargo-deny-action@3c6349835b2b7b196a839186cb8b78e02f7b5f25 # v2.1.1
```

Notes

- `cargo llvm-cov` runs the test suite; do not also run `cargo test` for unit/integration tests.
  Doc tests are excluded from llvm-cov on stable, hence the separate `--doc` step.
- With a `rust-toolchain.toml`, rustup installs the pinned channel on first `cargo` call;
  add its components there.
- Declared MSRV: add a second job or step `cargo +<msrv> check --workspace --locked`.
- Keep the SHAs current with Dependabot (`package-ecosystem: github-actions`); it updates the
  version comment too.
