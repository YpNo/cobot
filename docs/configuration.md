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
| `~/.claude/cobot/grants/<session>.json` | JSON, written by cobot's gate and hooks only | absent | the session's grants (`kind`, `target`, `granted`, `expires`), pending requests, and the commands run under a grant (at most 200, 200 characters each); Edit, Write and shell writes to it are denied; removed at SessionEnd, files older than a week pruned |
| `~/.claude/cobot/machine.md` | Markdown, one `## <host>` or `## <host>/<container>` section | absent | the owner's answers only: `route:` (install route) and `declined:` (helpers not to advise), written by `cobot-env prefer` and `decline`; lines you add are kept; nothing detected is stored |
| `.agent/CONTEXT.md` `runs:` | header field | `host` | where commands run locally (`podman · builds: distrobox enter dev --`), asked by onboard step 3b or a new project's first spec; verified commands stay bare and CI runs them bare |
| `.agent/CONTEXT.md` `gcp-mcp:` | header field, `yes` or `no`, a `# comment` may follow; not in the template | absent (asked) | whether Google Cloud live reads go through the owner's `gcp-*` MCP servers (`yes`) or `gcloud` and `kubectl` (`no`); asked once by the first Google Cloud work (onboard step 6c, `/cobot:consult gcp`, spec or wrap picking the gcp consultant, `/cobot:debug` on a Google Cloud target), never again; any other value, a second line or a line below the header counts as unset and `cobot-memory check` warns (decision 37) |
| `CLAUDE_CONFIG_DIR` | path | `~/.claude` | where the owner files above live, under both runtimes; Claude Code's sandbox keeps it read-only to Bash, so there `cobot-memory init --add-identity` or `--trust-root` still writes the memory, then prints `trust not recorded:` with the command for the owner's own terminal and exits 1 (`cobot-env prefer` and `decline` print `answer not recorded:` the same way) |
| `XDG_DATA_HOME` | path | `~/.local/share` | foreign-mode memory under `cobot/repos/<host>/<owner>/<repo>`; the gate's per-session ask counts under `cobot/asks/` (rule texts and counts, a week kept); the report check's per-session state under `cobot/reports/` (refused builder and investigator ids, and an id with the sha256 of each report let through, never the report text; a week kept) |
| `.agent/debug/<date>-<slug>.md` | Markdown from `skills/debug/template.md`, `status: open \| resolved \| unresolved` | absent | one record per `/cobot:debug` investigation, committed like a spec (outside the tree in foreign mode); the gate refuses an Edit or Write there whose text is secret-shaped (`SECRET_RE` plus `ya29.` tokens, JWTs, `Bearer` headers, URL credentials, kubeconfig `client-*-data`, `"private_key":`), naming the kind, and `cobot-memory debug check` and `check` exit 1 on one or on an excerpt over 20 lines or 2000 characters; `<redacted>` is clean; the brief's findings line ends `; debug: <n> open` (decision 35) |
| `.agent/noticed.md` | Markdown, one dated line per item | absent | builders' `Noticed:` items the report hook parked; `/cobot:wrap` files or drops each, and `cobot-memory noticed list` and `noticed clear` read and empty it |
| `DOCKER_HOST`, `DOCKER_CONTEXT`, `DOCKER_CONFIG`, `MISE_DATA_DIR`, `ASDF_DATA_DIR`, `CONTAINER_ID` | read only | unset | what `cobot-env detect` reads besides PATH: the engine behind docker, the mise and asdf shims folders (a hit there is a shim, not trusted in foreign mode; decision 29), the distrobox it runs in |
| `COBOT_RULES_OWNER`, `COBOT_RULES_PROJECT_DIR` | paths | unset | override the owner file and the project directory (tests, spikes) |
| `COBOT_GATE_LOG` | path | unset | append one JSON line per judged call: tool, decision, first 120 chars |
| `COBOT_GATE_DEADLINE` | seconds, 1 to 8 | `8` | agy gate shim: the deadline before it answers deny (the hook's timeout in the root `hooks.json` is 10) |
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

When several parts of one command ask, the reason gives the first ask in full, then names the
others: `…; also asks: ask Bash(git push*), ask Bash(git commit*)`. It names up to three in all,
then `+N more`. Another ask is named by its row (a project row by its place) and its runner, or
by the first 40 characters of the gate's note. The reason stays within the prompt's 200
characters, and a `git push` stamp keeps its room. A deny shows only the deny.

From the third time `ask Bash(git commit*)` or `ask Bash(git rebase*)` asks in one Claude Code
session, the reason ends once with the line that would stop it:
`· to stop asking: allow Bash(git commit*) in ~/.claude/cobot.rules`. cobot never writes the line;
you add it to your owner layer if you want. Only these two rows of local, undoable work are ever
offered, never an outward, install, credential, agent-scoped or owner-written row. The gate counts
asks per session in `~/.local/share/cobot/asks/` (rule texts and counts, no command text; files
older than a week are removed). agy's payload carries a `conversationId`, which cobot does not
use, so it is never offered there.

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
`~/.gemini`); `find ~ -exec … {} +` of any command; a `find -exec` or `fd -x`/`-X` body meets the
rows its command meets (`find … -exec rm -rf {} +` asks like `rm -rf`, `fd -Hx` included);
`busybox <applet>` is judged as the applet; runners whose command the gate does not read ask
like `xargs` (GNU `parallel` and its family, `watch`, `entr`, `watchexec`, `hyperfine`, `setsid`,
`taskset`, `chrt`, `unbuffer`, `strace`, `pkexec`, `run0`, `systemd-run`, `unshare`, `firejail`,
`script`, `tmux`, `screen`, `pueue`, `tsp`, `nq`), reads such as `watch git status` included;
a glob over a folder of more than 4 096 entries; every command run inside a protected folder.

