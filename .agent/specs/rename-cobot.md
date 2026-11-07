# Spec — rename the project to cobot

size: medium · profile: library · owner: YpNo · date: 2026-11-07

## Goal

The project is called **cobot**: the collaborative robot that works on the engineer's bench under
force limits, here a technical AI assistant for architects, developers and operators bounded by a
rules gate. One word serves the repository, the marketplace, the plugin, the slash prefix, the
binaries and the tag in every refusal. The role vocabulary of the protocol becomes "the cobot"
(the assistant) and "the owner" (the human). Nothing else changes: no behaviour, no rule, no
version of any knowledge line. The rename runs once, before the first user-scope install and
before the switch plan, which is the cheapest moment it will ever have.

## Principles check

- Proportionality: one mechanical pass over the tree plus a migration of the state this machine
  already holds; no new code path beyond the one-time moves in `install.sh`.
- Rules before autonomy: the GitHub repository rename, the remote URL change, the push and the
  PR are the owner's commands; the tree edits, the local state moves and the dogfood refreshes
  are the task.
- Proof: the suite, the lints, the plugin contract, strict validation, both dogfood installs
  refreshed and three gate dry runs, plus a grep that shows no stray old name.
- Delivery: branch `chore/rename-cobot` from `main` once PR 1 and PR 2 are merged; tasks below
  are the commits; one PR.

## Mapping

| today | after | where |
|---|---|---|
| `YpNo/agentic-partner` | `YpNo/cobot` | GitHub (redirect kept), `plugin.json`, README, `install.sh` `GITHUB_SOURCE` |
| marketplace `agentic-partner` | `cobot` | `.claude-plugin/marketplace.json`, `install.sh`, dogfood `enabledPlugins` |
| plugin `partner`, dir `plugins/partner` | `cobot`, `plugins/cobot` | manifest, workflows, scripts, tests, docs |
| `/partner:<skill>`, `partner:<agent>` | `/cobot:<skill>`, `cobot:<agent>` | skills, agents, rules, evals, docs, `knowledge-refresh.yml` |
| `partner-memory`, `-rules`, `-deps`, `-session` | `cobot-*` | `bin/`, `hooks.json`, rules, skills, tests, docs |
| `_partner_*.py`, `tests/test_partner_*.py` | `_cobot_*.py`, `tests/test_cobot_*.py` | imports follow |
| `PARTNER_RULES_PROJECT_DIR`, `PARTNER_RULES_OWNER`, `PARTNER_GATE_LOG`, `PARTNER_SOURCE` | `COBOT_*` | gate, memory, tests, spikes, docs |
| `partner rule:`, `partner gate:`, `partner session:` | `cobot rule:`, `cobot gate:`, `cobot session:` | gate and hook output, eval graders, mechanics reference |
| `partner@agentic-partner` | `cobot@cobot` | `install.sh`, tests, dogfood `enabledPlugins` |
| `partner_config_dir`, module aliases `partner_memory|partner_rules|partner_session`, `partner_deps_cli` | `cobot_*` | `_partner_common.py`, `conftest.py`, tests |
| `~/.claude/partner.rules`, `.agent/partner.rules` | `~/.claude/cobot.rules`, `.agent/cobot.rules` | rules loader, `rules` skill, docs |
| `~/.claude/partner/{identities,trusted}` | `~/.claude/cobot/` | `cobot_config_dir`, docs, migration |
| `~/.local/share/agentic-partner/` | `~/.local/share/cobot/` | `data_dir`, `deps`, `promote`, migration |
| alias `claude-partner` | `claude-cobot` | `install.sh --dev`, test |
| `partner-gcp`, `-reverse`, `-usage`, `-delivery-extra`, `partner-deny-probe` | `cobot-*` | design, ADR-0001, spikes, docs |
| "the partner", "this partner", "a partner", "the partner's" | "the cobot", … | protocol prose everywhere |

Left as written: `docs/design-inputs/` (inputs quoted from elsewhere), the `[0.1.0]` section of
the changelog (a released record), the journal's past entries and the earlier specs (records of
their day; their file names change only where they are `partner`-named, which none is), and
"partner" where it means the other party to an agreement (checked by hand in the residual grep).

## Tasks

1. **Tree.** `git mv` for the directory, the binaries, the modules and the tests; one scripted
   substitution over tracked text files in the order longest-first (`agentic-partner`,
   `plugins/partner`, `partner@`, `_partner_`, `partner_`, `partner-`, `/partner:`, `partner:`,
   `PARTNER_`, `partner.rules`, `.claude/partner`, `claude-partner`, `partner rule`,
   `partner gate`, `partner session`, the bare name in `plugin.json`, `marketplace.json`,
   `install.sh`, the README title and `protocol.md`, then the prose forms with their article and
   case); the exclusions above; then `git grep -n -i partner` (no `-w`: underscores and case
   hide `PARTNER_*` and `partner_memory` from a word grep) and a hand review of every remaining
   hit, which must be in an excluded file or mean the other party. The checkout directory
   `~/workspace/agentic-partner` keeps its path in this PR: the marketplace record, the
   worktrees, Claude Code's project memory and `source_checkout()` key on it; moving it is a
   separate owner step (re-add the marketplace, prune the worktrees).
   ADR-0004 records the old name and the reason. Changelog under Unreleased, *Changed*,
   marked breaking: plugin id `cobot@cobot`, prefix, binaries, env, state paths, with the
   migration named. Version stays `0.1.0` until the release that ships it.
