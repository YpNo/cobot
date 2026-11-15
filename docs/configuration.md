# Configuration

For agents and architects. Everything cobot reads, where it lives, and what changes when you set
it. Nothing here touches `~/.claude/CLAUDE.md`, `~/.claude/agents`, `~/.claude/skills` or
`~/.claude/settings.json` (ADR-0003), and under Antigravity nothing in `~/.gemini` except through
`agy plugin install` (ADR-0007).

## Install

| Command | Effect |
|---|---|
| `./install.sh --project [DIR]` | registers the marketplace (this checkout by default, or GitHub with `--source github`) and installs the plugin at project scope in `DIR` |
| `./install.sh --local [DIR]` | the same at local scope, for a repository you do not own: never committed |
| `./install.sh --refresh [DIR]` | uninstalls and reinstalls at the scope found there: the plugin cache only refreshes on a version change, so after editing a checkout this is how a dogfood repository picks it up |
| `./install.sh --dev` | prints a session-only alias using `claude --plugin-dir`; writes nothing |
| `./install.sh --check` | reports Claude Code, the marketplace, installed scopes, the legacy scaffold, name overlaps and, when `agy` is on PATH, agy's version and whether cobot is installed there |
| `./install.sh --uninstall [SCOPE]` | reverses an install (`project`, `local` or `user`) |
| `./install.sh --user` | user scope, reserved for the switch ([03-switch-plan.md](03-switch-plan.md)) |
| `./install.sh --agy` | Antigravity: a staged copy of the plugin whose hook group is named `cobot-<16 random hex>` (agy merges groups by name, so a repository could switch off a known one), then `agy plugin validate` and `agy plugin install` of it at user scope; the same command refreshes, with a new name, and never uninstalls first. A modifier: beside `--project`, `--local`, `--user` or `--refresh` it runs that action, then the agy install |

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
| `COBOT_GATE_DEADLINE` | seconds, 1 to 8 | `8` | agy gate shim: the deadline before it answers deny (agy's hook timeout is 10) |
| `~/.gemini/config/mcp_config.json`, `~/.gemini/config/plugins/*/mcp_config.json` or `mcp.json` | read only | absent | agy MCP server names, so an eager `mcp_<server>_<tool>` call splits at a known server |

## Rules

One rule per line: `decision Tool(pattern) [@agent]`, or `decision mcp__<server>__<tool>` for an
MCP tool. Examples: `ask Bash(git push*)`, `never Edit(~/.claude/settings*.json)`,
`allow Bash(cargo test*)`, `allow mcp__claude-in-chrome__*`, `ask mcp__supabase__get_publishable_keys`.
A trailing `# comment` on a default or owner row joins the reason the gate gives, as in
`ask Bash(agy *) # may replace or bypass the cobot gate`; a project-layer comment is dropped and a
project row is shown by its place only (`ask Bash rule at .agent/cobot.rules:4`), and a warning
about one names its line only (`project:4: unreadable rule ignored`), so repository text never
speaks in a permission prompt or on the hook's stderr. `/cobot:rules explain`, `show` and `sync`
print the project rules on your own terminal, by design.

A `never` Edit or Write row for a whole folder (`~/.gemini/config/*`) makes shell access to a
path inside it ask too. With a command substitution in the path, it asks only where the path
names the folder's last part with its `/`: `cp x "$(echo ~)/.gemini/config/hooks.json"` asks,
`cat "$(pwd)/README.md"` does not; a substitution that hides the whole folder is read like a
variable.

The protected-file check reads a path the way the shell and the disk will
(.agent/specs/gate-residuals.md):

- without case for `never` and `ask` rows (a case-insensitive volume opens `.Claude/settings.json`
  as `.claude/settings.json`), and with the program word in lower case too (`GIT push --force`
  is denied); `allow` rows and arguments keep their case;
- `$HOME/` and `${HOME}/` as `~/`;
- in the folder a `cd` or `pushd` in the same command reaches, redirect targets included; after
  a `cd` the gate cannot follow, a word naming a protected file by its last part
  (`settings.json`, `hooks.json`) asks;
- through a symlink a bare glob reaches (`cat al*`), by listing the folder before the glob's
  first hole, at most 4 096 entries and 0.25 s per command;
- deleting a protected folder's parent below HOME (`rm -r ~/.gemini`, behind any wrapper or
  through a glob) asks, like moving it; a `cd` target, a move, a link or a deletion written as a
  glob is judged by the names the glob expands to;
