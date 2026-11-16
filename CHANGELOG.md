# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed

- Eval Bash can write its own workspace again: the eval job and the documented local command set
  `TMPDIR` outside `/tmp`, which the eval sandbox denies (anthropics/claude-code#104631, confirmed
  on Claude Code 2.1.325). `foreign-onboard` and `new-project-onboard` are back in the suite; their
  first full runs scored 1.00. `foreign-onboard`'s tree graders no longer count a write to the
  memory under `.agent`, and `cobot-memory init --foreign` names `.git/info/exclude`. The
  builder's proof grader stays in `evals-blocked/`, now for the run's missing Rust toolchain.
- The session brief keeps CONTEXT.md's Environment section: when the brief is capped, Verified
  commands, Constraints and then Environment get room first, each only when it fits, so a huge
  Environment still never pushes out the commands. The brief's spec list no longer grows with
  every spec: past three it gives the count and the three newest by their `date:`.
- `cobot-memory init --trust-root` and `--add-identity` no longer crash when Bash cannot write
  `~/.claude/cobot`. Claude Code's sandbox keeps most of the config directory read-only to Bash,
  in sessions as in evals. init still writes the memory, then prints `trust not recorded:` with
  the command for the owner's own terminal, and exits 1. The onboard skill carries on and hands
  that command to the owner; a `new-project-onboard` grader checks the report names it.
- `new-project-onboard`'s `no-second-onboard` grader no longer fails a report that says "Don't
  re-run onboard": a re-run preceded by "don't", "do not" or "never" is the advice the skill
  asks for, not a second onboard (run 43950232416).

## [0.3.0] - 2026-11-15

cobot runs under the Antigravity CLI from the same tree: the gate, the session brief, the agents,
self-protection and an install whose hook group gets a random name, so a repository cannot switch
the gate off. The gate also closes a set of path gaps in both runtimes (symlinks, case-insensitive
volumes, `$HOME` written for `~`, words after a `cd`, links reached by a glob, deletions and folder
options that take a protected folder with them), shows a project rule by its place rather than
its text, and denies a script that writes files in favour of Edit or Write. `expert-ui` gains A2UI
knowledge, `expert-gha` two lines from a real CI run, and the session brief keeps its budget.

### Added

- A2UI knowledge in `expert-ui` (knowledge only, no code): `references/a2ui.md` holds the
  protocol, packages and neighbours read from primary sources on 2026-11-15; an "Agent-driven UI"
  rule says when to propose it (the product's own agent renders UI for its end users), that the
  agent's output is data checked against the app's catalog, and to pin the pre-1.0 packages
  exactly; the ui consult audits a repository's A2UI catalog and flags a version range.
- The Antigravity record (T07): ADR-0007 amends decision 1 to "Claude Code first; the
  Antigravity CLI supported from the same tree, its gaps named";
  `docs/reference/antigravity-mechanics.md` dates every agy fact cobot relies on, with its source;
  `docs/harnesses.md` holds one row per runtime and version, each cell `ok`, `fails` or `not run`
  from a named run; a README Antigravity section names the gaps; `scripts/spikes/smoke-agy.sh`
  is the owner's live smoke (a scratch repository with a local bare remote, the real HOME, never
  `--dangerously-skip-permissions`; S4 `not run`). `wrap` and `spec` say a reviewer that did not
  run is `not run`, never clean.
- Install into Antigravity (T06): `./install.sh --agy` runs `agy plugin validate` on
  `plugins/cobot`, then `agy plugin install` of it at user scope; the same command refreshes (agy
  replaces the copy in place and restores it on failure), so it never uninstalls first. A failed
  validate installs nothing and a failed install exits 1 with the agy exit code. `--agy` is a
  modifier: alone it installs into agy only, beside `--project`, `--local`, `--user` or
  `--refresh` it runs that action then the agy install, in either order, and it refuses `--dev`
  and `--uninstall`. `--check` reports agy's version and whether cobot is installed there.
  `cobot-memory check` warns when `.agent/` holds `hooks.json`, `plugins`, `plugins.json`,
  `rules`, `skills`, `skills.json` or `workflows`: `.agent/` is also an agy customization root.