2. **Migration.** In `--project`, `--local`, `--refresh` and `--user` (`--dev` keeps its
   "writes nothing" contract; `--check` only reports) `install.sh` moves the data directory
   (`$XDG_DATA_HOME` or `~/.local/share`, `agentic-partner` → `cobot`) and the config directory
   (`$CLAUDE_CONFIG_DIR` or `~/.claude`, `partner` → `cobot`) when the old exists (`-e` or `-L`,
   so a symlink counts) and the new does not exist in any form (a rename, reversible, never
   into a symlinked directory). For the repository it acts on, a `.agent` that is a symlink into
   the old data directory is re-pointed to the new one: the plugin created that link in foreign
   mode (`init --foreign`), so re-pointing it is not touching an owner symlink; `--check` lists
   such links. A `~/.claude/partner.rules` or `.agent/partner.rules` is reported, not moved.
   Plugin registrations per repository: uninstall `partner@agentic-partner` at that scope, then
   install `cobot@cobot`; the `agentic-partner` marketplace is removed only when
   `claude plugin list` shows no `@agentic-partner` entry left, otherwise the remaining scopes
   are printed and the removal waits for their refresh. Whether `marketplace remove` deletes
   `~/.claude/plugins/cache/agentic-partner` is verified in the dogfood run and recorded in the
   mechanics reference; the script reports a cache directory that remains and never removes it.
   `~/.claude/settings.json` keeps an `extraKnownMarketplaces.agentic-partner` record that only
   the owner may edit (`never Edit/Write(~/.claude/settings*.json)`): the migration prints the
   exact key to delete and task 4 lists it. `cobot-memory check` warns when an old-named rules
   file sits beside the new one. Tests in `test_install.py` with the fake home, `XDG_DATA_HOME`
   and `CLAUDE_CONFIG_DIR` set, and the fake `claude` listing one or two installs.
3. **Proof.** Full suite and coverage, ruff, shellcheck, markdownlint, `check-plugin`, strict
   validation, zizmor; `install.sh --refresh` on cartridge-os (project) and headscale (local)
   and `install.sh --check`; gate dry runs: `git push` asks, `pnpm run typecheck` silent on
   headplane, `make test` silent on headscale; the SessionStart brief appears once in a fresh
   session with the new prefix; `cobot-memory brief` reads headscale's external memory at its
   new path.
4. **Owner.** `gh repo rename cobot`, `git remote set-url origin git@github.com:YpNo/cobot.git`,
   push, PR; delete the `extraKnownMarketplaces.agentic-partner` key from `~/.claude/settings.json`
   after the last refresh (the migration prints it); commit cartridge-os's rewritten
   `.claude/settings.json` in that repository; repository description "cobot: a governed technical AI assistant for architects,
   developers and operators" and topics; `scripts/github-settings.sh --check` (it reads the
   remote, so nothing else changes). The auto-memory file of the orchestrator's own project
   notes is updated afterwards.

## Risks

- A substitution that reaches a word meaning the other party ("partner" in the upstream
  template or a maintainers' quote): the residual grep with `-w` and a hand review per hit.
- Sentence-initial "Partner" and the README title: the prose pass runs case by case, not
  `-i`.
- The cached plugin under `~/.claude/plugins/cache/agentic-partner` and the record in
  `~/.claude/plugins/known_marketplaces.json`: `claude plugin marketplace remove` clears both;
  the migration verifies the cache directory is gone and says so.
- Dogfood repositories' `.claude/settings.json` keep `partner@agentic-partner: true` until
  `install.sh --refresh` rewrites it; a stale key is harmless but the migration removes it.
- Open `learn/<topic>` branches or worktrees under the old `promote` directory: none exist
  today; the move carries the directory anyway.
- Eval results under `plugins/partner/evals/results/` are ignored by git and move with the
  directory.

## Challenger

SOUND WITH CHANGES (2026-11-07), nine points, all folded: the dangling foreign-mode `.agent`
link after the data move (blocker: the migration re-points links the plugin created); the
marketplace removed while another scope still used it (removal last, only when no install
remains); the `settings.json` marketplace record the rules forbid touching (printed for the
owner); six substitution forms the pattern list missed and a word grep that could not see them
(list extended, residual check is `git grep -i`); `--dev` migrating against its contract (it
does not); the checkout's own path left unstated (it stays); symlink-blind move guards (`-e`
or `-L`, both ends, XDG and `CLAUDE_CONFIG_DIR` honoured); the cache deletion asserted rather
than verified (verified in the dogfood run, reported never removed); the `gate:` and `session:`
tags beside `rule:`. Checked clear: no other-party "partner" in the tree, headings read
correctly, the deps cache and trust file survive the move, coverage follows the path change,
PR 1 and PR 2 add only pattern-covered hits.

## Out of scope

The switch plan, a version bump, any wording change beyond the name, the owner's legacy
`~/.agents` tree.
