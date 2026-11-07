# Switch plan — from the legacy scaffold to the cobot plugin

Runs only when the owner says so, after R1.1 dogfood. Nothing here is executed by the cobot on
its own; every step is `ask` or manual. Estimated time: 20 minutes plus the workstation-starter PR.

## Preconditions

- Eight evals green on `main`; a week of journaled use on two repositories.
- `install.sh --check` reports no open conflict other than the known legacy listing.
- No session with uncommitted work on this machine (the switch changes what every new session
  loads).

## Steps

1. **Backup**: `~/.claude/{CLAUDE.md,agents,skills,settings.json}` and `~/.agents` to
   `~/.claude/backup-<date>/` (links copied as links, targets as files).
2. **Install at user scope**: `install.sh --user` (marketplace add `YpNo/cobot`, plugin
   install `--scope user`); `install.sh --project` entries in dogfood repos may stay or be removed.
3. **Unlink legacy**: remove the `~/.claude/agents/*` and `~/.claude/skills/*` symlinks that point
   into `~/.agents`; leave anything that does not.
4. **CLAUDE.md**: replace `~/.claude/CLAUDE.md` with the RTK section only (the symlink to
   `~/.agents/AGENTS.md` is replaced by a file; the repo copy in workstation-starter is updated in
   step 7). Owner preferences that are not cobot protocol (test naming, commit format) move to
   `~/.claude/cobot.rules` or the lang skills, whichever already holds them.
5. **Rules**: `/cobot:rules sync`, review the diff, apply the `permissions.deny` block and the
   owner `allow` lines to `~/.claude/settings.json`; remove the legacy unconditional `git push`
   allow.
6. **Memory**: nothing to migrate; new files are additive. `cobot-memory check` on each active
   repo confirms it reads CONTEXT and JOURNAL.
7. **workstation-starter**: pull request that drops `ai/` and installs the marketplace in the
   bootstrap script; ADR there references ADR-0003 here.
8. **Verify**: a fresh `claude` session in a Rust repo lists only `cobot:*` agents, the
   SessionStart brief appears once, `/cobot:rules check "git push"` answers `ask`, and the old
   `/design` is gone.

## Rollback

Restore the backup directory over `~/.claude`, `claude plugin uninstall cobot@cobot
--scope user`, reopen the session. Under five minutes; no repository content is touched by the
switch.