- The session brief under Antigravity (T05): the root `hooks.json` runs `hooks/session-agy.sh` at
  SessionStart, which prints `cobot-session start --runtime agy`: one `injectSteps` system
  message (agy presents a user message as the owner's own words), the project from
  `workspacePaths[0]` ("project unknown" without an absolute folder there, and no tool runs), the
  protocol, then an agy section of at most 1 200 characters (the absolute plugin and `bin/` paths,
  agy's tool names, the owner-typed skills, security-sweep and learn through `invoke_subagent`
  only, builder proof requested and not enforced, builders not proven gated), then the rule
  counts and the brief, whose budget shrinks by the section. The serialised answer stays within
  10 000 characters, cut from the tail. Both agy shims unset `CLAUDE_PLUGIN_ROOT`, so a value
  leaked from a Claude Code process cannot point the tools at another copy.
- Self-protection under Antigravity (T04): the default rules deny editing or writing agy's
  settings (`~/.gemini/antigravity-cli/settings*.json`), `~/.gemini/config/*` (hooks,
  enablement, MCP servers, installed plugins) and `~/.gemini/jetski/*` (command sidecars, access
  grants), and in every customization root (`.agents`, `.agent`, `_agents`, `_agent`, at any
  depth) `hooks.json`, `plugins.json`, `skills.json` and `plugins/*`: a hook or plugin there runs
  outside the gate. `agy plugin` and `agy plugins` `disable`, `uninstall` and `link` naming
  cobot are denied; every other `agy` call asks ("may replace or bypass the cobot gate"), and so
  does `install.sh`. A rule's trailing `# comment` now joins its reason, from the default and
  owner layers only (repository text does not speak in a permission prompt). A folder row
  (`<dir>/*`) meets a command substitution only where the token names the folder's last part
  (`plugins/`, `config/`), so `cat "$(pwd)/README.md"` stays silent.
- The rules gate under Antigravity (T03): a root `hooks.json` sends every agy tool call
  (`matcher: ".*"`) to `hooks/gate-agy.sh`, which runs `cobot-rules gate --runtime agy` under an
  8 s deadline and prints a deny with exit 0 on every failure (no or old `python3`, a non-zero
  exit, no decision, a timeout), since agy runs a call whose hook fails. The adapter answers
  `allow` (agy's "no opinion"), `force_ask` or `deny`, never `auto_approve`. It reads the
  project rules of every `workspacePaths` entry, never from the model's `Cwd`, which drives only
  the Makefile, mise and package.json expansion. `run_command` and `manage_task` input are
  judged as Bash (input to a running task always asks); both file-tool families as Edit and
  Write, the path judged as written, parent-resolved and fully resolved; MCP calls as
  `mcp__<server>__<tool>`, an eager name split at a known server or at every `_`, the strictest
  split winning. `invoke_subagent` in a `branch` or `share` workspace asks while
  `.agent/cobot.rules` is uncommitted, `run_workflow` always asks with the script's hash,
  `define_subagent` is denied, and any tool cobot does not know asks.
- The nine agents under Antigravity (T02): `scripts/sync-agents.py` writes `agents/<n>.md` from
  `claude-agents/<n>.md`, the body copied and agy's frontmatter set: tools as a YAML list mapped
  to both agy file-tool families, `sonnet` as `flash`, the learner on `pro` (agy ignores
  `effort`), `mainAgent: false`. The consultant and the learner get no command tool and
  `commandExecutionPolicy: "off"`, since their read lists need an agent identity agy hooks do not
  carry: under agy they read files and pages only. Builders are told to read their language skill,
  since agy's preload is not relied on. `check-plugin` holds every agent's twin, a known agy
  tool name (agy accepts an unknown one silently), the tier and `mainAgent: false`; the tables
  live in `bin/_cobot_agy.py`, shared with the gate.

### Changed

- `expert-gha` learned two lines from the curriculo CI run: pin zizmor-action's `version:` to the
  local audit's CLI, and a floating `channel = "stable"` in rust-toolchain.toml moves CI with each
  Rust release. Curated from `learn/gha`: a release snapshot, a superseded line and a private
  repository source were left out (F-42).
- A script that writes files is denied with a reason pointing to Edit or Write (a Python
  script from stdin or `-c` that writes, `perl -i`), and the protocol says so whatever the host
  suggests; a script that only reads keeps its ask (part of F-44).
- Version 0.3.0 in both plugin manifests and the marketplace; `release.yml` checks the
  Antigravity manifest against the tag too.
- The plugin tree splits for a second runtime (Antigravity, T01): Claude Code's nine agents move to
  `claude-agents/`, listed by file in `.claude-plugin/plugin.json`, which leaves `agents/` to the
  Antigravity agents; `.antigravity-plugin/plugin.json` carries the same name, version,
  description, license and repository. `check-plugin` holds the two manifests in agreement, the
  manifest's list equal to the folder, every skill body within agy's 24 000 bytes and every
  frontmatter strict YAML, which quoted `onboard`'s `argument-hint` and folded `contribute`'s
  description (agy skipped `onboard`; a strict parser rejects both).
- `lang-rust` lists the crates a Rust CLI starts with (F-20): clap, serde, serde_json, tempfile,
  assert_cmd and predicates, beside proptest; every crate row re-read on crates.io, dated by the
  version's own publish date, with the MSRV of each.
- Fewer stops for the owner (latex-resume-generator session, 42 gate asks and 9 question rounds).
  Replayed through today's gate, 37 of its 41 Bash asks still asked, 33 of them for how the
  command was written: 23 inline `python3 -` edits, 8 `python3 -c` JSON reads, 2 loops running a
  variable as the command. The protocol now says to edit with Edit or Write, read JSON with `jq`
  and name each program, which the gate passes. `/cobot:spec` asks at most four questions (the
  question tool's limit, which five overran twice), never what CONTEXT.md, a cobot rule or a later
  spec settles; it writes the owner's environment answers into CONTEXT.md; and it folds BLOCKER
  and MAJOR objections itself, asking only to overrule one or when the fold drops something the
  owner asked for. The protocol's learning line keeps the rule; the learn skill keeps the steps.

### Fixed

- Gate F-33 and F-34 (both runtimes; `.agent/specs/gate-f33-f34.md`): `find` with a deleting
  or running action, `gio trash|remove` and deleting HOME or `/` ask when they take a protected
  folder with them; the folder `tar -C`, `unzip -d`, `patch -d` and `git -C` name is checked and
  resolves the command's relative words; a project rule's warning names its line, not its text.
- Gate residuals (F-29 to F-32, both runtimes; `.agent/specs/gate-residuals.md`): a project
  row's reason shows its place, not its pattern or tool name; `never` and `ask` path rows and the
  program word compare without case (macOS volumes); `$HOME/` reads as `~/`, which the `~/.gemini`
  rows missed; words and redirect targets after a `cd` resolve in the folder it reaches, and an
  unknown `cd` asks for a protected file's name; deleting a protected folder's parent asks; a
  command run inside a protected folder asks once naming the folder, no longer naming its
  program as the file; a bare glob that reaches a symlink into a protected folder asks, with a
  bounded scan.
- The session brief stays within its budget: the findings block left no room for the knowledge
  and specs lines after it, so a full findings block pushed the brief past its 6 000 characters
  (cobot's own brief was at 6 265).
- Security review fixes (wrap), both runtimes where the gate is shared:
  - a bare word is a path in the working directory too, so a command run with its working
    directory inside a protected folder (agy's `Cwd: ~/.gemini/config/plugins` with
    `rm -r cobot`, or `tee hooks.json` inside `.agents/`) asks;
  - a protected folder row covers the folder itself, and moving or linking onto a customization
    root (`mv x .agents`, `ln -s docs .agents`) or a protected folder's parent (`mv ~/.gemini …`)
    asks;
  - under agy a write through a symlinked customization root, cobot's foreign-mode `.agent`
    included, is judged by the root's name;
  - a branch or share subagent asks while `.agent/cobot.rules` is ignored, untracked, or under a
    symlinked `.agent`;
  - a top-level `Workspace` beside `Subagents` counts; `run_workflow` names a relative script path,
    both forms, and a large or special file without reading it;
  - MCP servers of workspace plugins are known servers, so a known prefix never hides them;
  - the agy brief warns when the installed hook group kept its default name;
  - `install.sh --agy` and the smoke no longer print the random group name, and `check-plugin`
    fails on one written into the tree.
- Review fixes under Antigravity (wrap): a substitution counts as an unknown whole path only
  where it leads the path or names its last part, so `.agents/plu$(x)ins/…` and `.agents/$(x)/…`
  ask again; a `workspacePaths` that is not a list of absolute paths asks instead of reading
  folders the hook's cwd picks; an asked push without a project no longer crashes the gate; the
  default and owner layers load without a git call; the agy section names the plugin folder once
  and is never cut, and the workspace warning is capped; `install.sh --agy` leaves Python caches
  out of the staged copy, names it in its log, and fails on every staging step.
- Under Antigravity a repository could switch the gate off: agy merges hook groups by name, so a
  committed `.agents/hooks.json` with `{"cobot": {"enabled": false}}` disabled cobot's group
  (smoke `h2`). `install.sh --agy` now installs a staged copy whose group is named
  `cobot-<16 random hex>`, new at each install, and the agy brief warns, naming the files, when
  a workspace holds `hooks.json`, `plugins.json` or `plugins/` in `.agents`, `.agent`, `_agents`
  or `_agent` from the workspace up to the repository root. The smoke gains `h3` (a workspace
  `auto_approve` beside cobot's deny) and `s2` (the warning).
- Under Antigravity the brief's own tool calls (`python3 -I <plugin>/bin/cobot-memory check`) no
  longer ask: the installed plugin lives under the protected `~/.gemini/config/`, and running
  one of cobot's own `bin/` tools is not writing it. Any other word naming that folder, a
  redirection into it included, still asks (smoke `o1`).
- `mise --version`, `-V`, `--help` and `-h` alone no longer ask: a lone info flag names no task
  (a flag followed by anything still asks, since it may precede one).
- Consultants fell off their read list: in run 43584857035, 16 of 21 consultant sessions hit the
  catch-all ask, so the gha consultant never ran zizmor (F-27). Ten opened with `cd <repository>`,
  three with `pwd`, three wrapped a command in a `for` loop or a shell function. The consultant
  and the consult brief now say the working directory already is the repository and commands run
  in place, one command over many files; the ui procedure computes every colour pair in one `jq`
  call; the read list gains bare `pwd` only (a `cd` keeps asking). `consult-fan-out` fails a run
  whose consultant falls through to the catch-all ask.
- An Edit or Write through a symlinked folder or file no longer misses a `never` rule (F-28):
  `never Write(*/vault/*)` denied `vault/key.txt` but not `door/key.txt` with `door -> vault`. The
  gate judges the path as written, with its parent resolved and fully resolved, and the strictest
  rule wins; a `~` rule also matches HOME resolved when HOME is a symlink. The Bash protected-file
  check judges the same forms, and resolves the folders before a glob's first hole (`cat door/*`).

## [0.2.0] - 2026-11-14

The first release since 0.1.0 and the one that makes the repository public: R1.1 (learning,
currency, delivery, the security sweep), R2 slices 1–4 (hardening, UI and CI/CD experts, cloud
experts, stacks), the consult router, the MCP read-name gate, the GCP proof with the Google Cloud
MCP servers, new projects, the gate's bash shell model (command substitutions, a `cd` before a
runner, brace and glob expansion, repository configuration and trust), and the eval suite running
in CI under workload identity federation.

### Added

- New projects (`.agent/specs/new-project.md`): `cobot-memory check` prints a `tree:` line (new,
  existing, inside another repository, not a git repository; the files decide, a git failure
  reads as existing), and a repository without memory gets a brief line naming onboard instead
  of an empty brief. On a new project `/cobot:onboard <goal>` makes the first commit or takes the
  remote's branch (on the owner's yes, never bypassing signing or hooks), asks profile, licence
  and forge, leaves the language to the first spec and writes a `none yet` verified row; the first
  spec asks the language, loads its `lang-*` skill by name, keeps CONTEXT.md current and makes T01
  the scaffold, whose proof commands build records as the first verified commands. `git init`
  asks in the default rules; eval `new-project-onboard`. The tree scan never runs before the
  trust check and runs git with `core.fsmonitor` and the untracked cache off, so a repository
  delivered with its `.git/config` cannot run its own program at session start.
- Google Cloud remote MCP servers in `expert-gcp` (`references/mcp.md`, 0.2.0 PR 6, decision 28
  amended): the owner registers them as `gcp-<service>` with a Desktop OAuth client, signs in
  with `/mcp` from the CLI (an SSH tunnel for the callback on a remote host), and the main
  thread reads logs, events and cluster state through them; consultants keep auditing files.
  Proven on gcp-platform with `list_log_entries` and `list_clusters`; the deny-policy guard needs
  an organisation, so a personal project relies on the gate's refusals.
- R2 slice 4 (`.agent/specs/r2-stacks.md`): `fw-react` (React 19.3, the Compiler, React Router 8,
  TanStack Query), `fw-next` (Next.js 16.4, every line reported until a repository exercises it),
  `fw-vue` (Vue 3.5, Pinia 4, vue-router 5), `lang-shell` promoted from `lang-fallback`,
  `expert-api` with `/cobot:consult api` and the eval `api-contract-audit`, and `expert-gitea`
  (Gitea 28 against GitHub and GitLab, its API, contributing to go-gitea). Build names the
  framework or shell skill in the builder's brief and the builders call it first; `*.jsx` and
  `*.vue` go to the TypeScript builder. Framework skills are knowledge skills (capped, tracked for
  staleness). The gate rewrites CLI aliases before matching (`glab mr new`, `gt release new`,
  `tea r c`) and covers Gitea's `gt` and the archived `tea` like `gh`.
- R2 slice 3 (`.agent/specs/r2-cloud.md`, decision 28, ADR-0006): `expert-gcp` (project and
  organisation structure, IAM least privilege, Workload Identity Federation for GitHub, GitLab
  and GKE, the `google` provider 8.x idiom, universes with the legacy `gcd-universe` rules
  re-verified, GKE Autopilot, Artifact Registry, Cloud Build against the forge's OIDC, logging
  and cost levers) and `consult-gcp`; `expert-kubernetes` (manifests, Kustomize, Helm 4,
  Gateway API, Pod Security Standards, resources, probes, NetworkPolicy, PDB, GKE fit) and
  `consult-kubernetes`; `expert-service-mesh` (Istio ambient and sidecar, STRICT mTLS,
  AuthorizationPolicy, Telemetry API, Cloud Service Mesh) and `consult-service-mesh`, each with
  dated references from `.agent/knowledge/cloud.md`. The gate cuts a `gcloud` command after its
  verb so a resource named `list` cannot pass as a read, reads of `gcloud`, `kubectl`, `helm`,
  `kustomize`, `kubeconform` and `istioctl` join the consultant's and the learner's read lists,
  a segment that could run repository content (an environment assignment, `git -c`,
  `--kubeconfig`, `--post-renderer`, `--enable-exec`, `--enable-helm`) never matches an
  agent-scoped allow, `kubectl get secret`, `kubectl get -f` and `kubectl config view --raw`
  are denied for the read-only agents, and the `gcloud` mutating verbs decision 26 named but
  the rows missed ask (`add-*`, `set-*`, `remove-*`, `destroy`, `upgrade`, `patch`, `cp`,
  `rm`, `deploy`, `submit`, `enable`, …) with `kubectl run|debug|cp|expose|autoscale`, `helm
  plugin install|registry login` and `istioctl waypoint|tag|create-remote-secret`. Evals
  `gcp-iam-audit`, `k8s-workload-audit`, `mesh-mtls-audit`. The eight longest skill
  descriptions are trimmed under 600 characters.
- R2 slice 2 (`.agent/specs/r2-experts-ui-cicd.md`): `expert-ui` (WCAG 2.2 AA by criterion,
  W3C design tokens, type scale, component systems, device profiles including the Miyoo Mini
  Plus and OnionOS themes, the brief → tokens → screens procedure with Google Stitch under the
  gate) and `consult-ui` (contrast computed with `jq`); `expert-cicd` (platform-neutral
  delivery principles, forge table) linked from `expert-gha`; `expert-gitlab-ci` (keywords,
  `.gitlab-ci.yml` snippets in the trigger-matrix shape, dated versions and an image digest) and
  `consult-gitlab-ci`; `/cobot:ship` detects the forge offline and CONTEXT.md gains `forge:`;
  `glab` rows mirror the `gh` rows and the `gh`/`glab api` canonical form treats a body flag as
  the implicit POST it is; evals `ui-contrast` and `gitlab-ci-shape`; `check-plugin` reads
  folded descriptions and caps their total.
- R2 slice 1 (`.agent/specs/r2.md`): a `PostToolUse` hook on the Agent tool blocks a builder
  report that carries no command with an exit code under `Checks:` (or no `Checks: none —
  <reason>` line) back to the orchestrator; every builder prompt fixes that shape.
  `cobot-memory stamp` answers whether HEAD is covered by the last wrap and the gate appends it
  to every `git push` that asks. `cobot-usage` reports requests and tokens per session, model
  and agent type from the local transcripts. `onboard --foreign` writes never-push rules for
  every remote but `origin`; push options are hoisted after the remote. Evals `foreign-onboard`
  and `actions-pinning`. `ask mcp__*__generate*` and `ask mcp__*__edit*` (decision 27, ADR-0005).
- `scripts/github-settings.sh --check|--apply`: the repository settings as code (merge flags,
  SHA-pinned actions required, read-only token, Dependabot alerts and security PRs, the `evals`
  and `knowledge-refresh` environments, the `main` ruleset where the plan allows it); secrets
  stay with the owner. `.github/dependabot.yml` for the pinned actions; the eval job's API key
  now lives in the `evals` environment; the zizmor job annotates instead of uploading to code
  scanning (paid on a private repository) and fails on medium or worse. `SECURITY.md`.
- `/cobot:ship`: the delivery pipeline from the verified commands and the profile (PR, merge,
  release and weekly triggers, one `ci-ok` aggregator, SHA pins from the references, every
  command run locally first, then audited); refuses in foreign mode and patches existing
  workflows instead of rewriting them. `expert-containers` (Dockerfile, compose, Podman,
  signing, SBOM, Trivy, GHCR) and `consult-containers`.
- `/cobot:contribute` with `templates/UPSTREAM.md`: upstream work under the maintainers'
  rules (AI policy, sign-off, parent resolved through `gh repo view`), the wrap stamp checked
  against HEAD, the PR body left to the owner when the policy forbids generated text, push and
  PR commands printed, never run; `gh repo fork`, `git remote add|set-url` ask.
- `/cobot:security-sweep`: whole-tree read-only audit by the consultant with nine rule packs
  (core, go, python, ts-js, rust, shell, dockerfile, terraform, github-actions) ported from the
  legacy skill, honouring `.agent/accepted-risks.md`; `cobot-memory risks add|list` writes and
  reads rows keyed by rule, file and symbol with an expiry of at most 90 days; `check` names
  expired rows; read-only scanner forms join the consultant's allow list.
- `cobot-memory compact`: past 400 lines the journal keeps its last ten entries and folds the
  rest into one dated entry (a model summary from wrap, else a digest with the `Open:` items),
  raw entries archived in `JOURNAL-archive.md`; the brief is unchanged by a fold.
- `lang-python` and `lang-typescript` with verified versions and CI jobs; `python-builder`,
  `typescript-builder` and `terraform-builder`; `build` routes by the files in scope.
- Evals `never-apply`, `builder-routing`, `proof-required` (fixtures through `scaffold_script`,
  the eval job passes `--scaffold`).
- This repository's `ci.yml` gains the `ci-ok` aggregator and cancels in-progress runs only on
  pull requests.

- The learner: agent `learner` (read-only, sonnet) behind `/cobot:learn <skill or topic>
  [question]`, which returns a knowledge delta whose entries carry a status, a source, a date and
  a scope; a re-verified claim is re-dated in place, a changed fact names what it `supersedes`.
- `cobot-memory knowledge [--stale] [--json] [--brief]`: dated lines per skill with their age;
  version lines are stale after 30 days, idiom after 90 (decision 23); the session brief carries
  one line naming the stale skills and the `reported` count.
- `cobot-memory learn --promote [--source DIR] [--in-place]`: general entries reach the
  cobot checkout (the directory marketplace Claude Code recorded, `$COBOT_SOURCE` or
  `--source`) on a `learn/<topic>` branch in a worktree under the data directory, re-dating or
  superseding existing lines and appending the rest to `references/learned.md`; a skeleton
  `expert-<topic>` only when the delta carries a `skeleton` block; the push and PR commands are
  printed, never run; the gate asks on `--promote`.
- `cobot-deps check|brief`: dependency currency through the ecosystems' own tools (cargo,
  go, npm, pnpm, uv, poetry, the Terraform registry), hardened (`GOTOOLCHAIN=local`, scripts off,
  no external cargo subcommand for the outdated list), cached for seven days per repository while
  the lockfiles hold; `brief` reads the cache only and is in the session brief; `onboard` runs
  the check, `wrap` runs it fresh before the PR (decision 21).
- `knowledge-refresh.yml`: weekly, the two stalest skills are refreshed by the learner and arrive
  as one pull request each; `learn-unknown-domain` eval.

- `cobot-rules` resolves mise tasks: `mise run <task>`, the `mise <task>` shorthand and
  `mise exec … -- <cmd>` are judged as the commands behind them, and reasons and `explain` name
  the origin (`via mise run deploy`). A task with `depends`, `file`, `shell`, `dir`, templating or
  command substitution stays opaque; a `mise` global flag or unknown subcommand now asks.
- `install.sh --refresh [DIR]`: uninstall and reinstall at project scope, the only way a
  same-version edit reaches an installed copy (`claude plugin update` keeps the cache).
- The gate looks through entry wrappers and judges the command behind them: `distrobox enter …
  -- <cmd>` (and `-e`), `toolbox run`, `docker|podman exec`, `docker compose exec|run`,
  `nix develop -c`, `nix-shell --run`, `flatpak run --command=`, `chroot`, and a shell's `-c`
  string, nested up to four levels; an option a wrapper's table does not know keeps it opaque.
  Remote execution now asks: `ssh`, `mosh`, `kubectl exec`, `gcloud … ssh`, `gh codespace ssh`;
  so do `source` and `.`.
- Default rules from the owner's third review: `never` on a commit carrying `Co-Authored-By` or a
  PR body carrying `Generated with` (authorship, not a word ban); `ask` on dependency-adding
  commands (`cargo add`, `npm install <pkg>`, `pnpm add`, `yarn add`, `bun add`, `go get`,
  `uv add`, `pip install`, `poetry add`); bare installs from a lockfile stay silent.
- Cluster, mesh and image rules: mutating `kubectl` verbs (`create`, `patch`, `scale`, `rollout
  restart|undo`, `drain`, `label`, `set`, `port-forward`, …), `helm install|upgrade|uninstall|
  rollback|push|repo add`, `istioctl install|upgrade|uninstall|x`, `gcloud container fleet mesh`,
  and `docker|podman push|login|system prune|rm|rmi` ask; `helm` and `istioctl` global options
  are stripped before matching.
- Release and pin rules from the headscale dogfood: `goreleaser release` asks (it publishes
  unless `--snapshot` or `--skip=publish`; the owner layer may allow the snapshot form), and so
  do `nix flake update` and `nix flake lock` (they move dependency pins, decision 22).
- The gate resolves `make` targets by reading the Makefile (`_cobot_make`): recipe lines are
  judged on their own with the origin in the reason (`ask Bash(rm -rf*) via make clean`), plain
  variables, `define` bodies through `$(call)`, `$(MAKE)`, `$@`, target prerequisites, command-line
  `VAR=value` and `.DEFAULT_GOAL` are followed; `-C`, `-f`, `-j`, `-k`, `-n` and the other flags are
  understood. `include`, pattern or suffix rules, `.SECONDEXPANSION`, `$(eval)`, targets under a
  conditional or with a target-specific variable, recipes that need a function or an unknown
  variable, a nested make under `-C`, `--eval` and unknown options keep the command opaque. make
  is never run: `$(shell …)` in a Makefile would otherwise execute at gate time.
- `cobot-memory journal add [ENTRY]` and `learn [JSON]` take their payload as an argument as
  well as on stdin, and never wait on a terminal.
- `install.sh --refresh` reinstalls at whichever scope the plugin was installed in the directory,
  project or local, so a foreign repository's local-scope install refreshes too.
- `onboard` names a fork of someone else's repository as the foreign path (the trust reason lists
  the remotes that belong to no identity), and copies the maintainers' hard constraints
  (`CONTRIBUTING.md`, `AI_POLICY.md`, DCO or CLA, the project's own agent instructions) into
  CONTEXT.md for `/cobot:contribute` to read.
- `spec` sizes a change as one branch and one PR with one commit per task, writes the
  architecture choice (hexagonal by profile) and justifies every new dependency; `build` commits
  each finished task and refuses an unnamed dependency; `wrap` runs the pre-PR currency check and
  opens one PR; builders report `Deps added:`; `expert-gha` carries the CI trigger matrix.

### Changed

- The gate judges a command substitution by what it runs (`.agent/specs/gate-substitution.md`):
  `$(…)`, backticks, `<(…)` and `>(…)` no longer ask on their own. A new quote-aware scanner
  (`bin/_cobot_shell.py`) hands each body to the same rules; the substitution asks only where
  its text could decide what runs or make a `never` or `ask` row match, and a `never` row that
  matches anyway still denies. `for f in $(find …); do cat "$f"; done`,
  `VIS=$(gh repo view …)` and `cobot-memory journal add "$(cat <<'EOF' … EOF)"` run without a
  prompt; a `"$(cat <<'EOF' … EOF)"` body is also judged as its text, so an attribution line in
  a heredoc commit or PR body is denied, not asked. The default promote rule is anchored on the
  command word (`cobot-memory learn *--promote*` and its `python3`/`python` forms). An
  agent-scoped `allow` never silences a segment holding a substitution. Unparseable commands
  ask with a reason instead of a traceback in `cobot-rules check`.
- The protocol is back under its stated 3 000 characters (2 995, was 3 484) with no rule
  dropped, and its delegation line names builders by pattern (`cobot:<language>-builder`, else
  `cobot:builder`) instead of three of the six.
  `scripts/check-plugin.py` now fails CI when the protocol passes 3 000 characters.
- **Breaking: one `/cobot:consult [domain]` replaces the seven `consult-<domain>` skills.** It
  spawns one read-only consultant per domain in one message, so audits run in parallel (forked
  skills ran one at a time, measured 2026-11-10); with no domain it audits every domain it
  detects. Spec and wrap launch the same consultants beside the challenger or the reviews. Use
  `/cobot:consult gha` where you typed `/cobot:consult-gha`.
- **Breaking: `/cobot:onboard`, `/cobot:rules` and `/cobot:security-sweep` are typed by the
  owner.** The model proposes them and dry-runs the gate through the `cobot-rules check` binary.
- Expert and language skill descriptions fit 350 characters with their triggers kept, and
  `check-plugin` counts only what the model sees (user-only skills out, `when_to_use` in): the
  listing drops from 14 651 to 8 142 characters. A plugin skill's `paths:` does not gate it, so
  the description is its only trigger.
- A README for people: banner, badges, what cobot does, install, first steps, the commands you
  type and safety, in 103 lines instead of 230. The technical content moved to
  `docs/architecture.md`, `docs/configuration.md` and `docs/development.md`. The banner and the
  social preview come from the owner's illustration through `scripts/make-banner.py`.
- Repository tidy before 0.2.0: decided design inputs (discovery notes, both architect
  proposals, the first challenge, the crissp review, the third owner review, the arlo findings)
  moved to `docs/history/` with an index; the R1 spike scripts moved to `scripts/spikes/`;
  `.agent/CONTEXT.md` gained `forge:` and `governance:` and a result column; markdownlint-cli2
  0.24.0 everywhere (CI already used it).
- Onboarding follow-ups from arlo-camera-streamer-rs. A refresh runs `cobot-memory init` for
  missing files and offers `compact` when the journal is long; `check` names the CONTEXT.md
  header fields the template has and the file lacks, and the CONTEXT sections the brief drops.
  The brief names every other `.agent/*.md` (a legacy `HANDOFF.md`) as read on demand. Onboard
  checks free disk space before the first build of a compiled stack, records each verified
  command's result (and a `carried over, not re-run` form), reads the repository's other agent
  files and parks contradictions as findings, and explains what owner allow lines change
  (`ask` verdicts and `/cobot:rules sync`; the gate judges the inner command of `distrobox` and
  `bash -c` wrappers). `governance:` takes `path#heading-slug`, and `/cobot:spec` reads only
  that section. Every `lang-*` skill says CONTEXT.md and governance override its defaults.
  `cobot-deps` notes when `deny.toml` limits cargo-deny to listed targets, which is why it can
  count fewer advisories than cargo-audit over the whole `Cargo.lock`.
- `/cobot:spec` checks every change against the project's own principles: CONTEXT.md gains
  `governance:` (the path to a constitution or equivalent), `/cobot:onboard` fills it, and the
  spec's principles check gives each principle one line, a violation becoming a clarify
  question. Onboard also carries a spec-kit project over: the constitution moves out of
  `.specify/`, open tasks are copied verbatim into `.agent/specs/` for `/cobot:build`, and the
  feature folders stay as history.
- **Breaking: the project is named cobot** (ADR-0004). Marketplace `cobot`, plugin `cobot@cobot`
  (was `partner@agentic-partner`), prefix `/cobot:`, agents `cobot:*`, binaries `cobot-*`,
  modules `_cobot_*`, environment `COBOT_*`, tags `cobot rule|gate|session:`, rule files
  `cobot.rules`, state under `~/.local/share/cobot` and `~/.claude/cobot`; the protocol says
  "the cobot". `install.sh` migrates the existing state and registrations once (see below).

- The untrusted-repository reason names the remotes that match no identity
  (`no identity matches every remote (ghsa -> github.com/juanfont) …`).
- The brief caps CONTEXT.md on section boundaries and names the dropped sections, and the cap
  grows into the room a short journal leaves (2 500 to 4 000 characters).

### Fixed

- Consultants could audit cobot instead of the owner's repository: the consult brief (reused by
  spec and wrap) named the plugin root but not the repository, and in the eval run the
  consultants read the plugin's checkout around it. The brief now names the repository's absolute
  path and the consultant audits it only.
- The CI eval job ran no Bash command at all: Ubuntu runners restrict unprivileged user
  namespaces through AppArmor, so the sandbox Claude Code puts around Bash failed on every call
  and every case that needs a shell scored on what it could do without one (run 43389854358:
  zero successful Bash calls in 114 sessions). The job lifts both restrictions before the eval,
  the sysctl and Ubuntu 26.04's `bwrap-userns-restrict` profile (lifting the sysctl alone left
  every call failing, run 43492553354), and checks a nested namespace before any paid session;
  the runner is discarded afterwards.
