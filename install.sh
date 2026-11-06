#!/bin/sh
# agentic-partner installer. POSIX sh. Writes nothing outside the chosen scope.
#   --dev                 print the session-only alias (claude --plugin-dir); writes nothing
#   --project [DIR]       register the marketplace and install at project scope in DIR (default: .)
#   --refresh [DIR]       uninstall and reinstall at project scope: the cache only refreshes on a version change
#   --local [DIR]         same, at local scope (foreign repositories: never committed)
#   --user                install at user scope (reserved for the switch, docs/03-switch-plan.md)
#   --check               report Claude Code, marketplace, installed scopes and the legacy scaffold
#   --uninstall [SCOPE]   uninstall from SCOPE (project | local | user; default project)
#   --source github|path  where the marketplace comes from (default: path = this checkout)
set -eu

REPO_DIR=$(cd "$(dirname "$0")" && pwd)
PLUGIN_DIR="$REPO_DIR/plugins/partner"
MARKETPLACE=agentic-partner
PLUGIN=partner
GITHUB_SOURCE=YpNo/agentic-partner
HOME_DIR=${HOME:-/root}
CLAUDE_DIR=${CLAUDE_CONFIG_DIR:-$HOME_DIR/.claude}
LEGACY_DIR=$HOME_DIR/.agents
source_kind=path

usage() { sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; }

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

cmd_dev() {
  echo "alias claude-partner='claude --plugin-dir \"$PLUGIN_DIR\"'"
  echo "# session only: nothing is written. Verify with:"
  echo "#   claude-partner -p 'name the agent types whose name starts with partner:'"
}

cmd_install() {
  scope=$1; dir=${2:-.}
  need_claude
  ensure_marketplace
  echo "installing $PLUGIN@$MARKETPLACE at scope $scope in $dir"
  (cd "$dir" && claude plugin install "$PLUGIN@$MARKETPLACE" --scope "$scope")
}

cmd_refresh() {
  dir=${1:-.}
  need_claude
  (cd "$dir" && claude plugin uninstall "$PLUGIN@$MARKETPLACE" --scope project) \
    || echo "refresh: nothing to uninstall at project scope in $dir"
  cmd_install project "$dir"
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
  for file in "$PLUGIN_DIR"/agents/*.md; do
    [ -e "$file" ] || continue
    name=$(basename "$file" .md)
    if [ -e "$CLAUDE_DIR/agents/$name.md" ] || [ -L "$CLAUDE_DIR/agents/$name.md" ]; then
      echo "  agent '$name': also present in $CLAUDE_DIR/agents (plugin one is 'partner:$name'; no conflict)"
    fi
  done
  for dir in "$PLUGIN_DIR"/skills/*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    if [ -e "$CLAUDE_DIR/skills/$name" ] || [ -L "$CLAUDE_DIR/skills/$name" ]; then
      echo "  skill '$name': also present in $CLAUDE_DIR/skills (plugin one is '/partner:$name'; no conflict)"
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
}

[ $# -ge 1 ] || { usage; exit 2; }
action=""; arg=""
while [ $# -gt 0 ]; do
  case $1 in
    --dev|--check|--user) action=$1 ;;
    --project|--local|--refresh|--uninstall) action=$1; if [ $# -gt 1 ] && [ "${2#--}" = "$2" ]; then arg=$2; shift; fi ;;
    --source) [ $# -gt 1 ] || { usage; exit 2; }; source_kind=$2; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "install: unknown option $1" >&2; usage; exit 2 ;;
  esac
  shift
done
case $source_kind in github|path) ;; *) echo "install: --source must be github or path" >&2; exit 2 ;; esac
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
