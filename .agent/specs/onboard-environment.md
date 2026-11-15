# Spec — onboarding learns the machine's development environment

size: medium · profile: library · owner: YpNo · date: 2026-11-15 · revision 2 (challenger pass
folded) · built on `main` `349a940`

## Goal

Today onboarding writes only "the runtimes present" and a disk check into a repository's
CONTEXT.md. It does not know whether the owner runs containers with Docker or Podman, manages
runtimes with mise, builds inside a distrobox, or lacks a tool the repository needs; nor does it
suggest the tools that make cobot itself work better (RTK, ripgrep, jq, gh). Builders guess the
command prefix, ship guesses the container engine, and a missing tool shows up as a failed
command mid-build.

After this spec:

- **Detection runs nothing.** `cobot-env` reads presence only: files and environment variables,
  never a program's output, so no repository-chosen binary or shim runs. It is cheap, so it runs
  fresh at every onboarding; nothing detected is cached.
- **A machine profile holds only the owner's answers** (install route, declined helpers),
  at owner level, keyed by host and container, so a distrobox and its host never overwrite each
  other. Nothing about the machine is committed into a repository.
- **Onboarding asks per repository where things run**, when there is more than one way, before
  it runs any command; the answer is a CONTEXT.md header field the brief always keeps.
- **A missing tool gets an install command** in the owner's route, printed for the owner to run;
  the gate asks on every install route cobot emits.
- **Helpers cobot benefits from are advised once**, in one printed line; a decline is remembered.

Unchanged: the gate's unwrapping of `rtk`, `mise exec` and `distrobox enter` (checked
2026-11-15); the verified commands stay bare, as CI runs them.

## Owner's answers (2026-11-15, before drafting)

- Where machine facts live → a machine profile at owner level; each repo keeps only its needs.
- A missing tool → propose, the owner runs.
- Advice for cobot's own tools → a curated list, advised once, a decline remembered.
- Two ways to run things → ask per repository, recommending what the repository's files name.

## Principles check

- Proportionality: medium (a new tool, an owner-level file, onboard steps in both paths, rules).
- Rules before autonomy: detection executes nothing; installs are proposed and the gate asks on
  them; the per-repo question replaces a guess.
- Knowledge is a skill: install routes, package names and helpers live in a dated reference.
- Proof not promises: a marker test proves no repository program runs; eval cases prove the
  question count and order and that no prefix reaches CI.
- Governance (`docs/01-decisions.md`): new decision 29 (detection by presence, answers at owner
  level keyed by host, installs proposed and asked, advice once); 21, 22 and 28 (programs the
  repository chooses are untrusted) hold.
- Architecture: plain layering; a new stdlib tool `bin/cobot-env` beside `cobot-deps`.
- New dependencies: none.
- Delivery: one branch `feat/onboard-environment`, one PR; tasks below are the commits.

## Stories and acceptance

1. **Detect by presence.** `cobot-env detect` reports, executing nothing: container engines
   (`docker`, `podman`; one engine when `docker` resolves to podman, or `DOCKER_HOST` or the
   current context in `~/.docker/config.json` points at a podman, Colima or OrbStack socket);
   runtime managers (mise, asdf); isolation (distrobox, toolbox, nix, devcontainer); whether the
   session runs inside a container (`/run/.containerenv`, `/.dockerenv`, `CONTAINER_ID`) and
   which; the OS and package manager (`/etc/os-release`; apt, dnf, pacman, zypper, apk, brew);
   helpers by name and alias (`fd`/`fdfind`). PATH entries under the repository root, relative
   entries and the mise shims folder are not trusted: a hit there is reported `via repository` or
   `via mise shim`, never followed. Accept: a stub on a repository PATH entry that writes a
   marker is reported and the marker is never written; the aliases and the podman-as-docker
   cases have tests; the whole detection takes under 100 ms.
2. **Owner answers, per host.** `~/.claude/cobot/machine.md` holds, per `host[/container]`
   key, the install route and the declined helpers. `cobot-env prefer <route>` and
   `cobot-env decline <helper>` (helpers from the curated list only) write it, re-reading and
   replacing it atomically and keeping lines the owner edited. Accept: two keys (host and a
   distrobox) never overwrite each other; an unknown helper name is refused.
3. **Ask per repository, before running.** In an existing repository, after trust (step 2) and
   before step 4 runs a command, onboard detects the repository's runtime files
   (`Containerfile`/`Dockerfile`, compose, `.mise.toml`/`.tool-versions`, `distrobox.ini`,
   `.devcontainer/`) and, when the machine offers more than one way, asks one combined question
   (engine · where builds run · runtime manager), recommending what the files name; with one way
   only, no question. This is a second question call in the existing path. The answer is a
   header field `runs:` (`runs: podman · builds: distrobox enter dev --`); step 4 runs its
   commands that way and records them bare. Accept: an eval case checks the question count and
   that it comes before the first command; a ship eval checks no `runs:` prefix reaches ci.yml.