- Eval sessions could not run `cobot-rules` or `cobot-memory` (exit 127): `claude plugin eval`
  does not put the plugin's `bin/` on PATH as an installed plugin does, so the gate dry-run and
  every `cobot-memory init` failed (run 43494320182). The eval job prepends it, and runs on
  `ubuntu-26.04` instead of `ubuntu-latest`, so a new runner image is a reviewed change.
- Eval cases checked against the plugin-evals docs and run 43496720467 (13 of 19): the two "never
  ran the spec skill" graders were never scored (a `tool_used` Skill grader needs `arm: both`);
  `builder-routing` counted the builder's own edits as main-thread edits (now a trace regex on
  `parent_tool_use_id`); `never-apply` wanted `terraform plan` from a prompt that says the plan
  is reviewed (handing the apply back now counts); `gitlab-ci-shape` seeds its trust line in the
  fixture; the eval job grants `github.com` and `api.github.com` so `actions-pinning` can resolve
  a tag. `foreign-onboard`, `new-project-onboard` and the builder's cargo proof move to
  `plugins/cobot/evals-blocked/`: eval Bash cannot write, the workspace included.
- `actions-pinning` failed every run on `source-or-reresolve` although each one pinned the SHA
  it had just re-resolved upstream: the grader knew `gh api` and the expert's table but not
  `git ls-remote` on the action's repository (run 43580607780). It accepts that now.