Where a file lands (spec gate-f56-f60):

- An option value is read in every form: `cp -t`/`--target-directory` (joined, `=`, a long
  prefix such as `--t=`), `curl -o`/`--output-dir`, `wget -O`/`-P`, `7z -o`, `cpio -D`, and a
  path joined to any short option (`sort -o~/x`).
- Each source of a copy is judged where it lands: `<target>/<basename>`, or the full path for
  `cp --parents` and `rsync -R`. This covers `cp`, `mv`, `ln`, `install`, `rsync`, `scp`,
  `docker`/`podman`/`kubectl cp`, `rclone`, `gio` and `git mv`. So `cp e/.claude.json ~/` asks.
- A download lands at `<folder>/<url name>`, in the working directory when it names no folder.
  Names the gate cannot know (`curl -J`, URL globbing, `wget -i`, `-r`) ask in a folder that holds
  the config dir. `curl -K`, `wget --config` and a `wget -e` that moves output ask.
- An extraction with no folder option lands in the working directory, and asks there when that
  is or holds the config dir. So does a session started in HOME (owner's choice). `tar -P`,
  `cpio -i` without `--no-absolute-filenames`, `unzip -:`, `7z -spf`, and `TAR_OPTIONS` or `UNZIP`
  set in the command ask.
- A config dir moved outside HOME keeps its folder protection. Moving a folder that holds the
  config dir is refused like removing it (`mv /home x`).

Not covered: a link reached after a second hole segment (`*/d*/key.txt`), an inherited variable
or run-time data standing for a whole protected path (F-59), a `CDPATH` set only in your shell
profile, a link created between the check and the run, archive members (the gate never opens an
archive), writers whose output folder it does not read (F-61: `pax`, `ditto`, `sftp`, `aria2c`,
`gh … download -D`, decompression in place), taking the config dir away by `tar --remove-files`,
`zip -m`, `chmod`, `mount --bind` or a symlinked `CLAUDE_CONFIG_DIR` (F-62), and `busybox find`.

A script that writes files is denied, whatever the host suggests: a Python script read from stdin
or `-c` whose code opens a file for writing, calls `write_text`, `write_bytes`, `shutil.copy`,
`shutil.move`, `os.replace` or `os.rename`, and `perl -i`. Edit and Write show you the diff and
meet the path rules; a script is opaque to both. A script that only reads keeps its ask.

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
verb is an alias the line defines). The forge CLIs' built-in aliases are read as their commands
(`gh pr new` is `gh pr create`, `gh secret remove` is `gh secret delete`, `glab mr new`, `tea r
c`). Options before a `gh` or `glab` group or verb are read as cobra reads them, every way a
value option could take the next word (`gh release --title x create v1` is `gh release create`;
`-R`/`--repo` are known to take one). A top-level `gh` word gh does not know is a user alias or
an extension, so it asks, and so do `gh alias set` and `gh alias import`. An escaped or quoted
`;` (`find … -exec x \;`) is a word, not a separator.

