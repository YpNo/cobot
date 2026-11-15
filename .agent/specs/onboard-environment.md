# Spec — onboarding learns the machine's development environment

size: medium · profile: library · owner: YpNo · date: 2026-11-15 · revision 1 · built on `main`
`349a940`

## Goal

Today onboarding writes only "the runtimes present" and a disk check into a repository's
CONTEXT.md. It does not know whether the owner runs containers with Docker or Podman, manages
runtimes with mise, builds inside a distrobox, or lacks a tool the repository needs. Nor does it
suggest the tools that make cobot itself work better (RTK, ripgrep, jq, gh). So builders guess
the command prefix, the ship skill guesses the container runtime, and a missing tool shows up as
a failed command mid-build.

After this spec:

- cobot keeps a **machine profile** at owner level (`~/.claude/cobot/machine.md`), detected once
  per machine by a read-only probe and refreshed when stale. Nothing about the machine is
  committed into a repository.
- **Onboarding asks per repository** where things run when the machine offers more than one way
  (Docker or Podman; the host or a distrobox; mise or the system runtime), recommending what the
  repository's own files name, and records the answer in that repository's CONTEXT.md.
- A **missing tool** the repository needs gets an install command in the owner's preferred route
  (asked once per machine), printed for the owner to run; cobot never installs.
- A **curated, dated list** of tools that help cobot's own work is advised once when a tool is
  absent; a decline is remembered and never asked again.

Unchanged: the gate (it already reads through `rtk`, `mise exec` and `distrobox enter`, checked
2026-11-15); the question budget of one `AskUserQuestion` with at most four questions; foreign
mode (its CONTEXT.md lives outside the repository already).

## Owner's answers (2026-11-15, before drafting)

- Where machine facts live → **a machine profile**, one owner-level file; each repo's CONTEXT.md
  keeps only what that repository needs.
- A missing tool → **propose, the owner runs**: the install command in the preferred route.
- Advice for cobot's own tools → **a curated list**, advised once, a decline remembered.
- Two ways to run things → **ask per repository** (the question recommends what the repository's
  files name, when they name one).

## Principles check

- Proportionality: medium (a new tool, a new owner-level file, onboard steps in two paths).
- Rules before autonomy: detection is read-only; installs are proposed only (protocol: global and
  outward steps are proposed); the per-repo question replaces a guess.
- Knowledge is a skill: the advice list is a dated reference with sources, refreshed like any
  knowledge line; no version is written without one.
- Proof not promises: the probe's output is the evidence; a tool reported present carries the
  version line it printed.
- Governance (`docs/01-decisions.md`): a new decision 29 (machine profile at owner level, install
  proposed only, advice once); decisions 21 (dependency currency) and 22 (no dependency without a
  spec) hold.
- Architecture: plain layering; a new stdlib tool `bin/cobot-env` beside `cobot-deps`.
- New dependencies: none (`shutil.which`, `subprocess` with a timeout).
- Delivery: one branch `feat/onboard-environment`, one PR; tasks below are the commits.

## Stories and acceptance

1. As the owner, cobot knows my machine without asking twice. Accept: `cobot-env detect` probes a
   fixed list (container: docker, podman, their compose commands and whether `docker` is podman;
   runtimes: mise, asdf; isolation: distrobox, toolbox, nix, devcontainer CLI; whether it runs
   inside a container or a distrobox; helpers: rtk, rg, fd, jq, gh, uv) with `--version` and a
   2-second timeout each, writes `~/.claude/cobot/machine.md` (dated lines, the version each tool
   printed), and prints what changed since the last run. It runs nothing from a repository and
   needs no network. Tests: a fake PATH of stub tools; a hanging stub times out; an absent tool is
   `absent`, never guessed.
2. As the owner, I am asked once per machine how missing tools should be installed. Accept: the
   first onboarding on a machine without a preference asks it (mise · the distro's package
   manager · inside a named distrobox · a container), within the onboarding's one question call;
   the answer goes to the profile; later onboardings read it.
