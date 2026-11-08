# Keeping cobot simple to use — reviewed 2026-11-08

Sources, read today:

- Google Cloud blog, "Behind the scenes, two months later: How we ship Google Agent Skills like
  products" (2026-10-29, R. Samborski), its predecessor (2026-08-03) and `github.com/google/skills`
  (170+ skills, Apache-2.0).
- `mattpocock-skills` 1.3.1 as installed here (`~/.claude/plugins/cache/claude-plugins-official/`):
  27 skills, `.agents/invocation.md`, ADR-0001, README.
- Claude Code skills docs (`code.claude.com/docs/en/skills.md`), for the listing mechanics below.

The question asked: what does a user have to know and type to get value from cobot, and what can
we remove from that. Neither source is adopted as a framework. Google ships a library of 170
independent product skills; Pocock ships small composable skills he says replace process
frameworks. cobot is a governed process: a gate, memory and an orchestrator that routes work.
The owner prefers the spec-kit style of one planning path (decision 2), so ticket and board flows
stay out.

## What the user faces

| Surface | `main` today | With slice 3 (`feat/r2-cloud`, built, not merged) |
|---|---|---|
| Slash commands in the menu | 13 (`onboard`, `spec`, `build`, `wrap`, `learn`, `rules`, `ship`, `contribute`, `security-sweep`, four `consult-*`) | 16 (seven `consult-*`) |
| Skill descriptions in the model's listing, every session | 24 skills, 13 782 chars | 30 skills, 14 651 of our 15 000 cap |
| `install.sh` modes | `--dev`, `--project`, `--local`, `--refresh`, `--user`, `--check`, `--uninstall`, `--source` | same |
| Overlapping verbs on the owner's machine | legacy `/onboard /design /build /wrap /ship /security-sweep`, Pocock's `code-review`, `pr`, `research`, `tdd`, built-in `/code-review`, `/security-review` | same |

What a user needs is three things: install, `/cobot:onboard` once, then ask. The protocol
already sizes the request and runs spec, build and wrap itself. Everything else is occasional
(`ship`, `contribute`, `security-sweep`, `rules`) or something the orchestrator reaches for on
its own (`learn`, the consults). Slice 3's decision 28 already moves the "one `consult` skill"
choice to slice 4, because slice 4 has no room left under the cap.

## A fact that changes the budget argument

The Claude Code docs, read today, state that the skill listing budget "scales at 1% of the
model's context window", that every name is always listed, and that past the budget
"Claude Code drops descriptions starting with the skills you invoke least". Per entry the cap is
1 536 chars. The docs call it a character budget without giving the conversion, so `/context`
(Skills row) is the measure. `disable-model-invocation: true` removes a skill from the model's
context entirely: zero listing cost, the Skill tool call is blocked, the user can still type it.
`user-invocable: false` only hides it from the menu. Whether `paths:` keeps a skill out of the
listing until a matching file is touched is not documented.

Our 15 000-char cap is our own sum, not that budget, which every installed plugin and user skill
shares. The 11 `expert-*` and `lang-*` skills sit in the listing (`user-invocable: false`) and are
the "invoked least", so theirs would be the first descriptions dropped. Whether any are dropped
today is unmeasured.

## Challenge

A red-team pass against the repository and the slice-3 worktree returned **unsound as first
written**, sound with changes. Every point below is folded into the proposals that follow.

- **Blocker.** A no-argument `/cobot:consult` that audits every detected domain cannot fork per
  domain: a forked skill forks once, the consultant has no Agent tool, and delegation depth is
  one. It would audit every domain in one context under one ten-finding cap.
- **Consult knowledge would drop out of staleness tracking**: `cobot-memory knowledge` matches the
  `consult-` folder prefix, so a folder named `consult` silently leaves the weekly refresh.
- **Hiding `ship` and `contribute` lowers safety instead of raising it.** It takes no tool away;
  the model would prepare a workflow or an upstream PR without the rules those skills enforce
  (SHA pins, the AI policy, the forbidden PR text of decision 18).
- **Two evals invoke `onboard` and `ship` mid-prompt**, which only works through the Skill tool
  that `disable-model-invocation` blocks.
- **A per-PR version-bump gate fails in ordinary use**: sibling PRs both bump to the same version,
  the weekly refresh PR touches skills only, eval edits would force bumps, and every bump means a
  changelog cut and a tag the owner pushes.
- **A 300-char cap per description fails all 30 skills** and undoes slice 3's trims; expert
  triggers such as "designing a CI pipeline" fire before any file exists, so `paths:` does not
  replace them.
- **Hiding `lang-*` would starve the risk tasks** the protocol keeps in the main thread.
- **Simpler than all of it: measure first.**

## Proposals, ranked by what the user gains