- `~+` as the folder the command runs in; `~-` and `~1` (OLDPWD, the directory stack) ask;
- a deletion that takes a protected folder with it asks: `find` with `-delete`, `-exec`,
  `-execdir`, `-ok` or `-okdir` (its start paths), `gio trash|remove`, and deleting HOME or `/`;
- a folder an option names as the place a command writes (`tar -C`, `unzip -d`, `patch -d`,
  `git -C`, `--work-tree`, `--git-dir`) is checked the same way, and the command's relative words
  resolve in it (.agent/specs/gate-f33-f34.md);
- a command whose working folder is inside a `never` folder row asks once, naming the folder.

Known asks this costs: a protected file's name after any `cd` (`cd docs && tee settings.json`);
`git -C ~ …`, `git -C .. …` from a project directly in HOME, and `tar -C ~ …` (HOME holds
`~/.gemini`); `find ~ -exec … {} +` of any command; a `find -exec` body meets the rows its
command meets (`find … -exec rm -rf {} +` asks like `rm -rf`);
a glob over a folder of more than 4 096 entries; every command run inside a protected folder.
Not covered: a link reached after a second hole segment (`*/d*/key.txt`), a variable other than
HOME naming a protected path, a `CDPATH` set only in your shell profile, a link created between
the check and the run, archive members not written on the command line, folder options of
other tools (`7z -o`, `cpio -D`), extracting after a `cd` into a protected folder, and
`busybox find` or `fd -x`.

Anchor a Bash pattern on the command word (`cobot-memory learn *--promote*`, not
`*cobot-memory learn*`): text a command substitution produces can be anything, so a pattern
that starts with `*` could match any command holding one, and every such command then asks.

Braces and globs (.agent/specs/gate-expansion.md): the gate expands braces as bash does, so a rule
matches the words bash runs (`cargo {publish,}` is `cargo publish`); more than 256 built words
ask. A glob (`*`, `?`, `[…]`) is a hole for file names: in the command word or a CLI's verb it
asks, elsewhere it asks only when a `never` or `ask` row could match. Under an agent scope a glob
counts for the read list only when anchored by literal text (`./*.py`, `src/*`,
`--include=*.py`); a bare `*.py` could expand to an option and asks. Known asks this costs: any
glob after an interpreter (`python3 -m pytest tests/*`, `node --test test/*.js`), and for
`python`/`python3` also the anchored promote rows; `terragrunt` with any glob; a glob read by a
shell or a runner resolved by name (`bash scripts/*.sh`, `npm test -- src/*`, `make test
FILES=src/*`), by `npm exec`, `toolbox`, `distrobox` or `nix-shell --run`, or by a runner's own
options (`uv run --with * …`); `ls ~/.claude/*` (the protected files); `kubectl get pods x*`
under an agent scope; a glob after a builtin that evaluates names or arithmetic (`let`,
`unset`, `read`, `declare`, `export`, `local`, `mapfile`, `printf -v`, `test -v`: a file named
`a[$(…)]` would run), and `cat **` anywhere (`globstar` may be on); `[[ $x == @(a|b) ]]` and
`if !(grep -q x f)` (extended-glob syntax); a word mixing braces and brackets; `echo {1..300}`.

