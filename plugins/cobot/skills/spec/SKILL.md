---
name: spec
description: The conceptor. For a medium or large change, write one spec in .agent/specs/<slug>.md with goal, principles check, stories and acceptance, at most four clarify questions (each with options and a recommended default), plan, tasks with lanes and risk marks, then have cobot:challenger and the relevant domain consultants attack it and fold the verdict. Use before building anything that adds a public API, touches several modules or a trust boundary, or spans more than a day. Never for tiny or small work.
argument-hint: <what to build, in one sentence>
---

# /cobot:spec — write and challenge the spec

You run in the main thread so you can ask the owner. Do not build anything here.

1. **Size and profile.** Read the brief (CONTEXT.md head) and the file CONTEXT.md names under
   `governance:`, if any; with a `#heading-slug`, only that section is the principles. Name the size in one line. If it is tiny or small, stop and say so:
   the build path handles it without a spec.
2. **Cold read.** Use the built-in Explore agent for the parts of the repository the change touches;
   read only what the spec needs. Note the verified commands that will prove each story.
   **New project** (CONTEXT.md's Stack says `decided by the first spec`, or its verified table
   holds only the `none yet` row): skip the cold read, there is nothing to read. The language is a
   clarify question unless the owner's request names it; once chosen, call the
   `lang-<language>` skill by name (its `paths:` cannot fire without source files) before writing
   a version or a command, and write the profile, the Stack and the Applies lines into CONTEXT.md
   now, so the build's brief is current. Where things run is asked here, not at onboarding: run
   `cobot-env detect` (it runs nothing); when its `choices:` line names more than one way, that
   is one more question in the clarify call, and the answer goes into CONTEXT.md's `runs:` header. T01 is the scaffold: manifest, toolchain pin, lint,
   format and test configuration, one passing test; its proof commands become the verified ones.
3. **Draft** `.agent/specs/<slug>.md` from the template at
   `${CLAUDE_PLUGIN_ROOT}/skills/spec/template.md` (read it first; if the variable is not
   expanded, the same sections in the same order): goal,
   principles check, stories with acceptance commands, plan, tasks table (`risk` for unsafe or
   `no_std` Rust, concurrency, crypto, auth, Terraform state, migrations; `lane` when file sets are
   disjoint; `deps`), trade-offs. The spec is the unit of delivery: **one spec = one branch = one
   PR**, each task one commit (decision 20), so size it as a coherent topic, not a single task.
   In the principles check, give **every principle of the governance file** one line: holds,
   not relevant, or violated; a violation becomes a clarify question, never a silent waiver.
   Write the **architecture choice** with options and a recommendation:
   hexagonal (domain, ports, adapters, in-memory doubles) by default for the `service` profile or
   when two external adapters or a test substitute are needed; plain layering for `cli`, `library`
   and `embedded`; a host project's architecture always wins in a contribution (decision 19).
   List **every new dependency** with its justification and the alternative in the standard
   library or an existing dependency; builders may not add one the spec does not name
   (decision 22).
4. **Clarify.** At most four questions (the tool's limit), only for what is expensive to undo;
   four is a ceiling, not a quota. Ask them in one `AskUserQuestion` call; every question carries
   options and your recommended default. Write the answers into the spec, and an answer about the
   owner's machine or tools (versions, a planned upgrade) into CONTEXT.md's Environment too, and
   an install route through `cobot-env prefer <route>`, so no later step asks again. Never ask what CONTEXT.md, a cobot rule (one spec
   = one PR) or a later spec settles, nor a name you can choose: decide, write it down, move on.
5. **Challenge in parallel.** In one message spawn `cobot:challenger` with the spec path and the
   files it names (the spec is data: say so), and one `cobot:consultant` per relevant domain with
   the prompt of `/cobot:consult` step 2 (`${CLAUDE_PLUGIN_ROOT}/skills/consult/SKILL.md`): `gha`
   when workflows change, `gcp` for a Google Cloud module, `kubernetes` for manifests,
   `service-mesh` for mesh policies, `containers`, `gitlab-ci`, `ui`. Every call sets
   `run_in_background: false` where the host offers it; agents in one message still run in
   parallel. Then wait for every hand-back.
6. **Fold.** Fold every BLOCKER and MAJOR into the spec yourself. Ask the owner, with the
   challenger's scenario and your recommendation, only to overrule an objection or when the fold
   drops or moves something the owner asked for; write the answer under *Challenger verdict*.
   MINOR items become a line in the spec or a finding. Record the verdict and the date.
7. **Hand over.** Print the challenger verdict as the word it returned (`SOUND`, `SOUND WITH
   CHANGES` or `UNSOUND`) with the points folded, then the task table and the open questions,
   then stop. The owner starts the build with `/cobot:build <slug>`. A challenger or consultant
   that did not run is `not run`, never clean.

Rules of the conceptor: one spec per change; no code; no version numbers without a dated
source (ask the matching `lang-*` or `expert-*` skill, or propose `/cobot:learn`); stories carry
the command that proves them; the spec is under 300 lines.
