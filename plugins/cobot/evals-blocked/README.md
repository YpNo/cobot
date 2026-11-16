# Eval cases set aside

Graders that cannot pass under `claude plugin eval` for a reason outside cobot stay here, outside
`evals/`, so a run does not score them.

| What | Blocked on |
|---|---|
| `builder-routing/graders/proof-quoted.md` | the builder's `cargo` finds no toolchain: each run gets a fresh HOME, so the rustup proxy sees an empty `~/.rustup` ("no installed toolchains", 2.1.325, 2026-11-16); the rest of `builder-routing` stays in the suite |

Writing inside the run's workspace is no longer a blocker: eval runs set `TMPDIR` outside `/tmp`
(anthropics/claude-code#104631), and `foreign-onboard` and `new-project-onboard` moved back to
`evals/` on 2026-11-16.

To restore one: `git mv` it back under `evals/` (the grader into `evals/builder-routing/graders/`)
and run that case once with `--case <name> --runs 1 --ablation none`.
