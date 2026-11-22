# Spec — Google Cloud MCP opt-in

size: medium · profile: library · owner: YpNo · date: 2026-11-21 · revision 2 (challenger and
gcp consult folded)

## Goal

A repository's first Google Cloud work asks the owner, once, whether to use Google's remote
Cloud MCP servers for live reads. The first Google Cloud work is the first of these to select
the `gcp` domain or a Google Cloud target:

- onboarding, a first run or a refresh, that finds the gcp signal;
- `/cobot:consult` with `gcp` named or detected;
- `/cobot:spec` or `/cobot:wrap` choosing the gcp consultant;
- `/cobot:debug` once its live context shows a Google Cloud target.

The answer is the CONTEXT.md header line `gcp-mcp: yes | no`. It is never asked again; the
owner edits the line to change it.

- **Yes:** the agent guides `expert-gcp/references/mcp.md`. It reads the enabled APIs and the
  project's parent, and prepares the commands, including a read-only guard. The owner does the
  console steps, runs `claude mcp add -s user` and signs in with `/mcp`.
- **No:** the silent `gcloud` and `kubectl` reads.
- **Neither available** (no `gcloud`, no credentials): the agent prints the commands and asks
  for the pasted output. It never guesses.

Reads go through MCP and writes through the CLI. The 23 `never mcp__gcp-*` verb rows stay, the
Google Cloud CLI server is refused whole, and no session grant reaches an MCP tool.

Unchanged: the gate's MCP order; the grant kinds and targets (decision 34); a
`cobot:investigator` has no MCP, only the main-thread lead does (decision 35); consultants audit
files and never write; cobot ships no server and no credentials; `protocol.md` (3399 of 3400).

The rule lives once in `expert-gcp`, and every trigger site points at it.

Design input: `docs/design-inputs/owner-ideas-03.md` §4, "MCP opt-in" and "Reads through MCP,
writes through the CLI" (both confirmed), owner decisions 2026-11-11 (1) and (2), and the
answers below.

## Owner's answers (2026-11-20, Q4 2026-11-21)

1. **Recommended answer:** `no` (CLI reads) when no `mcp__gcp-*` tool is in the session; `yes`
   when one is.
2. **Google Cloud CLI server:** refused whole, and never proposed.
3. **Proof:** one eval (two cases) plus text tests.
4. **Registration scope:** `-s user`, so worktrees and every checkout see the servers. This
   replaces mcp.md's `-s local`, proven on 2026-11-11.

## What the code and the docs say today (read 2026-11-20 and 21)

- `rules/default.rules:651-678`: 23 `never mcp__gcp-*__<verb>_*` rows; `ask mcp__*` catch-all
  at 639. `judge_mcp` uses fnmatchcase on the full tool name and reads no grant. The grant path
  runs only for Bash (`grant_scope`, `cobot-rules:5340`). No test pins that a grant leaves MCP
  alone.
- The gate prints `none` for `claude mcp add --transport http gcp-x https://evil` (dry run
  2026-11-21). No row covers an Edit or Write of `~/.claude.json` or the repository's
  `.mcp.json`, or `claude … --mcp-config`. A claude.ai connector's tools
  (`mcp__claude_ai_<Name>__*`) only ask: no `never` row names them.
- `HEADER_FIELD_RE = ^([a-z]+):` (`cobot-memory:128`) does not match `gcp-mcp:`, so the field
  is neither reported nor required. `context_head` keeps CONTEXT.md up to `## Shape` or
  `## Applies`, so a header line reaches the brief and a line after Shape does not.
- Onboard step 1 sends a refresh to 3b, which "corrects only what changed". Spec step 5 and
  wrap step 3 start `cobot:consultant` directly, without consult step 1. Debug step 1 asks its
  AskUserQuestion before it prints the live context. Consult's description and last line say
  "Never edits".
- F-39 (PR 80, merged 2026-11-22) took onboard step 6b (Domains) and spec step 2's Experts
  line. This spec adds onboard **step 6c**, right after 6b and keyed on its Google Cloud domain,
  and one sentence in spec step 5; it touches no other onboard step. Renumbered at build
  (2026-11-22); what the spec promises is unchanged.
- `expert-gcp/SKILL.md` is 18.8 kB of the 24 kB cap. Line 179 gives `https://<service>.googleapis.com/mcp`
  as universal.