`git config` is read into one canonical form, `git config <scope> <read|write> [exec] <key>
<value>`, where a file scope keeps its path (`--file <path>`). It reads either syntax
(`git config --global user.name x`, `git config set --global user.name x`) in any option order,
with options abbreviated as git allows (`--glob`) and short options clustered (`-zf <file>`).
Reads stay silent, and so do local writes of a plain key (`git config user.email x`,
`git config alias.st status`). A write asks when it outlives the repository's own config:

- **Scope:** a `--global`, `--system` or `--file` write, including one moved there by a
  `GIT_CONFIG`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_DIR` or `GIT_COMMON_DIR` prefix,
  or by `git --git-dir=…`.
- **Keys that run code (`exec`):** a key whose value git runs or follows later (`core.hooksPath`,
  `core.fsmonitor`, `core.sshCommand`, any `*.cmd`, `*.command`, `*.program`, `*.helper`,
  `*.driver`, `*.textconv`, `*.path`, `*.editor` or `*.pager`, `filter.*`, `url.*.insteadOf`,
  `remote.*.url`, `protocol.allow`, `init.templateDir`, and more).
- **Aliases:** any alias except one read-only verb alone (`status`, `log`, `diff`, `show`,
  `blame`, `shortlog`, `describe`). An alias of `config --global` writes what the rows ask for,
  and one of `push --force` runs what they deny.
- **Edits and renames:** `--edit` and `--rename-section`.
- **Unreadable words:** a key or alias value the gate cannot read (`$k`), or an option it does
  not know.

`export`, `declare`, `typeset` or `local` of those variables asks too, and so do `set -a` and
`set -o allexport`, which export every later assignment. `git submodule foreach` asks: it runs a
shell command in each submodule. To allow a form, name the canonical one:
`allow Bash(git config --global write user.email *)`, or
`allow Bash(git config --file .gitmodules write submodule.*)`.

Outward and account commands ask: changes to the forge account (`gh auth login`, `setup-git`,
`switch`), repository settings (`gh repo create|edit|archive`, secrets, variables, labels), CI
(`gh workflow run`, `gh run rerun|cancel`), issues and PRs (`edit`, `close`, `transfer`),
releases and gists, keys, and the machine's tool configuration (`rustup update|default`, its
`toolchain`, `target`, `component`, `override` and `self` verbs, `gcloud config set|unset`,
npm, pnpm, yarn and pip registry and account config, `docker logout`). Reads such as
`rustup toolchain list` or `gh secret list` stay silent.

Forge deletions are refused in every layer, for `gh`, `glab`, `gt` and `tea` alike: releases,
secrets, variables, labels, caches, runs, gists, keys, issues, merge requests, pipelines and
deploy keys, with or without `-R`. `cobot-rules sync` renders them in `permissions.deny`.

Commands that print a credential into the transcript ask. The claim covers these named printers,
not every way a secret can be printed:

- `gh auth token`, and `gh auth status` or `glab auth status` showing the token (`-t`,
  `--show-token`, in a cluster too);
- `glab config get token`;
- `gcloud auth print-access-token` and `print-identity-token` (also under `application-default`),
  `gcloud config config-helper` and `gcloud secrets versions access`;
- `git credential fill`, `git credential-<helper> get` and `docker-credential-* get`;
- `kubectl config view --raw` or `--flatten`, `kubectl get secret` with an output that prints its
  data (`yaml`, `kyaml`, `json`, `jsonpath`, `go-template`, `custom-columns`, in any case, or
  `--template`), and `kubectl get --raw` of a secrets path;
- `npm token list`.

An owner `allow` line lifts one form (`allow Bash(gh auth token*)`). A gcloud command is read
without its release track and the flags between its words (`gcloud beta secrets --project p
versions access`), so these rows and the read lists see its command words.

Text the agent writes into a file through the shell is refused, wherever the file is, with the
reason to use Edit or Write instead: their diff is what you review.

- **Refused:** a here-document, a here-string, or an `echo`, `printf`, `jq -n` or
  `awk 'BEGIN{…}'` stage whose text reaches a file through pass-through stages only (`cat`, `tee`,
  `dd`, `sponge`, `tr`, `sed`, `base64`, `xxd`, `head`, `tail`, `sort`, `uniq`, `cut`, `envsubst`),
  by a `>`, `>>` or `&>` redirection, `tee`, `dd of=`, `sponge`, `sort -o`, or `cp`/`install`
  from standard input. Also refused: `patch`, `git apply`, `ed` and `ex` fed such text, and the
  in-place editors `sed -i`, `awk -i inplace`, `ruby -i` and `yq -i`.
- **Asks** (an owner `allow` on the writing command lifts it): a write the gate cannot trace for
  certain, in a command that holds such text. That covers a stage that is not a pass-through
  before the write (`ssh h <<EOF > out`), a write owned by a group, subshell or loop
  (`{ echo a; } > f`), an `exec` redirection, a function defined in the command, and a group or
  `bash -c` body the text feeds.
- **Silent:** command output to a file (`cargo metadata > m.json`, `make | tee log`, and an
  `echo` or here-string of expansions alone, such as `echo "$(git rev-parse HEAD)" > f`), and
  text to `/dev/null`, `/dev/tty`, or `/dev/stdout`, `/dev/stderr`, `/dev/fd/1` and `/dev/fd/2`
  while they still reach the terminal. Redirections are read in order, so `2>f >&2` writes `f`.
  Any other device path, `/dev/tcp/…` included, is a file. An expansion of text the command
  wrote (`x=a; echo "$x" > f`, `echo "$(printf a)" > f`) is literal text.
- **Not claimed:** sed's `w` command, `split` and `csplit`, and sources the gate does not name.

A `never` row that only an unknown option before a `gh` or `glab` verb reaches asks instead of
denying: in `gh issue --label delete list` the word `delete` may be the label's value, and in
`gh release --title x create v1` the word `create` may be the verb. No `allow` lifts that ask.
Known options and attached values (`-R o/r`, `--notes=x`, `-tx`) are read for certain, so
`gh release -R o/r delete v1` is still refused. `gh pr merge --delete-branch` asks like any
merge; the branch deletion is not refused.

`${…}` and `$"…"`: a variable is a hole read by how the command sets it (spec gate-f55):

- **Put in:** one literal assignment at the top of the list, before its use. `X=publish; cargo $X`
  is denied. A `for` list is put in word by word.
- **Alternatives:** `${x:-word}`, `${x:+word}` and `${x:=word}` are the value or the word, each
  judged, so `cargo ${x:-publish}` is denied.
- **Full hole, a path word that is never spared:**
  - other operators (`${x#pat}`, `${x@Q}`), `${!x}`, `${a[0]}` and `$_`;
  - a positional after `set`, `shift` or a function;
  - a second or nested assignment;
  - every variable of a runner body or a `sh -c` string.
- **Spared as a whole word, like `$(…)` (F-59):** an inherited name, or run-time data (`read`,
  `mapfile`, a loop over `$(…)`). Glued to path text it is a hole, so `cp x ~/.claude/$X` asks.
- **Text:** `${#x}`, `$?`, `$$`, `$#`, and `$HOME` and `$PWD`, which the gate puts in itself. A
  command that assigns HOME or PWD adds that reading.

A locale string `$"…"` is a hole whose known value is its untranslated text, so `cargo
$"publish"` is denied.

The files a later Bash call sources are sealed, the start files ask, and so do the variables
that point a program at a file:

- `~/.claude/shell-snapshots/*` and `~/.claude/session-env/*` (with the moved config dir's
  twins) are refused to scripts and the file tools.
- The shell start files ask: bash, zsh (with `ZDOTDIR`'s twins), fish, nushell,
  `environment.d`, `~/.pam_environment`, `~/.inputrc` and `~/.ssh/rc`. So do `~/.curlrc` and
  `~/.wgetrc`.
- Setting `BASH_ENV`, `ZDOTDIR`, `HOME`, `XDG_CONFIG_HOME`, `CURL_HOME`, `WGETRC`, `PS4`,
  `SHELLOPTS`, `BASHOPTS`, `PROMPT_COMMAND` or an exported function asks, and so does `ENV`
  with a shell.

Precedence: `never` in any layer wins; a prompt-only ask (`terraform`, `tofu` and `terragrunt`
`apply` and `destroy`) asks whatever else matches; an `allow` from the owner layer (or an
agent-scoped one from the default layer) silences the gate; `ask` prompts; otherwise the host's
own permissions decide. For MCP tools, an owner or project `ask` also outranks a read and the
host's UI tools, which are otherwise silent. Under Claude Code the gate emits `allow` only for a
command a session grant covers (below); under agy it answers `allow` meaning no opinion,
`force_ask` for an ask, and never `auto_approve`.

### Session grants

For a lab or a demo, you can let the main thread run one kind of write on one named target for
the rest of a Claude Code session, without a prompt for each. Kinds: `gcloud` and
`gcloud-delete` (target: a project id), `kubectl`, `kubectl-delete`, `helm` and
`helm-uninstall` (target: a context name).

- The model asks you once with three answers: this command only, every `<kind>` on `<target>`
  this session, or no. On the second it runs `cobot-rules grant <kind> --target <t>`; the gate
  asks you about that command, and your approval is the grant. A rule cannot lift that ask, and
  a subagent or an agy session is denied. The grant is recorded only where Claude Code sets
  `CLAUDE_CODE_SESSION_ATTENDED=1` (the interactive CLI and the desktop app), so a headless
  session never holds one.
- A covered command is a plain one (no pipe, `&&`, substitution or assignment) in the groups,
  verbs and options `expert-gcp` and `expert-kubernetes` list, naming its target flag once. Its
  reason reads `cobot grant: <kind> on <target> (cobot-rules grant --revoke)`. Anything else
  asks as before; a `never` row stays denied.
- Your settings still win: a `permissions.ask` or `deny` line in `settings.json` that matches
  the command keeps asking or denying under a grant.
- `cobot-rules grant --list` shows the session's grants and the commands run under them;
  `--revoke [<kind> --target <t>]` ends one or all. A grant expires after 12 hours, and the
  file is removed when the session ends.
- Terraform is never granted: each `apply` and `destroy` asks, and no `allow` line silences it.

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
  `expert-gcp`, an opt-in per repository (decision 37). The first Google Cloud work asks once
  whether to use them and writes `gcp-mcp: yes` or `gcp-mcp: no` into CONTEXT.md's header; edit
  the line to change it. On yes, the agent prints the setup and you run it: the APIs, the
  `roles/mcp.toolUser` binding, a read-only guard (the IAM deny policy with an organisation or
  folder, else a second identity on viewer roles), a Desktop OAuth client, then one line per
  server, registered once for every folder:
  `claude mcp add --transport http --client-id … --client-secret --callback-port 8765 -H "x-goog-user-project: <project>" -s user gcp-logging https://logging.googleapis.com/mcp`,
  and `/mcp` → Authenticate from the CLI. Under a `gcp-*` name, read tools are silent,
  write tools with a known verb (`create_`, `delete_`, `apply_`, …) are refused (`never`) and any
  other tool asks; under any other name, every tool that is not a read asks. The Google Cloud
  CLI server (`run_gcloud_command`, `run_bq_command`) is refused under any name, a claude.ai
  connector is not supported, and no session grant reaches an MCP tool. `claude mcp add`,
  `remove`, `reset-project-choices`, `claude --mcp-config` and `--settings`, an Edit or Write of
  `~/.claude.json` or `.mcp.json`, and a shell word naming either file (`cp`, `tee`, a
  redirection, `curl -o`) ask; a glob that only could name them does not.
  `cobot-memory check` warns on a `gcp-mcp:` value other than yes or no, a second line or one
  below the header, and on a repository `.mcp.json` declaring `gcp-*` or the Cloud CLI URL.
  The full setup, including the SSH tunnel for a remote host, is in
  `plugins/cobot/skills/expert-gcp/references/mcp.md`.

## Home Assistant

`hass-cli` reads its server and token from the environment: set `HASS_SERVER` and `HASS_TOKEN`
in your shell profile, or from a secret manager, before the session (decision 36). The gate then
judges it like this:

- refused: `--token`, `--supervisor-token` or `--password` on the command line, and any command
  that sets `HASS_TOKEN`, `HASSIO_TOKEN`, `HASS_SUPERVISOR_TOKEN`, `HASS_PASSWORD` or their
  `HOMEASSISTANT_` fallbacks (an assignment, `export`, `read`, `printf -v`, `for`), whatever the
  value: set them in your own shell before the session;
- asked: every write verb (`service call`, `state edit|delete|toggle|turn_on|turn_off`,
  `event fire`, `raw post|ws`, entity, device, area and integration writes), the whole `ha`
  Supervisor group, `discover`, `map`, `-s`/`--server` and `-x`/`--insecure` (in any short
  cluster too), `--debug`, `HASS_SERVER` set in a command, and a command that expands or prints
  a token variable (`echo $HASS_TOKEN`, `printenv HASS_TOKEN`);
- silent: the other reads, in the main thread only. No read-only agent has `hass-cli`.

A long-lived token acts with its user's full rights: a non-admin user's token is enough to read.
The consultant, learner, auditor and investigator are refused a command that would print
`secrets.yaml` or a `.storage/` file: naming it, a `<` redirect, a recursive `grep`, `rg`,
`semgrep` or verbose unredacted `gitleaks` over a tree holding one (exclude it:
`--exclude=secrets.yaml --exclude-dir=.storage`, `-g '!secrets.yaml' -g '!.storage'`), a history
printer (`git log -p`, `git show`, `git diff`, `git grep`) in a repository that tracks or tracked
one unless a pathspec excludes it (`-- . ':!*secrets.yaml' ':!*.storage/*'`), or a `curl` `file:`
URL; they are refused any expansion of a token variable. The Read tool is not gated, so the
consult's procedure carries the rule there.

## Cloud read lists

The security sweep's `cobot:auditor` and the debug path's `cobot:investigator` read with the
consultant's list: every `@consultant` row applies to them, and to no other agent name (an agent
of your own called `auditor` or `investigator` keeps no scope). A session grant never reaches
them.

For the read-only agents (consultant, learner, auditor, investigator), `gcloud … list|describe`,
`kubectl get|describe|logs|diff`, `helm template|lint`, `kustomize build`, `kubeconform` and
`istioctl analyze|proxy-status` are silent like `gh api repos/*`. A command that could run
repository content (an environment assignment, `git -c`, `--kubeconfig`, `--post-renderer`,
`--enable-exec`) asks instead, and `kubectl get secret` is denied for them (decision 28,
ADR-0006). These ask too (decision 35):

- an output that prints field values: `kubectl get` with `-o` or `--output` other than `wide` or
  `name` (`-oyaml`, `-o=json`, `-Ao jsonpath=…`), `--template` or `--raw`;
- a read that never ends: `kubectl logs -f|--follow`, `kubectl get|events -w|--watch|--watch-only`,
  in a short cluster too (`-pf`, `-Aw`);
- another cluster or identity than the kubeconfig's context: on `kubectl` and `istioctl`,
  `--server` (`-s`), `--token`, `--as`, `--as-group`, `--as-uid`, `--username`, `--password`,
  `--certificate-authority`, `--client-certificate`, `--client-key`, `--tls-server-name`,
  `--insecure-skip-tls-verify`; on `gcloud`, `--configuration`, `--impersonate-service-account`,
  `--account`, `--access-token-file`. `--context` stays silent: it names a context of your own
  kubeconfig.

`kubectl diff --show-secrets` is denied in every scope, the main thread included.

## What the read lists never cover

For the read-only agents, a read-list command loses its read list, and asks, when it
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
lists still take an inherited variable as a word (`find $X`): an agent cannot carry a variable
across Bash calls while the shell snapshots are sealed, and an assignment in the command asks.

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
