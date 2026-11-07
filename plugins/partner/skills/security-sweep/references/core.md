# Core rules

Language-neutral pack: loads for every file regardless of extension, and language or infra packs add
idiom-specific detection without replacing these categories. Rule ids are `CORE-<CAT>-<nn>`; cite the id in
every finding.

## SECRET — credentials and key material

- **CORE-SECRET-01** Hardcoded credential: API key, password, token, private key, connection string, cloud key.
  A `testdata/` fixture or obvious dummy (`AKIAIOSFODNN7EXAMPLE`) is LOW; a real key in a test file is CRITICAL.
- **CORE-SECRET-02** Secret file committed, now or ever: `.env`, `*.pem`, `*.key`, `*.p12`, `*.jks`,
  service-account JSON, kubeconfig with tokens. Deleted-but-in-history is still CRITICAL.
- **CORE-SECRET-03** Secret in logs, stdout, stderr, traces, metric labels or error payloads, including object dumps.
- **CORE-SECRET-04** Secret in a URL, query string or redirect target: proxy logs, referrers, browser history.
- **CORE-SECRET-05** Secret in a mutable string with no zeroization where offered, or forwarded beyond its purpose.
- **CORE-SECRET-06** `.gitignore` does not cover the secret file patterns the project actually uses.

## INJECT — untrusted input reaching an interpreter

- **CORE-INJECT-01** SQL/NoSQL built by concatenation or interpolation, not parameterized. ORM raw escapes count.
- **CORE-INJECT-02** Shell or process execution with an interpolated argument, especially via a shell (`sh -c`,
  `shell=True`, backticks). Argument-array exec with a user-controlled binary path is also this rule.
- **CORE-INJECT-03** Path traversal: path built from input without canonicalization plus a containment check
  against a base directory. Filtering `..` alone is insufficient: check symlinks and encoding.
- **CORE-INJECT-04** Template injection: user input into a template string rather than a template variable.
- **CORE-INJECT-05** Unescaped user content in HTML, JS, LDAP, XPath, log lines (newline forging), CSV formulas
  or shell scripts generated at runtime.
- **CORE-INJECT-06** Header/CRLF injection: input into HTTP headers, redirect targets or email fields, unstripped.

## AUTHZ — access control

- **CORE-AUTHZ-01** Protected operation with no authentication check, or a check that is opt-in per route rather
  than applied by default (allow-list beats deny-list; middleware beats per-handler).
- **CORE-AUTHZ-02** IDOR: object fetched by a caller-supplied id with no check that the caller may access it.
- **CORE-AUTHZ-03** Authorization from client data: a role in the body, an unverified header, an unvalidated claim.
- **CORE-AUTHZ-04** Escalation: a low-privilege call sets fields, roles or flags of a higher one (mass assignment).
- **CORE-AUTHZ-05** Token validation gaps: signature unverified, algorithm not pinned (`alg: none`, HS/RS
  confusion), expiry/audience/issuer unchecked, revocation impossible.
- **CORE-AUTHZ-06** Session handling: no rotation on privilege change, no expiry, cookies missing
  `Secure`/`HttpOnly`/`SameSite`, tokens in `localStorage` where XSS reaches them.

## CRYPTO — cryptographic use

- **CORE-CRYPTO-01** Broken primitive for security: MD5/SHA1, DES/3DES/RC4, ECB mode, raw RSA without padding.
- **CORE-CRYPTO-02** Password stored with a fast hash. Must be argon2id, scrypt or bcrypt with a sane cost.
- **CORE-CRYPTO-03** Non-cryptographic RNG for a token, salt, IV, nonce, session id or password reset code.
- **CORE-CRYPTO-04** Static or reused IV/nonce, or a key derived from low-entropy input without a proper KDF.
- **CORE-CRYPTO-05** Secret compared with variable-time equality (timing oracle). Needs constant-time compare.
- **CORE-CRYPTO-06** TLS verification disabled or weakened: skip-verify flags, accept-any-cert callbacks, floor
  below TLS 1.2. A skip-verify must be gated to non-production and logged loudly; ungated is CRITICAL.
- **CORE-CRYPTO-07** Hand-rolled cryptography where a vetted library exists.

## INPUT — validation and resource bounds