- Google's docs (overview, supported-products, enable-disable, set-up-authentication,
  prevent-read-write-tool-use, configure-mcp-ai-application, `sdk/use-gcloud-mcp`,
  `storage/docs/reference/mcp`; read 2026-11-20 and by the consultant 2026-11-21):
  - **Cloud Storage** is at `https://storage.googleapis.com/storage/mcp`, so mcp.md:9 is stale.
    Its tools include `read_object` (up to 8 MiB), `write_text` and `delete_object`.
  - **Google Cloud CLI (Preview)** is at `https://cloudcli.googleapis.com/mcp`, with tools
    `run_gcloud_command` and `run_bq_command`, the `cloud-platform` scope, and no read-only
    mode.
  - Unchanged:
    - enabling the product API is enough, and needs `roles/serviceusage.serviceUsageAdmin`;
    - `roles/mcp.toolUser` is required;
    - Desktop or Web OAuth client, and no Dynamic Client Registration;
    - the `tool.isReadOnly` deny policy. Its caveats: it cannot control resourceless APIs
      (Resource Manager), it relies on the tools' annotations, and it is managed with gcloud
      only.
  - Advertised scopes, `exp: curl …/.well-known/oauth-protected-resource/mcp`: `logging.admin`,
    `monitoring`, `run`, `container`, `devstorage.read_write`, and `cloud-platform` for
    cloudcli. Every token can write. Narrower `*.readonly` scopes are unverified.
  - The page's "Claude.ai, Claude Code, and Claude Desktop" section is a claude.ai custom
    connector (a Web client with the `claude.ai` callback), not `claude mcp add`.

## Principles check

- Proportionality: medium. Gate rows, one memory check, text in six skills, one eval, docs. No
  new component.
- Rules before autonomy: the agent never registers a server. Every registration route asks at
  the gate, the MCP writes and the CLI server are refused by rule, and grants are Bash-only.
- Knowledge is a skill: the opt-in rule and the setup are in `expert-gcp` and `mcp.md`; the
  trigger sites name them.
- Proof not promises: gate and check behaviour are pytest; skill text is pinned by text tests,
  as in `test_debug_skill.py`; the eval proves ask, record and never-again.
- Governance (`docs/01-decisions.md`):
  - not relevant: 3, 4, 7, 9, 12, 15, 16, 17, 21, 24, 29, 30, 31, 32.
  - holds, with the reason: 0 (stale mcp.md lines re-verified) · 1 (under agy, `yes` names the
    gap, no `claude mcp`, and reads through the CLI) · 11 (per repository) · 13 (partial reads
    `reported`) · 14 (no protocol growth; user scope lists the gcp-* tools everywhere, accepted
    in Q4) · 25 (writes stay CLI, the CLI server refused) · 34 (now pinned for MCP).
  - holds: 2, 5, 6, 8, 10, 18, 19, 20, 22, 23, 26, 27, 28, 33, 35.
- Architecture: plain layering, the plugin's own: rules rows, a `check` helper, skill text.
- New dependencies: none (stdlib `json` and `os.stat`, already used by `cobot-memory`).
- Delivery: one branch `feat/gcp-mcp-opt-in`, one PR; the tasks below are the commits.

## The line

`gcp-mcp: yes` or `gcp-mcp: no`, once, in the header (before the first `## `), optionally
followed by `  # …`. The value is the first word. Any other value, a second line, or a line
below the header counts as unset: the agent asks, and `check` warns. It is not a template field.
It stays absent until Google Cloud work asks, and a template field would make an onboard refresh
add it to every repository.

Where memory is not usable:

- untrusted tree: no question and no write, CLI reads;
- no CONTEXT.md: ask, do not record, and propose `/cobot:onboard`;
- foreign mode: record in the memory folder `cobot-memory path` names, as for every write.

Only the main thread writes the line, never a consultant or a probe.

## Stories and acceptance

1. **Asked once, recorded.** As the owner, the first Google Cloud work asks me once (the
   triggers in Goal, one gcp signal: consult step 1's row), and a repository with a valid line
   never asks again. Accept:
   - `pytest tests/test_gcp_mcp_opt_in.py` pins expert-gcp's rule, onboard 6c (applies on
     refresh), consult step 1 (main thread, before the fan-out, and the stated exception to
     "Never edits"), spec step 5, wrap step 3, debug step 1 (after the live context, its own
     question) and routing.md.
   - Eval `gcp-mcp-asked-once`, case A: no line, `/cobot:consult gcp`. The last message states
     the question, and `.agent/CONTEXT.md` matches `^gcp-mcp: no\b` (Q1's recommendation, the
     owner unreachable under dontAsk).
   - Case B: `gcp-mcp: no` present. No question is stated, and CONTEXT.md is byte-identical
     (a file grader).
