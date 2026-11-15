#!/bin/sh
# cobot installer. POSIX sh. Writes nothing outside the chosen scope.
#   --dev                 print the session-only alias (claude --plugin-dir); writes nothing
#   --project [DIR]       register the marketplace and install at project scope in DIR (default: .)
#   --refresh [DIR]       uninstall and reinstall at the installed scope (project or local): the cache only refreshes on a version change
#   --local [DIR]         same, at local scope (foreign repositories: never committed)
#   --user                install at user scope (reserved for the switch, docs/03-switch-plan.md)
#   --check               report Claude Code, marketplace, installed scopes, the legacy scaffold and agy
#   --uninstall [SCOPE]   uninstall from SCOPE (project | local | user; default project)
#   --source github|path  where the marketplace comes from (default: path = this checkout)
#   --agy                 also (or alone: only) validate and install this checkout into Antigravity (agy), user scope; it refreshes too
set -eu

REPO_DIR=$(cd "$(dirname "$0")" && pwd)
PLUGIN_DIR="$REPO_DIR/plugins/cobot"
MARKETPLACE=cobot
PLUGIN=cobot
GITHUB_SOURCE=YpNo/cobot
HOME_DIR=${HOME:-/root}
CLAUDE_DIR=${CLAUDE_CONFIG_DIR:-$HOME_DIR/.claude}
LEGACY_DIR=$HOME_DIR/.agents
# the name before 2026-11-07 (ADR-0004): state and registrations are migrated once, never deleted
OLD_MARKETPLACE=agentic-partner
# its name line in `claude plugin marketplace list`; a bare match would also hit the cobot
# marketplace's Source line, whose folder is still named agentic-partner
OLD_MARKETPLACE_LINE="[[:space:]]${OLD_MARKETPLACE}[[:space:]]*\$"
OLD_PLUGIN=partner
DATA_BASE=${XDG_DATA_HOME:-$HOME_DIR/.local/share}
OLD_DATA=$DATA_BASE/$OLD_MARKETPLACE
NEW_DATA=$DATA_BASE/$MARKETPLACE
OLD_CONF=$CLAUDE_DIR/$OLD_PLUGIN
NEW_CONF=$CLAUDE_DIR/$PLUGIN
source_kind=path

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; }

need_claude() {
  command -v claude >/dev/null 2>&1 || { echo "install: claude not found on PATH" >&2; exit 1; }
}

marketplace_source() {
  if [ "$source_kind" = github ]; then echo "$GITHUB_SOURCE"; else echo "$REPO_DIR"; fi
}

marketplace_known() { claude plugin marketplace list 2>/dev/null | grep -q "$MARKETPLACE"; }

ensure_marketplace() {
  if marketplace_known; then
    echo "marketplace $MARKETPLACE already registered"
  else
    echo "registering marketplace from $(marketplace_source)"
    claude plugin marketplace add "$(marketplace_source)"
  fi
}

present() { [ -e "$1" ] || [ -L "$1" ]; }

migrate_dir() { # MODE OLD NEW: rename OLD to NEW when NEW is absent in any form; MODE check only reports
  present "$2" || return 0
  if present "$3"; then echo "migrate: $2 and $3 both exist; nothing moved, merge by hand"; return 0; fi
  if [ "$1" = check ]; then echo "  would move $2 -> $3"; else mv "$2" "$3" && echo "migrate: moved $2 -> $3"; fi
}

