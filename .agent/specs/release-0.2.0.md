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
| 2 | `fix/eval-suite` | F-13 and review proposal 6. **As built:** no stub tools were needed: `builder-routing` grades a cargo command quoted with its exit code (any code, so a toolchain the sandbox cannot run still grades the protocol); `never-apply` and `proof-required` lose their judges for deterministic graders (one terraform call at most, no rules or settings edit, no question, no `Apply complete`; a refusal regex and a rerun-or-send-back regex), `proof-required`'s fixture moves from pytest to the standard library's `unittest`, and `never-apply`'s prompt asks for the alternative without running anything else. `tests/test_eval_graders.py` checks, for free, that every pattern compiles, no case has more than one judge (only `learn-unknown-domain` keeps one: it ties each fact to its own verified entry) and every fixture runs. The four cases once below the bar were already 1.00 after the F-12 fix (journal 2026-11-08). Then the owner dispatches one full run on `main` (paid) and the result is journaled | 1 |
| 3 | `security/mcp-read-verbs` | the gate's MCP rules flip from seven write verbs to a catch-all `ask mcp__*` with two exceptions: a read (the last part of the name starts with `list`, `get`, `describe`, `search` or `read`, and no write word follows `and`, `or`, `then`, `plus`: `get_or_create_user` asks, `get_commit` stays a read; `check` is left out, `check_in_file` writes) and the desktop host's UI tools named one by one (`update_plan`, `wrap_up`, `mark_chapter`, `show_widget`, …). Order for MCP: never > owner allow > owner or project ask > read or host tool > the catch-all, so a default rule never cancels an ask the owner or the project wrote (challenger BLOCKER, folded). **Friction accepted:** browser servers (`claude-in-chrome`, Playwright), `fetch` and context7's `resolve-library-id` now ask until the owner adds `allow mcp__<server>__*`; `update_plan`, which asked on every call before, is silent. Found 2026-11-09 against Google's remote Cloud MCP servers (tool lists read without credentials): `deploy_service_from_image`, `start_instance`, `stop_instance`, `reset_instance`, `set_instance_machine_type`, `apply_k8s_manifest`, `patch_k8s_resource`, `cancel_operation`, `write_text` and `undelete_role` matched no rule. Tests take all 86 tools of the seven servers with Google's `readOnlyHint` as the oracle (not read-only must ask; read-only may ask: `check_k8s_auth` does) | 1 |
| 4 | `feat/r2-surface` | review proposals 1–3 with their own spec: one `/cobot:consult <domain>` replacing the eight `consult-*` skills (spike first: two Skill calls in one message run in parallel), `onboard`, `rules`, `security-sweep` user-only, `expert-*` and `lang-*` descriptions capped near 350 characters | 1 |
| 5 | `feat/r2-stacks` | R2 slice 4: `fw-react`, `fw-next`, `fw-vue`, `lang-shell` promoted, `expert-api`, Gitea through `tea`; its own spec, challenged | 4 |
| 6 | none (journal), then `docs/expert-gcp-mcp` | live proofs: a builder run through the report hook, `/cobot:security-sweep` and a full `/cobot:ship` on a service repository, GCP module work end to end (R2's exit criterion; needs one of the owner's GCP repositories) **with the Google Cloud MCP spike** (below), a clean `/cobot:wrap` here so `git push` reads a stamp. **As built (2026-11-10 and 11, gcp-platform):** onboard (profile infra, F-01 google-beta `$` found unprompted), `/cobot:consult gcp kubernetes service-mesh` (three consultants in one message), fixes proven offline (fmt, `hcl validate`, 7/7 module validate, tftest 3 passed; plan is the owner's, no credentials here), `/cobot:security-sweep` (forked, MEDIUM only; it skipped `shell.md`: fixed in PR 23 with the gate's opaque-reason fix), `/cobot:wrap` with review fan-out; the MCP spike proved Logging and GKE reads and showed the deny policy needs an organisation, so `never mcp__gcp-*__<write verb>_*` rules ship in `docs/expert-gcp-mcp`. **Builder proof (2026-11-11):** a headless `/cobot:build` here sent the protocol-budget check to `cobot:python-builder` (tests failing first, then green); its report passed the report check, and the same report with exit codes stripped is blocked. **Wrap (2026-11-11):** a headless `/cobot:wrap` here ran the full set and the reviews and parked F-15 to F-19 (stamp blind in worktrees, sync regression, test isolation, doc wording), all fixed on this branch; the journal's last stamp reads `ok` in the worktree. **Still open:** `/cobot:ship` on a service repository | 2, 3, 5 |
| 7 | `docs/readme` | the README below, `docs/architecture.md`, `docs/configuration.md`, `docs/development.md`, badges, the banner. **As built (2026-11-09), before slice 4 at the owner's request:** a 103-line README, the three documents carrying the moved content, the six badges, `banner.jpg` and `social.jpg` from the owner's illustration with the wordmark set by `scripts/make-banner.py` (Inter 4.1, not committed); PR 4 edits the consult row of the command table | 1 |
| 8 | `chore/release-0.2.0` | **As built (2026-11-12, rebased onto main 2026-11-14):** versions and the changelog cut on the branch; the rest is the owner's. `plugin.json` and `marketplace.json` to 0.2.0, Unreleased cut to `[0.2.0] - <date>`; `scripts/github-settings.sh --apply` as the repository goes public and `docs/assets/social.jpg` uploaded as the social preview; the owner pushes the tag and `release.yml` publishes; then the switch (`docs/03-switch-plan.md`) | 2, 6, 7 |

2, 3 and 4 can run in parallel. The README came early at the owner's request; PR 4 edits its
command table when the consult skills merge.

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

Two crops from one image: `docs/assets/banner.jpg` 1600 wide for the README and
`docs/assets/social.jpg` at 1280×640 for GitHub's social preview (as built).

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