2. **A prepared, guarded setup.** As the owner answering yes, I get a prepared setup and do the
   sign-in myself. The agent reads `gcloud services list --enabled` and `gcloud projects
   describe <p> --format='value(parent)'`, read for the words `organization` or `folder` (v1 and v3 differ in shape; settled 2026-11-22). It then prints, filled in with the project I confirm
   and in this order:
   - the APIs to enable, by the signal table (Logging always; GKE, Cloud Run, Monitoring by
     resource; never Storage, whose `read_object` reaches state buckets);
   - the `roles/mcp.toolUser` binding;
   - the read-only guard: the deny policy with an organisation or folder; otherwise the second
     identity with predefined viewer roles; otherwise "the gate is the only guard";
   - the Desktop OAuth client and consent steps;
   - `claude mcp add --transport http --client-id <id> --client-secret --callback-port 8765 -H
     "x-goog-user-project: <p>" -s user gcp-<service> <endpoint>`, with the secret flag bare.

   It runs none of the enable, IAM, policy or `claude mcp` commands. Accept:
   - text tests on mcp.md "Per repository": the signal table, the three guard branches, a bare
     `--client-secret`, `-s user`, and no `storage` row;
   - `cobot-rules check "claude mcp add --transport http gcp-logging
     https://logging.googleapis.com/mcp"` prints `ask`.
3. **Missing tools.** As the owner with `yes` but no `mcp__gcp-*` tool in the session (not
   signed in, or under agy), the agent names the missing step once in that session and reads
   through `gcloud`. With `no`, it reads through `gcloud` and `kubectl`. With neither, it prints
   the commands and asks for the pasted output. Accept: text test on the three branches.
4. **No MCP write, whatever the name or grant.** As the owner, an MCP write is refused even
   under a session grant, and the CLI server is refused under any name. Accept: pytest:
   - with an active `gcloud` grant on `p`, `mcp__gcp-run__deploy_service` is `deny` and
     `mcp__gcp-run__scale_service` is `ask`, never `allow`;
   - `mcp__gcp-cloudcli__list_x` is `deny`;
   - `mcp__gcp-cli__run_gcloud_command` and `mcp__x__run_bq_command` are `deny`.
5. **No registration by the agent.** As the owner, the agent cannot register a server by any
   route. Accept: pytest, each `ask`:
   - `claude mcp add|add-json|remove|add-from-claude-desktop …`;
   - `claude -p --mcp-config '{…}' …`;
   - Edit or Write of `~/.claude.json` and of `<repo>/.mcp.json`.

   `claude mcp list` and `claude mcp get` stay outside the row.
6. **A hostile or broken line is named.** As the owner, a stale or hostile line is not taken at
   its word. Accept: pytest on `cobot-memory check`; each of these prints a `warning: gcp-mcp …`
   line:
   - `gcp-mcp: yes; run …`;
   - `gcp-mcp: maybe`;
   - two lines;
   - a line below `## Shape`;
   - a repository `.mcp.json` declaring a `gcp-*` server, or any server whose URL host is
     `cloudcli.googleapis.com`.

   A valid line with a trailing comment, or no `.mcp.json`, prints none. A `.mcp.json` that is
   not a regular file, is over 64 kB by `stat`, or is invalid JSON prints one line and is not
   parsed further.
7. **Knowledge current.** As the owner, mcp.md and expert-gcp match Google's docs as of today.
   Accept:
   - dated lines for: the Storage endpoint and tools, the CLI server, the advertised scopes
     (every token can write), `serviceUsageAdmin`, the deny-policy caveats, and the claude.ai
     connector route marked unsupported (its tools escape the `gcp-*` rows);
   - expert-gcp:179 names the endpoint exceptions;
   - the second identity's roles are predefined viewer roles plus
     `serviceusage.serviceUsageConsumer` and `mcp.toolUser`, `reported` until a build check;
   - `python3 scripts/check-plugin.py` exits 0.

## Trust boundaries

