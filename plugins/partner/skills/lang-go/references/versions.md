# Go — verified versions and facts

Format: `- [verified YYYY-MM-DD · src: <url>] claim`. The brief flags version lines after 30 days, idiom after 90 (`partner-memory knowledge --stale lang-go`).

## Toolchain

- [verified 2026-11-06 · src: https://go.dev/dl/?mode=json] Supported: go1.27.3 (current), go1.26.10.
- [verified 2026-11-06 · src: https://go.dev/doc/go1.27] 1.27 (Aug 2026): generic methods (cannot implement interface methods); `encoding/json` backed by json/v2 (`GOEXPERIMENT=nojsonv2` to opt out); new `uuid`, `crypto/mldsa`; `httptest.NewTestServer`, `synctest.Sleep`, `strings.CutLast`; `goroutineleak` pprof profile GA; `go test` runs vet `stdversion`; vet `printf` flags `%w` on `*E` when `E` implements `error`; non-final `GODEBUG` values in `go.mod` fail the build; go fix modernizers `atomictypes`, `embedlit`, `slicesbackward`, `unsafefuncs`, `waitgroup` renamed `waitgroupgo`.
- [verified 2026-11-06 · src: https://go.dev/doc/go1.26] 1.26: `new(expr)`; `go fix` rewritten as modernizer suite sharing vet's framework, honours `//go:fix inline`; `errors.AsType`; `T.ArtifactDir`; hybrid PQ TLS key exchange default; `ReverseProxy.Director` deprecated for `Rewrite`; Green Tea GC default; `go mod init` writes previous minor.
- [verified 2026-11-06 · src: https://pkg.go.dev/errors#AsType] `func AsType[E error](err error) (E, bool)`, since 1.26.0.
- [verified 2026-11-06 · src: https://go.dev/doc/go1.25] 1.25: `sync.WaitGroup.Go`; `testing/synctest` GA; `http.CrossOriginProtection`; vet `waitgroup`, `hostport`; container-aware `GOMAXPROCS`.
- [verified 2026-11-06 · src: https://go.dev/doc/go1.24] 1.24: `tool` directive + `go tool`; `T.Context`; `B.Loop`; `os.Root`/`os.OpenRoot`; generic type aliases; `omitzero` JSON tag.
- [verified 2026-11-06 · exp: go help mod tidy] `go mod tidy -diff` prints the diff and exits non-zero when not tidy.
- [verified 2026-11-06 · src: https://pkg.go.dev/net/http] `http.DefaultClient` is `&Client{}`: zero `Timeout` = none; `MaxBytesReader` returns `*MaxBytesError`; `DefaultMaxHeaderBytes` 1 MB; `DefaultMaxHeaderValueCount` 500.

## Tools

- [verified 2026-11-06 · src: https://github.com/golangci/golangci-lint/releases] golangci-lint v2.15.0 (2026-10-16).
- [verified 2026-11-06 · src: https://golangci-lint.run/docs/configuration/file/] v2 config: `version: "2"` (only value); `linters.default: standard|all|none|fast` (default `standard`); `formatters.enable` (e.g. `gofmt`, `gofumpt`, `goimports`, `gci`, `golines`); `run.timeout` default 0 (none).
- [verified 2026-11-06 · src: https://golangci-lint.run/docs/welcome/quick-start/] `golangci-lint fmt` formats; `golangci-lint run` lints.
- [verified 2026-11-06 · src: https://golangci-lint.run/docs/product/migration-guide/] `golangci-lint migrate` converts v1 configs.
- [verified 2026-11-06 · src: https://proxy.golang.org/golang.org/x/vuln/@latest] govulncheck (golang.org/x/vuln) v1.9.0 (2026-10-11). GitHub releases page stops at v1.1.4 — use the module proxy, not GitHub releases.
- [verified 2026-11-06 · src: https://proxy.golang.org/golang.org/x/sync/@latest] golang.org/x/sync v0.24.0 (`errgroup`).
- [verified 2026-11-06 · src: https://proxy.golang.org/golang.org/x/tools/@latest] golang.org/x/tools v0.52.0.
- [verified 2026-11-06 · src: https://proxy.golang.org/github.com/google/go-cmp/@latest] go-cmp v0.7.0 (2025-01-14): dormant but mature; acceptable, re-check.

## Local machine (not upstream)

- [verified 2026-11-06 · exp: go version] workstation has go1.27.2, one patch behind current.