3. As the owner, onboarding asks per repository where things run, when there is a choice.
   Accept: with both Docker and Podman, or a distrobox beside the host, or mise beside a system
   runtime, onboard asks which applies to this repository; the recommended option is what the
   repository names (`Containerfile`/`Dockerfile`, a compose file, `.mise.toml`/`.tool-versions`,
   `distrobox.ini`, `.devcontainer/`); with one way only, no question. The answer becomes a line
   in CONTEXT.md's Environment (`runs: podman · builds: distrobox enter dev --`), and the verified
   commands carry that prefix.
4. As the owner, a missing tool is named with its install command, never installed. Accept: a
   verified or needed command whose program is absent gets one CONTEXT line and a journal Open
   line with the command in the preferred route (`mise use <tool>@<version>` with the version
   from the matching `lang-*` skill, `sudo dnf install <pkg>`, `distrobox enter <box> -- …`);
   cobot runs none of them.
5. As the owner, cobot advises its own helper tools once. Accept: `skills/onboard/references/
   workstation.md` lists each helper with what it saves cobot, its licence, its repository and a
   dated `[verified …]` line; onboarding names the absent ones once; a decline is written to the
   profile and never advised again; RTK's line says the gate reads through its rewrite.
6. As a builder or a later skill, I read where things run. Accept: the brief carries one machine
   line (at most 160 characters: runtime, isolation, the profile's date, `stale` past 30 days);
   ship and build read CONTEXT's Environment prefix instead of guessing.
7. Under the Antigravity CLI the same profile and lines apply. Accept: `cobot-session start
   --runtime agy` carries the machine line; `cobot-env` is one of cobot's own tools there too.

## Plan

1. `bin/cobot-env` (stdlib): `detect` (probe, write the profile, print the change), `show`,
   `decline <tool>`; the profile format is markdown with dated lines and a preferences block the
   owner may edit; a missing or unreadable profile is `none yet`, never an error.
2. Repository detection inside onboard step 4 (file names only, no content run): the runtime and
   isolation files of story 3.
3. Onboard: existing repositories gain step 4b (profile, the per-repo question, missing tools,
   advice); the new-project path N3 writes the Environment from the profile instead of "the
   runtimes present". The questions share the one `AskUserQuestion` call and its four-question
   cap; the per-repo question has priority over advice.
4. `skills/onboard/references/workstation.md`: helpers and install routes, every line verified at
   build time from its repository or package registry.
5. Brief: `cobot-session` adds the machine line after the memory brief, inside the existing caps.
6. Default rule: `cobot-env` runs silently like cobot's other tools; check-plugin and
   sync-agents learn the new tool.
7. Docs (configuration, architecture), decision 29, CHANGELOG.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `cobot-env detect`, `show`, `decline` and the profile; tests with stub tools | a | — | — |
| T02 | repository runtime detection (file names); tests | b | — | — |
| T03 | onboard steps 4b and N3, the per-repo and per-machine questions, missing-tool lines | a | — | T01, T02 |
| T04 | `references/workstation.md`, every line verified at build time | b | — | — |
| T05 | the brief's machine line in both runtimes; default rule; check-plugin | a | — | T01 |
| T06 | docs, decision 29, CHANGELOG | b | — | T03–T05 |

## Trade-offs

- An owner-level profile over per-repo detection: one probe per machine, nothing machine-specific
  committed; the cost is one more owner file, which the owner may edit.
- Ask per repository (the owner's choice) over remembering a machine default: a repository can
  differ from the machine's habit; the recommended option keeps the question one click.
- Propose installs over running them: consistent with the protocol and finding F-36; the cost is
  one command the owner pastes.
- A fixed probe list over discovering everything on PATH: bounded, testable, fast; a tool outside
  the list is found only when a verified command needs it.

## Clarify

Asked before drafting; the answers are under *Owner's answers*.

## Challenger verdict

pending

## Converge

pending