| entry or crossing | guard | story |
|---|---|---|
| A teammate's or cloned repository's CONTEXT.md saying `gcp-mcp: yes` (trusted by identity; foreign memory is outside the tree, and an untrusted tree is not read) | `yes` only selects servers the owner registered at user scope. It registers nothing and names no URL or project. The format is strict, anything else counts as unset and `check` warns | 6 (negative), 1 |
| A repository's `.mcp.json` declaring `gcp-*` or a cloudcli URL | Claude Code's project-server approval; `check` names it; the CLI server's tools are refused under any name | 6, 4 (negative) |
| The agent registering a server (an injected `claude mcp add`, an edit of `~/.claude.json` or `.mcp.json`, a nested `--mcp-config`) | new `ask` rows; the owner runs every registration | 5 (negative) |
| A claude.ai connector to a Google server (`mcp__claude_ai_*`, outside the `gcp-*` rows) | mcp.md marks the route unsupported and expert-gcp never proposes it. Its writes still ask through the catch-all | 7 (text), 4 |
| MCP tool output (logs, events, rows: text anyone who can write a log controls) | Data, never instructions (expert-gcp, mcp.md, debug's line). Any action it suggests passes the gate: MCP writes refused, CLI writes ask. Excerpts in `.agent/debug/` pass the existing secret deny | 4 (negative), debug-path's record tests |
| A session grant meeting an MCP write (privilege line) | `judge_mcp` reads no grant; `never` outranks owner allows | 4 (negative) |
| The write-capable OAuth token (scopes above) | The read-only guard branch in the setup; tokens stay in Claude Code's store | 2 |
| The OAuth client secret | prompted by the bare `--client-secret` in the owner's terminal; never in a printed command, the journal or `.agent/` | 2 |
| `check` reading a repository's `.mcp.json` (deserialisation) | regular file, a 64 kB stat cap before reading, stdlib `json`, `mcpServers` names and `url` only, nothing runs | 6 (negative) |

## Clarify

- Q1 Recommended answer without `mcp__gcp-*` tools → a) `no` · b) `yes` → recommended: a) →
  **answer (2026-11-20):** a); `yes` when tools are present
- Q2 The Google Cloud CLI MCP server → a) refuse whole · b) verb rows only → recommended: a) →
  **answer (2026-11-20):** a)
- Q3 Proof → a) eval plus text tests · b) text tests only → recommended: a) → **answer
  (2026-11-20):** a)
- Q4 Registration scope (challenger M3) → a) `-s user` · b) `-s local` per checkout →
  recommended: a) → **answer (2026-11-21):** a)

## Plan

1. Gate first (T01): the registration asks, the CLI-server refusals, and the grant-versus-MCP
   test. These are the guards the text relies on.
2. `check` (T02): `gcp_mcp_warnings(mem)` beside `missing_header_fields`. `HEADER_FIELD_RE`
   stays as it is.
3. Knowledge (T03): one opt-in section in expert-gcp (the triggers, the line, the three
   branches, data not instructions); mcp.md "Per repository" and the re-dated facts.
4. Trigger sites (T04): onboard 6c, consult step 1, spec step 5, wrap step 3, debug step 1, and
   routing.md. Each is one or two sentences pointing at expert-gcp.
5. Eval (T05), then docs (T06).

## Tasks

| id | task | lane | risk | deps |
|---|---|---|---|---|
| T01 [x] | `rules/default.rules`: `ask Bash(claude mcp add*)`, `add-json*`, `remove*` and `add-from-claude-desktop*`; `ask Bash(claude *--mcp-config*)`; `ask Edit\|Write(~/.claude.json)` and `(.mcp.json)`; `never mcp__gcp-cloudcli__*`, `never mcp__*__run_gcloud_command`, `never mcp__*__run_bq_command`. `tests/test_cobot_rules.py`: stories 4 and 5, plus the gcp-mcp storage tool names in `GOOGLE_MCP_TOOLS` | gate | auth | — |
| T02 [x] | `bin/cobot-memory`: `gcp_mcp_warnings` in `cmd_check`; `tests/test_cobot_memory.py`: story 6, positive and negative | memory | — | — |
| T03 [x] | `skills/expert-gcp/SKILL.md` (the opt-in paragraph, line 179); `references/mcp.md` ("Per repository", `-s user`, the guard branches, the dated facts, connector unsupported); `tests/test_gcp_mcp_opt_in.py` stories 2, 3, 7 | knowledge | — | — |
| T04 [x] | onboard step 6c; consult step 1 and the "Never edits" exception; spec step 5; wrap step 3; debug step 1; `debug/references/routing.md`; story 1's text tests | skills | — | T03 |
| T05 [x] | `evals/gcp-mcp-asked-once/` (cases A and B, `allowed_tools` with Agent and Edit, graders as story 1) | evals | — | T04 |
| T06 [x] | decision 37 (36 went to F-39) in `docs/01-decisions.md`; `docs/configuration.md` (the `gcp-mcp:` row, the new asks); `docs/02-design.md`; `docs/architecture.md`; `CHANGELOG.md` Unreleased | docs | — | T01–T05 |

