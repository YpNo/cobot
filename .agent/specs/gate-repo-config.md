# Spec — read-list tools that load repository configuration (finding F-25)

size: small-medium · profile: library · owner: YpNo · date: 2026-11-14 · revision 2 (challenger pass folded) · built on
`chore/journal-compact` `c4d4b13` (gate-findings merged as PR 41)

## Goal

Some commands on the `@consultant` and `@learner` read lists run a program that the repository
chooses. They do this through files in the working directory, not through anything the command
shows. Measured 2026-11-14 with bash 5.2.37, cargo 1.99.0, rustup 1.29.2 and mise:

| command (agent scope) | what the repository controls | today | after, untrusted or foreign | after, trusted |
|---|---|---|---|---|
| `cargo --version` · `rustc --version` | `rust-toolchain.toml` `path = "<dir>"`: rustup runs `<dir>/bin/cargo` (checked: the planted binary ran when `RUSTUP_TOOLCHAIN` was unset) | silent | ask | silent |
| `cargo tree` · `cargo metadata` | the same, plus `.cargo/config.toml` `build.rustc-wrapper` (cargo asks rustc for target info) | silent | ask | silent |
| `cargo-audit audit` · `cargo-deny check` | both call cargo (`generate-lockfile`, `metadata`) through the proxy | silent | ask | silent |
| `docker build --check …` | the Dockerfile's `# syntax=` line names the frontend image BuildKit runs | silent | ask | silent |
| `trivy fs\|config\|image …` | `trivy.yaml` in the working directory (it can set `output`, modules) | silent | ask | silent |
| `npm audit` · `pnpm audit` | `.npmrc` (`pnpm-workspace.yaml`): a registry the repository picks gets an environment token (checked: `Bearer` from `${PROBE_SECRET}`) | silent | ask | silent |
| `pip-audit -r req.txt` · `pip-audit .` | resolving builds source-only dependencies and runs their `setup.py` | silent | ask | ask |
| `uv audit` | locking runs the project's build backend (checked, uv 0.12.23, `backend-path=["."]`) | silent | ask | ask, unless `--frozen` |
| `terraform providers schema` · `tofu providers schema` | a provider binary committed under `.terraform/` whose hash the lock file matches (checked, terraform 1.16.2) | silent | ask | ask |
| `docker build --check --build-arg BUILDKIT_SYNTAX=<image>` · `--builder` · `-f -` | the agent picks the frontend image or the Dockerfile | silent | ask | ask |

These stay silent everywhere: `pip-audit`, `pip-audit --no-deps --disable-pip -r req.txt`,
`pip-audit -f json`, and every other read-list row.

The owner's decision (2026-11-14, relayed by the gate-substitution session): the rows that load
repository configuration stay on the read lists but are silent only in a **trusted** repository.
`pip-audit` that resolves requirements asks everywhere. The main thread does not change.

Checked and out of scope: mise shims refuse an untrusted repository's `.tool-versions` and
`mise.toml` (`mise ERROR … are not trusted`). Parked as **F-26**: a repository delivered with its
`.git/config` (an archive, not a clone). Its `diff.external` and `core.fsmonitor` ran a program
on `git diff` and `git status` (checked). Every git read on the read lists is exposed.

## Principles check

- Proportionality: small-medium. One gate rule fed by the existing trust check; holds.
- Rules before autonomy: fails closed. No trust answer (git missing, a timeout, no remote) means
  untrusted; holds.
- Proof not promises: a row per table line, and a gate test against real temporary repositories;
  holds.
- Governance (`docs/01-decisions.md`): 28 amended again (trust-gated rows); 6 and 20 hold; the
  others are not relevant.
- Architecture: plain layering. The trust check moves from `cobot-memory` to `_cobot_common.py`,
  so the gate and memory share one function.
- New dependencies: none.
- Delivery: one branch `security/gate-repo-config`, one PR; tasks below are the commits.

## The model

**Trust at hook time.** `_cobot_common.repo_trust(cwd) -> (trusted, reason)` is
`Memory.trust` moved, and `Memory.trust` calls it. The gate uses a **stricter** form
(`gate_trust`): only the identity rule counts (every remote owner listed in `identities`). The
root-commit rule counts only with no remote and exactly one root commit, which is listed. A
fork shares its upstream's root, and so does a merge of unrelated histories (challenger,
reproduced), so a listed root alone cannot let a stranger's toolchain run. This also skips `rev-list`
over the whole history whenever a remote exists. It reads what it reads today and never scans
the tree: whether `.agent` is a symlink, `git remote -v`, `git rev-list --max-parents=0 HEAD`,
and `~/.claude/cobot/identities` and `trusted`. `_cobot_common.git` now passes `-c
core.fsmonitor=false -c core.untrackedCache=false` on every call. The gate's trust adds **foreign
mode**: a repository whose `.agent` is a symlink is third-party code, so the gate reads it as
untrusted even though memory trusts it. The gate asks the question once per hook call, lazily,
only when a segment meets a trust-gated row. The answer is for the hook's `cwd`. An agent's `cd`
asks already through `ask Bash(*)`, and a segment a runner expanded (`origin` set) is never
trust-gated silent. **Parents above the repository:** rustup, cargo and npm also read
`rust-toolchain`, `rust-toolchain.toml`, `.cargo/config`, `.cargo/config.toml` and `.npmrc` in
every parent directory. One of them between the filesystem root and the repository's top level
makes the gate untrusted (challenger, reproduced with a trusted repository inside an untrusted
directory). The user's own `$CARGO_HOME` (default `~/.cargo`) and `~/.npmrc` are left out. Only
`stat` is used, nothing is read.