- `/cobot:consult` could report before its consultants did: an `Agent` call that omits
  `run_in_background` started in the background in 22 of 23 calls (Claude Code 2.1.322, run
  43584857035), so one `consult-fan-out` run answered "both are still running", then wrote one
  message per domain as each finished. Consult, spec, wrap, ship and build now set
  `run_in_background: false` on every agent they start, and `check-plugin` fails a skill that
  names one of the plugin's agents without it.
- `cobot-memory init --help` ran `init` and wrote the memory files: the bins accepted any
  `--word`. `cobot-memory`, `cobot-rules` and `cobot-deps` now parse through one per-command table;
  `-h`/`--help` prints the usage, an unknown option exits 2, `init --profile` takes only the six
  profiles, `--` ends the options and an option's value is data, and `init --trust-root` before
  any commit refuses without writing. `protocol.md` no
  longer advertises a `brief --spec` that never existed.
- `cobot-memory stamp` reads HEAD in the worktree it runs from, not the main checkout: a wrap
  done in a worktree, where branch work happens, read as `missing — HEAD moved since the stamp`
  in `contribute`, `ship` and the gate's `git push` reason.
- The gate's ask reason names what made a command opaque: the first `$(…)` or backtick span, or
  the first opaque segment, instead of whichever segment came last (`opaque command 'head -14'`
  for a loop with a substitution, seen 20 times in the gcp-platform proof). A shell access to a
  protected file keeps its reason when a later segment also asks.