relink_agent() { # MODE DIR: a .agent symlink the plugin created into the old data directory follows it
  link=$2/.agent
  [ -L "$link" ] || return 0
  target=$(readlink "$link")
  case $target in "$OLD_DATA"/*) ;; *) return 0 ;; esac
  new=$NEW_DATA${target#"$OLD_DATA"}
  if [ "$1" = check ]; then echo "  would re-point $link -> $new"; else rm "$link" && ln -s "$new" "$link" && echo "migrate: re-pointed $link -> $new"; fi
}

report_old_rules() { # DIR: the owner's rule files are reported, never moved
  for f in "$CLAUDE_DIR/$OLD_PLUGIN.rules" "$1/.agent/$OLD_PLUGIN.rules"; do
    present "$f" && echo "migrate: $f is yours: rename it to $PLUGIN.rules by hand (the gate reads $PLUGIN.rules)"
  done
  return 0
}

migrate_state() { # MODE DIR
  migrate_dir "$1" "$OLD_DATA" "$NEW_DATA"
  migrate_dir "$1" "$OLD_CONF" "$NEW_CONF"
  relink_agent "$1" "$2"
  report_old_rules "$2"
}

uninstall_old() { # SCOPE DIR: the old plugin id at this scope, when installed
  if (cd "$2" && claude plugin uninstall "$OLD_PLUGIN@$OLD_MARKETPLACE" --scope "$1" 2>/dev/null); then
    echo "migrate: uninstalled $OLD_PLUGIN@$OLD_MARKETPLACE at scope $1 in $2"
  fi
  return 0
}

old_marketplace_path() { # the folder the old marketplace was registered from, when it was a folder
  claude plugin marketplace list 2>/dev/null | sed -n "/$OLD_MARKETPLACE_LINE/{n;s/.*Folder (\(.*\)).*/\1/p;}"
}

retire_old_marketplace() { # before the new marketplace registers: a folder carries one marketplace name only
  claude plugin marketplace list 2>/dev/null | grep -q "$OLD_MARKETPLACE_LINE" || return 0
  remaining=$(claude plugin list 2>/dev/null | grep -c "$OLD_PLUGIN@$OLD_MARKETPLACE" || true)
  if [ "$remaining" -gt 0 ]; then
    if [ "$(old_marketplace_path)" != "$REPO_DIR" ]; then
      echo "migrate: marketplace $OLD_MARKETPLACE kept: $remaining install(s) of $OLD_PLUGIN@$OLD_MARKETPLACE remain; refresh them first"
      claude plugin list 2>/dev/null | grep -A3 "$OLD_PLUGIN@$OLD_MARKETPLACE"
      return 0
    fi
    echo "migrate: $remaining install(s) of $OLD_PLUGIN@$OLD_MARKETPLACE remain but share this folder with $MARKETPLACE; refresh them next:"
    claude plugin list 2>/dev/null | grep -A3 "$OLD_PLUGIN@$OLD_MARKETPLACE"
  fi
  claude plugin marketplace remove "$OLD_MARKETPLACE" && echo "migrate: removed marketplace $OLD_MARKETPLACE"
  present "$CLAUDE_DIR/plugins/cache/$OLD_MARKETPLACE" && echo "migrate: $CLAUDE_DIR/plugins/cache/$OLD_MARKETPLACE remains; remove it by hand"
  if [ -f "$CLAUDE_DIR/settings.json" ] && grep -q "\"$OLD_MARKETPLACE\"" "$CLAUDE_DIR/settings.json"; then
    echo "migrate: $CLAUDE_DIR/settings.json still has extraKnownMarketplaces.$OLD_MARKETPLACE: delete that key by hand"
  fi
  return 0
}

# agy merges hook groups by name across sources, so a repository's .agents/hooks.json naming the
# plugin's group with "enabled": false switches it off (smoke h2): each install gets a group name
# no committed file can know. The staged copy is validated, installed, then removed.
AGY_GROUP_LINE='  "cobot": {'

