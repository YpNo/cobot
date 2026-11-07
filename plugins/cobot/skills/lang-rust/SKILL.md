---
name: lang-rust
description: >-
  Senior Rust developer knowledge for this cobot: verified toolchain versions, the exact
  fmt/clippy/test/coverage/audit/build commands, current idiom (edition 2024, errors, async,
  ownership), project shape for small crates, test rules, unsafe and supply-chain policy,
  pitfalls. Applies whenever Rust files are read or changed — `**/*.rs`, `**/Cargo.toml`,
  `**/Cargo.lock`, `**/rust-toolchain.toml` — and is preloaded into the rust-builder agent.
  Use it before writing, reviewing or testing Rust code, adding a crate, or touching Rust CI.
  Versions and sources live in references/versions.md; the CI job in references/ci.md.
paths:
  - "**/*.rs"
  - "**/Cargo.toml"
  - "**/Cargo.lock"
  - "**/rust-toolchain.toml"
user-invocable: false
---

# lang-rust

Versions, dates and sources: `references/versions.md`. Re-verify a line the brief flags stale (versions after 30 days, idiom after 90)
before relying on it; never "upgrade" a repo as a side effect — report the gap.

## Toolchain and commands

- [verified 2026-11-06 · src: https://github.com/rust-lang/rust/releases] stable is 1.99.1; next release lands every six weeks.
- Repo pins win: read `rust-toolchain.toml` and `rust-version` before assuming stable.

| step | command |
|---|---|
| format | `cargo fmt --all --check` (fix: drop `--check`) |
| lint | `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings` |
| test (focused) | `cargo test -p <crate> <name_filter>` |
| test (all) | `cargo test --workspace --all-features --locked` |
| coverage | `cargo llvm-cov --workspace --all-features --locked --fail-under-lines 85` |
| audit | `cargo deny check` (advisories, bans, licenses, sources; config in `deny.toml`, start with `cargo deny init`) |
| build | `cargo build --workspace --release --locked` |
| MSRV check | `cargo +<rust-version> check --workspace --locked` when `rust-version` is declared |

- Lock file: `Cargo.lock` is committed for binaries **and** libraries; every CI command takes `--locked`.
- `cargo-deny` replaces `cargo-audit` (same RustSec database, plus licenses/bans/sources). One tool, not both.
- Lints live in `Cargo.toml` `[lints]` / `[workspace.lints]`, not in scattered `#![deny]` attributes.

## Idiom

- Edition 2024 for new crates; declare `rust-version`. The 2024 resolver is MSRV-aware: it
  will not pick a dependency newer than your `rust-version` allows.
- Errors: `thiserror` enums in libraries (callers match on variants); `anyhow` only in
  binaries/`main`, with `.context("doing X")` at every boundary crossing. Never return
  `anyhow::Error` from a library's public API. Never `Box<dyn Error>` in new code.
- `unwrap`/`expect` only in tests, `main` setup, or on a proven invariant with the reason in
  the `expect` message. Library crates: `clippy::unwrap_used = "deny"`.
- `?` everywhere; map foreign errors at the adapter edge with `#[from]` or `map_err`, never
  leak `sqlx::Error`/`reqwest::Error` through a domain type.
- Let chains (`if let Some(x) = a && cond`) over nested `if let`; `let … else` for early exit.
- Newtypes for IDs, units and validated input; constructors enforce invariants (`TryFrom`).
- Ownership: borrow by default; take `impl AsRef<str>`/`&str` in, return owned out. `clone()`
  is fine on `Arc` and small `Copy`-like data, a smell on large owned data in loops.
- Statics: `std::sync::LazyLock`/`OnceLock`. `lazy_static` and `once_cell` are legacy.
- Shared state: `Arc<Mutex<T>>` with `std::sync::Mutex` unless the guard crosses `.await`
  (then `tokio::sync::Mutex`, or restructure). Prefer message passing (`mpsc`) for ownership hand-off.

### Async

- Runtime: `tokio`, only when there is real I/O concurrency. A CLI that makes three HTTP
  calls does not need async; use a blocking client.
- `async fn` in traits is stable: use it for static dispatch. It is not dyn-compatible and
  carries no `Send` bound — for `dyn Trait` keep `async-trait`; for a `Send` public trait use
  `trait-variant` or write `fn f(&self) -> impl Future<Output = T> + Send`.
- Never block a runtime thread: `spawn_blocking` for CPU or sync I/O; no `std::thread::sleep`.
- Cancellation: `tokio_util::sync::CancellationToken` + `select!`; every spawned task has an
  owner (`JoinSet`) and an exit path. A detached `tokio::spawn` with no handle is a leak.
- Keep the domain sync; async belongs at the ports.

## Project shape

- One crate until a second binary, a published library, or compile times force a split.
  Then a workspace with `crates/<name>`; shared deps in `[workspace.dependencies]`.
- Hexagonal split pays when there are ≥ 2 real adapters for a port (Postgres + in-memory,
  HTTP + CLI) or the domain logic is worth testing without I/O. It does not pay for a CLI
  wrapper, a glue binary, or a library with one backend: modules (`domain`, `io`) suffice.
- When split: the domain crate depends on `std` + `thiserror` only; traits (ports) live
  there; `main.rs` is the only place concrete adapters are wired.
- No `utils`/`common` module. Name modules after what they provide.

## Tests

- Name: `unit_scenario_expected` — `parse_config_missing_port_returns_error`.
- Unit tests in `#[cfg(test)] mod tests` beside the code; integration tests in `tests/*.rs`
  against the public API only; doc tests for every public example.
- Table-driven: a `const CASES: &[(&str, Expected)]` or array of structs, loop with the case
  name in the assertion message; or `rstest` `#[case]` if the crate already uses it.
- Property tests (`proptest`) for parsers, codecs and anything with an inverse.
- Snapshots (`insta`) for large structured output; review with `cargo insta review`.
- Coverage floor 85 % lines, measured by `cargo-llvm-cov` (`--fail-under-lines 85`).
  Exclude `main.rs`/generated code with `--ignore-filename-regex`, not by lowering the floor.
- Never mock what you own: hand-written in-memory adapters for ports. Never mock the
  database, the filesystem (`tempfile`) or HTTP (`wiremock`/a local server) in integration
  tests. `mockall` is a last resort for third-party traits.
- Overflow: release builds wrap silently. Test arithmetic at full scale; use `checked_*`/
  `saturating_*` or widen where the range is not proven.

## Security

- `unsafe_code = "forbid"` in `[lints.rust]` for every crate that does not need FFI or
  hand-rolled data structures (equivalent to `#![forbid(unsafe_code)]`, but in one place).
- Where `unsafe` is needed: isolate it in one module, `// SAFETY:` on every block stating the
  invariant, `unsafe_op_in_unsafe_fn` (warn by default in 2024) kept on, and a Miri run
  (`cargo +nightly miri test`) in CI for that module.
- Supply chain: `cargo deny check` on every CI run; `deny.toml` denies unknown registries and
  git sources, lists allowed licenses, and flags unmaintained crates. Ignore an advisory only
  with an ID, a reason and a date.
- New dependency: check maintenance, downloads, `unsafe` footprint and transitive count
  (`cargo tree -e normal -p <crate>`) before adding. Disable default features you do not use.
- TLS: `rustls`, not `openssl`/`native-tls`, unless the platform requires it.
- Secrets: wrap in a type whose `Debug` redacts (`secrecy::SecretString`); never `#[derive(Debug)]`
  on a struct holding a token. Never log request bodies or headers wholesale.
- Untrusted input: bound sizes before allocating (`take(n)`, body limits); `serde` with
  `#[serde(deny_unknown_fields)]` at trust boundaries.
- Commands: `std::process::Command::new(bin).args([...])`, never `sh -c` with interpolation.

## CI

One minimal job (fmt, clippy, test + coverage gate, cargo-deny), actions pinned to verified
SHAs: `references/ci.md`.

## Pitfalls

1. `std::sync::MutexGuard` held across `.await` — compiles in some cases, deadlocks or makes the future `!Send`.
2. `tokio::spawn` without keeping the `JoinHandle` — panics and errors vanish.
3. `RUSTFLAGS=-Dwarnings` in CI invalidates the build cache; use `-- -D warnings` on clippy or `CARGO_BUILD_WARNINGS=deny` (see versions.md).
4. Missing `--locked` — CI silently resolves a different graph than the developer.
5. `impl Trait` in return position captures all generic lifetimes in 2024; add `use<..>` to narrow.
6. Feature unification: a dev-dependency enabling a feature hides a missing feature in the real build — test with `--no-default-features` too.
7. `as` casts truncate silently; use `TryFrom` for any narrowing conversion.
8. `#[derive(Debug)]` on secrets leaks them through `tracing` and `anyhow` chains.
9. Blocking DNS/file I/O inside async handlers — use `tokio::fs`/`spawn_blocking`.
10. `async fn` in a public trait without deciding `Send` — a breaking change to fix later.

## Do not

- Add `async-trait` for a trait used only generically.
- Use `cargo-audit` alongside `cargo-deny`, or `lazy_static`, `failure`, `once_cell` in new code.
- Silence clippy crate-wide; `#[expect(clippy::x, reason = "...")]` on the item instead.
- Commit `unsafe` without a `// SAFETY:` comment and a test that exercises it.
- Bump edition, MSRV or a major dependency as part of an unrelated change.