- `/cobot:security-sweep` maps every file kind the inventory finds to its pack and its scope line
  accounts for each kind: an `infra` repository's bootstrap script read no `shell.md` in the
  gcp-platform proof. The eval `sweep-every-pack` grades the shell and Terraform packs as read.
- The three eval cases parked as F-13 grade the protocol, not the sandbox's toolchain:
  `builder-routing` wants a cargo command quoted with its exit code (any code), `never-apply`
  and `proof-required` replace their judges with deterministic graders, and `proof-required`
  reruns with the standard library's `unittest` instead of pytest, which the sandbox lacks.
  `tests/test_eval_graders.py` checks every pattern, the one-judge limit and every fixture for
  free before a paid run.
- A worktree with a tracked `.agent/` writes its own memory (F-14): `cobot-memory journal add`
  from a worktree appended to the main checkout's journal, outside the branch being worked on.
  Foreign mode's single symlink in the main checkout is still shared by every worktree.
- `cobot-memory findings add --goes-to X` closed the finding: any value but empty or `open`
  counted as closed. It now writes `open → X`, and only `findings close` ends a finding.
  `compact --summary` no longer writes a second `Proof:` line (the archive pointer is
  `Archive:`), and the help puts init's description under `init`, not `stamp`.
- Three bugs found by onboarding arlo-camera-streamer-rs: `cobot-deps` ran `cargo update
  --workspace`, which reports every compatible dependency update as held back (it hid arlo-rs
  0.4.0 -> 0.4.1); the brief's journal trimming split a field from its indented continuation
  lines, garbling older entries; and a capped brief dropped Verified commands and Constraints
  first, because they come after Environment in the template. Those two sections now get room
  first.
