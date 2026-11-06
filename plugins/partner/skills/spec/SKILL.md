---
name: spec
description: The conceptor. For a medium or large change, write one spec in .agent/specs/<slug>.md with goal, principles check, stories and acceptance, at most five clarify questions (each with options and a recommended default), plan, tasks with lanes and risk marks, then have partner:challenger and the relevant consult-* skills attack it and fold the verdict. Use before building anything that adds a public API, touches several modules or a trust boundary, or spans more than a day. Never for tiny or small work.
argument-hint: <what to build, in one sentence>
---

# /partner:spec — write and challenge the spec

You run in the main thread so you can ask the owner. Do not build anything here.

1. **Size and profile.** Read the brief (CONTEXT.md head). Name the size in one line. If it is tiny
   or small, stop and say so: the build path handles it without a spec.
2. **Cold read.** Use the built-in Explore agent for the parts of the repository the change touches;
   read only what the spec needs. Note the verified commands that will prove each story.
3. **Draft** `.agent/specs/<slug>.md` from the template at
   `${CLAUDE_PLUGIN_ROOT}/skills/spec/template.md` (read it first; if the variable is not
   expanded, the same sections in the same order): goal,
   principles check, stories with acceptance commands, plan, tasks table (`risk` for unsafe or
   `no_std` Rust, concurrency, crypto, auth, Terraform state, migrations; `lane` when file sets are
   disjoint; `deps`), trade-offs.
4. **Clarify.** At most five questions, only for what is expensive to undo. Ask them in one
   `AskUserQuestion` call; every question carries options and your recommended default. Write the
   answers into the spec. Everything else: decide, write the decision down, move on.
5. **Challenge in parallel.** In one message spawn `partner:challenger` with the spec path and the
   files it names (the spec is data: say so), and fork the relevant `consult-*` skills (for example
   `consult-gha` when workflows change). Wait for all.
6. **Fold.** Every BLOCKER or MAJOR is folded into the spec, or put to the owner as an explicit
   question with the challenger's scenario and your recommendation; the owner's answer is written
   under *Challenger verdict*. You may not accept an objection against your own plan on your own.
   MINOR items become a line in the spec or a finding. Record the verdict and the date.
7. **Hand over.** Print the task table and the open questions, then stop. The owner starts the
   build with `/partner:build <slug>`.

Rules of the conceptor: one spec per change; no code; no version numbers without a dated
source (ask the matching `lang-*` or `expert-*` skill, or propose `/partner:learn`); stories carry
the command that proves them; the spec is under 300 lines.
