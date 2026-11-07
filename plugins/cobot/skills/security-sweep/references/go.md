# Go rule pack

Loads for `.go` files and applies `core.md` through Go idioms. Rule ids are `GO-<CAT>-<nn>`.

## Injection & process

- **GO-EXEC-01** `exec.Command("sh", "-c", ...)` or `bash -c` with an interpolated argument. The argument-slice
  form is safe only if the binary path is not caller-controlled; also flag `exec.CommandContext` with a user `name`.
- **GO-SQL-01** `db.Query`/`Exec`/`QueryRow` with `fmt.Sprintf` or `+` building the statement. Placeholders (`$1`,
  `?`) are the only acceptable form; `sqlx.In` needs `Rebind`; table/column names need an allow-list, not escaping.
- **GO-PATH-01** `filepath.Join(base, userInput)` without `filepath.Clean` plus a `strings.HasPrefix(cleaned, base)`
  check. Prefer `os.Root`/`os.OpenInRoot`, which enforce containment including symlinks. Flag `http.Dir` or
  `http.FileServer` rooted at a path that includes sensitive files.
- **GO-TMPL-01** `text/template` rendering HTML (no contextual escaping); `html/template` is required. Flag
  `template.HTML`/`JS`/`URL` conversions applied to non-constant data: they disable escaping.
- **GO-INJECT-01** User input into `http.Header.Set`/`Add` values or a redirect target without stripping `\r\n`.

## TLS & crypto

- **GO-TLS-01** `tls.Config{InsecureSkipVerify: true}`. CRITICAL unless gated behind an explicit non-production
  flag and logged at warn/error on activation; check the gate is real, not a constant.
- **GO-TLS-02** `MinVersion` unset or below `tls.VersionTLS12`. Unset means the Go default, acceptable for clients
  but it should be explicit on servers.
- **GO-TLS-03** Custom `VerifyPeerCertificate`/`VerifyConnection` returning `nil` unconditionally, or a `RootCAs`
  pool whose `AppendCertsFromPEM` bool is ignored (silently yielding an empty pool).
- **GO-CRYPTO-01** `math/rand` (or `math/rand/v2`) for a token, salt, nonce, session id or password. Use `crypto/rand`.
- **GO-CRYPTO-02** `crypto/md5`, `sha1`, `des`, `rc4` on a security path. Cache keys and checksums are fine; check use.
- **GO-CRYPTO-03** Secret compared with `==` or `bytes.Equal`. Use `crypto/subtle.ConstantTimeCompare` (it leaks
  length, so hash first for variable-length secrets).
- **GO-CRYPTO-04** AES-GCM with a reused or zero nonce; `cipher.NewCBCEncrypter` without a MAC; ECB via repeated
  `Encrypt` calls.
- **GO-CRYPTO-05** Password hashed with anything other than `golang.org/x/crypto/bcrypt`, `argon2` or `scrypt`.

## HTTP server & client

- **GO-HTTP-01** `http.Server` with no `ReadHeaderTimeout` (Slowloris). Also check `ReadTimeout`, `WriteTimeout`,
  `IdleTimeout` and `MaxHeaderBytes`.
- **GO-HTTP-02** Body read without `http.MaxBytesReader` or an equivalent cap: `io.ReadAll(r.Body)` is the pattern.
- **GO-HTTP-03** `_ "net/http/pprof"` registers debug handlers on `DefaultServeMux`; HIGH when that mux is public.
- **GO-HTTP-04** Handler registered outside the auth middleware where auth is per-route. Enumerate all routes and
  diff against the protected set.
- **GO-HTTP-05** `http.Client` with no `Timeout` and no per-request deadline; default client used for untrusted hosts.
- **GO-HTTP-06** SSRF: `http.Get`/`client.Do` with a URL derived from input. Check host allow-listing and
  `CheckRedirect` (a redirect defeats a pre-flight check); block link-local `169.254.169.254`.