4. **New project.** No environment question at onboarding: the first spec, which already
   decides the language, asks it with the stack, and writes `runs:`. N3 writes Environment from
   detection only.
5. **Missing tools.** A verified or needed command whose program is absent gets one Environment
   line and a journal Open line with the command in the owner's route: `mise install` when the
   repository pins the version; otherwise `mise use -g <tool>@<version>` from a lang-* line that
   is not stale, labelled an owner-level change; a package name from the reference's map for the
   detected package manager; `distrobox enter <box> -- …`. The install-route question is asked
   only when a tool is missing and the profile has no route. cobot runs none of them, and the
   gate asks on each (`mise use*`, `mise install*`, `brew install*`, `uv tool install*`,
   `pipx install*`, `cargo install*`, `npm install -g*`, the package managers), with F-36.
6. **Advice once.** `skills/onboard/references/workstation.md` lists each helper with what it
   saves cobot, its licence, its repository and a dated verified line, and rtk's identity check
   (the Rust Token Killer, not the "Rust Type Kit"). Onboarding prints one line naming the absent
   helpers and how to decline; it never takes a question slot.
7. **Brief and agy.** The brief carries one machine line (at most 160 characters) after the
   memory brief, with `LINES_RESERVE` raised by 160; `agy_section` names `cobot-env`. Accept:
   both runtimes at the maximum warning size keep the machine and deps lines.
8. **Templates claim nothing (F-38, folded).** The CONTEXT and JOURNAL templates stop claiming
   exit 0 or "were run"; init writes the new tree's `none yet` row itself.

## Plan

1. `bin/cobot-env` (`detect`, `prefer`, `decline`, `show`) and its tests.
2. Default rules: ask rows for the install routes; `cobot-env` runs silently like cobot's tools.
3. Onboard: step 3b (detect, the combined question, `runs:`) before step 4; N3 and the spec
   skill for new projects; missing-tool lines; the advice line.
4. `references/workstation.md`: routes, package-name map per manager, helpers, every line
   verified at build time.
5. cobot-memory: the `runs:` header field kept by the brief; the templates (F-38).
6. cobot-session: the machine line, the reserve, agy.
7. Docs (configuration, architecture), decision 29, CHANGELOG, F-38 closed.

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `cobot-env` presence detection, untrusted PATH entries, the profile and its writers; tests incl. the marker | a | auth | — |
| T02 | default ask rows for install routes; `cobot-env` silent; tests | b | auth | — |
| T03 | `references/workstation.md`, verified at build time | c | — | — |
| T04 | onboard step 3b, N3, the spec skill's new-project question, missing tools, advice | a | — | T01, T03 |
| T05 | `runs:` header, templates (F-38), brief line and reserve, agy section | a | — | T01 |
| T06 | eval cases (question order, no prefix in CI), docs, decision 29, CHANGELOG | b | — | T04, T05 |

## Trade-offs

- Presence over running `--version`: nothing the repository chooses runs, and detection is cheap
  enough to need no cache; no story needs a version string.
- Answers keyed by host and container over one file per machine: HOME is shared by a distrobox,
  an NFS home or synced dotfiles.
- A header field over prefixed verified commands: CI runs the commands bare; the brief keeps the
  header when it is capped.
- No environment question on a new project: the first spec decides the stack and asks it there.
- Advice as a printed line over a question: the question call is already full.

## Clarify

Asked before drafting; the answers are under *Owner's answers*.

## Challenger verdict

Pass 1, 2026-11-15: **SOUND WITH CHANGES**, fifteen points, all folded.

- BLOCKER running `--version` could execute a repository-chosen binary or shim (direnv, mise
  activation) → presence only, untrusted PATH entries reported, never followed (story 1).
- MAJOR no story needed version strings; caching added timeouts, staleness and tool output in
  prompts → detect fresh, the profile holds answers only.
- MAJOR the question came after step 4 had recorded commands → step 3b, before any command.
- MAJOR a prefix in the verified commands would reach CI; Environment is dropped when the brief
  is capped → a `runs:` header field.
- MAJOR the question budget overflowed → one combined question; none on a new project; the
  install route only when a tool is missing; advice printed.
- MAJOR the install routes cobot emits passed the gate silently → ask rows (with F-36).
- MAJOR `mise use` without `-g` writes the repository's mise.toml and overrides its pin → `mise
  install` for a repo pin, `mise use -g` labelled owner-level, versions only from fresh lines.
- MAJOR one profile per HOME is not per machine (distrobox, NFS) → keyed by host and container.
- MAJOR the engine was read from the CLI name → `DOCKER_HOST` and the docker context; the podman
  alias is one engine.
- MAJOR no package manager detection or name map → os-release, managers, a map per route.
- MINOR aliases (`fdfind`) and rtk's identity; writers for the answers, atomic; the brief
  reserve and agy section; acceptance that proves the stories; F-38 folded.

Moved by the fold, confirmed by the owner (2026-11-15): on a **new project** the "where things
run" question moves from onboarding to the first spec.

## Converge

pending
