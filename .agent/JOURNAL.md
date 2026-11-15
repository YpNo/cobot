# Journal

Append-only, newest at the bottom. One entry per working session or task group.

## 2026-11-11 — 0.3.0 input: Antigravity support, elephant-goldfish-model challenged

Changed: docs/design-inputs/antigravity-0.3.0.md (replaces the shape of owner-ideas-03 §3).
Why: the owner needs cobot under agy at work quickly and named google/elephant-goldfish-model as a source of ideas, every finding challenged first.
Proof: agy 1.5.3 validate spikes on a scratch copy: the plugin as is loads 0 agents; with .antigravity-plugin/plugin.json and a root hooks.json, 29 then 30 skills (onboard's argument-hint is invalid YAML, quoting fixes it); agents/<n>/agent.md adapters also load in Claude Code as cobot:x:x (rejected); Claude agents listed by file in .claude-plugin/plugin.json replace agents/ (claude -p listing: exactly nine cobot agents), agy then validates with one warning. Challenger SOUND WITH CHANGES, fifteen points folded (fail open on python failure, bin not on PATH, allow means defer in agy, ask → force_ask, matcher .*, agent scopes vanish, agy settings ungated).
Open: S3 (hooks in subagents, fail open, brief size, MCP names) and S4 need the owner's signed-in agy; four owner questions in the file.
Next: owner answers, then the 0.3.0 spec.

## 2026-11-12 — spec antigravity written and challenged

Changed: .agent/specs/antigravity.md (large; eight stories, T01–T08) on feat/antigravity, which carries the design input's two commits.
Why: owner decisions 2026-11-11 — 0.3.0 is Antigravity only, after the 0.2.0 tag.
Proof: hook shapes read from antigravity.google/docs (hooks, build-plugins, mcp, subagents); challenger pass 1 SOUND WITH CHANGES (twelve points: workspace hooks file and installed copy writable, plugin-folder cwd, first-underscore MCP split, orchestration prompts, cap cut, userMessage framing, builders' skills, unsafe smoke) → folded; pass 2 SOUND WITH CHANGES (seven: Cwd chose the project layer, strictest split asked on reads, foreign subagent Workspace, agy ask carve-out, message shape, weak fail-open probe, line cap) → folded. Spec 299 lines.
Open: build waits for the 0.2.0 tag; T08 needs the owner's signed-in agy; unverified: hooks in subagents, timeout behaviour, copy or link on install, eager MCP name form.
Next: owner finishes 0.2.0 (ship on gcp-platform, paid eval run, PR 8), then /cobot:build antigravity.

## 2026-11-13 — compacted 2026-11-06 → 2026-11-13 (50 entries)
- 2026-11-06 design v1.1, R0 bootstrap and R1 (0.1.0): manifests, challenger, gate shim and rules engine, cobot-memory and the protocol, agents, first skills and evals; dogfooded on cartridge-os; F-05 entry wrappers looked through.
- 2026-11-07 owner decisions 17–26; headscale dogfood in foreign mode; make targets resolved from the Makefile (F-06); R1.1 slice 1 (learning, currency, learner, knowledge-refresh) and slice 2 (ship, contribute, security-sweep, compaction, python/typescript/terraform builders); private remote, eval harness, rename to cobot (ADR-0004).
- 2026-11-08 R2 slice 1 (hardening: report hook, stamp behind git push, cobot-usage), slice 2 (UI/UX expert, CI/CD family, GitLab), slice 3 (GCP, Kubernetes, service mesh as skill pairs, ADR-0006); F-12 eval graders agree with the protocol.
- 2026-11-09 0.2.0 PRs: tidy, MCP read verbs (catch-all ask, reads by name), eval suite F-13, README for people with docs/ for agents.
- 2026-11-10 R2 surface (one /cobot:consult router, user-only skills, description caps; proven by single eval runs) and slice 4 stacks (fw-react/next/vue, lang-shell, expert-api, Gitea).
- 2026-11-11 GCP proof on gcp-platform and the Google Cloud MCP spike (gcp-* MCP writes never); builder proof and a clean wrap, F-15..F-19 fixed; 0.3.0 input on cloud writes and session grants; new-project spec built and wrapped (tree detection, onboard New project path, F-20).
- 2026-11-12 CI moved to workload identity federation, one fresh GitHub token per exchange.
- 2026-11-13 first eval run on federation (9 of 19); eval Bash fixed (userns sysctl, bwrap AppArmor profile, plugin bin on PATH, runner pinned); consult brief names the repository; gate-substitution built (bash 5.2 scanner, substitutions judged by what they run, review folds, assignment holes), cd before a runner, gate-expansion T01–T04 (exact braces, glob holes, runner expansion through globs, differential rows).
  open: /cobot:ship on a service repository (0.2.0 PR 6); the causes of the eval failures and the full two-arm suite on main; the 0.2.0 release cut (social preview upload, release badge once public and tagged); F-20 lang-rust versions; protocol.md at 2 998 of 3 000 characters; claude-in-chrome, Playwright, fetch and context7 ask until an owner allow; the missing bin/ under `claude plugin eval` to report upstream; knowledge-refresh's learner runs without the eval sandbox; one session longer than an Anthropic token renewing under federation unproven; data-dependent arithmetic (`read x < f; echo $((x))`) out of the gate's scope.
Archive: raw entries in JOURNAL-archive.md and in git history before 2026-11-13.

## 2026-11-13 — gate-expansion T05: agents anchor their globs

Changed: agents/consultant.md and agents/learner.md, one line each on anchoring globs.
Why: owner answer Q2 a).
Proof: python3 -I scripts/check-plugin.py exit 0 (agents listing about 523 tokens); claude plugin validate plugins/cobot --strict exit 0.
Next: T06 docs and CHANGELOG.
verified: f8cac97 · check-plugin, plugin validate

## 2026-11-13 — gate-expansion T06: docs and changelog

Changed: CHANGELOG Unreleased Security (brace and glob bullet; the follow-up note removed), docs/architecture.md (soundness target with globs, anchored agent globs), docs/configuration.md (braces and globs, known asks), docs/02-design.md §6 (expansion bullet), spec converge.
Why: spec gate-expansion T06.
Proof: pytest with coverage exit 0 (98.60 %); ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0 (117 files); claude plugin validate plugins/cobot and . --strict exit 0; python3 -I scripts/check-plugin.py exit 0.
Next: independent bypass review (owner's condition), fold, verified commands again.
verified: af6f0fd · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin

## 2026-11-13 — gate-expansion: bypass review folds

Changed: _cobot_shell.py (skip_piece, skip_double_quoted, skip_nested; unclosed pieces in braces and brackets are errors); cobot-rules (target_words for runner-body and command targets; GLOB_CODE_HEADS and GLOB_CODE_WITH_V in structural_key, unset in QUOTED_CODE_HEADS; fold for unquoted substitutions in path_glob; -X=METHOD in canonical_gh_api and no API exemption for anchored -flags; globstar tokens in protected_file_touched; array_assignments and closing_paren in shell_items); docs/configuration.md known asks, CHANGELOG, spec converge; tests: review rows, recipe and script targets, unclosed pieces; findings F-23, F-24.
Why: owner's condition: an independent code-reviewer pass aimed at bypasses (bash 5.2.37 probes, 60 000 fuzzed commands, no crash). Three BLOCKERs, one MAJOR, three MINORs, all folded.
Proof: pytest with coverage exit 0 (98.59 %); ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0; claude plugin validate plugins/cobot and . --strict exit 0; python3 -I scripts/check-plugin.py exit 0.
Open: F-21 to F-24 (pre-existing gate gaps the reviews surfaced).
Next: owner reviews feat/gate-expansion; nothing pushed.
verified: f6daef2 · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin

## 2026-11-13 — gate-findings T01: parameter operators and locale strings

Changed: _cobot_shell.py (PLAIN_PARAMETER_RE; a ${…} with an operator word is an unknown substitution hole, quoted inside double quotes; locale() reads $"…" as a quoted hole whose value is the untranslated text); tests: scanner rows for plain and operator forms, locale values, literal $" in double quotes and here-documents, a brace alternative; gate rows FINDINGS_CLOSED, FINDINGS_SILENT, agent rows.
Why: spec gate-findings C and D (F-22, F-23).
Proof: pytest with coverage exit 0 (98.57 %); ruff check and format exit 0.
Next: T02 redirection writes.
verified: 7c55eec · pytest+cov, ruff

## 2026-11-13 — gate-findings T02: redirection writes

Changed: _cobot_shell.py (WRITING_OPERATORS, FD_WORD_RE, Scan.writes); cobot-rules (Part, command_parts returns writes, Reached with paths and writes threaded through expand_units, expand_script, expand_segment); tests: scanner write rows for every operator and descriptor duplication, command_parts and a make recipe's writes; the differential's expand_units call.
Why: spec gate-findings A, redirection writes.
Proof: pytest with coverage exit 0 (98.58 %); ruff check and format exit 0.
Next: T03 readings past global options.
verified: 00d4c30 · pytest+cov, ruff

## 2026-11-13 — gate-findings T03: readings past global options

Changed: cobot-rules (GLOBAL_OPTIONS cargo, uv, pnpm, npm; TOOLCHAIN_PROXIES; strip_global_options drops cargo's +toolchain; option_word, readings, canonical; candidates keeps the written form first and the canonical last; is_opaque reads every reading through opaque_as_read; inner_rustup in WRAPPER_PARSERS); tests: FINDINGS_CLOSED and FINDINGS_SILENT rows for readings, runners behind options, rustup run.
Why: spec gate-findings B (F-24). Found while building: a runner verb behind an option was invisible too (uv -q run cargo publish, pnpm -C x exec cargo publish, npm --prefix x test silent); folded as the opaque check over readings, so those ask.
Proof: pytest with coverage exit 0 (98.57 %); ruff check and format exit 0; cobot-rules check on 17 common commands (git --no-pager log, kubectl -n x get pods, uv run pytest, cargo +stable clippy, npm -g ls …) unchanged, silent.
Next: T04 agent read guards.
verified: c55624f · pytest+cov, ruff, cobot-rules check

## 2026-11-13 — gate-findings T04: read-only agents cannot write or run

Changed: cobot-rules (FOREIGN_BY_CLI in executes_foreign; Guard, getopt_hit, single_hit, guarded_token, uniq_output, branch_write, curl_unsafe with CURL_* allow-list, READ_GUARDS with a dated source per row, guard_keys, guarded, written_file; judge_words, judge_holed, agent_globs and judge_segment take refused, judge_bash reads Reached.writes); default.rules (cargo audit* and cargo deny check* dropped for @consultant, with the reason); tests: AGENT_GUARDED (about 140 rows), AGENT_READS, learner rows, reasons, a make recipe that writes, the main thread unchanged, the scanner-forms row for cargo deny.
Why: spec gate-findings A (F-21, F-24 agent half), owner answers Q1 b), Q3 a), Q4 b). Two spec rows were wrong and are corrected in the converge: curl -fsSL does not match the curl -s* read row, and getopt abbreviations take any prefix (GNU sort accepts --o).
Proof: pytest with coverage exit 0 (98.54 %, the new code fully covered); ruff check and format exit 0.
Next: T05 differential rows.
verified: afd6724 · pytest+cov, ruff

