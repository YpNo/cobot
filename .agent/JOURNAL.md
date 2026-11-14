# Journal

Append-only, newest at the bottom. One entry per working session or task group.

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