| # | Proposal | User gains | Source | Cost |
|---|---|---|---|---|
| 0 | **Measure first.** Remove `mattpocock-skills`, open a session in a repository with cobot, read the Skills row in `/context` and note which descriptions are dropped. Proposals 3 and 8 proceed only if some are. | Decisions on evidence; one plugin's eleven listing entries gone | red team | Two owner commands, below |
| 1 | **One `/cobot:consult <domain>` in slice 4**, as decision 28 planned. The domain is required and must be in a fixed list; with no argument the skill only lists the domains detected from the `ship` and `paths:` signals, and the orchestrator calls it once per domain, so each audit keeps its own fork and its ten-finding cap. The dated facts now in `consult-*` move to the matching `expert-*/references`, so consult references hold procedure only and staleness tracking keeps working. Spike first: two Skill calls to the same skill in one message run in parallel (spec and wrap rely on parallel consults). | 16 → 10 commands, and the menu stops growing with each domain | Pocock (small surface), Google (flat references, one hop), decision 28 | Medium: its own spec. Touches decisions 27 and 28 (owner amends), design §4, README, `ship`, `expert-ui`, `expert-containers`, the `cobot-deps` hint and its test, four graders, the `../` paths, and an argument grammar for `consult ui site/` |
| 2 | **User-only for `onboard`, `rules`, `security-sweep`** (`disable-model-invocation: true`). `ship` and `contribute` stay model-invocable because they carry rules the model must follow whenever that work comes up. The two eval prompts start with the slash command; the protocol's "Dry-run with `/cobot:rules check`" becomes the `cobot-rules check` binary the model can run. | About 1 500 listing chars; three commands the model never fires on its own | Pocock `.agents/invocation.md` | Small, plus one check: the eval sandbox must let `fixture.sh` hold what the prompt carried |
| 3 | **Only if proposal 0 shows drops:** cap `expert-*` and `lang-*` descriptions at about 350 chars, keep their task triggers, shrink the `learn` skeleton template to fit, and re-run `actions-pinning`. | The descriptions most at risk survive the budget | Google L1 | Small |
| 4 | **Cut a release after each merged slice.** `release.yml` already refuses a tag unless `plugin.json`, `marketplace.json` and the changelog heading agree; what is missing is the habit: 0.1.0 has carried R1.1 and R2 slices 1–2 unchanged, so `claude plugin update` has never had anything to pick up. `--refresh` stays for dogfooding inside a branch. No per-PR gate (see Challenge). | Updates the documented way, one version per slice | Google ("every behavioral change requires an explicit version bump"), narrowed to releases | Small: a version bump, a changelog cut and a tag the owner pushes |
| 5 | **README front door in three steps**: install, `/cobot:onboard`, ask. Commands grouped "you type" and "cobot uses". `check-plugin` asserts every skill name appears in the README; no generator. Fix the broken skills row on the way. | One screen to start | Pocock README grouping; Google's drift lesson, scaled down | Small |
| 6 | **Graders: regex where possible, at most one judge per case**, each regex checking one thing. Applied to F-13. | A red eval says what to fix, without extra judge noise under `--threshold 1.0` | Google lesson 2; our F-12 | Small |
| 7 | **Spike before hiding `lang-*`**, only if proposal 0 shows drops. Pass criteria: a builder's `skills:` preload still loads a `disable-model-invocation` skill, and a main-thread risk task (Terraform state, `unsafe`) still gets its language skill. | Possibly 3 500 more chars | Claude Code docs (silent here) | One spike |

A weekly link check (Google's lychee job) is not proposed: the staleness check of decision 23
already re-fetches sources, and adding outbound fetches to the job that holds the API key and PR
write permission widens it.

## Ideas left out

| Idea | Why not |
|---|---|
| Per-skill semver and `index.json` (Google) | One owner, one plugin: the plugin version (proposal 4) is enough |
| AI review agent and full evals on every push (Google) | API cost in the owner-only phase; the challenger and `/code-review` run locally, deterministic gates already run first |
| "MCP tools first, CLI as fallback" (Google) | Our `bin/` scripts cost no context and pass one gate; MCP stays for external products such as Stitch |
| Router skill like `ask-matt` | With ten commands (after proposal 1) and a three-step README it adds a command to explain commands; reconsider if the menu passes ten again |
| `grill-me` / `grill-with-docs`, `GLOSSARY.md` | `spec` already asks at most five questions with options and a recommendation; a glossary section in CONTEXT.md is a possible later addition, not a skill |
| `to-spec`, `to-tickets`, `wayfinder`, `triage` | Issue-tracker flows; one planning path (decision 2), the owner prefers specs |
| `handoff`, `wait-what`, `retro`, `teach` | Compaction, the brief and the journal cover the first; the rest are personal habits, not process |
| `tdd`, `code-review`, `pr`, `research` | Covered by `build`, built-in `/code-review`, `contribute` and `learn` |
| `wizard` (bash wizard for human-only steps) | `github-settings.sh` already prints the owner's commands; worth a look on public day, when secrets and rulesets need setting |

## Removing `mattpocock-skills` from this machine

It is installed at user scope from `claude-plugins-official` and enabled in
`~/.claude/settings.json`. Eleven of its skills are model-invoked, so their descriptions sit in
every session's listing beside cobot's, and its `code-review` shares a name with the built-in.
Nothing in cobot depends on it (one historical mention in `docs/00-discovery.md`). It is the only
plugin installed from that marketplace; the marketplace itself can stay.

The cobot rules forbid editing `~/.claude/settings*.json`, so the steps are the owner's:

```bash
claude plugin uninstall mattpocock-skills@claude-plugins-official --scope user
```

```bash
claude plugin list
```

If `~/.claude/plugins/cache/claude-plugins-official/mattpocock-skills` is still there afterwards,
it can be removed by hand. Then read `/context` in a cobot session (proposal 0). The legacy unprefixed skills (`/onboard`, `/design`, `/build`, `/wrap`,
`/ship`, `/security-sweep`) are the larger overlap; they leave with the switch
(`docs/03-switch-plan.md`), not before (decision 15).
