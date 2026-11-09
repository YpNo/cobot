# Challenger pass 1 on design draft v0 — 2026-11-06

VERDICT: SOUND WITH CHANGES. All twelve findings were folded into `02-design.md` v1 (see its §13).

| # | Sev | Claim | Resolution |
|---|---|---|---|
| 1 | MAJOR | The rtk hook rewrites Bash input to `rtk <cmd>`; permission rules are evaluated on the rewritten input, so a pasted `Bash(git push --force*)` deny never matches on the owner's machine | `rules sync` emits each Bash pattern twice (plain and `rtk `-prefixed); the gate strips a leading `rtk ` per segment; rtk case in the pytest table |
| 2 | MAJOR | "Fail closed" is false when python3 is missing or the script tracebacks (non-2 exit codes do not block) | hooks.json calls a POSIX `sh` shim: missing python3 → exit 2; `exec python3 -I … \|\| exit 2`; top-level `except` prints the ask decision |
| 3 | MAJOR | Prefix fnmatch misses `terraform -chdir=… apply`, `git -C . push`, `( git push )`, `git push &`, `env git push`, `curl … \| sh`; task runners (`mise run`, `make`, `npm run`) are a clean bypass | shlex → argv; strip global options for git/terraform/tofu/gh; match on (binary, subcommand); interpreters and task runners opaque → `ask` unless the owner layer allows that exact command; split on `&` too |
| 4 | MAJOR | A cloned repo's `.agent/CONTEXT.md` / `.agent/partner.rules` is injected as trusted memory and can reach `permissions.allow` through `sync` | SessionStart injects `.agent/*` only for trusted repos; `sync` takes `allow` from the owner layer only; project layer contributes `never`/`ask` only; reasons quoted and truncated |
| 5 | MAJOR | One SKILL.md cannot be both the paths-gated inline idiom and the forked consult; `agent: <plugin agent>` as a fork target is unverified | two skill dirs per expert (`expert-gha`, `consult-gha`); "`agent: partner:consultant` resolves" added to the day-one spike |
| 6 | MAJOR | The legacy scaffold stays live during the dogfood week (symlinked agents and skills, 12.6 KB CLAUDE.md) and wins over a 3k injected protocol | step 0 of R1: unlink legacy agents/skills and cut `~/.claude/CLAUDE.md` to the RTK section, with the owner's go-ahead |
| 7 | MAJOR | Worktree lanes lose `.agent/` (symlink excluded from checkout) and three lanes appending JOURNAL conflict | builders never write `.agent/`; `WorktreeCreate` hook symlinks `<worktree>/.agent`; the gate resolves the project layer via `git rev-parse --git-common-dir` |
| 8 | MAJOR | R1 ships Python and TypeScript stacks no R1 repo dogfoods; they rot like `rust.md` did | R1 = gate + onboard/spec/build/wrap + challenger/consultant/builder + rust/go builders + lang-{rust,go,terraform,fallback} + expert-gha; R1.1 adds python/typescript (dreame-vacuum, headplane), ship, contribute, security-sweep, compaction |
| 9 | MINOR | §4 and §8 disagreed on `risk:` tasks; per-call `model` takes an alias, never `inherit` | `risk:` tasks are built inline by the orchestrator; §8 row deleted |
| 10 | MINOR | "Last two entries from the tail" breaks on a newest-on-top journal (server-automation) | `partner-memory` picks the two latest `## YYYY-MM-DD` headings regardless of position; onboard offers to normalise |
| 11 | MINOR | Consultant "read-only Bash" was a prompt property, not a tool property | rules gain an agent scope (`ask Bash(*) @consultant`); table says "read-only by rule" |
| 12 | MINOR | No owner gate on accepting BLOCKER/MAJOR objections; `deep-review.js` and `SubagentStop` unexplained | acceptance needs an AskUserQuestion answer written into the spec; `deep-review.js` and `SubagentStop` move to R2; SessionStart matcher includes `compact` |

CHECKED-AND-CLEAR: hook never emits allow · most restrictive wins · thin per-language builders ·
conceptor in main thread (challenger is a fresh context) · per-session cost ≈ 5–6k tokens ·
background `ask` surfaces in the main session · one plugin, no GitHub MCP, journal at bottom,
foreign symlink + `info/exclude` · reversibility. Note: the HashiCorp Terraform MCP is not
installed at user scope on this machine; `lang-terraform` must work without it.
