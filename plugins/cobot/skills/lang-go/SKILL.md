---
name: lang-go
description: >-
  Senior Go developer knowledge for this cobot: verified toolchain versions, the exact
  format/lint/test/coverage/vuln/build commands, current idiom (modules, errors, context,
  interfaces, generics, concurrency), project shape for small modules, test rules,
  security specifics (govulncheck, net/http timeouts, input bounds, secrets), pitfalls.
  Applies whenever Go files are read or changed — `**/*.go`, `**/go.mod`, `**/go.sum` — and
  is preloaded into the go-builder agent. Use it before writing, reviewing or testing Go code,
  adding a module, or touching Go CI. Versions and sources live in references/versions.md;
  the CI job in references/ci.md.
paths:
  - "**/*.go"
  - "**/go.mod"
  - "**/go.sum"
user-invocable: false
---

# lang-go

Versions, dates and sources: `references/versions.md`. Re-verify a line the brief flags stale (versions after 30 days, idiom after 90)
before relying on it; never "upgrade" a repo as a side effect — report the gap.

## Toolchain and commands

- [verified 2026-11-06 · src: https://go.dev/dl/?mode=json] Go 1.27.3 current; 1.26.x is the other supported line.
- [verified 2026-11-06 · src: https://github.com/golangci/golangci-lint/releases] golangci-lint v2.15.0; config needs `version: "2"`.
- The `go` and `toolchain` lines in `go.mod` win over whatever is installed.

| step | command |
|---|---|
| format | `golangci-lint fmt` (formatters from `.golangci.yml`); fallback `gofmt -l -w .` |
| lint | `golangci-lint run` ; fallback `go vet ./...` |
| modernize | `go fix ./...` (review the diff; never in CI) |
| test (focused) | `go test ./<pkg>/ -run '^TestName$' -race -count=1` |
| test (all) | `go test ./... -race -count=1 -shuffle=on` |
| coverage | `go test ./... -race -covermode=atomic -coverprofile=cover.out && go tool cover -func=cover.out \| tail -1` |
| vuln | `go run golang.org/x/vuln/cmd/govulncheck@v1.9.0 ./...` (or a `tool` directive) |
| build | `go build -trimpath ./...` |
| lock check | `go mod tidy -diff` (non-zero exit if `go.mod`/`go.sum` drift) |

- Lock rule: `go.sum` committed; `go mod tidy -diff` gates CI; `go mod verify` before release.
- Dev tools: `tool` directive in `go.mod` (`go get -tool <pkg>@<ver>`, run with `go tool <name>`),
  not a `tools.go` blank-import file.
- v1 `.golangci.yml` is rejected by v2: run `golangci-lint migrate`, do not hand-edit.

## Idiom

- Modules: one `go.mod` per repo unless a sub-tree is released separately. `go` line = the
  oldest version you test; do not bump it to get a stdlib helper in an unrelated change.
- Errors: wrap with `fmt.Errorf("load config: %w", err)` — lowercase, no "failed to", no
  trailing punctuation. Branch with `errors.Is`; extract with `errors.AsType[*E](err)`
  (generic, faster) over `errors.As`. Sentinels for conditions callers branch on, typed
  errors when they need data. `errors.Join` for multi-error. Never compare error strings.
- Discarding an error with `_` needs a same-line comment. `panic` only for programmer error
  at construction; never across a package boundary.
- Context: first parameter, named `ctx`, never stored in a struct, never `nil` (use
  `context.TODO()` while plumbing). Every blocking loop selects on `ctx.Done()`. In tests use
  `t.Context()`.
- Interfaces: defined at the consumer, one or two methods; accept interfaces, return
  concrete types. No interface "for mocking" with a single implementation in the same package.
- Generics: for containers and algorithms over types (`slices`, `maps`, `cmp` first). Do not
  genericise business logic with one concrete type. Generic methods exist since 1.27 but
  cannot satisfy interface methods — prefer functions.
- Prefer stdlib: `log/slog` for logs, `net/http` `ServeMux` patterns (`"GET /items/{id}"`,
  `r.PathValue`) before a router, `encoding/json` (now backed by json/v2) before a third-party codec.
- Constructor injection `NewX(deps) *X`; no package-level mutable state, no `init()` with side effects.
- Package names say what they provide (`billing`), never `util`, `common`, `models`, `helpers`.
- `new(expr)` for optional pointer fields instead of helper `ptr()` functions.

### Concurrency

- Every goroutine has an owner and an exit path; if you cannot say when it stops, it leaks.
- `wg.Go(func() { ... })` over `Add`/`Done`; `errgroup.WithContext` when work can fail;
  `errgroup.SetLimit` to bound fan-out.
- One mechanism per piece of state: mutex *or* channel. Channels transfer ownership; mutexes
  guard it. `atomic.Int64` and friends over `atomic.AddInt64`.
- Unbuffered channels by default; a buffer size needs a reason.
- `-race` on every test run; `testing/synctest` for code driven by time or goroutine scheduling.

## Project shape

- Small module: `main.go` + a few packages at the root, or `cmd/<bin>/` once there are two
  binaries. `internal/` for anything not meant for import. No `pkg/`.
- Hexagonal split pays with ≥ 2 real adapters for a port (Postgres + in-memory, HTTP + CLI)
  or domain logic worth testing without I/O. It does not pay for a CLI, a glue service or a
  library with one backend — flat packages suffice.
- When split: the domain package imports stdlib only and declares the interfaces it needs;
  `main` wires concrete adapters. Adapters never import each other.

## Tests

- Name: Go requires `TestXxx`; encode `unit_scenario_expected` as `TestParseConfig_MissingPort_ReturnsError`
  or as the subtest name `t.Run("missing_port_returns_error", ...)`.
- Table-driven: `tests := []struct{ name string; ... }{...}` + `t.Run(tt.name, ...)`;
  `t.Parallel()` where state allows; `t.Cleanup` over `defer`; `t.Setenv`, `t.TempDir`.
- Assertions: stdlib + `github.com/google/go-cmp/cmp` for diffs. No assertion framework
  unless the repo already uses one.
- Integration tests: `_test.go` beside the package, gated by a build tag
  (`//go:build integration`) or `testing.Short()`; black-box tests in `package x_test`.
- Coverage floor 85 % of statements, measured by `go test -coverprofile` + `go tool cover
  -func` (total line). Use `-coverpkg=./...` when integration tests cover other packages.
- Never mock what you own; use in-memory fakes. Never mock HTTP (`httptest.NewServer` /
  `httptest.NewTestServer`), the filesystem (`t.TempDir`, `testing/fstest`), or `time`
  (`testing/synctest`). Real database via a container in integration tests.
- Fuzz (`func FuzzX(f *testing.F)`) parsers and decoders; commit the seed corpus.
- Benchmarks use `for b.Loop()`; attach numbers to any performance claim.

## Security

- `govulncheck ./...` on every CI run — reachability-aware, so a finding is real; fix by
  upgrading the module, never by ignoring.
- `net/http`: the zero `http.Server` and `http.DefaultClient` have no timeouts. Always set
  `ReadHeaderTimeout`, `ReadTimeout`, `WriteTimeout`, `IdleTimeout` on servers and `Timeout`
  on clients. Wrap bodies with `http.MaxBytesReader`; cap other reads with `io.LimitReader`.
- CSRF for browser-facing handlers: `http.CrossOriginProtection`.
- Input: validate at the edge, decode into typed structs, `json.Decoder.DisallowUnknownFields`
  at trust boundaries. SQL via placeholders only. `exec.Command(bin, args...)`, never `sh -c`.
- Files from untrusted paths: `os.OpenRoot` / `os.Root` to stay inside a directory.
- Randomness: `crypto/rand` for anything security-relevant; `math/rand/v2` otherwise.
- Secrets: from env or a secret manager, never in code or flags' defaults. Redact with a
  `LogValue()` (slog) / `String()` method on the holding type; never log headers or bodies wholesale.
- `unsafe` and cgo: none without a written reason; `CGO_ENABLED=0` for static binaries.
- Reverse proxies: `httputil.ReverseProxy.Rewrite`, not the deprecated `Director`.

## CI

One minimal job (tidy check, lint, race tests + coverage gate, govulncheck), actions pinned
to verified SHAs: `references/ci.md`.

## Pitfalls

1. Loop variable capture is per-iteration since 1.22 — but only for modules whose `go` line is ≥ 1.22.
2. `defer` inside a loop holds every resource until the function returns.
3. A nil `*T` stored in an interface is a non-nil interface — `err != nil` is true.
4. `time.After` in a long `select` loop — use a `time.Timer` you reset.
5. Map iteration order is random; never let tests depend on it.
6. `append` to a sub-slice can overwrite the parent's backing array — use full slice expr `s[a:b:b]`.
7. Forgetting `resp.Body.Close()` (and draining) leaks connections.
8. `%w` given a `*E` where `E` itself implements `error` — vet flags it since 1.27; wrap the value type.
9. `GODEBUG` lines in `go.mod` with non-final values break the build on 1.27.
10. Goroutine leaks — check `/debug/pprof/goroutineleak` (GA in 1.27) before blaming GC.

## Do not

- Add a router, logger, config or assertion library when stdlib covers the need.
- Use `golangci-lint` v1 configs, `tools.go`, `ioutil`, `interface{}` (use `any`), or `pkg/`.
- Store `context.Context` in a struct or pass `nil` as a context.
- Ship a server without timeouts or a goroutine without an exit path.
- Bump the `go` line or a major module version as part of an unrelated change.