**Trust-gated rows.** `TRUST_GATED` maps a guard key to the file that decides what runs:
`cargo --version`, `cargo tree`, `cargo metadata`, `rustc --version`, `cargo-audit audit` and
`cargo-deny check` (`rust-toolchain.toml` / `.cargo/config.toml`), `docker build` (the
Dockerfile's `# syntax=`), `trivy` (`trivy.yaml`), and `npm audit` and `pnpm audit` (`.npmrc`,
`pnpm-workspace.yaml`). An agent-scoped allow counts on such a
segment only when the repository is trusted. Otherwise the ask names the cause: `cargo tree
loads the repository's rust-toolchain.toml and .cargo/config.toml; the repository is not trusted
(<reason>)`. In a trusted repository, `docker build` still asks when its context or `-f` is not
a relative path inside the working directory. That covers an absolute path, `..`, `~`, `-` (a
Dockerfile on stdin), a URL, or a hole. `trivy -c|--config` is guarded everywhere: the config
file would be the agent's choice. Guarded everywhere for the same reason: `docker build
--build-arg BUILDKIT_SYNTAX…` and `--builder`, a Dockerfile on stdin (`-f -`, `-f-`,
`--file=-`), `terraform|tofu providers schema` (it starts the provider binaries), and `uv audit`
without `--frozen` (locking builds the project).

**`pip-audit`.** `READ_GUARDS["pip-audit"]` becomes a parser. It asks when `-r|--requirement`
(any abbreviation) or a project-path operand appears, unless both `--no-deps` and
`--disable-pip` are given. The `--fix` and `-o|--output` guards stay. Values of `-f --format -s
--vulnerability-service --cache-dir --progress-spinner --timeout --path --index-url
--extra-index-url --ignore-vuln -o --output` are not operands, and `--desc` and `--aliases`
take `on|off|auto` (pip-audit README, read 2026-11-14). argparse forms count: `-rreq.txt`,
`-vr req.txt` (a cluster ending in `r`), `--requirem=req.txt`. pip-audit, docker and trivy are
not installed here, so their rows follow their documentation and are unit-tested only.

## Stories and acceptance

1. As the owner, an untrusted or foreign repository cannot pick the program behind a read.
   Accept: each trust-gated row of *Goal* asks for both agents in an untrusted temporary
   repository and in a foreign-mode one, and is silent in a trusted one (remote owner in
   `identities`). A runner-expanded `cargo tree` asks even when trusted. `docker build --check
   /abs`, `../x`, `-f -` and a URL ask when trusted. A fork with a listed root but a stranger's
   remote is untrusted. A trusted repository inside a directory holding a `rust-toolchain.toml`
   is untrusted. `npm audit` asks when untrusted (`pytest -k trust`).
2. As the owner, resolving never builds code silently. Accept: the `pip-audit`, `uv audit`,
   `terraform providers schema` and docker frontend rows of *Goal* (`-k "pip_audit or
   resolves"`).
3. As a maintainer, trust reads no tree. Accept: every `_cobot_common.git` call carries
   `NO_FSMONITOR` (a unit test of the argv: no trust-path command reads the index, so a planted
   program could not prove it); the existing `test_cobot_memory.py` trust tests pass unchanged;
   the gate's trust tests run with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and a
   temporary `XDG_DATA_HOME` and `CLAUDE_CONFIG_DIR`.
4. As the owner, the full gate passes: the verified commands of `.agent/CONTEXT.md`.

## Clarify

None: the owner decided the behaviour (*Goal*). These were decided here and are recorded:
foreign mode is untrusted for the gate; a git failure means untrusted; the main thread is
unchanged; `cargo --version` and `rustc --version` are included (a `rust-toolchain.toml` path,
measured above).

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 | `_cobot_common.py`: `repo_trust`, git without fsmonitor; `cobot-memory` delegates; tests | common | trust boundary | — |
| T02 | `cobot-rules`: `TRUST_GATED`, lazy trust per hook call, docker context check, trivy `--config`; tests with temporary repositories; conftest trust fixture | gate | trust boundary | T01 |
| T03 | `cobot-rules`: the pip-audit parser; rows | gate | trust boundary | — |
| T04 | docs, CHANGELOG, decision 28, F-25 closed, F-26 parked | docs | — | T02, T03 |
| T05 | bypass review folds | gate | trust boundary | T04 |

## Trade-offs

- Trust gating over removal: the consultant audits the owner's repositories with these tools,
  and in those repositories the files are the owner's own.
- Foreign mode counts as untrusted: memory trusts it because the memory sits outside the tree,
  but the tree is someone else's code.
- Trust of the hook's `cwd`, not of each path a command names: the files that decide what runs
  (toolchain file, cargo config, `trivy.yaml`) are read from the working directory, except the
  Dockerfile, which gets the path check.

## Challenger verdict

2026-11-14, challenger: **UNSOUND** (rethink). Folded: BLOCKER root-commit trust (the gate uses
the identity rule only); BLOCKER `uv audit` builds the project (asks unless `--frozen`); MAJOR
`terraform providers schema`, `npm audit` and `.npmrc`, config files in parent directories,
docker `BUILDKIT_SYNTAX`, `--builder` and stdin; MINOR the fsmonitor test (now an argv test),
`rev-list` cost (skipped with a remote), pip-audit forms and test isolation. Put to the owner:
MAJOR a pull request checked out in the owner's repository (`gh pr checkout`) keeps the
repository trusted while its `.cargo/config.toml` is the contributor's. **Owner's answer:**
pending.

## Converge

pending
