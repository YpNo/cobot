# Rust — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days, idiom after 90 (`partner-memory knowledge --stale lang-rust`).

## Toolchain

- [verified 2026-11-06 · src: https://github.com/rust-lang/rust/releases] Rust stable 1.99.1 (2026-10-16); 1.99.0 on 2026-10-01; six-week cadence.
- [verified 2026-11-06 · src: https://blog.rust-lang.org/releases/] No edition newer than 2024 announced; 2024 is current.
- [verified 2026-11-06 · src: https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/] Edition 2024 stable since 1.85.0: `unsafe extern`, `unsafe_op_in_unsafe_fn` warns, `gen` reserved, new RPIT capture rules, MSRV-aware resolver default, tail-expression and `if let` temporary rescoping; async closures (`AsyncFn*`) stable.
- [verified 2026-11-06 · src: https://blog.rust-lang.org/2025/06/26/Rust-1.88.0/] Let chains stable in 1.88.0, edition 2024 only; Cargo auto-GC of `~/.cargo` cache.
- [verified 2026-11-06 · src: https://blog.rust-lang.org/2024/09/05/Rust-1.81.0/] `#[expect(lint, reason = "...")]` stable since 1.81.0.
- [verified 2026-11-06 · src: https://blog.rust-lang.org/2023/11/16/Rust-1.74.0/] `[lints]` table in `Cargo.toml` stable since 1.74.0.
- [verified 2026-11-06 · src: https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/] `async fn` / RPITIT in traits stable since 1.75; not dyn-compatible; `trait-variant` for `Send` variants, `async-trait` for `dyn`.
- [verified 2026-11-06 · src: https://blog.rust-lang.org/2026/07/09/Rust-1.97.0/] `CARGO_BUILD_WARNINGS=allow|warn|deny` (1.97) controls warnings without invalidating the build cache.
- [verified 2026-11-06 · src: https://blog.rust-lang.org/2026/10/01/Rust-1.99.0/] 1.99 adds C-variadic fns, `Vec::into_parts`/`from_parts`, `std::fs::set_times`; no edition change.

## Tools

- [verified 2026-11-06 · src: https://github.com/EmbarkStudios/cargo-deny/releases] cargo-deny 0.20.2 (2026-07-09); `cargo deny check advisories` uses RustSec advisory-db.
- [verified 2026-11-06 · src: https://embarkstudios.github.io/cargo-deny/checks/advisories/index.html] Unmaintained advisories are errors by default; `[advisories] unmaintained = "workspace"` limits to direct deps.
- [verified 2026-11-06 · src: https://github.com/taiki-e/cargo-llvm-cov/releases] cargo-llvm-cov 0.9.1 (2026-09-06); `--fail-under-lines <MIN>`, `--ignore-filename-regex`; `--doctests` is unstable (nightly), so doc tests run separately.
- [verified 2026-11-06 · src: https://crates.io/crates/cargo-nextest] cargo-nextest 0.9.151 — optional faster runner; doc tests still need `cargo test --doc`.
- [verified 2026-11-06 · src: https://crates.io/crates/cargo-semver-checks] cargo-semver-checks 0.51.0 — run before publishing a library release.

## Crates (current stable on crates.io)

| crate | version | updated | note |
|---|---|---|---|
| thiserror | 2.0.21 | 2026-09-23 | library errors |
| anyhow | 1.0.104 | 2026-07-18 | binary errors |
| tokio | 1.54.1 | 2026-10-21 | runtime |
| tokio-util | 0.7.20 | 2026-10-09 | `CancellationToken` |
| async-trait | 0.1.92 | 2026-08-08 | `dyn` async traits only |
| trait-variant | 0.1.3 | 2026-07-22 | `Send` variant of async traits |
| proptest | 1.12.0 | 2026-10-10 | property tests |
| insta | 1.49.0 | 2026-10-03 | snapshots |
| secrecy | 0.10.3 | 2024-10-09 | dormant (> 6 months) but small and stable; acceptable, re-check |

- [verified 2026-11-06 · src: https://crates.io/api/v1/crates/<name>] all rows above, `max_stable_version`.

## Local machine (not upstream)

- [verified 2026-11-06 · exp: rustc --version] workstation has 1.99.0, one patch behind stable.
