# Configuration

For agents and architects. Everything cobot reads, where it lives, and what changes when you set
it. Nothing here touches `~/.claude/CLAUDE.md`, `~/.claude/agents`, `~/.claude/skills` or
`~/.claude/settings.json` (ADR-0003).

## Install

| Command | Effect |
|---|---|
| `./install.sh --project [DIR]` | registers the marketplace (this checkout by default, or GitHub with `--source github`) and installs the plugin at project scope in `DIR` |
| `./install.sh --local [DIR]` | the same at local scope, for a repository you do not own: never committed |
| `./install.sh --refresh [DIR]` | uninstalls and reinstalls at the scope found there: the plugin cache only refreshes on a version change, so after editing a checkout this is how a dogfood repository picks it up |
| `./install.sh --dev` | prints a session-only alias using `claude --plugin-dir`; writes nothing |
| `./install.sh --check` | reports Claude Code, the marketplace, installed scopes, the legacy scaffold and name overlaps |
| `./install.sh --uninstall [SCOPE]` | reverses an install (`project`, `local` or `user`) |
| `./install.sh --user` | user scope, reserved for the switch ([03-switch-plan.md](03-switch-plan.md)) |

## Files and environment

| Setting | Type | Default | Effect |
|---|---|---|---|
| `~/.claude/cobot.rules` | rule file | absent | owner layer: `allow` lines silence a default `ask`; `never` and `ask` tighten |
| `.agent/cobot.rules` | rule file | absent | project layer: `never` and `ask` only |
| `~/.claude/cobot/identities` | `host/owner` per line | absent | repositories whose every remote belongs to one of these owners are trusted |
| `~/.claude/cobot/trusted` | `<root commit> <name>` per line | absent | repositories trusted by root commit (no remote, or a fork with foreign remotes) |
| `CLAUDE_CONFIG_DIR` | path | `~/.claude` | where the owner files above live |
| `XDG_DATA_HOME` | path | `~/.local/share` | foreign-mode memory under `cobot/repos/<host>/<owner>/<repo>` |
| `COBOT_RULES_OWNER`, `COBOT_RULES_PROJECT_DIR` | paths | unset | override the owner file and the project directory (tests, spikes) |
| `COBOT_GATE_LOG` | path | unset | append one JSON line per judged call: tool, decision, first 120 chars |

## Rules

One rule per line: `decision Tool(pattern) [@agent]`, or `decision mcp__<server>__<tool>` for an
MCP tool. Examples: `ask Bash(git push*)`, `never Edit(~/.claude/settings*.json)`,
`allow Bash(cargo test*)`, `allow mcp__claude-in-chrome__*`, `ask mcp__supabase__get_publishable_keys`.

Precedence: `never` in any layer wins; an `allow` from the owner layer (or an agent-scoped one
from the default layer) silences the gate; `ask` prompts; otherwise Claude Code's own
permissions decide. For MCP tools, an owner or project `ask` also outranks a read and the host's
UI tools, which are otherwise silent. The gate never emits `allow`.

`/cobot:rules check "<command>"` dry-runs the gate, `explain` names every matching rule, and
`sync` renders the hard wall (a `permissions.deny` block and the owner's `allow` lines, in plain
and `rtk` forms) for you to apply to `settings.json` yourself.

## MCP servers you register

cobot ships no MCP server and no credentials; you register a server at user scope and the gate
judges its tools.

- **Google Stitch** for `expert-ui` (decision 27):
  `claude mcp add stitch --transport http https://stitch.googleapis.com/mcp --header "X-Goog-Api-Key: …" -s user`.
  Generate and edit tools ask, list and get tools are silent.
- **Google Cloud remote MCP servers** (`https://<service>.googleapis.com/mcp`) for
  `expert-gcp`: register each one as `gcp-<service>` with a Desktop OAuth client, from inside
  the repository:
  `claude mcp add --transport http --client-id … --client-secret --callback-port 8765 -H "x-goog-user-project: <project>" -s local gcp-logging https://logging.googleapis.com/mcp`,
  then sign in with `/mcp` from the CLI. Under a `gcp-*` name, read tools are silent and
  write tools are refused (`never`); under any other name, write tools ask. The full setup,
  including the IAM deny policy for projects in an organisation and the SSH tunnel for a remote
  host, is in `plugins/cobot/skills/expert-gcp/references/mcp.md`.

## Cloud read lists

For the read-only agents (consultant, learner), `gcloud … list|describe`,
`kubectl get|describe|logs|diff`, `helm template|lint`, `kustomize build`, `kubeconform` and
`istioctl analyze|proxy-status` are silent like `gh api repos/*`. A command that could run
repository content (an environment assignment, `git -c`, `--kubeconfig`, `--post-renderer`,
`--enable-exec`) asks instead, and `kubectl get secret` is denied for them (decision 28,
ADR-0006).
