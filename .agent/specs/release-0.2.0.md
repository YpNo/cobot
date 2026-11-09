# Spec — release 0.2.0: close R2, tidy, a human README

size: large · profile: library · owner: YpNo · date: 2026-11-09 · eight PRs, one branch each

## Goal

0.2.0 is the first tagged release. It carries everything merged since 0.1.0 (R1.1, R2 slices
1–3, the rename, the onboarding fixes) and closes what is still open: a green eval suite, a gap
in the gate's MCP rules, R2 slice 4, the live proofs R2 owes, a tidy repository, and a README a person reads in two minutes,
with everything technical moved to documents written for agents and architects. After the tag,
the owner runs the switch. What does not change: the gate's contract, memory formats, the agent
listing under 600 tokens, the skill listing under its 15 000-character budget.

## Principles check

- Proportionality: one release, eight PRs, each one concern; no new dependency.
- Evidence before structure: slice 4's surface changes (one `consult` skill, user-only skills)
  come with the measurement from the simplicity review; the eval run proves the suite before the
  switch relies on it.
- Currency (read 2026-11-09): the five pinned actions, ruff 0.17.4, pytest 9.2.0 and pytest-cov
  7.1.0 are current; markdownlint-cli2 is pinned at 0.21.0 against 0.24.0; this machine runs
  Claude Code 2.1.311 against 2.1.321 upstream (the owner's call).
- The owner's global README template lists twelve sections. The owner asked for a concise README
  for people; the twelve stay covered, most of them by one line and a link into `docs/`.

## Plan

| # | Branch | Content | Depends on |
|---|---|---|---|
| 1 | `chore/tidy` | history moves to `docs/history/` with an index (`00-discovery.md`, the design inputs that are decided: `challenge-01`, `crissp-review`, `proposal-a-lean`, `proposal-b-layered`, `owner-ideas-02`, `simplicity-review`, `onboard-arlo-findings`; `reference/legacy-audit.md` after the switch is planned); R1 spike scripts to `scripts/spikes/`; F-10 closed (fixed in R1.1 slice 2); F-14 fixed (`journal add` from a worktree writes the worktree's memory); markdownlint-cli2 0.24.0; CONTEXT.md refreshed | — |
| 2 | `fix/eval-suite` | F-13 and review proposal 6: regex graders for rule names and rejections, at most one judge per case, fixtures that stub cargo, terraform and pytest; the four cases below the bar re-read against the F-12 grader fix (GitHub PR 7); then the owner dispatches one full run on `main` (paid) and the result is journaled | 1 |
| 3 | `security/mcp-read-verbs` | the gate's MCP rules flip from a write-verb denylist to a read-verb allowlist: an MCP tool is silent only when its name starts with `list`, `get`, `describe`, `search`, `read` or `check`, and asks otherwise; `never` rules and owner `allow mcp__<server>__<tool>` lines keep their precedence. Found 2026-11-09 against Google's remote Cloud MCP servers (tool lists read without credentials): `deploy_service_from_image`, `start_instance`, `stop_instance`, `reset_instance`, `set_instance_machine_type`, `apply_k8s_manifest`, `patch_k8s_resource`, `cancel_operation`, `write_text` and `undelete_role` matched no rule. Tests take every tool of the seven servers read that day, with Google's `readOnlyHint` and `destructiveHint` as the oracle; the agent scopes (consultant, learner) get the same check | 1 |
| 4 | `feat/r2-surface` | review proposals 1–3 with their own spec: one `/cobot:consult <domain>` replacing the eight `consult-*` skills (spike first: two Skill calls in one message run in parallel), `onboard`, `rules`, `security-sweep` user-only, `expert-*` and `lang-*` descriptions capped near 350 characters | 1 |
| 5 | `feat/r2-stacks` | R2 slice 4: `fw-react`, `fw-next`, `fw-vue`, `lang-shell` promoted, `expert-api`, Gitea through `tea`; its own spec, challenged | 4 |
| 6 | none (journal), then `docs/expert-gcp-mcp` | live proofs: a builder run through the report hook, `/cobot:security-sweep` and a full `/cobot:ship` on a service repository, GCP module work end to end (R2's exit criterion; needs one of the owner's GCP repositories) **with the Google Cloud MCP spike** (below), a clean `/cobot:wrap` here so `git push` reads a stamp | 2, 3, 5 |
| 7 | `docs/readme` | the README below, `docs/architecture.md`, `docs/configuration.md`, `docs/development.md`, badges, the banner, `scripts/github-settings.sh --apply` if the repository goes public | 5 |
| 8 | `chore/release-0.2.0` | `plugin.json` and `marketplace.json` to 0.2.0, Unreleased cut to `[0.2.0] - <date>`; the owner pushes the tag and `release.yml` publishes; then the switch (`docs/03-switch-plan.md`) | 2, 6, 7 |

2, 3 and 4 can run in parallel. The README comes after slice 4 because slice 4 changes the
command list it shows.

## Google Cloud MCP spike (inside PR 6)

Google hosts remote MCP servers at `https://<service>.googleapis.com/mcp` (Streamable HTTP,
IAM-controlled: `roles/mcp.toolUser` plus the service's own roles; an IAM condition can block a
principal from read-write tools server-side; read 2026-11-09 at
docs.cloud.google.com/mcp/supported-products and /mcp/authenticate-mcp). `google/mcp` is a
curated list, "not an officially supported Google product".

1. On the project of the GCP proof repository, a principal with `roles/mcp.toolUser`, viewer
   roles and the IAM condition that prevents read-write tool use.
2. `claude mcp add --transport http --client-id <id> --client-secret --callback-port <port>
   gcp-logging https://logging.googleapis.com/mcp -s user` (Google's docs describe only the
   claude.ai connector; the CLI flags exist in 2.1.311, the flow is unverified), then the same
   for `container.googleapis.com/mcp`.
3. Prove: `list_log_entries` and `list_k8s_events` answer from the main thread and from a
   consult fork; a write tool asks through the gate (PR 3) and fails at IAM even when approved.
4. Write the setup into `expert-gcp` the way Stitch is set up (decision 27): the owner
   registers servers and holds the credentials, cobot ships none. ADR-0006 stands: `cobot-gcp`
   is created only once cobot ships a server configuration. Decisions 25 and 26 are refined for
   Google Cloud: Google-hosted read tools are welcome (structured, no local code); writes stay
   with `gcloud` under the gate. The local open-source servers (`gcloud-mcp`, `gke-mcp`, MCP
   Toolbox) run code on the machine and are used only where no remote server exists.

## README (PR 7)

For people, under 120 lines:

1. Banner, badges, one sentence: *a governed co-pilot for Claude Code — it plans, builds and
   remembers, and asks before anything leaves your machine.*
2. What you get, four bullets: spec and challenge before code; builders with proof; memory per
   repository; a rules gate (`never`, `ask`, `allow`).
3. How it works: one small diagram (you → orchestrator → spec · build · consult; gate and memory
   around them).
4. Install in three commands; first use in three steps (`/cobot:onboard`, ask, `/cobot:spec` →
   `/cobot:build` → `/cobot:wrap`).
5. Commands you type (one table); what cobot uses on its own (one line).
6. Safety in one paragraph; requirements; links: for agents and architects
   (`.agent/CONTEXT.md`, `docs/architecture.md`, `docs/configuration.md`,
   `docs/development.md`, `docs/02-design.md`, `docs/adr/`); security, contributing, changelog,
   license, one line each.

Moved out of the README: the layer table and roster (architecture), the configuration table,
rule syntax and environment (configuration), testing, evals, CI/CD, release and repository
settings (development).

## Badges

Rendered for everyone only once the repository is public (shields.io cannot read a private
repository; GitHub's own workflow badge shows to people with access).

```markdown
[![CI](https://github.com/YpNo/cobot/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/YpNo/cobot/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/YpNo/cobot?sort=semver)](https://github.com/YpNo/cobot/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.285-d97757)](https://code.claude.com/docs/en/plugins)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776ab)](pyproject.toml)
[![Coverage gate](https://img.shields.io/badge/coverage%20gate-85%25-brightgreen)](.github/workflows/ci.yml)
```

The last one states the gate CI enforces, not a measured number; a measured badge needs a
coverage service, which this spec does not add.

## Banner (prompt for the image agent)

Two crops from one image: `docs/assets/banner.png` at 1600×400 for the README and
`docs/assets/social.png` at 1280×640 for GitHub's social preview.

> A wide, calm banner illustration for a developer tool named "cobot". Flat vector style with
> soft depth, clean geometric shapes, generous negative space on the left third for a wordmark
> added later. Scene: a friendly collaborative robot arm (an industrial "cobot", rounded,
> white and graphite) working side by side with a developer at a terminal. The robot holds a
> blueprint sheet (planning); behind them, a translucent shield-shaped gate with three small
> lights — red, amber, green — stands between the desk and a doorway glowing outward (actions
> leaving the machine pass the gate); on the desk, a closed notebook with a bookmark (memory).
> Palette: deep navy background (#0f1b2d), teal accents (#2bb3a3), one warm amber highlight
> (#f2a541), off-white lines. Mood: trustworthy, precise, quietly playful. No text, no letters,
> no logos, no brand marks, no real products, no people's faces in detail. Even lighting, no
> gradients banding, crisp edges, readable at small sizes.

The wordmark and tagline are set afterwards in SVG, so no generated lettering ends up garbled.

## Exit criterion

The tag `v0.2.0` exists and `release.yml` published it; the full eval run on `main` is green at
the suite's thresholds; R2's GCP proof and the MCP spike are journaled; no MCP tool outside the read verbs passes the
gate silently; the README passes a two-minute read by the
owner; `install.sh --check` is clean, so the switch can start.

## Owner decisions (2026-11-09)

1. **Public with 0.2.0** (decision 10 holds): PR 7 runs `scripts/github-settings.sh --apply`,
   the badges render for everyone, and 0.3.0's Antigravity install can use the GitHub URL.
2. GCP proof: the owner names the repository; open until then.
3. Banner: generated by the owner's image agent from the prompt above; the result goes to
   `docs/assets/` in PR 7.
