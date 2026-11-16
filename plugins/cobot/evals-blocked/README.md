# Eval cases set aside

Graders that cannot pass under `claude plugin eval` for a reason outside cobot stay here, outside
`evals/`, so a run does not score them.

| What | Blocked on |
|---|---|
| `builder-routing/graders/proof-quoted.md` | the builder's `cargo` finds no toolchain: each run gets a fresh HOME, so the rustup proxy sees an empty `~/.rustup` ("no installed toolchains", 2.1.325, 2026-11-16); the rest of `builder-routing` stays in the suite |
| `onboard-runs-question/graders/one-question.md`, `question-before-command.md` | `AskUserQuestion` cannot be called in an eval run: runs use `dontAsk`, which denies it even when the case's `allowed_tools` grants it (headless docs, "Auto-approve tools"), and the plugin-eval docs offer no way to answer one; a run on 2.1.311 had no such tool at all (2026-11-16). The rest of the case grades the question the report states instead; restore these with a prompt that lets the question be asked |

Writing inside the run's workspace is no longer a blocker: eval runs set `TMPDIR` outside `/tmp`
(anthropics/claude-code#104631), and `foreign-onboard` and `new-project-onboard` moved back to
`evals/` on 2026-11-16.

To restore one: `git mv` it back under `evals/` (the grader into `evals/builder-routing/graders/`)
and run that case once with `--case <name> --runs 1 --ablation none`.
