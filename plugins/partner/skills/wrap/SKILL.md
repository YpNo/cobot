---
name: wrap
description: Close a working session. Converge against the spec (what is missing), run the full verified command set with output tails, fan out the reviews (/code-review, /security-review, relevant consult-* skills) in parallel, fold or journal every finding, triage FINDINGS.md rows, refresh CONTEXT.md if commands changed, write the journal entry with the verified stamp (commit, commands). Use once at the end of a session, before any commit, push or pull request is proposed.
argument-hint: [spec slug]
---

# /partner:wrap — converge, prove, review, remember

1. **Converge.** If a spec is given: for every story, state whether its acceptance command passed
   today; list what is missing under *Converge* in the spec. No story is "done" without its proof.
2. **Full run.** Run the complete verified command set from CONTEXT.md (tests with coverage, lint,
   format check, type check, security scan, plugin or schema validation, whatever the table lists).
   Keep the output tails; do not condense failures (`rtk proxy` if needed).
   Then the **pre-PR currency check** (decision 21): the ecosystem's outdated and advisory
   commands from the matching `lang-*` skill (`cargo outdated` and `cargo deny check advisories`,
   `go list -m -u all` and `govulncheck`, `npm outdated` and `npm audit`, `uv pip list --outdated`
   and `pip-audit`, `terraform providers lock` dry run). Report the gap; upgrade nothing unasked.
3. **Review fan-out**, in one message: `/code-review` at the size's level, `/security-review` when
   the diff touches inputs, auth, secrets, shell or infra, and the relevant `consult-*` skills
   (workflows changed → `consult-gha`). Fold what is cheap and safe; everything else is journaled
   under `Open` with the finding text, or becomes a findings row.
4. **Findings triage.** `partner-memory findings list --open`: each row becomes a spec task, an
   issue the owner may open (propose the `gh issue create` command, do not run it), or
   `partner-memory findings close F-nn "<reason>"`.
5. **Memory.** If a verified command changed or a new one was proven, update CONTEXT.md's table
   with today's date. Keep CONTEXT.md under 120 lines.
6. **Journal.** One entry through `partner-memory journal add`:
   `## YYYY-MM-DD — <title>` then `Changed:` `Why:` `Proof:` (commands, exit codes, tails)
   `Open:` `Next:` and the stamp `verified: <HEAD sha> · <commands run>`. The stamp is what
   `contribute` and `ship` will require before proposing a push.
7. **Hand over.** The spec's branch becomes **one PR** (decision 20): check the commit log for an
   attribution footer or an AI named as author (decision 18) before proposing it, then list what
   the owner may now do (push, `gh pr create` with the body you drafted), each as a command the
   owner runs or approves. Nothing outward happens here.