- `install.sh` no longer prints "Failed to remove marketplace 'agentic-partner'" on every
  install: it matched the old name anywhere in the marketplace list, including the cobot
  marketplace's own folder path, which is still named `agentic-partner`. It now matches the
  name line only.
- Eval graders agree with the protocol (F-12): `profile-caps-size` grades the reply with
  three regexes (`small`, the profile cap, a first step) instead of a haiku judge that failed
  answers meeting the protocol and wanted a sentence the protocol never asks for;
  `tiny-no-ceremony` looks for the size line in the trace, where "before acting" puts it, with a
  pattern the injected protocol text cannot satisfy; the protocol and `/cobot:learn` have the
  orchestrator quote a learner's delta verbatim, and `/cobot:spec` prints the challenger verdict
  word at hand-over, so the `learn-unknown-domain` and `medium-spec-then-challenge` regexes
  grade what the skills ask for.
- The CI workflow and the `expert-gha` template fire on every pull request, not only those
  based on `main`: a PR stacked on an unmerged branch got no run at all.
- Eval cases: fixtures moved from the unknown `scaffold_script` frontmatter key to `case.yaml`
  and `fixture.sh`; `gate-asks`, `learn-unknown-domain`, `medium-spec-then-challenge` and
  `tiny-no-ceremony` now list the `Bash`, `Write` or `Edit` their graders need; the learner is
  detected through the `Skill` call a forked skill records, not an `Agent` call. README names the
  full command with `--allow-tools Bash Write Edit`.

- The brief's hard cap could overshoot its limit by one character.
- A backslash line continuation split a command into two segments, so `git push \` followed by
  `--force` on the next line only asked. A `#` inside a word (`nix develop .#dev`) no longer
  truncates the command.

