# Eval cases set aside

These cases and graders need Bash to write inside the eval workspace, and `claude plugin eval`
mounts every path read-only for Bash, the workspace included (Claude Code 2.1.311, 2.1.322 and
2.1.325, reproduced locally against a fake API; the plugin-evals docs say "Writes are confined to
the run's workspace"). They stay here, outside `evals/`, so a run does not score them, and move
back once a Claude Code release lets eval Bash write to its workspace.

| What | Blocked on |
|---|---|
| `foreign-onboard/` | `cobot-memory init --foreign` creates the memory under `~/.local/share/cobot` |
| `new-project-onboard/` | `cobot-memory init --trust-root` creates `.agent/` and the trust line |
| `builder-routing/graders/proof-quoted.md` | the builder's `cargo` needs a writable `~/.rustup` and target directory; the rest of `builder-routing` stays in the suite |

To restore one: `git mv` it back under `evals/` (the grader into `evals/builder-routing/graders/`)
and run that case once with `--case <name> --runs 1 --ablation none`.