Options before the verb (.agent/specs/gate-findings.md): `never` and `ask` rows also match
each place the verb could start past the options before it, so `npm --registry x publish` and
`cargo +nightly -vv publish` match `never Bash(npm publish*)` and `never Bash(cargo publish*)`;
an `allow` matches only the canonical form. The gate knows the value options of `git`, `cargo`,
`npm`, `pnpm`, `uv`, `kubectl`, `helm` and a few more; after an option it does not know, the
next word is read both as the verb and as that option's value. Known cost: an unknown option
whose value is a ruled verb reads as that verb (`npm --zz publish test` is denied, and an owner
`allow` cannot lift a `never`). A runner behind such an option (`uv -q run …`, `pnpm -r build`,
`npm --prefix web test`) asks, a prompt on common monorepo commands that the form without the
option avoids. `npm` verbs are read as npm reads them (an alias or a unique prefix: `npm publ`
is `npm publish`), `pnpm recursive <verb>` as `pnpm <verb>`, and `git -c alias.…` asks (the
verb is an alias the line defines).

`${…}` and `$"…"`: a `${…}` with an operator word (`${x:-word}`, `${x#pat}`, `${x@Q}`) is a
hole of unknown text, like a substitution; `${x}`, `$x` and `${#x}` stay text, a variable's
value. A locale string `$"…"` is a hole whose known value is its untranslated text, so `cargo
$"publish"` is denied.

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
  then sign in with `/mcp` from the CLI. Under a `gcp-*` name, read tools are silent,
  write tools with a known verb (`create_`, `delete_`, `apply_`, …) are refused (`never`) and any
  other tool asks; under any other name, every tool that is not a read asks. The full setup,
  including the IAM deny policy for projects in an organisation and the SSH tunnel for a remote
  host, is in `plugins/cobot/skills/expert-gcp/references/mcp.md`.

## Cloud read lists

For the read-only agents (consultant, learner), `gcloud … list|describe`,
`kubectl get|describe|logs|diff`, `helm template|lint`, `kustomize build`, `kubeconform` and
`istioctl analyze|proxy-status` are silent like `gh api repos/*`. A command that could run
repository content (an environment assignment, `git -c`, `--kubeconfig`, `--post-renderer`,
`--enable-exec`) asks instead, and `kubectl get secret` is denied for them (decision 28,
ADR-0006).

## What the read lists never cover

For the consultant and the learner, a read-list command loses its read list, and asks, when it
could write a file or run a program (decision 28, `.agent/specs/gate-findings.md`):

- a command word that only starts like a read row: `cat*` covers `cat` and `cat …`, never
  `catatonit`; `git diff*` never `git difftool`;