stage_agy() { # DIR: copy the plugin into DIR/cobot with a random hook group name
  # called as `stage_agy … || exit 1`, where set -e does not apply: every step fails on its own
  name="cobot-$(od -An -N8 -tx1 /dev/urandom | tr -d ' \n')"
  [ ${#name} -eq 22 ] || { echo "install: no random hook group name" >&2; return 1; }
  cp -R "$PLUGIN_DIR" "$1/cobot" || { echo "install: cannot stage the plugin" >&2; return 1; }
  # caches of a local test run stay out of the install
  find "$1/cobot" -name __pycache__ -type d -prune -exec rm -rf {} + || return 1
  sed "s/^$AGY_GROUP_LINE\$/  \"$name\": {/" "$PLUGIN_DIR/hooks.json" >"$1/cobot/hooks.json" || return 1
  grep -q "^  \"$name\": {\$" "$1/cobot/hooks.json" || {
    echo "install: hooks.json has no '$AGY_GROUP_LINE' line to rename; nothing installed" >&2
    return 1
  }
  echo "agy: hook group named $name for this install"
}

cmd_agy() { # validate, then install: agy replaces an installed copy in place and restores it on failure
  command -v agy >/dev/null 2>&1 || { echo "install: agy not found on PATH" >&2; exit 1; }
  stage=$(mktemp -d) || { echo "install: no temporary folder" >&2; exit 1; }
  trap 'rm -rf "$stage"' EXIT
  stage_agy "$stage" || exit 1
  echo "agy: validating $stage/cobot (staged from $PLUGIN_DIR; run this with no agy session open)"
  agy plugin validate "$stage/cobot" || { echo "install: agy plugin validate failed; nothing installed" >&2; exit 1; }
  echo "agy: installing $stage/cobot at user scope"
  rc=0; agy plugin install "$stage/cobot" || rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "install: agy plugin install failed (exit $rc); agy keeps the previous copy, if one was installed" >&2
    exit 1
  fi
}

report_agy() {
  echo "== Antigravity (agy)"
  if ! command -v agy >/dev/null 2>&1; then echo "  agy: not found"; return 0; fi
  echo "  agy $(agy --version 2>/dev/null || echo 'version unknown')"
  agy plugin list 2>/dev/null | grep "$PLUGIN" || echo "  $PLUGIN: not installed"
}

cmd_dev() {
  echo "alias claude-cobot='claude --plugin-dir \"$PLUGIN_DIR\"'"
  echo "# session only: nothing is written. Verify with:"
  echo "#   claude-cobot -p 'name the agent types whose name starts with cobot:'"
}

cmd_install() {
  scope=$1; dir=${2:-.}
  need_claude
  migrate_state run "$dir"
  uninstall_old "$scope" "$dir"
  retire_old_marketplace
  ensure_marketplace
  echo "installing $PLUGIN@$MARKETPLACE at scope $scope in $dir"
  (cd "$dir" && claude plugin install "$PLUGIN@$MARKETPLACE" --scope "$scope")
}

cmd_refresh() {
  dir=${1:-.}; refreshed=0
  need_claude
  for scope in project local; do
    if (cd "$dir" && claude plugin uninstall "$PLUGIN@$MARKETPLACE" --scope "$scope" 2>/dev/null); then
      cmd_install "$scope" "$dir"; refreshed=1
    elif (cd "$dir" && claude plugin uninstall "$OLD_PLUGIN@$OLD_MARKETPLACE" --scope "$scope" 2>/dev/null); then
      echo "migrate: uninstalled $OLD_PLUGIN@$OLD_MARKETPLACE at scope $scope in $dir"
      cmd_install "$scope" "$dir"; refreshed=1
    fi
  done
  if [ "$refreshed" -eq 0 ]; then
    echo "refresh: nothing to uninstall at project or local scope in $dir"
    cmd_install project "$dir"
  fi
}

cmd_uninstall() {
  scope=${1:-project}
  need_claude
  claude plugin uninstall "$PLUGIN@$MARKETPLACE" --scope "$scope"
}

count_links_into_legacy() {
  dir=$1; n=0
  [ -d "$dir" ] || { echo 0; return; }
  for entry in "$dir"/* "$dir"/.[!.]*; do
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    if [ -L "$entry" ]; then
      case $(readlink "$entry") in "$LEGACY_DIR"/*) n=$((n + 1)) ;; esac
    fi
  done
  echo "$n"
}

report_overlaps() {
  # the agents Claude Code loads: check-plugin holds the manifest's list equal to this folder
  for file in "$PLUGIN_DIR"/claude-agents/*.md; do
    [ -e "$file" ] || continue
    name=$(basename "$file" .md)
    if [ -e "$CLAUDE_DIR/agents/$name.md" ] || [ -L "$CLAUDE_DIR/agents/$name.md" ]; then
      echo "  agent '$name': also present in $CLAUDE_DIR/agents (plugin one is 'cobot:$name'; no conflict)"
    fi
  done
  for dir in "$PLUGIN_DIR"/skills/*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    if [ -e "$CLAUDE_DIR/skills/$name" ] || [ -L "$CLAUDE_DIR/skills/$name" ]; then
      echo "  skill '$name': also present in $CLAUDE_DIR/skills (plugin one is '/cobot:$name'; no conflict)"
    fi
  done
}

cmd_check() {
  echo "== Claude Code"
  if command -v claude >/dev/null 2>&1; then claude --version; else echo "  claude: not found"; fi
  echo "== Marketplace $MARKETPLACE"
  if command -v claude >/dev/null 2>&1 && marketplace_known; then echo "  registered"; else echo "  not registered"; fi
  echo "== Plugin $PLUGIN"
  if command -v claude >/dev/null 2>&1; then
    claude plugin list 2>/dev/null | grep -A3 "$PLUGIN@$MARKETPLACE" || echo "  not installed in any scope"
  fi
  echo "== Legacy scaffold"
  echo "  $LEGACY_DIR: $([ -d "$LEGACY_DIR" ] && echo present || echo absent)"
  echo "  links into it from $CLAUDE_DIR/agents: $(count_links_into_legacy "$CLAUDE_DIR/agents")"
  echo "  links into it from $CLAUDE_DIR/skills: $(count_links_into_legacy "$CLAUDE_DIR/skills")"
  if [ -L "$CLAUDE_DIR/CLAUDE.md" ]; then
    echo "  $CLAUDE_DIR/CLAUDE.md -> $(readlink "$CLAUDE_DIR/CLAUDE.md")"
  else
    echo "  $CLAUDE_DIR/CLAUDE.md: $([ -e "$CLAUDE_DIR/CLAUDE.md" ] && echo 'plain file' || echo absent)"
  fi
  echo "== Name overlaps"
  overlaps=$(report_overlaps)
  if [ -n "$overlaps" ]; then echo "$overlaps"; else echo "  none"; fi
  echo "== Migration from $OLD_MARKETPLACE"
  pending=$(migrate_state check .)
  if [ -n "$pending" ]; then echo "$pending"; else echo "  nothing to migrate"; fi
  report_agy
}

[ $# -ge 1 ] || { usage; exit 2; }
action=""; arg=""; agy=0
while [ $# -gt 0 ]; do
  case $1 in
    --agy) agy=1 ;;
    --dev|--check|--user) action=$1 ;;
    --project|--local|--refresh|--uninstall) action=$1; if [ $# -gt 1 ] && [ "${2#--}" = "$2" ]; then arg=$2; shift; fi ;;
    --source) [ $# -gt 1 ] || { usage; exit 2; }; source_kind=$2; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "install: unknown option $1" >&2; usage; exit 2 ;;
  esac
  shift
done
case $source_kind in github|path) ;; *) echo "install: --source must be github or path" >&2; exit 2 ;; esac
# --agy is a modifier: alone it installs into agy only; it never uninstalls (agy replaces in place)
if [ "$agy" -eq 1 ]; then
  case $action in
    --dev|--uninstall) echo "install: --agy installs or refreshes only; it does not combine with $action" >&2; exit 2 ;;
    "") cmd_agy; exit 0 ;;
  esac
fi
case $action in
  --dev) cmd_dev ;;
  --project) cmd_install project "$arg" ;;
  --local) cmd_install local "$arg" ;;
  --refresh) cmd_refresh "$arg" ;;
  --user) cmd_install user "$REPO_DIR" ;;
  --check) cmd_check ;;
  --uninstall) cmd_uninstall "$arg" ;;
  *) usage; exit 2 ;;
esac
if [ "$agy" -eq 1 ] && [ "$action" != --check ]; then cmd_agy; fi