- **GO-HTTP-07** CORS middleware reflecting `Origin`, or `*` alongside `Access-Control-Allow-Credentials: true`.
- **GO-HTTP-08** `httputil.ReverseProxy` with no `ErrorHandler` (leaks upstream errors), or a `Director` forwarding
  hop-by-hop or auth headers to a rewritten host it should not trust.

## Deserialization & parsing

- **GO-DESER-01** `encoding/gob` decoding untrusted data; gob is not designed for hostile input.
- **GO-DESER-02** `encoding/xml` on untrusted input: Go resolves no external entities, but check billion-laughs
  nesting and `xml.Unmarshal` into recursive structures.
- **GO-DESER-03** YAML unmarshal into `interface{}` from untrusted input plus type-asserting logic: resource
  exhaustion and type confusion.
- **GO-DESER-04** `json.Unmarshal` silently ignoring unknown fields on a security-relevant payload; use
  `Decoder.DisallowUnknownFields`. Also a `json.Decoder` on a stream with no size cap.
- **GO-DESER-05** `archive/zip` or `tar` extraction without per-entry path validation against the destination
  root (zip-slip) and without a cumulative size cap (zip bomb).

## Errors, logging, secrets

- **GO-LOG-01** `slog`/`log` call whose arguments include a token, password, `Authorization` header, or a whole
  request/config struct containing one. A secret-bearing type with no redacting `LogValue()` is itself a finding.
- **GO-LOG-02** `fmt.Errorf("...: %w", err)` chains reaching an HTTP response body; check the error-to-response map.
- **GO-LOG-03** `%v` on a struct containing credentials, in logs or errors.
- **GO-ERR-01** `err` assigned and not checked; `_ = someCall()` on a security path; `defer f.Close()` on a writable
  file, which drops the flush error.
- **GO-ERR-02** `panic` in library code reachable from untrusted input, or a handler with no recovery middleware
  (`net/http` recovers per connection; a custom server loop may not).

## Concurrency & resources

- **GO-CONC-01** Shared map or slice written from multiple goroutines without a mutex (`go test -race` evidence);
  `sync.WaitGroup` misuse; closure capture of a loop variable under older Go semantics.
- **GO-CONC-02** Goroutine launched with no context or done channel: leaked for the process lifetime.
- **GO-CONC-03** Unbounded goroutine spawning per request with no semaphore: DoS amplifier.
- **GO-RES-01** `rows.Close()`, `resp.Body.Close()` or a lock release missing on an error path. A deferred
  `resp.Body.Close()` placed before the error check nil-panics; after it is correct.
- **GO-CTX-01** Blocking call with no `context.Context`, or `context.Background()` where the caller's context
  should propagate (defeats cancellation).

## Build, config, supply chain

- **GO-SUP-01** `govulncheck ./...` findings; prefer it over generic scanners since it reports reachable
  vulnerabilities. Rate unreachable ones lower.
- **GO-SUP-02** `replace` directive to a local path or fork in `go.mod` on a release build; a branch pseudo-version
  rather than a tag.
- **GO-SUP-03** `go.sum` missing or not committed.
- **GO-SUP-04** `cgo` used: expands the memory-safety surface; check the C side is reviewed and its input bounded.
- **GO-CFG-01** Secret read from a flag (`flag.String`) rather than env or a file: flags land in `ps` and history.
- **GO-CFG-02** `os.Getenv` for a required secret with no error on empty: fails open with an empty credential.
- **GO-CFG-03** Key/token written with `os.WriteFile(..., 0644)` or wider, or a `0777` directory. Keys need `0600`.
- **GO-CFG-04** `unsafe` package use: check bounds and lifetime assumptions.

## Verification commands (read-only)

```bash
go vet ./...
govulncheck ./...                 # if installed
gosec -quiet ./...                # if installed
staticcheck ./...                 # if installed
go test -race ./... -count=1      # only if the user permits running tests
grep -rn "InsecureSkipVerify\|math/rand\|exec.Command\|fmt.Sprintf" --include='*.go' .
```