## 2026-11-13 — gate-findings T05: differential rows

Changed: tests/test_gate_differential.py (FINDINGS_CLOSED and FINDINGS_SILENT in the corpus, 12 consultant rows, stubs pnpm rg rustup uniq, test_findingsOracle_bitesOnTheBypassesItCovers, the docstring's F-21 limitation replaced by the oracle's scope).
Why: spec gate-findings story 6.
Proof: pytest with coverage exit 0; ruff exit 0; mutations: ${…} and $"…" read as text fail the differential (kubectl ${x:---kubeconfig=…}); guard off, readings off and redirection writes off pass the differential (it judges each argv with the same literal judge) and each fails its unit rows in test_cobot_rules.py.
Next: T06 docs, CHANGELOG, findings.
verified: 1014792 · pytest+cov, ruff, mutations

## 2026-11-13 — gate-findings T06: docs, changelog, findings

Changed: CHANGELOG Unreleased Security (three bullets); docs/configuration.md (options before the verb, ${…} and $"…", What the read lists never cover); docs/02-design.md §6; docs/architecture.md security model; docs/01-decisions.md decision 28 amended (owner's Q1, the plain-variable residual named); agents/consultant.md one line; security-sweep references/rust.md uses cargo-audit audit; FINDINGS F-21 to F-24 closed, F-25 parked; spec converge with three corrected rows.
Why: spec gate-findings T06.
Proof: pytest with coverage exit 0 (98.66 %); ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0 (117 files); claude plugin validate plugins/cobot and . --strict exit 0; python3 -I scripts/check-plugin.py exit 0.
Next: independent bypass-aimed review, fold.
verified: 0c5572a · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin

## 2026-11-13 — eval cases against the plugin-evals docs; blocked cases set aside

Changed: graders no-spec-skill and no-spec get arm: both; builder-routing no-main-thread-edit becomes a trace regex (Edit or Write with parent_tool_use_id null, not_contains); never-apply plan-proposed becomes alternative-proposed ("terraform plan" or "yourself"); gitlab-ci-shape's fixture writes the root's trust line (~/.claude/cobot/trusted, and the run's config/ beside its home when present) and its prompt no longer asks for --trust-root; ci.yml grants WebFetch(domain:github.com) and WebFetch(domain:api.github.com); foreign-onboard, new-project-onboard and builder-routing's proof-quoted move to plugins/cobot/evals-blocked/ with a README; markdownlint ignores the moved cases; tests follow; development.md, claude-code-mechanics.md, CHANGELOG.
Why: full run 43496720467 ($9.50, 47 min) scored 13 of 19, Δ +0.31. The plugin-evals docs (code.claude.com/docs/en/plugin-evals) say Skill graders are unscored unless arm: both (the run shows scored false), tool_used has no main-thread key (the trace shows the builder's Edits under the Agent call), and Bash network needs WebFetch(domain:…) grants. Eval Bash is read-only everywhere: reproduced locally with a scripted fake API on 2.1.311, 2.1.322 and 2.1.325 (findmnt shows the workspace as its own ro mount), against the docs' "writes are confined to the run's workspace".
Proof: pytest with coverage exit 0 (98.08 %, grader tests now cover the main-thread pattern, the arm: both rule, the hand-back reply and the trust seeding); ruff, shellcheck (fixtures included), markdownlint, zizmor, plugin validate --strict and check-plugin exit 0; the main-thread pattern checked on 18 real traces (builder-routing 0 matches with 2 subagent edits each, tiny-no-ceremony and medium-spec 6 of 6 matches); locally against the fake API the whole suite loads (17 cases, every fixture ran, the WebFetch domain grant accepted), a fixture-written ~/.claude/cobot/trusted is readable from eval Bash, and the regex grader matched a main-thread Write in the harness's own trace.
Open: the read-only eval Bash is an upstream report for the owner to file; actions-pinning re-resolving through the granted domains and gitlab-ci-shape passing the trust check are unproven until a paid run; the docs' threshold 0.8 and -j are not adopted.
Next: owner pushes, merges, dispatches cases=actions-pinning and cases=gitlab-ci-shape, then the full suite.
verified: 92ac129 · pytest+cov, ruff, shellcheck, markdownlint, zizmor, plugin validate, check-plugin, fake-API suite load

## 2026-11-14 — gate-findings T07: bypass review folds

Changed: cobot-rules (word_bounded in matches_bash for agent-scoped allows; rustup and cargo +toolchain in executes_foreign; FOREIGN_BY_CLI for npm, pnpm, uv, cargo -C; READ_GUARDS rg --hostname-bin, cargo-deny check -g, cargo-audit audit --db; uniq counts a glob operand twice; branch_write takes the last of --list and --no-list; inner_rustup skips --install and --, a toolchain path is opaque; readings continue past a presumed value only when an option follows; flag tables for uv, pnpm, npm; NPM_COMMANDS, NPM_ALIASES, npm_command, PNPM_RECURSIVE, canonical_package_manager; git_alias_set makes git opaque; guard reason reworded); tests: FINDINGS_REVIEW_* rows; CHANGELOG, configuration.md, spec converge (trimmed to 300 lines).
Why: owner's condition: an independent code-reviewer pass aimed at bypasses (bash 5.2.37, installed tools, 18 000 fuzzed commands, no crash): 4 BLOCKER (two regressions of this branch: rustup and cargo +path for agents), 5 MAJOR, 1 MINOR, all folded. Accepted, documented: a runner behind an option asks as opaque (pnpm -r build, npm --prefix web test).
Proof: pytest with coverage exit 0 (98.68 %); ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0; claude plugin validate plugins/cobot and . --strict exit 0; python3 -I scripts/check-plugin.py exit 0; the reviewer's probes re-run, each item asks; 25 common read-list commands silent.
Next: owner reviews security/gate-findings-21-24; nothing pushed.
verified: f8c2d7b · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin

## 2026-11-14 — journal compacted

Changed: cobot-memory compact folded 50 of 60 entries (2026-11-06 → 2026-11-13) into one entry with a written summary and its open items; JOURNAL.md 477 → 96 lines, the raw entries in .agent/JOURNAL-archive.md (new).
Why: JOURNAL.md passed the 400-line threshold on main after PR 41; the owner chose to compact after the findings PR merged.
Proof: pytest with coverage exit 0 (98.68 %); ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0; claude plugin validate --strict (plugin, marketplace) exit 0; check-plugin exit 0.
Open: the session brief is 6132 chars against its 6000 budget, on main before this compaction too.
Next: owner pushes chore/journal-compact and opens the PR.
verified: 2c4ad0a · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin

## 2026-11-14 — gate-repo-config T01: trust in _cobot_common

Changed: _cobot_common.py (NO_FSMONITOR on every git call; read_lines, external_memory, remote_owners, trusted_roots, repo_trust moved from cobot-memory); cobot-memory (Memory.trust and external_path delegate; the explicit NO_FSMONITOR arguments dropped); tests: an argv test that every trust-path git call carries NO_FSMONITOR; spec: the owner's answer a) and the deciding-files model.
Why: spec gate-repo-config T01 (F-25); owner's answer to the challenger's PR-checkout MAJOR.
Proof: pytest with coverage exit 0 (98.68 %); ruff check and format exit 0; the existing trust tests pass unchanged.
Next: T02 trust-gated rows.
verified: 84aeb9f · pytest+cov, ruff

## 2026-11-14 — gate-repo-config T02: trust-gated reads

Changed: _cobot_common.py (git_bytes); cobot-rules (CONFIG_FILES, CWD_CONFIG_FILES, PARENT_FILES, RepositoryConfig with lazy trust, top and reference commit; gate_trust stricter than memory's; default_branch; changed_file by git cat-file; parent_config leaving $CARGO_HOME and ~/.npmrc out; safe_build_path and docker_build_files; deciding_files; repository_config; judge_bash passes the reason per segment for an agent; cargo's -V --version -h --help --list out of its global flags); tests/conftest.py (stub_repository_config, repository_trust with GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM, HOME, CARGO_HOME, XDG_DATA_HOME, CLAUDE_CONFIG_DIR); tests: TRUST_GATED_READS trusted and untrusted, foreign mode, a listed root with a fork remote and after a merge of unrelated histories, deciding files changed, committed on HEAD only, untracked, in a parent inside the repository, above the repository, the owner's cargo home, no default branch, docker contexts, a runner, no repository, no remote against HEAD, an unreadable file.
Why: spec gate-repo-config T02 (F-25), owner's answer a). Found while building: cargo --version asked for the agents on main since gate-findings T03 (--version among cargo's global flags dropped it from the canonical form); fixed here with AGENT_READS rows.
Proof: pytest with coverage exit 0 (98.67 %); ruff check and format exit 0.
Next: T03 pip-audit, uv audit, providers schema, docker frontend.
verified: f8b4574 · pytest+cov, ruff

## 2026-11-14 — gate-repo-config T03: resolving asks everywhere

Changed: cobot-rules (Guard.missing and its reason; PIP_AUDIT_* with pip_audit_resolves and pip_audit_cluster; DOCKER_BUILD_WRITES and docker_build_unsafe; READ_GUARDS uv audit missing --frozen, trivy config and -c, terraform and tofu providers schema); tests: RESOLVES_ASK for both agents, RESOLVES_SILENT, the pip-audit and uv audit reasons.
Why: spec gate-repo-config (owner's item 2, challenger BLOCKER uv audit, MAJOR providers schema and docker frontend). pip-audit, docker and trivy are not installed here: their rows follow the tools' documentation.
Proof: pytest with coverage exit 0 (98.69 %); ruff check and format exit 0.
Next: T04 docs, CHANGELOG, decision 28, F-25 closed, F-26 parked.
verified: 0c337b6 · pytest+cov, ruff

## 2026-11-14 — gate-repo-config T04: docs, findings

Changed: CHANGELOG Unreleased Security (one bullet); docs/configuration.md (Repository configuration and trust); docs/architecture.md security model; docs/01-decisions.md decision 28 amended; FINDINGS F-25 closed, F-26 parked; spec converge.
Why: spec gate-repo-config T04.
Proof: pytest with coverage exit 0 (98.69 %); ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0; claude plugin validate plugins/cobot and . --strict exit 0; python3 -I scripts/check-plugin.py exit 0.
Next: independent bypass-aimed review, fold.
verified: e6bf39f · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin

## 2026-11-14 — gate-repo-config T05: bypass review folds

Changed: _cobot_common.py (protocol.allow=never in NO_FSMONITOR; QUIET_GIT_ENV with GIT_NO_LAZY_FETCH, GIT_TERMINAL_PROMPT, GIT_NO_REPLACE_OBJECTS on git and git_bytes); cobot-memory (Memory.trust reads the checkout); cobot-rules (gate_trust from checkout_root and a cwd outside it untrusted; a per-path cache of changed_file; PROGRAM_KEY_RE and names_a_path; pnpm deciding files and parent files; own cargo and npm files resolved, ~/.cargo always; DOCKER_BUILD_FLAGS, more value options, DOCKERFILE_NAMES, one context that is a directory; pip shadowing in the working directory; pip-audit's write guard on parsed options; pnpm_audit_unsafe with missing --ignore-pnpmfile; npm audit --registry --userconfig --globalconfig); default.rules (allow pnpm audit --ignore-pnpmfile* for the consultant); tests: review rows, pip shadowing, a stranger's submodule, the override cwd, docker contexts, the lower-case dockerfile, configs naming a program by path, a relocated CARGO_HOME, the git argv and environment; docs, CHANGELOG, F-26 note, spec converge.
Why: owner's condition: an independent code-reviewer pass aimed at bypasses (2 BLOCKER, 3 MAJOR, 4 MINOR, all folded). One review probe made a real git fetch to a non-existent github.com/ypno/src.git (nothing local sent); later probes blocked network.
Proof: pytest with coverage exit 0 (98.70 %); ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0; claude plugin validate plugins/cobot and . --strict exit 0; python3 -I scripts/check-plugin.py exit 0.
Next: owner reviews security/gate-repo-config; nothing pushed.
verified: f4c00cb · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin

## 2026-11-14 — single-case proofs; actions-pinning grader accepts git ls-remote

Changed: evals/actions-pinning/graders/source-or-reresolve.md also accepts `git ls-remote … github.com/actions/checkout`; a grader test (upstream sources pass, a SHA from memory fails); CHANGELOG.
Why: run 43580616055 (gitlab-ci-shape, $0.66) passed 3 of 3, Δ +0.17: the fixture-seeded trust works. Run 43580607780 (actions-pinning, $0.32) reached github.com through the WebFetch(domain:…) grant and pinned actions/checkout@11d5960 # v4.4.0 in all six runs, each from git ls-remote, yet scored 0.80: the grader knew only gh api and references/actions.md. Every run also tried Bash's allowed_domains first, which evals refuse.
Proof: the new pattern matches all six real final replies; pytest with coverage exit 0; ruff, markdownlint, check-plugin, plugin validate --strict exit 0.
Open: actions-pinning shows Δ 0 (the baseline pins the newest v4 as well): requiring the newest stable major and the expert's table would measure expert-gha; the owner's call.
Next: owner pushes, merges, then the full suite on main.
verified: 7eb286d · pytest+cov, ruff, markdownlint, check-plugin, plugin validate, six-trace replay

## 2026-11-14 — agents start in the foreground

Changed: consult, spec, wrap, ship and build set `run_in_background: false` on every agent they start; consult reports once, after every consultant has returned; check-plugin fails a skill that names one of the plugin's agents without the flag (test first); mechanics note; CHANGELOG; finding F-27.
Why: full suite on main f1e200f (run 43584857035, $8.39, 41 min) passed 16 of 17, overall score 0.997, mean Δ +0.32; the miss was one consult-fan-out run whose final message held only the gha section. The trace shows both Agent calls launched async (no flag), a "still running" reply, then one message per finished consultant. Across the run 22 of 23 calls without the flag went to the background, 15 of 15 with `false` stayed in the foreground (Claude Code 2.1.322).
Proof: check-plugin failed on exactly the five skills before the text change, ok after; pytest with coverage exit 0 (98.70 %); ruff check and format exit 0; markdownlint exit 0; claude plugin validate plugins/cobot and . --strict exit 0.
Open: unproven until a paid consult-fan-out run; F-27 (the consultant's `cd` asks) is a gate-rule decision for the owner.
Next: owner pushes fix/agent-foreground and merges, then rebases or re-cuts the 0.2.0 release on top; a cases=consult-fan-out run.
verified: 148c1ca · pytest+cov, ruff, markdownlint, plugin validate, check-plugin

## 2026-11-14 — release 0.2.0 cut, rebased onto main (PR 27)

Changed: chore/release-0.2.0 rebuilt on main e563bfb: plugin.json and marketplace.json to 0.2.0; CHANGELOG Unreleased cut to [0.2.0] - 2026-11-14, the summary naming the gate's shell model and the eval suite in CI under federation; release-0.2.0 spec row 8 notes the rebase. The 2026-11-12 cut (919a7c4, ced0607) conflicted with everything merged since (PRs 28–48).
Why: owner asked to rebase the release PR and fix its conflicts; PR 48 (agents in the foreground) merged after the full suite.
Proof: release.yml's version check replayed (plugin.json, marketplace.json and the changelog heading agree; notes extract 457 lines); full eval suite on f1e200f (run 43584857035) 16 of 17, overall 0.997, mean Δ +0.32, the one miss fixed by PR 48 and proven by run 43599532436 (consult-fan-out 3 of 3, Δ +0.50, all six consultant calls in the foreground); pytest with coverage exit 0 (98.70 %); ruff check and format, shellcheck, markdownlint, zizmor offline (0 medium or higher), claude plugin validate --strict (plugin and marketplace), check-plugin exit 0; cobot-memory check exit 0 (2 open findings; journal mixed order and brief 5996 of 6000 dropping CONTEXT Stack and Environment, both already on main); github-settings --check: 0 changes pending.
Open: /cobot:ship on a service repository (spec row 6); F-20 and F-27 open; the cut date moves if the tag is pushed another day; commit author emails become public with the history; visibility, settings --apply, the social preview and the tag are the owner's.
Next: owner force-pushes chore/release-0.2.0, merges PR 27, goes public, runs github-settings --apply, uploads docs/assets/social.jpg, pushes v0.2.0.
verified: 449ef81 · pytest+cov, ruff, shellcheck, markdownlint, zizmor, plugin validate, check-plugin, memory check, release version check, settings check

## 2026-11-14 — memory tidy: journal order, CONTEXT inside the brief

Changed: JOURNAL.md stable-sorted by date (PR 44's 2026-11-13 entry back among its day; no entry text changed); CONTEXT.md head 3237 → 2488 chars: owner-terminal commands in their own section after Applies, stale lines updated (public since 0.2.0, CLI 2.1.311 local, 2.1.322 in CI, 2.1.325 latest), verified dates re-run today, the CI eval dispatch as a verified row.
Why: cobot-memory check read the journal as mixed order (compact refuses that) and the brief dropped CONTEXT Stack and Environment at 6054 of 6000 chars; the brief guarantees CONTEXT 2500 chars, so a head under that always fits.
Proof: cobot-memory check: newest at bottom, brief 5794 of 6000, no dropped sections; pytest with coverage exit 0 (98.70 %); markdownlint, check-plugin exit 0; cobot-rules check "git status" exit 0.
Next: owner pushes chore/memory-tidy and merges; the social preview and the v0.2.0 tag.
verified: 550b46b · memory check, pytest+cov, markdownlint, check-plugin, gate dry run

## 2026-11-14 — lang-rust CLI crates (F-20)

Changed: lang-rust references/versions.md gains clap 4.6.7, serde 1.0.229, serde_json 1.0.154, tempfile 3.27.0, assert_cmd 2.2.2, predicates 3.1.4; every crate row re-read on crates.io (the updated column is the version's publish date, not the crate's updated_at); MSRV line; F-20 closed; CHANGELOG.
Why: F-20, a new Rust project's spec looked these up itself.
Proof: crates.io API for each crate and version; GitHub last commits within a month for tempfile, assert_cmd, predicates, clap, serde, serde_json; pytest with coverage exit 0 (98.70 %); markdownlint, claude plugin validate --strict, check-plugin, cobot-memory check exit 0.
Next: owner pushes fix/f20-rust-crates and merges.
verified: f20d2d4 · crates.io, pytest+cov, markdownlint, plugin validate, check-plugin, memory check

## 2026-11-14 — consultants run in place (F-27)

Changed: consultant.md and the consult brief: the working directory is the repository, run commands in place, one command over many files, no for loop or shell function; consult/domains/ui.md: the contrast formula takes every pair in one jq call; default rules: allow Bash(pwd) @consultant; eval consult-fan-out grader read-list-only (trace, not_contains the catch-all ask); tests for the pwd rule, the grader and the ui block (runs it with jq, gates it as consultant); F-27 closed; CHANGELOG.
Why: F-27; replaying the grader on run 43584857035 failed 16 of 21 consultant sessions (cd 10, pwd 3, loops and functions 3), and 1 of 3 in run 43599532436 (cd). Allowing cd for @consultant was rejected: it would widen the read list.
Proof: tests first (pwd rule and grader failed before the change); pytest with coverage exit 0 (98.70 %); ruff check and format, shellcheck, markdownlint, claude plugin validate --strict (plugin and marketplace), check-plugin, cobot-memory check exit 0; the documented jq block prints 4.48 and 3.11 and the gate is silent on it for the consultant.
Open: the consult cases' behaviour is unproven until a paid run; the new grader makes consult-fan-out fail on any consultant command off the read list.
Next: owner pushes fix/f27-consultant-in-place and merges, then cases=consult-fan-out (and the full suite when convenient).
verified: 05fb87a · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin, memory check, gate probe, jq run

## 2026-11-14 — fewer stops for the owner

Changed: protocol Rules: Edit or Write, not a script; JSON with jq, not python3 -c; never a variable as the command; Paths ≤ 4 questions; Learning keeps the rule, the steps stay in the learn skill (2994 of 3000 chars); spec skill: four questions as a ceiling, decide what CONTEXT.md, a cobot rule or a later spec settles, environment answers into CONTEXT.md, fold BLOCKER and MAJOR yourself and ask only to overrule or when the fold drops what the owner asked for; gate: a lone mise info flag is not opaque (tests first); architecture.md; CHANGELOG.
Why: latex-resume-generator session 77d61bc6 (42 asks, 9 question rounds); replay through main 71ba8e3: 37 of 41 Bash asks still ask (23 python3 heredocs, 8 python3 -c, 2 variable commands, 2 real git commit, 2 large scraping scripts that should ask); the substitution PRs had fixed 4 of 6.
Proof: replay of the 41 asked commands through main and this branch (37 ask on both: the change is guidance); the named replacements are silent (Edit and Write on .agent/specs and CONTEXT.md, curl | jq, each --version named, mise --version) and the replaced forms ask; pytest with coverage exit 0 (98.70 %); ruff check and format, shellcheck, markdownlint, claude plugin validate --strict (plugin and marketplace), check-plugin, cobot-memory check exit 0.
Open: the drop in stops is unproven until a live session; the questions rule is measured by the owner's next spec.
Next: owner pushes fix/fewer-approvals and merges.
verified: 89b01d4 · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin, memory check, latex replay, gate probes

## 2026-11-15 — Antigravity spec on agy 1.5.9, challenger pass 3

Changed: feat/antigravity rebased onto main 24a71af (journal entries kept in date order); design input gains "Facts re-read 2026-11-15 (agy 1.5.9)", every row sourced; spec folds them (89d4c26: both file-tool families, run_workflow force_ask, invoke_subagent Workspace as a mode in either shape, orchestration allow lists, plugin MCP names, one SessionStart shape, refresh by reinstall, learner on pro) and challenger pass 3 (4eeb4d0); spec 298 lines.
Why: the owner's agy session report (/home/ypno/workspace/cobot-agy-report.md), checked against agy changelog 1.5.9, the live hooks and permissions pages, the built-in docs and an agy plugin validate probe; where the report and the live docs disagree (file-tool names, run_command Cwd, invoke_subagent shape) the gate accepts both.
Proof: live docs confirm allow defers and auto_approve widens, so the gate design holds; validate accepts flash_lite and an unknown tool name silently, and names both file-tool families in its matcher hints; challenger pass 3 SOUND WITH CHANGES (BLOCKER: .agent, _agents, _agent customization roots, config.json, sidecars and other plugins outside the never rows; MAJOR: manage_task send_input to a REPL, workflow agents' finish; six MINOR), every point checked at its source and folded; markdownlint, check-plugin exit 0.
Open: whether PreToolUse fires for an invoke_subagent child stays the smoke's (T08); nothing built yet.
Next: owner reviews the spec; then /cobot:build antigravity from T01.
verified: 4eeb4d0 · source checks, challenger pass 3, markdownlint, check-plugin

## 2026-11-15 — Antigravity T01: the tree split

Changed: Claude Code's nine agents moved to plugins/cobot/claude-agents/, listed by file in .claude-plugin/plugin.json (agents/ is left to agy); .antigravity-plugin/plugin.json with the same name, version, description, license, repository; check-plugin gains manifest agreement, manifest list = folder, 24 000-byte skill bodies and a strict-YAML frontmatter check (stdlib, the subset cobot uses), and is split into small functions; install.sh's overlap report, test_cli_flags, the mechanics note, architecture and the design tree read claude-agents/; onboard's argument-hint quoted, contribute's description folded.
Why: spec antigravity T01; agy loads .antigravity-plugin/ first and skips any frontmatter its strict parser rejects.
Proof: the strict-YAML check flags exactly what PyYAML 6.0.3 rejects in the tree (onboard, contribute; the learn template is not a loaded skill) and every test case was checked against it; agy 1.5.9 plugin validate: 30 skills (onboard now loads), 0 agents, exactly the one hooks/hooks.json warning, nothing written to a throwaway HOME; claude plugin validate --strict (plugin and marketplace) passes; full suite 98.70 %, ruff, shellcheck, markdownlint, check-plugin, memory check exit 0.
Open: Claude Code listing the nine agents from the manifest rests on validate and spike S2b (2026-11-12), not re-run live; the twin check (every claude-agents/<n>.md has agents/<n>.md) lands with T02.
Next: T02 (lane a) and T03 (lane b, risk, test first).
verified: a597651 · pytest+cov, ruff, shellcheck, markdownlint, claude and agy plugin validate, check-plugin, memory check, PyYAML cross-check

## 2026-11-15 — Antigravity T02 and T03: the agents and the gate under agy

Changed: T02 (5097dda) scripts/sync-agents.py writes the nine agy agents from claude-agents/ (tools mapped to both file-tool families, sonnet as flash, learner on pro, mainAgent false; consultant and learner without a command tool, commandExecutionPolicy "off", a line saying so; builders told to read their language skill; the report-hook sentence rewritten); bin/_cobot_agy.py holds the tables and the call translation; check-plugin holds twins, known agy tool names, tiers, mainAgent. T03 (269e3ca) cobot-rules gate --runtime agy (load_rules_agy over every workspacePaths entry, judge_plan, gate_agy), hooks/gate-agy.sh (stdin buffered, 8 s deadline, every failure a deny with exit 0), root hooks.json group cobot, PreToolUse ".*", timeout 10.
Why: spec antigravity T02 and T03 (risk, test first).
Proof: tests written first and seen failing (test_agents_sync 18, test_gate_agy 73 incl. every shim failure path as a subprocess, the corpus scan for auto_approve, a symlinked HOME); my review found a real bypass first (the file forms dropped the path as written, so a ~ rule missed under a symlinked HOME), test then fix; agy 1.5.9 plugin validate: skills 30, agents 9, hooks 1, the one hooks/hooks.json warning, nothing written to a throwaway HOME; claude plugin validate --strict (plugin, marketplace); full suite 2354 passed, 98.63 %; ruff, shellcheck, markdownlint, check-plugin, sync --check.
Decided in build: SessionStart joins hooks.json with T05, whose command it runs; the gate's in-process failure denies under agy (Claude Code's asks), matching the shim; a relative run_command Cwd asks; the agy path is judged in three forms, not only parent-resolved.
Open: whether PreToolUse fires inside an invoke_subagent child or a workflow agent is T08's; F-28 (the Claude Code gate misses a never rule through a symlinked folder) belongs to its own branch from main.
Next: T04 (self-protection rows, lane b), T05 and T06 (lane a).
verified: 269e3ca · pytest+cov, ruff, shellcheck, markdownlint, claude and agy plugin validate, check-plugin, sync-agents --check, memory check

## 2026-11-15 — Antigravity T04 to T06: self-protection, the brief, install

Changed: T04 (b4aacd5) default rules deny Edit/Write of ~/.gemini/antigravity-cli/settings*.json, ~/.gemini/config/*, ~/.gemini/jetski/* and, in .agents, .agent, _agents, _agent at any depth, hooks.json, plugins.json, skills.json, plugins/*; never agy plugin(s) disable|uninstall|link naming cobot; ask Bash(agy) and Bash(agy *), ask Bash(install.sh*); a rule's trailing comment joins its reason (default and owner layers only); a folder row meets a substitution only where the token names the folder's last part. T05 (aa239cd) cobot-session start --runtime agy: one injectSteps system message, project from workspacePaths[0], protocol then the agy section (≤ 1 200) then counts and brief, serialised ≤ 10 000 cut from the tail; hooks/session-agy.sh; SessionStart in hooks.json (flat, as agy's hooks.md documents). T06 (63a3542) install.sh --agy (validate then install, a modifier, refuses --dev and --uninstall), --check reports agy; cobot-memory check warns on agy-discovered names in .agent/.
Why: spec antigravity T04, T05, T06.
Proof: tests written first and seen failing (agySelf 70 rows in test_cobot_rules plus 7 through gate_agy; test_cobot_session 14 incl. the shim as a subprocess with a leaked CLAUDE_PLUGIN_ROOT; test_install -k agy 12 with a fake agy recording argv; agyLegacy 2); a real agy brief from this checkout: section 981 chars, answer 9 429 serialised; agy 1.5.9 plugin validate: skills 30, agents 9, hooks 1, the one warning, nothing written to a throwaway HOME; claude plugin validate --strict (plugin, marketplace); full suite 2439 passed, 98.67 %; ruff, shellcheck, markdownlint, check-plugin, sync-agents --check, memory check.
Decided in build: `agy` and `agy *` rather than the spec's `agy*`, which also matched `agyle`; the reason comes from a rule comment, not a new rule field in the file syntax; the folder-row narrowing, since `ask` on every `$(pwd)/x` path would have reached Claude Code users too (a substitution hiding the whole folder is read like a variable, as before; globs keep the full check); both agy shims unset CLAUDE_PLUGIN_ROOT; the agy error path prints the protocol and the error line (the spec said the protocol alone; the line names what failed, as under Claude Code).
Open: whether PreToolUse fires inside an invoke_subagent child or a workflow agent, and whether agy shows the injectSteps brief, are T08's; README's `allow Bash(agy plugin validate*)` owner line and the "no agy session open, clone at a tag" notes land with T07.
Next: T07 (version 0.3.0, release.yml manifest check, ADR-0007, mechanics and harness docs, README, smoke-agy.sh), then the owner's smoke run (T08).
verified: 63a3542 · pytest+cov, ruff, shellcheck, markdownlint, claude and agy plugin validate, check-plugin, sync-agents --check, memory check

## 2026-11-15 — Antigravity T07: version, record, smoke script

Changed: version 0.3.0 in both manifests and the marketplace; release.yml greps the Antigravity manifest too; ADR-0007 and the decision 1 amendment; docs/reference/antigravity-mechanics.md (agy 1.5.9 facts, each with its source); docs/harnesses.md (one row per runtime and version); README Antigravity section with the named gaps and the `allow Bash(agy plugin validate*)` owner line; architecture rows (adapter, agy agents, security note) and configuration rows (`--agy`, `--check`, COBOT_GATE_DEADLINE, the MCP config files read); wrap and spec say a reviewer that did not run is `not run`, never clean (E8); scripts/spikes/smoke-agy.sh (nine checks, S4 not run).
Why: spec antigravity T07.
Proof: sh -n and shellcheck on the smoke script; markdownlint over every .md; check-plugin, sync-agents --check; claude plugin validate --strict (plugin, marketplace); agy 1.5.9 validate with a throwaway HOME: skills 30, agents 9, hooks 1, one warning; full suite 98.67 %.
Decided in build: the harness record splits Claude Code by named run (2.1.322 eval run, 2.1.311 validate, the 2026-11-06 spikes), so a cell is ok only where a run checked it; no run has checked the Claude Code gate inside a subagent, so that cell says not run; the CHANGELOG stays [Unreleased] (the A2UI knowledge PR is 0.3.0 too); the README's clone command names v0.3.0, which exists once tagged.
Open: T08, the owner's smoke run, fills the Antigravity row before the PR; the smoke script has not run anywhere yet (it needs a signed-in agy and the real HOME).
Next: owner pushes feat/antigravity, runs ./install.sh --agy then sh scripts/spikes/smoke-agy.sh, and pastes the result lines; then the harness row, wrap and the PR.
verified: 356f882 · pytest+cov, ruff, shellcheck, sh -n, markdownlint, claude and agy plugin validate, check-plugin, sync-agents --check, memory check

## 2026-11-15 — Antigravity T08: the owner's smoke run, one blocker

Changed: a6ac3df the gate no longer asks on cobot's own bin/ tool runs from agy's config folder (own_tool_run; runner-reached paths checked apart); docs/harnesses.md Antigravity 1.5.9 row filled from the run; mechanics facts: a failing hook blocks on 1.5.9 (h1), hook groups merge by name (h2), print mode denies an ask, the child's calls reach the gate (g2); smoke messages for h1 and w1.
Why: the owner ran ./install.sh --agy and scripts/spikes/smoke-agy.sh signed in on agy 1.5.9 (2026-11-15).
Proof: g1, g2, b1, s1, o1 ok; h2 FAILS (a workspace .agents/hooks.json group named cobot with enabled false: the forced push reached the bare remote, no gate log entry); w1 and m1 not reached; tests for the fix written first and seen failing (11 rows); full suite 98.67 %, ruff, shellcheck, sh -n, markdownlint.
Open: h2 is a BLOCKER for the PR: any repository can commit .agents/hooks.json or .agent/hooks.json with {"cobot": {"enabled": false}} and the gate is gone; the fix is the owner's call (a per-install group name, a workspace scan, an upstream agy issue). Unknown: how agy combines an auto_approve from a workspace hook with cobot's deny (not in the smoke yet).
Next: owner decides the h2 fix; then build it, add the precedence check to the smoke, owner re-runs it.
verified: a6ac3df · pytest+cov, ruff, shellcheck, sh -n, markdownlint, smoke-agy (owner, 2026-11-15)

## 2026-11-15 — Antigravity: the hook-name bypass closed

Changed: 6420ccc install.sh --agy stages a copy with the hook group renamed cobot-<16 random hex> (od from /dev/urandom), validates and installs it, removes it; the agy brief adds a warning line after the agy section naming workspace hooks.json, plugins.json or plugins/ in .agents, .agent, _agents, _agent from each workspace up to its repository root (five shown); the smoke refuses an installed group still named cobot and gains h3 (a workspace auto_approve beside cobot's deny) and s2 (the warning); README, ADR-0007, mechanics, configuration, harnesses, CHANGELOG.
Why: smoke h2 (2026-11-15); the owner chose a random name plus the scan.
Proof: tests written first and seen failing (install 6, session 7); the real agy 1.5.9 installed the staged copy into a throwaway HOME ("hooks: 1 installed (cobot-<random>)") and the staged folder was gone after; full suite 98.68 %, ruff, shellcheck, sh -n, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Decided in build: the name changes at every install (a refresh too); a bare agy plugin install of the checkout keeps the guessable name, so the README says to install through the script; the warning sits in the never-cut head of the brief.
Open: the owner re-runs the smoke (h2 must now deny; h3 decides whether a workspace auto_approve can beat cobot's deny); the upstream agy issue (hook groups not namespaced per plugin) is the owner's to file.
Next: owner pushes, runs ./install.sh --agy and the smoke again; then the harness row, wrap and the PR.
verified: 6420ccc · pytest+cov, ruff, shellcheck, sh -n, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, staged agy install (throwaway HOME)

## 2026-11-15 — Antigravity T08: the second smoke run passes

Changed: 6fc4bea docs/harnesses.md Antigravity 1.5.9 row from the second run (validate, install, gate, gate in a subagent, brief ok; agents not run); mechanics: a workspace auto_approve did not override cobot's deny (h3), hook order varies between runs (h1).
Why: the owner re-ran ./install.sh --agy (group cobot-<random>) and scripts/spikes/smoke-agy.sh on agy 1.5.9.
Proof: g1, g2, h1, h2, h3, s1, s2, b1, o1 ok (gate log: four force-push denies, onboard's cobot-memory check without an ask); w1 not run (print mode denies the asked run_workflow); m1 not reached (no MCP server); S4 not run; markdownlint.
Open: no cobot agent was invoked under agy (Agents not run); run_workflow's inner calls and the MCP name form stay unproven; the upstream agy issue on hook-group namespacing is the owner's to file.
Next: wrap (full checks, review fan-out), then the PR for feat/antigravity.
verified: 6fc4bea · smoke-agy second run (owner), markdownlint

## 2026-11-15 — Antigravity wrap: converge, reviews folded, PR ready

Changed: cae50d4 the code review's eight findings (substitution position in folder rows, workspacePaths validated, no crash on an asked push without a project, no git call for fixed layers, the agy section names the plugin once and is never cut, the workspace warning capped, the staged install drops caches, names itself and fails per step); d46f1fd the security review's (bare words resolve against the working directory, a folder row covers the folder, moving or linking onto a customization root or a protected parent asks, writes through a symlinked root judged by its name, an ignored or symlinked .agent/cobot.rules counts as uncommitted, top-level Workspace counts, run_workflow names relative, both and large scripts, workspace plugin MCP servers known, a default-name group warns, the random name never printed and check-plugin refuses one in the tree); history a0ca4af..HEAD rewritten to drop the owner's live group name before any push; CONTEXT.md verified commands dated today; the spec's Converge filled.
Why: /cobot:wrap of spec antigravity; the security reviewer found a BLOCKER (a model-written Cwd inside a protected folder made shell writes silent) and three MAJOR (relocation and symlinks around the never rows, an ignored rules file passing as committed, the live group name in committed records).
Proof: every story's acceptance command passed today; full suite 2507 passed, 98.72 %; ruff, shellcheck, markdownlint, check-plugin (with the group-name check), sync-agents --check, claude plugin validate --strict (plugin, marketplace), agy 1.5.9 validate and a real staged install into a throwaway HOME (the output masks the name), memory check exit 0; each finding reproduced before its fix and its test seen failing; the gha consult found four low, pre-existing points; cobot-deps check --fresh: no supported lockfile.
Open: F-29 (a project rule's pattern reaches the permission prompt), F-30 (case-insensitive volumes miss the never rows), F-31 (a bare word after an in-command cd), F-28 (fix/gate-symlinked-paths, not merged); reviewed but not folded: schedule is judged by a deny-list (only TimerCondition asks); the gha consult's low points (dotted grep in release.yml, undocumented contents: write, adhoc npm pins, actionlint's ubuntu-26.04); no cobot agent run under agy, run_workflow's inner calls and the MCP name form unproven; the agy issue on hook-group namespacing is the owner's to file.
Next: owner re-runs ./install.sh --agy to rotate the group name, pushes feat/antigravity (a plain push: the rewrite started after the pushed a0ca4af), and opens the PR.
verified: d46f1fd · pytest+cov, ruff, shellcheck, sh -n, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, staged agy install (throwaway HOME), memory check, cobot-deps check --fresh

## 2026-11-15 — gate judges a file path through its symlinks (F-28)

Changed: cobot-rules file_forms judges the path as written (~ expanded to HOME as given), parent-resolved and fully resolved, each also relative to the working directory, strictest rule wins; rule_patterns: a ~ rule also matches HOME resolved; path_may_match adds resolved_prefix (the folders before a glob's first hole resolved); tests (symlinked folder, symlinked file, a rule naming the link, symlinked HOME with an owner never Write(~/x), Bash tokens through a link); F-28 added from the feat/antigravity row and closed; CHANGELOG.
Why: F-28 (Antigravity T03 review): never Write(*/vault/*) denied vault/key.txt but not door/key.txt with door -> vault; the Bash protected-file check missed cat ./alias and cat door/* the same way.
Proof: tests first (7 failed before the fix: door/key.txt, alias, door/new.txt, the link rule, real HOME path, cat ./alias, cat door/*); pytest with coverage exit 0 (98.70 %); ruff check and format, markdownlint, check-plugin, cobot-memory check exit 0; the F-28 probe gives deny for vault/key.txt, door/key.txt and alias.
Open: rebased onto main c34f304 after PR 53 (matches_file now joins both: a folder row protects the folder itself, with ~ read both ways, tested); main's bare-word resolution already asks on cat alias, cat key.txt inside vault and cp a vault/; still open: a glob whose matching name is a link (cat al* none); F-32 (with the cwd in a protected folder every command asks and the reason names the program).
Next: owner pushes fix/gate-symlinked-paths and opens its PR; the brief is over budget on main too (6265 of 6000, PR 53's journal entries): compact the journal.
verified: 5ef8dd3 · pytest+cov (2519, 98.73 %), ruff, shellcheck, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, memory check, F-28 probe after the rebase