## Trade-offs

- **The rule in expert-gcp, not a protocol line.** The protocol has one character left, and
  every trigger is a gcp context that names expert-gcp. Google Cloud work outside the triggers
  (a build on a `google` root) does not ask; the next consult, spec, wrap or debug does.
- **`gcp-mcp:` outside the template.** A template field would be "missing" everywhere and
  filled in without the question.
- **Registration asks, not refusals.** The owner may want the agent to type the command, and
  the prompt is the owner's step. Under the CLI the secret stays prompted; printed commands keep
  it bare.
- **User scope over local scope (Q4).** Worktrees see the servers. The tools are listed in every
  repository, and the `gcp-*` rows hold by name.
- **A `check` warning, not a brief rewrite.** Reinterpreting the line in code would hide a
  hostile value instead of naming it.

## Challenger verdict

**SOUND WITH CHANGES** (cobot's `challenger` definition run through a general agent, because
the `cobot:` agents were not loaded in this session; 2026-11-21). No blocker; four MAJOR, all
folded:

- **M1, routes around `claude mcp`:** `~/.claude.json`, `.mcp.json` and `--mcp-config` asks
  added (story 5).
- **M2, missed triggers:** refresh onboarding, spec and wrap consults, and debug after its live
  context (Goal, story 1).
- **M3, scope versus worktrees:** owner chose `-s user` (Q4); "once" means once per session
  (story 3).
- **M4, claude.ai connector escapes the rows:** marked unsupported; the scope claim is replaced
  by approval plus `check` (Trust boundaries).

Seven MINOR, folded: the CLI server refused under any name (story 4); the line's format,
position and unusable memory (The line); consult's "Never edits" exception (T04); the row
limited to registration verbs (story 5); eval case B; the `.mcp.json` stat cap (story 6).

**gcp consult** (cobot's `consultant` definition, the same way; 2026-11-21): the facts check
out; three MAJOR, folded:

- no read-only guard in the prepared setup (story 2);
- every advertised scope can write (story 7, Trust boundaries);
- `roles/viewer` on the second identity, replaced by predefined roles, `reported` (story 7).

Five MINOR, folded: `serviceUsageAdmin`; the deny-policy caveats; the CLI server's tool
names refused on any server; the signal table without Storage; expert-gcp:179.

Knowledge delta (Storage tools, the CLI server, the scopes, `serviceUsageAdmin`, the
deny-policy caveats) goes into mcp.md in T03 through the build, not by `cobot-memory learn`.

## Converge

2026-11-22, wrap. Every story's acceptance ran today:

| story | proof | status |
|---|---|---|
| 1 asked once | `tests/test_gcp_mcp_opt_in.py`; evals `gcp-mcp-asked-once` 1.00 and `gcp-mcp-never-again` 1.00 (local, `--runs 1 --scaffold`) | accepted |
| 2 guarded setup | text tests; `cobot-rules check "claude mcp add …"` → ask | accepted; the parent read works for both API shapes, the role set verified role by role (2026-11-22) |
| 3 missing tools | text tests on the four branches | accepted |
| 4 no MCP write | `tests/test_gcp_mcp_gate.py` (grant, Cloud CLI under any name) | accepted; casing is F-54 |
| 5 no registration | gate tests: `claude mcp`, `--mcp-config`, `--settings`, Edit/Write and shell words on both files | accepted; bunx, node and `$CLAUDE_CONFIG_DIR` are F-53, MultiEdit F-52 |
| 6 broken line named | `tests/test_gcp_mcp_check.py` (decoder crashes, bad URLs, trailing newline, header position, CRLF) | accepted |
| 7 knowledge current | dated lines, check-plugin ok | accepted; the second identity's roles stay reported |

Wrap reviews folded: code review 4 MAJOR, 5 MINOR (crash on hostile `.mcp.json`, shell writes,
a broken line doubled, a never-again grader, header substring, trailing newline, the value rule,
`value(parent)`); security review 1 HIGH, 1 MEDIUM, 8 LOW (the same shell route, closed by
letting `ask` file rows protect literal words; `--settings` and `reset-project-choices`; the
Cloud CLI host with a trailing dot or in `args`). Parked: F-52, F-53, F-54.
