# Rust rule pack

Loads for `.rs` files and applies `core.md` through Rust idioms. Rule ids are `RS-<CAT>-<nn>`. Rust removes
memory-safety bugs from safe code, not logic, crypto, injection or supply-chain bugs; give `unsafe` disproportionate
attention, because it is where the guarantee stops.

## Unsafe & memory safety

- **RS-UNSAFE-01** `unsafe` block with no `// SAFETY:` comment stating the invariant upheld. Each is a finding until
  justified.
- **RS-UNSAFE-02** `SAFETY` comment present but the invariant is not upheld by the surrounding code; read the callers.
- **RS-UNSAFE-03** Raw pointer deref, `transmute`, `from_raw_parts`, `get_unchecked`, `set_len` on a length from
  external input. `transmute` between types with differing validity invariants is UB.
- **RS-UNSAFE-04** `unsafe impl Send`/`Sync`: asserts thread safety the compiler could not prove. Verify by hand.
- **RS-UNSAFE-05** Crate that needs no `unsafe` but lacks `#![forbid(unsafe_code)]`. Low severity; high leverage.
- **RS-UNSAFE-06** FFI boundary: C string without NUL guarantee, buffer length in the wrong unit (bytes vs
  elements), callback that can unwind across the boundary (UB; needs `catch_unwind`).

## Panics & error handling

- **RS-PANIC-01** `unwrap()`/`expect()` in library or handler code reachable from external input. A panic aborts
  the request task; with `panic = "abort"` it takes the process: DoS.
- **RS-PANIC-02** Slice indexing `v[i]` / `&s[a..b]` with an index from input. Use `get()`. String slicing on a
  non-char-boundary panics.
- **RS-PANIC-03** Arithmetic that panics in debug and wraps in release: overflow on a length, offset or monetary
  value. Use `checked_*`, `saturating_*`, or `overflow-checks = true` in the release profile.
- **RS-PANIC-04** `let _ = fallible();` discarding a `Result`; `#[must_use]` ignored; `.ok()` used to drop an error.
- **RS-PANIC-05** `todo!()`, `unimplemented!()`, `unreachable!()` reachable at runtime.
- **RS-PANIC-06** Error type carrying a secret or internal path into a `Display` impl that reaches a client response.

## Crypto & secrets

- **RS-CRYPTO-01** Custom crypto instead of `ring`, `RustCrypto` or `rustls`.
- **RS-CRYPTO-02** Password hashed with anything but `argon2`, `scrypt` or `bcrypt`. `sha2` on a password is a finding.
- **RS-CRYPTO-03** `rand::random`/`thread_rng` for key material without a confirmed CSPRNG backend; prefer
  `getrandom` or `rand::rngs::OsRng` explicitly for secrets.
- **RS-CRYPTO-04** Secret compared with `==`. Use `subtle::ConstantTimeEq`.
- **RS-CRYPTO-05** Secret in a plain `String`/`Vec<u8>` with no `zeroize` and no `secrecy::Secret<T>` wrapper:
  leaks via `Debug`, core dumps, swap.
- **RS-CRYPTO-06** Secret-holding type with `#[derive(Debug)]` and no redacting impl: prints in a `tracing` field
  or an error chain.
- **RS-TLS-01** `danger_accept_invalid_certs(true)` on reqwest, `dangerous()` rustls config, or `native-tls`
  verification disabled. CRITICAL unless gated to non-production and logged.
- **RS-TLS-02** `native-tls`/`openssl` where `rustls` is available: larger unsafe surface, system-dependent behaviour.

## Injection & I/O

- **RS-EXEC-01** `Command::new("sh").arg("-c")` with interpolation. The argument-vector form is otherwise safe.
- **RS-SQL-01** Query string built with `format!`. `sqlx::query!` gives compile-time checking and binding;
  `query(&format!(...))` throws it away. Diesel `sql_query` with interpolation is the same bug.
- **RS-PATH-01** Path built from input without canonicalization plus a containment check against a base.
- **RS-DESER-01** `serde` deserializing untrusted input into unbounded collections with no size limit; missing
  `#[serde(deny_unknown_fields)]` on a security-relevant payload.
- **RS-DESER-02** `bincode`/`rmp` with no configured size limit: an attacker-supplied length prefix preallocates.
- **RS-DESER-03** Untrusted XML/zip/tar handling: XXE, zip-slip and bomb concerns apply; memory safety does not help.

## Async & resources

- **RS-ASYNC-01** Blocking call (`std::fs`, `std::net`, long CPU loop, `std::sync::Mutex` held across `.await`)
  inside an async task stalls the executor. Use `spawn_blocking` / `tokio::sync::Mutex`.
- **RS-ASYNC-02** `tokio::spawn` with no cancellation path: task leak.
- **RS-ASYNC-03** No timeout on a network call or lock acquisition.
- **RS-ASYNC-04** Unbounded channel or unbounded `spawn` per connection: memory exhaustion. Use bounded channels.
- **RS-RES-01** `Mutex` poisoning handled by `.unwrap()`: one panic becomes a permanent outage.

## Web & service surface

- **RS-WEB-01** Axum/actix route without the auth layer where auth is per-route. Enumerate the router.
- **RS-WEB-02** No body size limit (`DefaultBodyLimit`, `PayloadConfig`).
- **RS-WEB-03** Permissive CORS layer (`Any` origin with credentials).
- **RS-WEB-04** Error into response leaking `Debug` of an internal error.
- **RS-WEB-05** SSRF via a reqwest client built with a URL from input, redirects enabled by default.

## Supply chain & build

- **RS-SUP-01** `cargo audit` advisories: report crate, version, CVE/RUSTSEC, whether a fix exists.
- **RS-SUP-02** `cargo deny check licenses bans advisories` violations; no `deny.toml` on a project that ships.
- **RS-SUP-03** `Cargo.lock` not committed for a binary crate.
- **RS-SUP-04** Dependency on a git branch rather than a tag/rev; `[patch]` pointing at a fork on a release build.
- **RS-SUP-05** `build.rs` that downloads or executes at build time.
- **RS-SUP-06** Unmaintained crate (`RUSTSEC-*-unmaintained`) on a security path.

## Architecture (if hexagonal)

- **RS-ARCH-01** Domain crate depending on infrastructure crates (sqlx, axum, reqwest, redis); check each `Cargo.toml`.
- **RS-ARCH-02** Infrastructure types leaking into domain signatures.
- **RS-ARCH-03** Validation in the adapter while the domain newtype constructor does not enforce the invariant.

## Verification commands (read-only)

```bash
cargo audit
cargo deny check advisories bans licenses    # if deny.toml exists
cargo clippy --all-targets -- -W clippy::pedantic
grep -rn "unsafe" --include='*.rs' . | grep -v "SAFETY:"
grep -rn "unwrap()\|expect(\|panic!\|accept_invalid_certs" --include='*.rs' .
```