- **CORE-INPUT-01** Input crosses into core logic without boundary validation: type, range, length, format, allow-list.
- **CORE-INPUT-02** Unbounded resource use from input: no body size limit, no pagination cap, allocation sized
  by an attacker-supplied length, unbounded concurrency or queue depth.
- **CORE-INPUT-03** Unsafe deserialization of untrusted data (pickle, Java native, YAML full-load, PHP unserialize).
- **CORE-INPUT-04** Decompression with no size or ratio cap (zip bomb); extraction with no path containment (zip-slip).
- **CORE-INPUT-05** Regex with catastrophic backtracking on attacker-controlled input (ReDoS).
- **CORE-INPUT-06** No rate limit or lockout on login, password reset, token exchange, search or expensive endpoints.

## SSRF — outbound request control

- **CORE-SSRF-01** Outbound request to a URL derived from external input with no allow-list of hosts or schemes.
- **CORE-SSRF-02** Redirects defeat a pre-flight host check: re-validate after each hop, or disable redirects.
- **CORE-SSRF-03** No block on link-local, loopback or private ranges; metadata `169.254.169.254` is the target.
- **CORE-SSRF-04** Open redirect: a redirect target taken from input without an allow-list.
- **CORE-SSRF-05** XXE: XML parsed with external entity resolution enabled.

## CONFIG — deployment and posture

- **CORE-CONFIG-01** Debug mode, verbose errors, profiling endpoints or developer backdoors reachable in production.
- **CORE-CONFIG-02** Insecure default: the safe behaviour needs a flag rather than being the default. Fail closed.
- **CORE-CONFIG-03** Overly permissive CORS: `*` with credentials, or origin reflected from the request.
- **CORE-CONFIG-04** Missing security headers on a web surface: HSTS, CSP, `X-Content-Type-Options`, frame options.
- **CORE-CONFIG-05** Binds `0.0.0.0` where loopback would do, or an admin/metrics/debug port on the public listener.
- **CORE-CONFIG-06** Excess privilege: runs as root, requests broader IAM/RBAC than used, wildcard permissions.

## OBSERV — logging and detectability

- **CORE-OBSERV-01** Unlogged security event: authn failure, authz denial, privilege change, secret or config change.
- **CORE-OBSERV-02** Log injection: unescaped newlines or control characters from user input into log lines.
- **CORE-OBSERV-03** Error response discloses internals: stack trace, SQL text, file path, dependency version, or
  "no such user" versus "wrong password" where enumeration matters.
- **CORE-OBSERV-04** Errors swallowed, or logged at a level nobody reads, on a security-relevant path.

## SUPPLY — dependencies and integrity

- **CORE-SUPPLY-01** Known CVE in a dependency. Rate by reachability: an unreachable path is MEDIUM, not CRITICAL.
- **CORE-SUPPLY-02** Unpinned or floating dependency version where the lockfile is absent or not committed.
- **CORE-SUPPLY-03** Dependency from a non-canonical source, an HTTP URL, or a movable git ref (branch, not tag/sha).
- **CORE-SUPPLY-04** Install/build-time script execution from a dependency, or a build that downloads and runs code.
- **CORE-SUPPLY-05** Abandoned dependency (no release in 2+ years) on a security path, or a typosquat-shaped name.

## HAZARD — correctness and robustness (not vulnerabilities; own section in the report)

- **CORE-HAZ-01** Error returned or thrown but discarded, or a failure path that continues as if it succeeded.
- **CORE-HAZ-02** Resource leak: file, socket, lock, transaction or thread not released on every path, errors included.
- **CORE-HAZ-03** Concurrency defect: unsynchronized shared mutable state, deadlock-prone lock order, check-then-act.
- **CORE-HAZ-04** TOCTOU between a check and the use of what was checked.
- **CORE-HAZ-05** Missing timeout, deadline or cancellation on a network call, lock or subprocess: cascading stalls.
- **CORE-HAZ-06** No retry/backoff on a transient failure, or retry without a cap (retry storm).
- **CORE-HAZ-07** Crash on bad input in library code: panic, unwrap, assert or uncaught throw where an error is owed.
- **CORE-HAZ-08** Integer overflow, truncating cast or precision loss on a size, index, offset or monetary value.
- **CORE-HAZ-09** Dead code, unreachable branch, or a `TODO`/`FIXME` on a security-relevant path with no tracking ref.
- **CORE-HAZ-10** Security-relevant behaviour with no test, especially the negative case: denial, rejection, redaction.