### Security

- Runner expansion ignored a `cd` in the same command: `cd sub && make deploy` read the root
  Makefile, so a harmless root `deploy` hid `sub/Makefile`'s `git push` and the gate stayed
  silent. The gate now follows `cd` and `pushd` through the command and resolves each `make`,
  `mise` and `npm`/`pnpm`/`yarn`/`bun` script in every directory it may run in (a `cd` may fail,
  so only the `&&` chain it leads is taken to run in its target), a substitution body and a
  runner's own commands included. A computed or unknown target (`cd $(…)`, `cd "$X"`, `cd -`,
  `~`), a `popd`, a `cd` in a pipeline, in the background, behind a wrapper or in a string, a
  loop around one, and a script that may redefine `cd` (a function, `alias`, `CDPATH`, `set -P`)
  keep the later runners opaque, so they ask; so do `uv run --directory` and `mise exec -C`. A
  recipe now starts in its physical `make -C` folder, so a nested make there resolves instead of
  asking. A bash oracle checks that every runner bash ran sits in a directory the gate followed.
- Gate bypasses in the shell parsing, silent before and now judged: a line cut at `<<`
  (`cat <<EOF > f; git push --force`), an unquoted here-document body's `$(…)`, a delimiter with
  quotes in it (`<<E"O"F`), a quote inside a comment hiding the next line, redirections before
  or inside a command (`</dev/null terraform apply`, `cargo 2>/dev/null publish`), reserved words
  at a segment head (`!`, `{`, `do`, `then`, `else`, `function f {`, `coproc`), wrapper options
  (`time -p`, `command -p`, `exec -a`, `rtk proxy`, `--` and combined flags such as
  `exec -la x`; an option the gate does not know leaves the wrapper opaque), a backslash-newline
  inside a word (`git pu\` ⏎ `sh --force`), and `trap '…'` (now opaque).
- Brace and glob expansion is judged by what bash runs (`.agent/specs/gate-expansion.md`); silent
  before: `cargo {publish,}`, `{terraform,} apply` and `git push origin {main,--force}` are
  denied (braces are expanded exactly, up to 256 words, as bash does); `cargo publis?` or
  `cargo publi[s]h` with a file named `publish` asks (a glob in the command word or verb zone is
  a hole, like a substitution); `cat ~/.claude/settings.js?`, its bracket, `**` and upper-case
  forms ask as protected files; `uv run --with * publish`, which runs `cargo publish` when files
  `aa` and `cargo` exist, asks. Extended globs (`+(…)`, `!(…)`), a word mixing braces and
  brackets and code inside a bracket ask as unparseable. Under the consultant and learner, a
  glob counts for their read lists only when anchored (`ls plugins/*/agents`, `src/*`,
  `--include=*.py`); a bare one (`ls *.py`, `find *`, `git log *`) asks, since a file named `-c`
  or `-delete` would become an option, and the reason says to write `./*.py`; both agent prompts
  say so. `ls *.py`, `git add src/*`, `mkdir -p src/{a,b}`, `gh api …?state=all`, `uv run pytest
  tests/test_*.py`, `files=(*.py)` and npm scripts holding globs stay silent; a glob in an
  interpreter's, a name-resolved runner's (`npm test -- src/*`, `make show X=*`) or `npm exec`'s
  argv asks, and so does one after a builtin that evaluates names (`let x=*`, `unset *`,
  `printf -v *`: a file named `a[$(…)]` would run). An independent review also closed, in the
  same paths: a runner body's redirection target with quotes or braces (`bash -c 'echo x >
  {~/.claude/settings.json,}'`), a brace whose `$'…'` or nested quote looked unclosed and was
  read as literal, `gh api … -X=DELETE` (now read as `-X DELETE`), and `unset 'a[$(id)]'`.
  A substitution only in a leading assignment no longer hides the command after it
  (`x=$(true) bash -c 'git push --force'` is denied, `x=$(true) make deploy` resolves the
  target).
- The read-only agents' read lists no longer cover a write or a run
  (`.agent/specs/gate-findings.md`, F-21, F-24, decision 28 amended). These were silent for the
  consultant and the learner and now ask, naming the cause: `find . -delete` (and `-exec`,
  `-ok`, `-fprint`, `-fls`), `rg --pre=./x`, `fd -x`, `sort -o` and `--compress-program`
  (abbreviations such as `--o` too), `uniq a b`, `tree -o`, `yq -i`, `git log|show|diff
  --output`, `git branch -D` or a new branch name, `zizmor --fix`, `trivy -o`, `gitleaks -r`,
  `pip-audit --fix`, `npm audit … fix`, `semgrep --autofix`, `go env -w`, `go list -toolexec`,
  `terraform providers lock`, `helm template --output-dir`, `kustomize build -o`, and `git
  --config-env`, `cargo --config` and `docker --config`. A command, or a runner body it expands,
  that redirects into a file (`cat a > b`, a make recipe holding one) asks too; `/dev/null` and
  descriptor duplications (`2>&1`) stay silent. `curl` keeps its read list only with read
  options (`-s`, `-S`, `-L`, `-f`, `-I`, `-H`, `-w` without `%output`, `-X GET` …): uploads,
  data, file writes and `-K` ask. `cargo audit` and `cargo deny check` leave the read lists,
  since a repository's `.cargo/config.toml` alias shadows them; `cargo-audit audit` and
  `cargo-deny check` stay.
- An option before the verb no longer hides it (F-24): `cargo +nightly publish`, `cargo --locked
  publish`, `cargo -vv publish`, `npm --registry x publish`, `pnpm -r publish`, `uv --directory x
  publish` and `rustup run nightly cargo publish` are denied, and a runner behind such an option
  asks (`uv -q run cargo publish`, `pnpm -C x exec …`, `npm --prefix x test`). Each place the
  verb could start past an option the gate does not know is read by `never` and `ask` rows;
  allows keep the canonical form.
- `${…}` with an operator word and locale strings are judged (F-22, F-23): `cargo ${x:-publish}`
  asks and `kubectl get pods ${x:---kubeconfig=./evil}` asks for the agents (the default word is
  text bash splits and globs); `cargo $"publish"` and `terraform {$"apply",}` are denied (the
  untranslated text), as `cargo publish` is.
- The same branch's independent bypass review closed, for the agents: a word boundary on read
  rows (`cat*` no longer covers `catatonit`, `git diff*` no longer `git difftool -x`, `fd*` no
  longer `fdisk`), `rg --hostname-bin`, `cargo-deny check -g`, `cargo-audit audit --db`, a
  `uniq` operand that is a glob, `git branch --list --no-list foo`, `rustup run <path>` and
  `cargo +<path>` (a toolchain path puts its `bin/` first), and `npm --cache|--userconfig`,
  `pnpm --env-file|-C`, `uv --config-file|--directory`, `cargo -C` before a read verb. On the
  main thread: `rustup run nightly -- cargo publish`, `npm publ` (npm takes unique prefixes and
  aliases), `pnpm recursive publish` are denied, and `git -c alias.p=… p` asks. An argument
  after a verb is no longer read as a verb (`uv -q run publish.py` asks as a runner, never a
  deny).
- Read-list commands whose program the repository's files choose are silent for the consultant
  and the learner only in a trusted repository (`.agent/specs/gate-repo-config.md`, F-25):
  `cargo --version`, `rustc --version`, `cargo tree`, `cargo metadata`, `cargo-audit audit` and
  `cargo-deny check` (a `rust-toolchain.toml` with `path =` made `cargo --version` run the
  repository's own binary; `.cargo/config.toml`'s `build.rustc-wrapper`), `npm audit` and `pnpm
  audit` (an `.npmrc` registry received an environment token), `trivy` (`trivy.yaml`) and
  `docker build --check` (the Dockerfile's `# syntax=` frontend). Trusted means every remote
  owner is an identity (a listed root commit counts only alone, with no remote: a fork shares its
  upstream's root), not foreign mode, no such file above the repository, and each deciding file
  matching its blob at origin's default branch, so a checked-out pull request that changes one
  asks. `docker build`'s context and `-f` must stay inside the working directory. Resolving
  asks in every repository: `pip-audit -r` or a project path (it builds source-only
  dependencies) unless `--no-deps` and `--disable-pip`, `uv audit` without `--frozen`,
  `terraform|tofu providers schema`, `docker build --builder`, a `BUILDKIT_SYNTAX` build argument
  or a Dockerfile on stdin, and `trivy --config`. The branch's bypass review also closed:
  `pnpm audit` runs `.pnpmfile.cjs` (it now needs `--ignore-pnpmfile`), `pip-audit` imports a
  `pip` planted in the working directory, a stranger's submodule was trusted through its
  superproject, docker options and git contexts that moved the Dockerfile read, a cargo config
  naming its wrapper by path, `--registry` and `--userconfig` on the audits, and a blobless
  clone's lazy fetch from inside the hook. Every git call cobot makes turns the repository's
  `core.fsmonitor`, lazy fetches, prompts and replace refs off. `cargo --version` is silent on
  the read list again.
- CI holds no Anthropic API key: the eval job and the weekly knowledge refresh authenticate by
  workload identity federation (`scripts/anthropic-federation.sh`): a named pipe mints a fresh
  GitHub OIDC token for each read, since Anthropic accepts a token's `jti` once and Claude Code
  reads the file for every exchange (a timer-refreshed file failed `jti_reused` mid-run), and
  each is exchanged for a short-lived Anthropic token under a Console rule
  pinned to the environment's immutable subject and `refs/heads/main`. The identifiers are
  environment variables; `github-settings.sh` prints the rules and the `gh variable set`
  commands instead of a `gh secret set` for a key. Proven by a manual spike (exchange, one
  session, Claude Code 2.1.322), now removed; both jobs move to Claude Code 2.1.322.
- Every MCP tool asks unless it is a read or one of the desktop app's UI tools. The gate asked on
  seven write verbs only, so Google's Cloud MCP servers' `deploy_service_from_image`,
  `start_instance`, `stop_instance`, `reset_instance`, `set_instance_machine_type`,
  `apply_k8s_manifest`, `patch_k8s_resource`, `cancel_operation`, `write_text` and
  `undelete_role`, and `run_in_terminal`, `javascript_tool` and `set_setting`, passed silently. A
  read is judged by name (`list`, `get`, `describe`, `search` or `read` first, no write word
  joined to it as in `get_or_create`); an owner or project `ask` outranks it. Browser servers,
  `fetch` and context7's `resolve-library-id` now ask until the owner adds
  `allow mcp__<server>__*`; `update_plan`, which asked on every call, is silent.
- Google Cloud MCP servers registered as `gcp-*` lose their known write tools: 23 default `never`
  rules refuse them by first verb (`create_`, `update_`, `delete_`, `apply_`, `deploy_`,
  `cancel_`, `set_`, `publish` and the rest, `execute_sql` exactly, since `execute_sql_readonly`
  is a read), and an owner `allow mcp__gcp-<server>__*` cannot lift them. A tool with another
  first word that is not a read still asks; none runs silently. A personal project with
  no organisation cannot hold the IAM deny policy that would refuse them server-side (the
  gcp-platform spike, 2026-11-11). `cobot-rules sync` lists a glob inside an MCP name as not
  expressible instead of writing it into settings; a trailing `__*` is still written.

## [0.1.0] - 2026-11-06

Release 1: the governed orchestrator, dogfood-ready through `install.sh --dev` and `--project`.

### Added

- Rules engine: rule files in three layers (`rules/default.rules`, `~/.claude/partner.rules`,
  `.agent/partner.rules`), argv normalisation (wrappers, prefix commands, global options,
  combined flags, `+refspec`, `gh api` methods, heredocs), opaque runners, Edit/Write/MCP rules,
  shell access to protected files, agent scopes, `show`, `check`, `explain`, `sync`.
- Read-only command lists for `consultant` and `learner` (agent-scoped allows in the default layer).
- `partner-memory`: `init` (committed or foreign mode, identity and trusted-root enrolment),
  `trust`, `check`, `brief` (capped, prioritised), `journal add`, `findings add|list|close`,
  `learn` (filtered, de-duplicated, secret-scanned, 80-line cap).
- `partner-session` and the SessionStart hook: protocol, rule counts and the brief, ≤ 10 000 chars,
  only for trusted repositories.
- Agents: `consultant`, `builder`, `rust-builder`, `go-builder` (and `challenger` from 0.0.1).
- Workflow skills: `onboard`, `spec` (+ template), `build`, `wrap`, `rules`.
- Knowledge skills, verified upstream on 2026-11-06: `lang-rust`, `lang-go`, `lang-terraform`,
  `lang-fallback`, `expert-gha`; consult skill `consult-gha`.
- Evals (four cases), `scripts/check-plugin.py` contract check, `scripts/spike-r1.sh`,
  `release.yml`, manual eval job in CI.

### Changed

- Precedence written down: `never` (any layer) > `allow` (owner layer, or agent-scoped default) >
  `ask` > silence; the project layer tightens only.
- The gate log records tool, decision and the first 120 characters only.

## [0.0.1] - 2026-11-06

Release 0: repository bootstrap, nothing written outside this repository.

### Added

- Marketplace `agentic-partner` and plugin `partner` manifests.
- `partner:challenger` agent (read-only, fresh context, red-team verdicts).
- Rules gate: `hooks/gate.sh` shim that blocks on any failure and `bin/partner-rules` with the
  built-in `git push` (ask) and force-push (deny) rules, `rtk`-aware.
- `install.sh` with `--dev`, `--project`, `--local`, `--user`, `--check`, `--uninstall`.
- CI: ruff, shellcheck, plugin validation, pytest with an 85 % coverage gate, markdownlint, zizmor.
- Design v1.1, ADR-0001 to ADR-0003, switch plan, crissp review.
