# Audit of the previous scaffold (`~/.agents`, workstation-starter `ai/`) — 2026-11-06

Produced by an adversarial audit agent; verified upstream versions the same day. Used to decide
what the blank-slate rewrite may salvage. Nothing is reused without the fix listed here.

## Worth keeping (the ideas, rewritten)
1. `.agent/CONTEXT.md` with a **verified-commands table** and a **project profile**: used in 6/6 repos.
2. `.agent/JOURNAL.md` (Changed / Why / Tests / Open / Next): used in 6/6 repos; holds the "why" git lacks.
3. The **proportionality table** (spike / script / cli / library / service / infra) as the root rule.
4. Test-first; review through built-ins (`/code-review`, `/security-review`, `/simplify`); one thin fallback reviewer.
5. **`challenger`** (red-team a plan, "simpler alternative outranks all", may return SOUND). No built-in equivalent.
6. **`security-sweep`** (whole repo, baseline, triage): found a real HIGH. Built-ins cover diffs only.
7. **`gcd-universe`**: niche, concrete, caught three blockers. One stale phrase (provider "5.x" → 8.x).
8. Terraform "what the plugins don't cover" half (state safety, module boundaries, secrets).
9. Go and Python standards, short, with version fixes.
10. "Host before device" rule from hardware work.

## Drop
Gemini/Antigravity plumbing · all four `rust-*` commands (stale SHA pins, removed cargo-deny keys,
nightly-only rustfmt options, double advisory scans) · `rust-architect`, `rust-test-engineer`
(pre-0.15 testcontainers API, `assert_matches!` not on stable), `devops-engineer`, `docs-writer`,
`test-engineer` (hard-coded 85 %) · `rust.md` as a 448-line monolith · AGENTS.md README/CI/RTK
boilerplate and its `>85 % no exceptions` rule · `workflows/security-audit.json` · most of the
permission allowlist (`git push`, `git rebase`, `cp`, `mv` were allowed unconditionally).

## Cross-cutting defects
- Installed copies were files, not links; `~/.agents` was not a git repo: edits did not propagate.
- JOURNAL ordering contradiction (template says newest on top, build skill reads the tail).
- Two planning systems coexisted (spec-kit in 3 repos, `/design` + ADR in 2).
- AGENTS.md contradicted `_core.md` on coverage gates and mandatory CI.
- Real repos converged on better choices than the scaffold: `mise` tasks, `cargo deny` only,
  SHA pins with version comments.

## Outdated facts (upstream on 2026-11-06)
| Topic | Old text | Current |
|---|---|---|
| Rust supply chain | `cargo audit` + `cargo deny` | `cargo deny check` only (0.20.x); same RustSec data |
| Rust async traits | `async_trait` "until RPITIT stable" | `async fn` in traits stable since 1.75; `async_trait` only for `dyn` ports |
| Rust coverage markers | tarpaulin attributes with llvm-cov | `--ignore-filename-regex`; `#[coverage(off)]` is nightly |
| Go | no version | go 1.27.x; golangci-lint v2.15; `tool` directive; `modernize` |
| Python | poetry first, 3.10+ | uv 0.13.x first, `uv.lock`, 3.13; ruff 0.17, mypy 2.x or pyright, pick one |
| Terraform | — | 1.17.x; `trivy config`, not checkov |
| GitHub Actions pins | checkout v4 SHA | checkout v7.0.1, rust-cache v2.9.3, cargo-deny-action v2.1.1; add `zizmor` |
| security-sweep tools | cargo-audit | cargo-deny, osv-scanner, zizmor; drop the `ReportFindings` conditional |

## Spec-kit: what to absorb into the single planning path
Keep: **principles** (a short section, not a versioned file), **spec** (user stories + acceptance
criteria, one file), **clarify** (≤ 5 targeted questions written back into the spec, the
highest-value step), **plan** (= the design step, with a trade-offs section), **tasks**
(dependency-ordered, `T001` ids, phases), **converge** (compare code with spec and tasks, append
what is missing). Drop: numbered feature branches, `feature.json`, the generated research /
data-model / contracts / quickstart set, checklist, tasks-to-issues, the 30-line hook boilerplate.
Single path: principles once → spec + clarify → plan + challenger → tasks → build → converge.

## Built-in overlap to respect
Plan mode and the `Plan` agent (design steps) · `/code-review`, `/simplify`, `/review` (diff
review) · `/security-review` (diff security) · the `tdd` skill · the app's task list · auto-memory.
Keep `.agent/` files because they are committed and shared; keep exactly one home for the
commands table (CONTEXT.md or CLAUDE.md, not both).