- an option the gate's guard table names: `find -delete -exec -execdir -ok -okdir -fprint
  -fprint0 -fprintf -fls`, `rg --pre --hostname-bin`, `fd -x -X`, `sort -o --compress-program`, a second
  `uniq` operand, `tree -o -R`, `file -C`, `yq -i -s`, `git log|show|diff --output`, `git branch`
  with a write option or a branch name outside `--list`, `zizmor --fix`, `trivy -o
  --module-dir`, `gitleaks -r --log-opts`, `pip-audit --fix -o`, `cargo-audit audit fix --db`, `cargo-deny check -g`, `npm
  audit fix`, `pnpm audit --fix`, `semgrep --autofix -o --*-output`, `docker build -o --push`,
  `docker compose config -o`, `cosign verify --output-file`, `actionlint -shellcheck -pyflakes`,
  `go list -toolexec -exec -mod -modfile`, `go env -w -u`, `terraform|tofu providers lock|mirror`,
  `kubectl kustomize -o`, `kustomize build -o`, `helm template --output-dir
  --dependency-update`, `kubeconform -cache`. Long options match any abbreviation, short ones
  any cluster (`sort -uo`), which can over-read a letter inside a value and ask;
- `git --config-env`, `cargo --config`, `-Z` or `-C`, `cargo +<toolchain>`, `rustup`, `docker
  --config`, `npm --userconfig --globalconfig --cache --prefix`, `pnpm --env-file
  --npmrc-auth-file --store-dir --state-dir -C --dir`, `uv --config-file --directory --project`
  (configuration or a directory that can change what runs), besides an environment assignment, `git -c` and the kubeconfig and plugin flags;
- a `curl` option outside its read set: `-s -S -L -f -I -i -v -k -g -4 -6 --compressed
  --http1.1 --http2 --fail-with-body`, and with a value `-H` (not `@file`), `-A`, `-e`, `-m`,
  `--connect-timeout`, `--retry*`, `-r`, `-X GET|HEAD`, `--url`, `-w` (not `@file`, no
  `%output{`);
- a redirection into a file anywhere in the command or in a runner body it expands, except
  `/dev/null`, `/dev/stdout`, `/dev/stderr`, `/dev/fd/1`, `/dev/fd/2` and descriptor
  duplications (`2>&1`).

`cargo audit` and `cargo deny check` are not on the read lists: a repository's
`.cargo/config.toml` alias shadows them. Use `cargo-audit audit` and `cargo-deny check`. Read
lists still take a plain variable as text (`find $X`): an agent cannot carry a variable across
Bash calls, and an assignment in the command asks.

### Repository configuration and trust

Some read-list commands run a program the repository's files choose
(`.agent/specs/gate-repo-config.md`). They are silent for the agents only in a **trusted**
repository:

| commands | the files that decide |
|---|---|
| `cargo --version`, `rustc --version`, `cargo tree`, `cargo metadata`, `cargo-audit audit`, `cargo-deny check` | `rust-toolchain`, `rust-toolchain.toml`, `.cargo/config`, `.cargo/config.toml` in the working directory and every parent |
| `npm audit`, `pnpm audit --ignore-pnpmfile` | `.npmrc` (and for pnpm `pnpm-workspace.yaml`, `package.json`) in the working directory and every parent |
| `trivy fs`, `trivy config`, `trivy image` | `trivy.yaml` in the working directory |
| `docker build --check` | the `Dockerfile` (or `dockerfile`) it reads; one context, an existing directory inside the working directory, and only options the gate reads |

Trusted, for the gate: every remote's owner is in `~/.claude/cobot/identities` (a root commit
listed in `~/.claude/cobot/trusted` counts only with no remote and a single root commit); the
repository is not in foreign mode; no such file sits above the repository's top level (your
`$CARGO_HOME` and `~/.npmrc` are left out); and each deciding file present in the tree matches
its blob at origin's default branch (`refs/remotes/origin/HEAD`, else `origin/main` or
`origin/master`; `HEAD` with no remote). A checked-out pull request, or your own branch, that
changes one of these files asks until it is merged. A toolchain or cargo file that names a
program by path (`rustc-wrapper = "scripts/w.sh"`, a toolchain `path`) asks even when it
matches, since the program it names is not compared. Remotes are read from the checkout itself,
so a stranger's submodule inside your repository is not trusted. A runner's expanded command (`make t` whose
recipe runs `cargo tree`) never counts. The main thread is not affected.

Resolving asks in every repository, trusted or not: `pip-audit -r …` or a project path
(resolving builds source-only dependencies) unless both `--no-deps` and `--disable-pip`; `uv
audit` without `--frozen`; `terraform|tofu providers schema`; `docker build --builder`, a
`BUILDKIT_SYNTAX` build argument, or a Dockerfile or context on stdin; `trivy -c|--config`;
`pnpm audit` without `--ignore-pnpmfile` (pnpm runs `.pnpmfile.cjs`, or any file
`pnpm-workspace.yaml` names); `npm|pnpm audit --registry`, `--userconfig`, `--config.*`;
`pip-audit` in a working directory holding `pip`, `pip.py` or another `pip.*` (it runs `python
-m pip`, which imports from there). The gate's own git calls never fetch, prompt or follow
replace refs.
A repository delivered with its own `.git/config` can still run a program on a git read (finding
F-26).
