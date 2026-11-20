# Journal

Append-only, newest at the bottom. One entry per working session or task group.

## 2026-11-15 — compacted 2026-11-11 → 2026-11-15 (35 entries)
- 2026-11-06 → 2026-11-12 (compacted 2026-11-13): design v1.1, R0 and R1 (0.1.0: gate shim and rules engine, cobot-memory, protocol, agents, first skills, evals); owner decisions 17–26; R1.1 (learning, currency, ship, contribute, security-sweep, builders); rename to cobot (ADR-0004); R2 slices 1–4 (hardening, UI/UX and CI/CD experts, GCP/Kubernetes/mesh, stacks), R2 surface (/cobot:consult); 0.2.0 PRs (tidy, MCP read verbs, eval suite, README); new-project spec; CI on workload identity federation.
- 2026-11-11 → 2026-11-12: 0.3.0 input (Antigravity, google/elephant-goldfish-model ideas challenged) and the antigravity spec, challenged twice.
- 2026-11-13: gate-substitution (bash 5.2 scanner) and gate-expansion (exact braces, glob holes, agents anchor globs), each with a bypass review fold; gate-findings T01–T06 (${…} operator words, $"…", redirection writes, readings past global options, read guards for the agents, differential rows); eval cases aligned with the plugin-evals docs, three cases moved to evals-blocked (eval Bash is read-only upstream).
- 2026-11-14: gate-findings T07 fold (F-21..F-24 closed); first compaction (JOURNAL-archive.md); gate-repo-config T01–T05 (repository-config reads silent only where trusted, F-25 closed, F-26 accepted risk); actions-pinning grader accepts git ls-remote; agents start in the foreground (PR 48); release 0.2.0 cut and published (PR 27); memory tidy; lang-rust crates (F-20); consultants run in place (F-27); fewer stops for the owner.
- 2026-11-15: Antigravity spec re-read on agy 1.5.9 (challenger pass 3); T01 tree split (claude-agents/, .antigravity-plugin), T02 sync-agents, T03 the gate under agy (gate-agy.sh, force_ask/deny, workspacePaths), T04 self-protection rows with rule comments, T05 the injectSteps brief, T06 install.sh --agy, T07 version 0.3.0, ADR-0007, mechanics and harness docs, smoke script; T08 owner smoke runs: run 1 found the hook-name bypass (h2), closed by a random hook group name per install and a workspace scan; run 2 passed g1 g2 h1 h2 h3 s1 s2 b1 o1.
  open: actions-pinning shows Δ 0 (baseline pins v4 too; measuring expert-gha is the owner's call); the read-only eval Bash upstream report; agy: run_workflow's inner calls and the MCP name form unproven, no cobot agent run under agy, the upstream hook-group namespacing issue (owner's); data-dependent arithmetic out of the gate's scope.
Archive: raw entries in JOURNAL-archive.md and in git history before 2026-11-15.

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

## 2026-11-15 — journal compacted; the brief keeps its budget
Changed: df7e645 cobot-memory build_brief caps the findings block after the knowledge and specs tail and the separators (PART_SEPARATOR), so the brief stays within its budget; test first; CHANGELOG Fixed. 221041f compact --force --keep 2 folded 35 entries (2026-11-11 → 2026-11-15) into one with a written summary; JOURNAL.md 325 → 30 lines, the raw entries in JOURNAL-archive.md.
Why: the owner asked to compact; the measured overage (6265 of 6000) was the brief's cap, not the journal (the brief only reads the last two entries).
Proof: the budget test failed first at 3335 of 3000 and 6335 of 6000; full suite 2521 passed, 98.73 %; ruff, shellcheck, markdownlint, check-plugin, sync-agents --check, claude plugin validate; cobot-memory check: brief 6000 of 6000.
Open: the findings block is now what gets cut when the brief is full (rows end with the truncation marker); four findings open (F-29..F-32).
Next: owner pushes chore/journal-compact-0.3 and opens its PR; the gate findings and the A2UI knowledge PR follow.
verified: 221041f · pytest+cov, ruff, shellcheck, markdownlint, check-plugin, sync-agents --check, claude plugin validate, memory check

## 2026-11-15 — A2UI knowledge in expert-ui
Changed: 0d86c63 expert-ui/references/a2ui.md (16 dated lines: project, protocol v1.0 and its 2026-11-11 breaking change, the catalog and function boundary, npm/PyPI/pub.dev packages, MCP Apps, AG-UI, AI SDK generative UI); SKILL.md names the file and gains an Agent-driven UI rule; consult/domains/ui.md audits an A2UI catalog and flags a pre-1.0 version range; CHANGELOG Added.
Why: the owner's 2026-11-14 decision (knowledge only, its own PR, before the 0.3.0 cut).
Proof: every line read from its primary source on 2026-11-15 (gh api, the npm, PyPI and pub.dev JSON, the spec on main); cobot-memory knowledge expert-ui 40 → 56 lines; full suite 2521 passed; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Decided in build: the neighbour lines are verified, not reported as the 2026-11-14 note planned, since each was read from its own repository or registry today.
Open: which spec revision the published 0.15.0 packages implement (before or after #4044) is not diffed; the version lines are flagged after 30 days.
Next: owner pushes feat/a2ui-knowledge and opens its PR after the journal tidy PR.
verified: 0d86c63 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, knowledge count

## 2026-11-15 — gate residuals (F-29 to F-32), challenged, built, bypass review folded
Changed: spec gate-residuals (challenger pass 1 SOUND WITH CHANGES, eleven points folded); 44c3031 + 9d83faa F-29 Rule.shown (a project row shows its place, the tool only when known); d5d9585 + 66c2a4d F-30 case fold for never/ask path rows, the program word, wrappers, relocations, anchors and BASH -c; e86960b $HOME/ read as ~/; 90e2631 F-31 segment folders threaded to the protected check, redirect targets in every visited folder, ~/$HOME cd targets, unknown-cd last parts; 05682e0 F-32 protected cwd named, parent deletion; 3b7dc9a link globs by a bounded scan; ac8cc9c bypass review folds; docs, CHANGELOG Fixed, F-29..F-32 closed, F-33 and F-34 added.
Why: the open gate findings after PR 53; owner: work the remaining topics (2026-11-15).
Proof: tests first for every row (stories 1–9, both runtimes); the independent bypass review found a BLOCKER regression of this branch (the program-word skip hid a for/select/case head and flock's file: ask → none) plus nine more gaps, all reproduced old against new and folded with tests; full suite 2680 passed, 98.67 %; ruff, shellcheck, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate; noise against main changes only cd docs && tee settings.json and a glob deleting the protected folder; latency 167 → 179 ms per check.
Decided in build: the runner walk stays as it is (cd ~ && make test still asks); HOME, bare-cd and CDPATH folders feed only the protected check; a whole-folder glob is judged by the names it expands to, not lexically (a lexical folder form asked on cp -r assets/* dist/); $HOME is read both ways even when the command assigns HOME.
Open: F-33 (find -delete, tar -C and other folder options), F-34 (project text on stderr); residuals named in the spec (second-hole links, other variables, profile CDPATH, a hung mount, the over-budget reason).
Next: owner pushes chore/journal-compact-0.3, then feat/a2ui-knowledge and security/gate-residuals, one PR each, the tidy PR first.
verified: 3dfc5f3 · pytest+cov, ruff, shellcheck, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, noise check, latency (rebased onto main 3b93474)

## 2026-11-15 — findings F-35 to F-44 from two dogfood sessions
Changed: 704f936 .agent/FINDINGS.md gains ten rows from the owner's curriculo /cobot:ship run and the first ha-manager session (onboard, spec, build).
Why: the owner asked to check how cobot behaved there and to record the results.
Proof: two read-only reviews of the transcripts; each claim re-checked here: cobot-rules check gives none for the outward commands (F-36), report() skips async_launched (F-35), lang-rust says stable 1.99.1 (F-37), the onboard templates write exit 0 and 'were run' (F-38), _cobot_deps.py:522 prints its hint unconditionally (F-44); a read of a protected file asking is a documented known ask, not recorded.
Open: F-33 and F-34 stay open on main until security/gate-f33-f34 lands (paused, review fold not built).
Next: owner pushes docs/findings-dogfood-1115 and opens its PR; the owner picks which findings become the next spec.
verified: 704f936 · markdownlint, cobot-memory check

## 2026-11-15 — gate F-33 and F-34: deletions, folder options, project text off stderr
Changed: spec gate-f33-f34 (challenger SOUND WITH CHANGES, eight points; independent review, two blockers and three majors), all folded with tests: project warnings name their line only (F-34); deleting finds, gio, and HOME or / as a deleted folder; folder options of tar, unzip, patch and git as targets and bases, linear with a cap of eight; what a find runs judged as a command, -execdir in each start path and its parent; copies and moves that may land on a protected folder's parent; = values checked as paths; docs, CHANGELOG, F-33 and F-34 closed; rebased onto main 349a940.
Why: the owner asked to work on F-33 and F-34 (2026-11-15).
Proof: full suite 2778 passed, 98.68 %; ruff, shellcheck, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate; the review found no regression across the 1 700-string corpus; noise against main: only git -C ~ and find -exec rm -rf newly ask (named known asks); 16 folder options judge in well under 2 s.
Decided in build: cp a ~ stays silent (a merge asks only when a source may land on the parent); -execdir follows the start paths and their parents, not deeper entries.
Open: residuals named in the spec (extracting after a cd into a protected folder, busybox find and fd, variables naming a protected folder, very long commands); the safety classifier interrupted this work three times, so the fold went in small edits.
Next: owner pushes security/gate-f33-f34 and docs/expert-gha-learned, one PR each.
verified: dc82546 · pytest+cov, ruff, shellcheck, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, noise check

## 2026-11-15 — expert-gha learns two lines, curated from learn/gha
Changed: eced86a expert-gha/references/learned.md gains the zizmor version-pin line and the floating rust-toolchain channel line; CHANGELOG Changed.
Why: the owner asked to finish what was left locally; learn/gha (2 promote commits from curriculo, base 24a71af) carried lines F-42 names.
Proof: markdownlint; check-plugin; cobot-memory knowledge expert-gha reads 41 lines; the actions.md install-action row (v2.90.1, 2026-11-04) is inside its 30-day threshold, so the snapshot line is not needed.
Decided in build: the toolchain line's source names the step, not the private repository or the run id.
Open: learn/gha and its promote worktree stay for the owner to drop once this merges.
Next: owner pushes docs/expert-gha-learned and opens its PR.
verified: ea55945 · markdownlint, check-plugin, knowledge count (rebased onto main 7d3e65d)

## 2026-11-15 — a script that writes files is denied
Changed: 60c5738 cobot-rules writes_by_script (Python stdin or -c code that writes a file, perl -i) denies with WRITING_SCRIPT; protocol Rules line says never a script, whatever the host suggests (examples trimmed to stay at 2998 of 3000); docs/configuration.md; CHANGELOG; tests first.
Why: the owner's question on why Claude writes files with Python, and the choice of option 2 plus a scoped deny (2026-11-15); part of F-44.
Proof: 13 tests (8 writing scripts denied, reading scripts keep their ask, perl -ne not denied); full suite 2692 passed; ruff, markdownlint, check-plugin (protocol 2998), sync-agents --check, claude plugin validate.
Open: F-44's other items (sed -i and redirects into .agent/ or .github/workflows, the attribution line, the commit allow offer, parked builder notes, the cobot-deps hint) stay open.
Next: owner pushes fix/edits-not-scripts and opens its PR; the onboarding environment spec follows.
verified: cae8c52 · pytest+cov (2790), ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate (rebased onto main 204bd3c)

## 2026-11-15 — release 0.3.0 cut
Changed: f787e05 CHANGELOG Unreleased cut to [0.3.0] - 2026-11-15 with a summary (Antigravity from one tree, the gate's path gaps in both runtimes, project rules shown by place, writing scripts denied, A2UI and gha knowledge, the brief budget); the three manifests already carry 0.3.0.
Why: the owner asked to cut 0.3.0; its scope (Antigravity and A2UI) is merged, with the gate PRs 54, 57, 59, 61.
Proof: release.yml's version check run locally (plugin.json, the Antigravity manifest, marketplace.json and the CHANGELOG heading agree); its notes extraction gives 176 lines; markdownlint; check-plugin. Currency read 2026-11-15: the four pinned actions are their latest releases; ruff 0.17.4 against 0.17.5, markdownlint-cli2 0.24.0 against 0.24.1, Claude Code 2.1.322 in CI against 2.1.325 (2.1.311 local): patch gaps, the owner's call.
Open: the onboarding environment build (spec on feat/onboard-environment) is not in 0.3.0; F-35 to F-44 open.
Next: owner pushes chore/release-0.3.0, merges, then pushes the annotated tag v0.3.0; release.yml publishes the GitHub release.
verified: f787e05 · release version check, notes extraction, markdownlint, check-plugin

## 2026-11-15 — spec onboard-environment, challenged
Changed: ef359d5 .agent/specs/onboard-environment.md (revision 2, 8 stories, T01–T06) on feat/onboard-environment.
Why: the owner asked that onboarding detect or ask the development environment (Docker or Podman, mise, distrobox, missing tools) and advise helpers such as RTK; four answers before drafting (machine profile, propose installs, curated advice, ask per repository).
Proof: the gate already unwraps rtk, mise exec and distrobox enter (cobot-rules check, 2026-11-15); challenger SOUND WITH CHANGES, fifteen points folded (BLOCKER: --version probes could run a repository-chosen binary or shim).
Open: the fold moves the 'where things run' question on a new project from onboarding to the first spec, for the owner to confirm; F-38 is folded into this spec.
Next: owner confirms the move, then /cobot:build onboard-environment from T01.
verified: ef359d5 · markdownlint

## 2026-11-16 — eval runs outside /tmp; two blocked cases restored
Changed: 2a5546c ci.yml's eval step sets TMPDIR under RUNNER_TEMP (the traces upload follows it), docs/development.md's local command uses ~/.cache/cobot-evals, the mechanics note corrected with anthropics/claude-code#104631; cc88212 foreign-onboard and new-project-onboard back under evals/, foreign-onboard's tree graders skip writes under .agent, cobot-memory init --foreign names .git/info/exclude, a grader test; proof-quoted stays blocked, now on the run's missing Rust toolchain; d0beb0f CHANGELOG.
Why: the owner asked to check for an existing upstream issue (#104631 and #104797 were open, with a TMPDIR workaround), posted a 2.1.325 confirmation, and asked to apply the workaround.
Proof: eval-ro-repro on 2.1.325 scored 0.50 with the default TMPDIR and 1.00 outside /tmp (the owner's runs); new-project-onboard 1.00, foreign-onboard 1.00 after the grader fix (0.67 before: a Write to .agent/CONTEXT.md and no info/exclude named), builder-routing 0.75 (cargo: no installed toolchains), one run each on 2.1.325; full suite 2794 passed, 98.68 %; ruff, markdownlint, check-plugin, sync-agents --check, zizmor (same three low as main), claude plugin validate.
Open: the rust-builder appended to src/lib.rs with cat >> and a heredoc in the builder-routing run (F-44, seen again); CI pins Claude Code 2.1.322, the workaround was proven on 2.1.325 and the eval job has not run with it yet.
Next: owner pushes fix/eval-tmpdir and opens its PR; one dispatched eval run (inputs.cases: *-onboard) proves the CI side.
verified: d0beb0f · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, zizmor, claude plugin validate, three eval cases

## 2026-11-16 — the brief keeps Environment; the spec list stops growing
Changed: ffed454 cobot-memory cap_sections gives room to the preamble, then Verified commands, Constraints and Environment in that priority, each only when it fits, then the rest in order; the brief's spec tail past three names the count and the three newest by date: (specs_by_date); onboard step 6 names the order; CHANGELOG Fixed; tests first.
Why: cobot-memory check warned that cobot's brief dropped Environment (the rtk hook, git settings, versions); the owner asked to fix the brief rather than trim CONTEXT.md, once a journal compaction was shown not to help (the brief reads only the two newest entries, and the journal is 98 of 400 lines).
Proof: four tests failed first (two cap_sections, the spec tail, the 20-spec budget case); two older tests changed with the order (Shape now fits once a huge Environment is skipped; Environment outranks Stack); cobot's own brief keeps Environment, 6000 of 6000, no warning; full suite 2794 passed, 98.69 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate.
Open: cobot-memory check still prints every spec name on its own line (a check, not the brief).
Next: owner pushes fix/brief-environment and opens its PR.
verified: ffed454 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, memory check

## 2026-11-16 — F-45 recorded: the security sweep on curriculo
Changed: 12ec912 .agent/FINDINGS.md gains F-45.
Why: the owner asked to check the curriculo /cobot:security-sweep and to record what it missed.
Proof: the sweep's consultant transcript read; cobot-rules check --agent cobot:consultant gives none for git log --all --diff-filter=A, zizmor, cargo-deny and gitleaks, and ask for cd into the packs folder; the install-action README and cargo-deny-action's Dockerfile at the pinned SHA read; the skipped history scan run by hand on curriculo found no secret file in 106 commits.
Open: F-45 is not fixed; the curriculo follow-ups (cargo deny check advisories, cargo audit, a LaTeX escaping pass, the cargo-deny-action download) are the owner's.
Next: owner pushes docs/sweep-findings and opens its PR.
verified: 12ec912 · findings list, markdownlint

## 2026-11-16 — init reports a read-only config dir; the eval case hands trust to the owner
Changed: 170028e cobot-memory init --trust-root and --add-identity catch the OSError writing ~/.claude/cobot, print 'trust not recorded:' with a quoted cd-and-init command for the owner's terminal and exit 1 (TRUST_NOT_RECORDED); onboard step 2 and N3 carry on and hand the command over; new-project-onboard gains the trust-handed-to-owner grader and its description; configuration.md and the mechanics note name the sandbox's protected config dir; CHANGELOG Fixed; tests first.
Why: the dispatched eval run 43927352477 on main (TMPDIR fix proven: every arm wrote, foreign-onboard 3 of 3) failed on new-project-onboard 0.89: init crashed with EROFS on ~/.claude/cobot in all three runs and one run stopped; the sandboxing docs say most of the config dir is read-only to Bash in sessions too, and allowWrite does not lift it. The owner asked for the fix.
Proof: three tests failed first (read-only trust-root, add-identity, main exit code); full suite 2803 passed, 98.69 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate; one local new-project-onboard run scored 1.00 (2.1.311: Bash inherits a writable CLAUDE_CONFIG_DIR there, init wrote, the next Bash call no longer saw the file, and the report named init --trust-root).
Open: CI pins Claude Code 2.1.322, the local run used 2.1.311; the CI side is proven by a dispatched run after merge.
Next: owner pushes fix/trust-readonly, opens and merges its PR, then dispatches the *-onboard eval run on main.
verified: 170028e · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, one eval case

## 2026-11-16 — CodeQL alert on init's output: a name, not a secret
Changed: 6be627e add_trusted_root renamed add_root_commit (cobot-memory and its tests).
Why: PR 67's CodeQL check failed on py/clear-text-logging-sensitive-data at main's print of init's output; the SARIF flow starts at add_trusted_root(), which the query's name heuristic takes for a secret. The same alert (1) has been open on main since 2026-11-14; the output is a root commit hash and a folder name.
Proof: cobot-memory and new-project tests 113 passed; ruff check and format; CodeQL itself runs only in CI (no local codeql), so the PR's next run proves it.
Open: alert 1 on main closes once this merges, if CodeQL agrees.
Next: owner pushes fix/trust-readonly.
verified: 6be627e · pytest (memory, new-project), ruff

## 2026-11-16 — security-auditor spec, challenger pass folded
Changed: 49c8cdf, e868798 .agent/specs/security-auditor.md: a cobot:auditor agent (inherit, high effort, no commands under agy), the gate's @consultant scope for cobot:auditor only, security-sweep as a main-thread router (counted inventory, per-pack units plus a repo-wide unit above 200 files, at most five; merge, cap, then a fresh check of MEDIUM and above), one confidence scale, CORE-INJECT-05 for document languages, two eval cases.
Why: the owner asked whether a security agent is missing after F-45; answers 2026-11-16: inherit and high, per pack when large, a fresh checker for MEDIUM and above, trust boundaries in /cobot:spec later.
Proof: challenger SOUND WITH CHANGES, eleven points folded; two checked by hand: sync-agents NO_COMMANDS holds consultant and learner only, and cobot-rules check gives none for an unrelated agent (no global ask Bash(*)).
Open: F-45 stays open until the build; the new decision takes the next free number (29 is the onboard-environment spec's).
Next: owner pushes feat/security-auditor and opens its PR; /cobot:build security-auditor after it merges.
verified: e868798 · challenger pass, gate dry runs, markdownlint

## 2026-11-16 — no-second-onboard passes a negated re-run; worktrees move into the project
Changed: 3271a30 new-project-onboard's no-second-onboard pattern skips a re-run preceded by don't (both apostrophes), do not or never, with seven grader tests and a CHANGELOG Fixed line; 9240b04 markdownlint ignores .claude/worktrees/**.
Why: dispatched run 43950232416 on main proved the TMPDIR and trust fixes (foreign-onboard 3 of 3, trust-handed-to-owner 3 of 3) and failed only on a report ending "Don't re-run onboard.", the advice step N4 asks for. The owner moved branch worktrees from the /tmp scratchpad into .claude/worktrees/ (already gitignored) to stop the cd-outside-the-project prompts, with each worktree removed once merged; from the main checkout markdownlint then read the worktrees' copies (759 files instead of 315).
Proof: four negated reports failed first, three real re-run reports still fail; the same pattern checked in node; full suite 2810 passed, 98.69 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate; a planted bad file under .claude/worktrees/ is linted with the old config and skipped with the new one; one local new-project-onboard run scored 1.00 (2.1.311).
Open: the CI side is proven by a dispatched *-onboard run after merge.
Next: owner pushes fix/eval-negated-onboard and opens its PR.
verified: 9240b04 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, one eval case

## 2026-11-16 — onboard-environment built: cobot-env, the runs: header, install routes ask
Changed: ff11827 main bcef2d0 merged into the spec branch; 31b99fc bin/cobot-env and _cobot_env.py (presence detection, untrusted PATH entries, machine.md per host, choices line); 817c242 install-route ask rows; 631a93d skills/onboard/references/workstation.md; fbd26dd runs: header, claim-nothing templates and init's none-yet row (F-38), the machine line in the brief (reserve +160), agy section names cobot-env; 49dae0f onboard step 3b, missing programs, helper line, N3, the spec skill's new-project question; 943e396 cobot-env in the CLI hygiene checks; be16b6b decision 29, eval cases onboard-runs-question and ship-runs-bare, ship reads runs: as local, docs, CHANGELOG, F-38 closed, F-46 added, spec converged.
Why: /cobot:build onboard-environment (spec rev 2, challenger SOUND WITH CHANGES; the owner confirmed the new-project move).
Proof: each task's tests failed first (module missing; 19 install rows none; five memory and four session tests); full suite 2922 passed, 98.52 %; ruff 0.17.4 check and format, markdownlint-cli2 0.24.0, check-plugin, sync-agents --check, claude plugin validate --strict (plugin, marketplace), shellcheck on the two fixtures, memory check; cobot-env detect on this machine 0.11 s with Python start, the marker stub never ran; both fixtures ran in a scratch HOME and trusted their root commit; apt-cache and the mise registry checked locally for workstation.md.
Decided in build: prefer and decline print answer not recorded: with the owner's command when the config directory is read-only; detect takes program names and prints choices:; the repository root is found by a .git walk, not git; the journal template has no entry; mise install now asks (a mise-task test expectation changed).
Open: the two eval cases are not run (paid); onboard-runs-question needs docker and podman on the runner; F-36 stays open beyond the install routes; F-46 (workstation.md outside the knowledge scan); rtk's licence and the non-Debian package names are reported, not verified.
Next: owner pushes feat/onboard-environment and opens the PR with the body in PR-onboard-environment.md at the worktree root (untracked); a dispatched eval run for the two new cases.
verified: be16b6b · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, shellcheck (fixtures), memory check

## 2026-11-16 — onboard-environment: evals cannot ask, shims may run
Changed: f3a16e3 cobot-env reports mise and asdf shims apart from not-trusted repository hits (found shims; the report counts them present), onboard step 3b runs them, docs, decision 29 and CHANGELOG reworded; 7d68086 onboard-runs-question's one-question and question-before-command moved to evals-blocked/ with the reason, the prompt has the report state the question, graders no-question-tool and question-stated, a test refusing any grader that needs a question call; 15205dc F-47.
Why: the parent session's local run scored 0.67: AskUserQuestion was not in the session (eval runs use dontAsk, which denies it even when allowed_tools grants it; headless docs), and python3 and uv resolved only to mise shims, which step 3b said never to run, so nothing was verified.
Proof: the new env tests and the grader rule failed first (KeyError shims; both moved graders rejected); full suite 2946 passed, 98.52 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate --strict (plugin, marketplace), memory check; onboard-runs-question run locally on 2.1.311 with --scaffold: 1.00, and it ran python3 -m unittest through a mise shim (a first run without --scaffold had an empty workspace and does not count).
Open: neither case has run in CI on 2.1.322; F-47 (init --trust-root writes ~/.claude/cobot while check reads the run's CLAUDE_CONFIG_DIR); F-36, F-46 as before.
Next: owner pushes feat/onboard-environment and opens the PR with the body in PR-onboard-environment.md at the worktree root (untracked); a dispatched eval run for both cases.
verified: 15205dc · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, memory check, eval onboard-runs-question (local, 1 run)

## 2026-11-16 — onboard-environment: shims not trusted in foreign mode
Changed: f20b2b6 cobot-env reads foreign mode from a .agent symlink at the repository root (no git call) and then puts every mise or asdf shim under not trusted, never under shims; runnable() decides what onboarding may run; the report says 'not trusted (foreign repository: shims too)'; the onboard skill, cobot-env's usage, _cobot_env's docstring, decision 29, architecture and CHANGELOG say both cases.
Why: the owner's decision on f3a16e3, relayed by the parent session ('I follow your recommandation'): shims run in the owner's own repositories and are untrusted in foreign mode, as the spec had it.
Proof: three tests failed first (KeyError foreign twice; the foreign run listed three shims under shims), then passed: foreign repository reports a mise shim as not trusted, the owner's repository as a shim, and the foreign path never lists a shim under shims (mise and asdf, helpers and programs, report and data); full suite 2949 passed, 98.52 %; ruff check and format, markdownlint, check-plugin, sync-agents --check, claude plugin validate --strict (plugin, marketplace), memory check.
Open: any .agent symlink counts as foreign, so a planted one only makes shims stricter; the eval cases still have not run in CI on 2.1.322; F-36, F-46, F-47 as before.
Next: owner pushes feat/onboard-environment and opens the PR with the body in PR-onboard-environment.md at the worktree root (untracked).
verified: f20b2b6 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, memory check

## 2026-11-16 — docs tidy: user-centric README, docs checked against main
Changed: 118b031 README rewritten for the person using cobot, Claude Code and the Antigravity CLI as two supported hosts (overview, host table, architecture, prerequisites, both installs, configuration, usage with each host's command form, differences under agy, testing, CI/CD, security, contributing, changelog, licence); architecture.md gains a Session brief row (10 000 and 6 000 caps, Verified commands, Constraints, Environment first, three newest specs), init's trust not recorded:, the gate's failure behaviour (an error asks, a gate that cannot run blocks), agy's exit-code fact per version, and its security model points to configuration.md instead of repeating it; configuration.md: CLAUDE_CONFIG_DIR under both runtimes with trust not recorded: and answer not recorded:, shims not trusted in foreign mode, the agy deadline's 10 s is cobot's hooks.json timeout, precedence per runtime; development.md: agy prerequisite, sync-agents --check and agy validate, smoke-agy among the live spikes, branch work in .claude/worktrees/; 01-decisions.md: missing sentence breaks in 24, 25, 27, 28, decision 26 notes the three experts shipped in 0.2.0; CHANGELOG Unreleased: a Changed entry, onboard-runs-question's blocked graders named, a stray blank line.
Why: the owner asked to tidy and check all the documentation before the security-auditor build, with a README that is user-centric and not Claude Code oriented only (relayed by the parent session).
Proof: every command, flag and path checked against install.sh --help, the bin tools' --help and the code (KEPT_SECTIONS, TRUST_NOT_RECORDED, BRIEF_CAP, TOTAL_CAP, SPECS_SHOWN, hooks.json timeouts, gate.sh, ci.yml TMPDIR); relative links and anchors resolve; markdownlint-cli2 0.24.0 0 issues; check-plugin ok; sync-agents --check in sync; claude plugin validate --strict passed; full suite 2949 passed, 98.52 %.
Open: left alone: cobot-rules --help says any internal error ends in ask while CONTEXT says any failure blocks (both partly true); CONTEXT says CI pins 2.1.322 but ci.yml's quality job installs 2.1.318 (evals 2.1.322; npm latest 2.1.325 on 2026-11-14); CONTEXT's local eval row lacks TMPDIR; wrap's description names Claude Code's /code-review and /security-review, absent under agy; ADR-0007's context still says a failing agy hook lets the call run (true on 1.5.3, recorded as context); decision 24 names ts-builder, built as typescript-builder.
Next: owner pushes docs/tidy and opens the PR with the body in PR-docs-tidy.md at the worktree root (untracked); then the security-auditor build.
verified: 118b031 · pytest+cov, markdownlint, check-plugin, sync-agents --check, claude plugin validate

## 2026-11-17 — spec gate-f36-f40-f44, challenged
Changed: baad3b3, 00f33b3 .agent/specs/gate-f36-f40-f44.md (revision 2, stories 0–7, T01–T06): outward and account commands ask, forge deletions never, git config writes that outlive the session ask, credential printers ask, every ask named in the reason, literal shell writes and in-place editors denied; story 0 makes existing rows reach -R/--repo forms, gh aliases and fd/parallel/watch runners.
Why: the owner asked to spec F-36, F-40 and F-44 after the 2026-11-16 recap; four answers 2026-11-16, all recommended: deny literal writes on any file, forge deletions never, global writes plus exec keys for git config, credential printers ask.
Proof: every Goal row measured with cobot-rules check on 4288978; the challenger's UNSOUND verdict (2 BLOCKER, 8 MAJOR, 7 MINOR) checked by hand before folding (gh release -R o/r create v1, gh pr new, watch git push, fd -x sh -c 'git push' silent today; Scan.writes is whole-command data).
Open: two live bypasses of existing rows (-R/--repo, gh aliases, unwrapped runners) until T01 lands; story 6's reworked design has not had a second challenger pass; F-36, F-40, F-44 stay open until the build.
Next: owner decides whether T01 ships alone and whether to run a second challenger pass, then /cobot:build gate-f36-f40-f44.
verified: 00f33b3 · gate dry runs, challenger pass

## 2026-11-17 — gate T01: rows reach the commands they name
Changed: ab9bb3a -R/--repo between a gh or glab group and its verb dropped, gh built-in aliases (gh 2.103.3 help) rewritten, fd -x/-X bodies judged, parallel and watch opaque; 97b18ef after a bypass review: every cobra reading of options before a gh/glab group or verb (moved after the verb, repository options dropped), an escaped or quoted ; is a word, fd -Hx clusters start a body, pkexec, run0, setsid, tmux, GNU parallel's family and job queues ask like xargs, busybox unwrapped, a gh user alias or extension asks with gh alias set|import, gh api kept out of the drop; docs/configuration.md, CHANGELOG Security.
Why: the challenger of spec gate-f36-f40-f44 found live bypasses of existing never and ask rows in 0.3.0 (gh release -R o/r create v1, gh release new, gh pr new, watch git push, fd -x); the owner chose to ship T01 alone first.
Proof: tests first (five failing, then five more after the review); a security reviewer attacked ab9bb3a and its four HIGH and two MEDIUM forms were each reproduced, then fixed with tests; an existing test (owner allow on a hole-free canonical form) caught a regression in the first cobra reading, fixed by dropping the repository options; consultant reads unchanged against the old gate; full suite 2970 passed, 98.55 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate.
Open: gt and tea option placement not checked (not installed); watch git status now asks; T02–T06 of the spec pending; a second challenger pass on story 6 not run.
Next: owner pushes security/gate-f36-f40-f44 and opens its PR (spec plus T01); T02–T06 follow on a new branch.
verified: 97b18ef · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, gate dry runs, bypass review

## 2026-11-17 — spec gate-f36-f40-f44 revision 3, story 6 challenged again
Changed: 9201ec7 .agent/specs/gate-f36-f40-f44.md (revision 3): story 6 denies only literal text that reaches a non-exempt fd-1 file through pass-through stages or a named writer (tee, dd of=, sponge, sort -o, cp/install from stdin); writes it cannot trace for certain ask (group, loop or exec ownership, nested stages, functions, a non-pass-through stage); named sources by basename (jq -n, awk BEGIN), process substitution, yq -i, patch/git apply/ed/ex from any literal source; /dev/fd/1 and /2 only; Plan 6 adds list indexes, opener stacks, textual exec scope, one shared split and inner scans for runner bodies; Plan 7 lists changed tests at T05 start; story 0 and Plan 1 shrunk to "built, T01"; pass 1 table condensed.
Why: the owner asked for a second challenger pass on story 6 before T02–T06; it came back UNSOUND (5 MAJOR, 3 MINOR), SOUND WITH CHANGES once folded; the owner said yes to folding all eight, including asking rather than denying the uncertain cases (a change to the Q1 answer's letter, in its direction).
Proof: the verified points reproduced on b972f61 (bash -c here-doc only asks; the scanner gives identical writes for both orders of cargo metadata > m.json and echo done; jq -rn x > f, cp /dev/stdin f <<<x, yq -i, printf x | git apply silent); the deny override at cobot-rules:3746 read; spec 299 lines.
Open: F-36, F-40, F-44 stay open until the build; the bypass-aimed review after T05 still applies.
Next: /cobot:build gate-f36-f40-f44 from T02 on security/gate-asks-and-writes.
verified: 9201ec7 · gate dry runs, challenger pass 2

## 2026-11-17 — gate T02: every ask named
Changed: 9465eb9 Verdict gains also and reason(budget): the winning ask, then up to two other distinct asks and +N more; ask_label (a rule shown as F-29 allows, or a note cut to 40, each with its via), ask_key, named_asks in judge_bash (the protected-file ask included) and judge_plan; agent-scoped asks lead for an agent's call; gate() and gate_agy() budget the reason as REASON_LIMIT minus the stamp suffix; docs/configuration.md, CHANGELOG Changed; test_judgeBash_ruleBackedAskAfterOpaque_reportsTheRule gains the list (Plan 7).
Why: F-40, story 5 of spec gate-f36-f40-f44: a compound that asks for several reasons named only the first.
Proof: tests first (eight failing); a security review of the diff found no decision change and three LOW items, each reproduced or proved by a test, then fixed: a runner body's ask now carries its via, asks alike only after the 40-character cut stay apart, the first reason is never cut for the tail; decisions compared against main on 18 compounds by the reviewer; full suite 2984 passed, 98.56 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate.
Open: a single long ask on a command holding git push still loses its stamp to the 200-character cut, as before F-40 (review item 4, kept); T03–T06 pending; F-40 closes in T06.
Next: T03, the git config canonical form.
verified: 9465eb9 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, gate dry runs, security review

## 2026-11-17 — gate T03: git config writes that outlive the repository ask
Changed: cb34eda canonical_git_config (both syntaxes, unique long-option prefixes, short clusters, unknown options fail closed as exec), git_config_scope (GIT_CONFIG*, GIT_DIR, GIT_COMMON_DIR prefixes and --git-dir, the file path kept in the form), git_exec_key families, an alias is exec unless one read-only verb, canonical_git_variables (export, declare, typeset, local of those variables), canonical_allexport (set -a, set -o allexport as one word so set -- <glob> stays silent), canonical() as a loop of steps; rows for --global, --system, --file <path> and exec writes, the variable builtins, set-allexport, git submodule foreach; docs/configuration.md, CHANGELOG Changed; spec Plan 5 shortened to as built.
Why: F-36 and story 3 of spec gate-f36-f40-f44: git config --global, local hooksPath-style keys and their environment routes passed silently.
Proof: tests first (44 failing); a bypass review of the first version found six gaps (abbreviated options, short clusters, aliases running a git command, missing exec keys, set -a and local -x, an owner allow unable to name the file), each reproduced against real git in a scratch HOME and by cobot-rules check, then made a failing test and fixed; full suite 3076 passed, 98.56 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate.
Open: git -c and GIT_CONFIG_COUNT run code for the session only (the agent's own command, silent as before); shell writes to .git/config and ~/.gitconfig belong to story 6 (T05); export -n of a git variable asks (LOW, accepted).
Next: T04, the outward and account rows, credential printers and forge deletions.
verified: cb34eda · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, gate dry runs, bypass review

## 2026-11-17 — gate T04: outward and account rows, credential printers, forge deletions never
Changed: 13283f0 default.rules: ask rows for the forge account, repository settings, secrets and variables, CI, issue and PR state, releases, gists, projects, discussions, codespaces and keys (gh, glab), rustup per verb with its aliases, gcloud config set/unset and activate, npm/pnpm/yarn/pip config and accounts, docker logout; the named credential printers; 43 forge deletions as never rows (gh, glab, gt, tea), the glab/gt/tea deletions moved from ask; kubectl config view --flatten never for the read-only agents; cobot-rules: gcloud verbs set, unset, activate, print-access-token, print-identity-token, config-helper; gcloud_words drops the release track and flags between command words; canonical_credential_printers (auth status showing the token, kubectl get secret with a data output, --template or a --raw secrets path); note lint and sync tests; docs/configuration.md, CHANGELOG Changed.
Why: F-36, stories 1, 2 and 4 of spec gate-f36-f40-f44 (owner answers Q2 never, Q4 ask).
Proof: tests first (107 failing, then 57 more after the review); a bypass review found ten HIGH and six MEDIUM gaps (kubectl output case, kyaml, --template, --raw paths, --flatten, gcloud beta and inner flags, glab config get options, git-credential-* binaries, missing deletions and verbs, rustup/npm/pip aliases), spot-checked by hand, each a failing test before its fix; three existing tests that pinned the old silence updated; consultant and learner read lists unchanged on the reviewer's 50-command sample; full suite 3261 passed, 98.52 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate.
Open: owner calls: a never row reads an option value before the verb as the verb (gh issue --label delete list is denied, from T01's cobra readings), and gh pr merge --delete-branch only asks; oc, kubecolor, microk8s and kubectl -f/-k with secrets are outside the claim; rustup options between group and verb not read.
Next: T05, shell writes (scanner list indexes, openers, exec scope, inner scans).
verified: 13283f0 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, gate dry runs, bypass review

## 2026-11-17 — gate: a never row reached only through an unknown option's reading asks
Changed: a4b33b1 cobra_forms (readings with their group and verb positions), uncertain_readings, branching_option, never_through_option_value in judge_words; tests: the T01 cobra cases with an unknown option before the verb now expect ask (gh release --title x create v1, the attribution form gh pr --body 'Generated with x' create), known options and attached values keep deny; docs/configuration.md, CHANGELOG.
Why: the T04 review found never rows denying reads such as gh issue --label delete list (the label value read as the verb), a deny nothing lifts; the owner chose to downgrade those to ask on 2026-11-17.
Proof: a failing test first (ask, and an owner allow on gh issue* does not lift it; gh release delete v1, -R o/r delete and delete --yes still deny); full suite 3262 passed, 98.53 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate. One test expectation in tests/test_gate_agy.py was edited with sed instead of the Edit tool (owner rule broken, reported).
Open: a deny through an unknown option before the verb is now an ask, including T01's bypass forms (closed, no longer silent); the holed path (never_anyway) is unchanged; gh pr merge --delete-branch stays an ask (owner).
Next: T05, shell writes.
verified: a4b33b1 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, gate dry runs

## 2026-11-17 — gate T05: shell writes refused, uncertain ones ask
Changed: b12d5ea _cobot_shell.py: Stage and Redirect records per scan (list item, pipeline index, span in outer; operator, fd, target, after a closer), separators with &&/||/|& and a newline after | kept in the pipeline; cobot-rules: edits_in_place (sed/gsed -i, awk -i inplace, ruby -i, yq -i) beside writes_by_script, shell_write once per command recursing into substitution and runner bodies (bash -c clusters, a shell behind distrobox or sudo, su -c, nix-shell --run), stage_words with case patterns dropped, literal_word (expansions alone are output unless the command wrote their text), writer_targets (tee, dd of=, sponge, sort -o in clusters and --output, cp/install from stdin or a process substitution), written_by_stage with an fd table, pipeline_writes and item_writes (deny through pass-through stages, ask for groups, loops, exec, functions, runners, non-pass-through stages, compound output), shell_write_verdict (an owner allow must cover every asking stage); 29 tests rewritten (Plan 7, recorded in the spec); docs/configuration.md, CHANGELOG Changed.
Why: F-44 and story 6 of spec gate-f36-f40-f44 (owner Q1 deny, revision 3: uncertain cases ask).
Proof: tests first (44 failing, then 29 more after the review); a bypass review found a crash (empty zip under strict, every bare awk; agy would have denied) and nine silent forms (fd duplication, a group or loop split by ;, case, a newline after |, bash -lc and runner wrappers, named-writer options, exec inside a group, cp from a process substitution) plus one MEDIUM (one owner allow lifted every ask), each reproduced, made a test and fixed; the reviewer's fuzz of 60k random commands now raises nothing; full suite 3358 passed, 98.56 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate.
Open: exec scope is the whole command (stricter than the spec's textual scope); //dev/null and ../dev/null are denied; in a pipeline with two sources only the first decides; yes and read loops are not named sources; sed w, split and csplit not claimed.
Next: T06, the agy parity sweep, docs, and closing F-36, F-40, F-44.
verified: b12d5ea · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, gate dry runs, bypass review, fuzz

## 2026-11-17 — gate T06: parity sweep, docs, findings closed
Changed: 3437cf5 tests/test_gate_agy.py PARITY_SWEEP (21 samples, stories 0 to 6, Claude Code and agy agree); README (forge deletions never, account changes and credential printers ask, files written with the edit tools), docs/architecture.md (stage records, canonical forms, bounded claims); FINDINGS: F-36, F-40, F-44 closed, F-48 filed (F-44's rest: commit approvals with no allow line offered, Noticed items never parked, the cobot-deps Actions hint, ship's global unpinned installs) toward the memory and ship spec; spec converge line: every task built.
Why: T06 of spec gate-f36-f40-f44.
Proof: full suite 3379 passed, 98.56 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate; cobot-memory check (10 open findings of 48, brief 6000 of 6000).
Open: the brief sits at its 6000-character budget; the branch is unpushed (T02 to T06 and the never-through-an-option fix); known limits are in the T04 and T05 entries.
Next: owner pushes security/gate-asks-and-writes and opens its PR; then the security-auditor build or the memory and ship spec (F-37, F-41 to F-43, F-46 to F-48).
verified: 3437cf5 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, parity sweep

## 2026-11-18 — security auditor and the sweep router built
Changed: 4ab0101 claude-agents/auditor.md (inherit, high, the consultant's tools) and its agy twin with no command tool (NO_COMMANDS), the manifest, ten agents in the README; f50d603 SCOPE_ALIASES in cobot-rules (@consultant rows match cobot:auditor only); 80648ce CORE-INJECT-05 names typesetting input; aaa127a security-sweep SKILL.md as a main-thread router (counts by git ls-files, one unit up to 200 files, else a repo-wide unit and one per pack, at most five, fan-out, merge and cap, a checking auditor, the report, the agy branch) with references/procedure.md for the units; 6b88b53 evals sweep-fan-out and sweep-history-secret, the one-confidence-scale grader, the procedure runs scanners directly; 65e4c58 decision 30, 02-design rows, configuration.md, CHANGELOG, F-45 closed, F-49 (trust boundaries in /cobot:spec) filed.
Why: spec security-auditor (owner answers 2026-11-16) and F-45 from the curriculo sweep.
Proof: tests first for T01 and T02 (the auditor gets the consultant's decision on every corpus command; auditor, x:auditor and cobot:builder get none of its rows); skill text tests; local evals at 1.00 (sweep-every-pack 0.33 USD, sweep-fan-out 0.66 USD, sweep-history-secret twice after a fixture fix); a first history run scored 0.50 because the auditor rightly rescaled a placeholder value to LOW and the grader matched the word in prose, so the fixture and the grader were fixed; GitGuardian then flagged the literal password-shaped value in the fixture, so the branch was rebuilt with the value drawn at scaffold time (no value in any commit; backup branch backup/security-auditor-a49187e, local); one run of that version scored 0.50 (the CRITICAL rating weighed against a repository with no remote), so the fixture adds one, then 3 of 3 runs at 1.00; full suite 3401 passed, 98.57 %; ruff, markdownlint, check-plugin (listing 568 of 600 tokens), sync-agents --check, claude plugin validate, agy plugin validate (the existing no-logo warning).
Open: the evals have run locally only (CI runs them from main after merge); one test file edit early in T02 used a shell heredoc instead of the Edit tool (owner rule broken, reported); the brief sits at its 6000-character budget.
Next: owner pushes feat/security-auditor and opens its PR; then the memory and ship spec (F-37, F-41 to F-43, F-46 to F-49 where they belong).
verified: 65e4c58 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, agy plugin validate, local evals

## 2026-11-18 — spec memory-and-ship, challenged
Changed: 3bff15e .agent/specs/memory-and-ship.md (revision 2, stories 1–9, T01–T07): keyed-tree stamp so code and journal share one commit, journal add exits 1 on an invalid entry; the gate offers an owner allow line from the third ask of an offered row (git commit, git rebase); builders' Noticed items parked in .agent/noticed.md and cleared at wrap; promotion lint in promote_entries; every skill's dated lines scanned; trust commands show their file and carry CLAUDE_CONFIG_DIR; cobot-deps toolchain channels and the Actions hint only with workflows; ship reads its remote (unreachable is not empty), toolchains and pins first; eval ship-ground.
Why: findings F-37, F-41, F-42, F-43, F-46, F-47, F-48 (dogfood 2026-11-15/16, evals); the owner answered four questions on 2026-11-18, all recommended: tree stamp, offer after repeats, hook parks and wrap clears, refuse promotions.
Proof: the brief is at its budget by design (build_brief fills the room), so it left the scope; the challenger's SOUND WITH CHANGES (5 MAJOR, 7 MINOR) checked by hand before folding: a written tree pruned by git gc --prune=now and a mktree key that survives it, ask Bash(*) @consultant at default.rules 608-609, promote_entries skipping filter_delta; spec 276 lines.
Open: the revision header was set with sed -i instead of the Edit tool (owner rule broken, reported); F-35, F-39, F-49 stay their own specs.
Next: owner reviews; then build from T01 on feat/memory-and-ship.
verified: 3bff15e · challenger pass, gate dry runs, scratch git checks

## 2026-11-18 — memory-and-ship T01: one commit per verified change
Changed: cobot-memory: tree_key (the tree with its root doc entries out, rebuilt by git mktree; the whole tree in foreign mode), stamp_readiness, stamp --tree, the tree form in STAMP_RE and cmd_stamp; journal add exits 1 on an invalid entry and takes --check; _cobot_common.git gains stdin; wrap step 6 and build step 5 name the one-commit flow; tests (test_cobot_memory story 1 block, test_workflow_skills); test_cli_journalAdd now expects 1 for an empty entry (the F-41 bug it pinned).
Why: F-41, story 1 of spec memory-and-ship (owner answer: one commit, tree stamp); challenger 1 and 2: a written tree is pruned by gc, and foreign mode has no journal to add.
Proof: tests first (six failing); the key survives git gc --prune=now and holds in a fresh clone; untracked or unstaged code is not ready, an untracked doc is; full suite 3409 passed, 98.51 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate; the gate is silent on stamp --tree and journal add --check. This entry is the first committed with its code under the new flow.
Open: T02–T07 of the spec; CHANGELOG and decision 31 come in T07.
Next: T02, the Noticed parking.
verified: tree c9e1c976796e57d72ab8223904f085d328d658d4 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate

## 2026-11-18 — memory-and-ship T02: builders' notices parked and cleared
Changed: cobot-rules: noticed_items (the text on the Noticed: line and its bullets, none is no item), park_noticed (cobot-memory noticed add in the payload's cwd, timeout 5 s, never raises), report() parks a passing report's items; cobot-memory: noticed add|list|clear on .agent/noticed.md (trusted memory only, dated, de-duplicated, control characters out, 300 characters an item), noticed.md in KNOWN_AGENT_FILES, check prints "noticed: N waiting"; wrap step 4 lists, files or drops, then clears; build step 4 parks an async hand-back's items itself; tests (rules parsing and hook, memory add/list/clear, untrusted, end to end, skill texts).
Why: F-48 (builder Noticed items never parked), story 3 of spec memory-and-ship (owner answer: the hook parks, wrap clears).
Proof: tests first (ten failing); full suite 3422 passed, 98.53 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate; the gate is silent on noticed clear.
Open: in a host where Agent returns "Async agent launched" (F-35) the hook sees no report, so the build skill parks the hand-back's items; T03–T07 of the spec.
Next: T03, the repeated-ask offer in the gate.
verified: tree ebca4ee720fac3f9661a0e409e1e8c5d82331905 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate

## 2026-11-18 — memory-and-ship T03: a repeated ask names its allow line
Changed: cobot-rules: OFFERED_ROWS (ask Bash(git commit*), ask Bash(git rebase*)), offered_rows (the winning default row and the rows in also, none the owner layer holds), the per-session counter in data_dir().parent/asks/<session>.json (UUID-shaped ids only, rule texts and counts, temp file and rename, files older than 7 days pruned), with_offer in gate(): from the third ask of an offered row the reason ends once with "· to stop asking: allow Bash(<pattern>) in <owner rules>", marked offered only when it fit; owner_rules_shown honours COBOT_RULES_OWNER and CLAUDE_CONFIG_DIR and shows ~ for home; docs/configuration.md.
Why: F-48 (four commit approvals with no allow line offered), story 2 of spec memory-and-ship (owner answer: offer after repeats); challenger 3 and 5: never an agent-scoped, outward, install or credential row, and the owner's real path.
Proof: tests first (four failing): third ask names the line, fourth does not; consultant curl and git push never offered; a new session starts at zero; rows in also count; a bad session id or a corrupt state file never blocks; old files pruned; with no room the next ask tries again; decisions unchanged (with_offer only appends to the reason); full suite 3428 passed, 98.50 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate.
Open: agy sends no session id, so no offer there; T04–T07 of the spec.
Next: T04, the promotion lint, every skill scanned, and the trust paths.
verified: tree 0706fcfa51ceb3e75747adc6c8de9782e7fbf950 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate

## 2026-11-18 — memory-and-ship T04: promotion lint, every skill scanned, trust paths shown
Changed: cobot-memory: promote_lint (run ids, a user's home path, release snapshots, the owner's owner/repo slugs from origin and the identities with the cobot checkout's own exempt, secrets, reported unless --allow-reported) and lint_context, inside promote_entries so the pending-lines path is linted too; --allow-reported threaded through cmd_learn; root commit and identity lines name their file; trust and check name the trust file when untrusted; trust_not_recorded's command carries CLAUDE_CONFIG_DIR when set (config_prefix); _cobot_knowledge: scan_plugin reads every skill, refreshed_by_learn, the brief's hint per kind; onboard step 2 re-checks after init and names the prefixed init command, never cobot-memory trust; tests; the old prefix-only scan test now expects every dated skill.
Why: F-42 (a slug, a run id, a snapshot and an unproven line promoted), F-46 (onboard's dated lines never in the brief), F-47 (init and check read different config folders); stories 4, 5 and 6 of spec memory-and-ship; challenger 4 and 5.
Proof: tests first (twelve failing): one per lint rule, clean lines with ~/ and the exempt slug pass, the pending path refuses a run id, an onboard reference is scanned and hinted, the trust lines name their files, the prefix appears only with the variable; full suite 3441 passed, 98.50 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate; cobot-memory knowledge --brief still fresh on the plugin.
Open: T05–T07 of the spec.
Next: T05, cobot-deps toolchain channels and ship's ground step.
verified: tree 1e8780298ec4ab9765c2848ec626810693c7bd2e · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate

## 2026-11-18 — memory-and-ship T05: cobot-deps toolchains, and a ship that checks its ground
Changed: _cobot_deps: floats, toolchain_versions and toolchain_rows (rust-toolchain.toml and rust-toolchain, .nvmrc, .node-version, .python-version, .tool-versions, mise.toml, .mise.toml, .config/mise.toml, mise/config.toml in string, list and table forms; go.mod without a toolchain line as a note), has_workflows, file_facts read fresh on a cached result too, report prints toolchain rows and the Actions hint only with a workflow; ship step 1 gains the toolchain, remote (get-url, then ls-remote with prompts off and a 20 s timeout; empty and unreachable told apart) and absent-tool checks, and the report's REMOTE and PINS lines; tests; the old check test now expects no hint without a workflow.
Why: F-37 (rust-toolchain on stable while CI took a newer release), F-43 (a PR proposed against an empty remote), F-48 (the Actions hint with no workflow, global unpinned installs); stories 7 and 8 of spec memory-and-ship; challenger 8 and 9.
Proof: tests first (seventeen failing): every file kind and form floats or passes, the go note, the hint only with a workflow, cached results re-read; ship text test names each rule; the gate is silent on the ls-remote form and git remote get-url; full suite 3459 passed, 98.49 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate.
Open: T06 (the ship-ground eval) and T07 (docs, decision 31, CHANGELOG, findings).
Next: T06.
verified: tree da47ace9ff42d90080baec91afd89fbd8571bd9e · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate

## 2026-11-18 — memory-and-ship T06: the ship-ground eval
Changed: evals/ship-ground (case, prompt, fixture, graders): a Rust library with rust-toolchain.toml on stable, committed memory with a wrap stamp, forge: github in CONTEXT, an empty bare origin at .git/remote.git, the root commit trusted as gitlab-ci-shape does; graders: toolchain-flagged and empty-remote regexes on last_message, remote-read (Bash input_match ls-remote), ship-skill; _cobot_deps: a cache that cannot be written (a read-only data folder, as in the eval sandbox) is reported as "cache: not written (<reason>)" instead of failing the check; a test for it.
Why: story 9 of spec memory-and-ship, proving story 8 (F-37, F-43) end to end; challenger 10.
Proof: the fixture run in scratch gives a clean tree, an empty remote (ls-remote exit 0, no output), stamp ok and the stable row; one local eval run scored 1.00 (4 graders, 0.11 USD, 19 s), and its trace shows cobot-deps, git remote get-url and the ls-remote form run, the empty remote told and main proposed first, no Rust version guessed; full suite 3463 passed, 98.49 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate. The read-only cache test was written together with its fix, not seen failing first.
Open: in that local run cobot-memory stamp answered "untrusted memory": the fixture's trust seeding (copied from gitlab-ci-shape) did not reach the run's config folder here; ship reported it and no grader depends on it; T07 remains.
Next: T07, docs, decision 31, CHANGELOG, findings closed.
verified: tree ee7778d84736d7571774cd37889e53aec8f74375 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, local eval

## 2026-11-18 — memory-and-ship T07: docs, decision 31, findings closed
Changed: docs/01-decisions.md decision 31 (one commit per verified change through the keyed tree stamp, parked notices, the offered allow line); docs/02-design.md (the journal stamp row, a noticed.md row); docs/configuration.md (noticed.md, the asks folder under XDG_DATA_HOME); CHANGELOG Unreleased (Added: one commit, notices, the offered line, ship's ground; Changed: promotion lint, every skill scanned, trust paths, cobot-deps); FINDINGS F-37, F-41, F-42, F-43, F-46, F-47 and F-48 closed; the spec's converge line.
Why: T07 of spec memory-and-ship.
Proof: full suite 3463 passed, 98.49 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate; cobot-memory check: 3 open findings of 49 (F-35, F-39, F-49, each its own spec).
Open: the eval's trust seed not seen in a local run (T06); F-35, F-39, F-49.
Next: owner pushes feat/memory-and-ship and opens its PR.
verified: tree ee7778d84736d7571774cd37889e53aec8f74375 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate

## 2026-11-18 — memory-and-ship: branch review folded
Changed: stamp_readiness reads git status -z as bytes, unstripped, and walks the records consuming each rename's or copy's source; tree_key reads ls-tree and feeds mktree as bytes; git() decodes with surrogateescape and git_bytes takes stdin; STAMP_RE reads 64-hex keys; noticed_refusal refuses a noticed.md that is a link or resolves outside the memory, and list and clear need a trusted memory too; promote_lint folds the text (URL-decoded, NFKC) and lints the checked field, RUN_ID_RE case-insensitive without a leading slash, HOME_PATH_RE adds /root/ and a home without a trailing slash but not a <user> placeholder, SNAPSHOT_RE wants a version or a date, slugs lose a trailing dot; _cobot_deps tolerates a mise tools or a rust toolchain value that is not a table; tests.
Why: an independent review of the whole branch found three HIGH (an unstaged first record read as staged, so stamp --tree said ready; the rename skip looked at the wrong record; noticed add wrote through a merged symlink), three MEDIUM (cobot-deps crashed on a wrong TOML shape; a non-UTF-8 name crashed the stamp; lint bypasses by case, encoding, fullwidth letters and wider phrasings) and LOW items.
Proof: tests first (twenty failing), each review input reproduced, H1 by hand in a scratch repo (now refused, exit 1); full suite 3481 passed, 98.50 %; ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate.
Open: kept as LOW: docs/ and .agent/cobot.rules sit outside the stamp key by design; submodule ignore=all hides a dirty submodule; parallel gate calls may lose an ask count; an offer that never fits is retried on each ask; .python-version 3.12 and rust 1.80 resolve to the latest patch but do not count as floating.
Next: owner pushes feat/memory-and-ship and opens its PR.
verified: tree c3bb687429dc6b4467d01ce9f01cc71ac65393ea · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude plugin validate, branch review

## 2026-11-18 — spec builder-proof-hosts (F-35), challenged
Changed: .agent/specs/builder-proof-hosts.md (revision 2, stories 1–7, T01–T05): a probe in a test project's settings.local measures the hook points in the desktop app first; PreToolUse on SubagentHandback checks a builder's report; one shared state (refusals by agent_id, hashes of allowed texts) so a report is judged once across paths; one refusal then through, marked UNPROVEN in the report itself and parked, failing open when no refusal can be recorded; SubagentStop only if the probe finds a host that needs it; the six skills carry two exact strings that check-plugin enforces; build step 3 refuses to tick an UNPROVEN task.
Why: F-35 (no builder report checked in the desktop app, where Agent returns "Async agent launched"); the owner answered three questions on 2026-11-18, all recommended: check every place a report is delivered, send it back, keep the parameter where the host has it and add the wait.
Proof: the Claude Code hooks and sub-agents docs read through the docs agent (SubagentHandback's message is the report; SubagentStop fields; run_in_background undocumented for Agent; the background case not covered); the challenger's SOUND WITH CHANGES (1 BLOCKER, 4 MAJOR, 3 MINOR) checked by hand before folding: claude plugin marketplace list shows cobot registered from the main checkout, r2.md dropped SubagentStop for the hand-back ambiguity, noticed add parks nothing in untrusted memory; spec 191 lines.
Open: the probe needs the owner to add a hook to a test project's .claude/settings.local.json and run one desktop session; agy not probed.
Next: owner reviews; then T01, the probe.
verified: tree c3bb687429dc6b4467d01ce9f01cc71ac65393ea · challenger pass, docs read

## 2026-11-18 — T02 builder-proof-hosts: the hand-back is checked, one shared state
Changed: plugins/cobot/hooks/hooks.json (PreToolUse on ^SubagentHandback$ runs report.sh handback); report.sh takes the mode as its argument, every failure still allows; cobot-rules: handback(), judge_report(text, agent_type, key, session) shared with report(), the per-session state in data_dir().parent/reports/<session>.json (refusals by key, allowed entries as key:sha256, written under an flock through a temporary file and a rename, a week kept, a bad file read as empty), one refusal then let through with UNPROVEN: in the message (updatedInput) or as additionalContext on the PostToolUse path, Noticed items parked detached from the hooks; report() keys by agentId, else tool_use_id; SESSION_RE anchored with \Z.
Why: F-35; the T01 probe showed the desktop app delivers a background builder's report only through the hand-back, that a deny reaches the builder and that updatedInput reaches the orchestrator.
Proof: tests first; the T02 review's 4 HIGH (an allowed id waving through later reports, the parallel race, a bad state disabling the check, no agentId losing the block), 2 MEDIUM (digest-only matching, a slow park timing the hook out) and 3 LOW (temporary files, the pruning race, a trailing newline in the session id) each reproduced as a failing test, then fixed; full suite 3497 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Open: LOW 11 accepted: a resumed session with a new id starts a fresh state, so a builder may be refused once more. probe/ is excluded locally in .git/info/exclude; remove the line with the worktree.
Next: T04, the six skills, build step 3 and check-plugin.
verified: tree b92df5884f2278cc6e1f3eb0a45ac0947f3e0ecc · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, T02 review folded

## 2026-11-18 — T04 builder-proof-hosts: the skills say what every host can do
Changed: the six skills that call Agent (build, consult, ship, security-sweep, wrap, spec) carry "`run_in_background: false` where the host offers it" and "wait for every hand-back"; security-sweep's "every unit's hand-back" reworded to match; build step 3 never ticks a report that starts with `UNPROVEN:` (re-run the task, or ask the owner); build's parking line says the hook parks from the Agent result or the hand-back, and only agy needs the manual noticed add; check-plugin's FOREGROUND rule requires both strings and names each missing one.
Why: F-35 story 6 and story 4's build rule; the desktop app has no run_in_background, so the wait is the rule that holds there.
Proof: tests first (five failing: one text test per skill rule, three check-plugin cases); the new check caught two real misses on its first run (spec's capitalised "Wait", ship's phrase split across a line), both fixed; full suite 3502 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Open: a text check cannot see a negation or a phrase split across lines; accepted in the spec.
Next: T05, docs, decision 32, CHANGELOG, F-35 closed.
verified: tree b878647bebb1cd48f5e41d3e1a34106ae1a5e4d3 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-18 — T05 builder-proof-hosts: decision 32, docs, F-35 closed
Changed: docs/01-decisions.md decision 32 (where a builder's report is checked: both paths, one state, one refusal then UNPROVEN, SubagentStop not used, agy requested not enforced); docs/architecture.md report-check row; docs/02-design.md layout (the hand-back hook, report.sh, SubagentStop dropped); docs/configuration.md the reports state under XDG_DATA_HOME; CHANGELOG Added entry; .agent/FINDINGS.md F-35 closed; the spec's build note (commits, T03 dropped, the T02 review's changes).
Why: spec builder-proof-hosts story 7.
Proof: markdownlint clean (one MD038 fixed); full suite 3502 passed, 98.46 %; ruff, check-plugin, sync-agents --check, claude and agy plugin validate; the tree key equals T04's, since only root doc entries changed.
Open: none for the spec; F-39, F-49 remain open findings.
Next: the owner reviews the branch, pushes feat/builder-proof-hosts and opens its PR; then remove the /probe/ line from .git/info/exclude with the worktree.
verified: tree b878647bebb1cd48f5e41d3e1a34106ae1a5e4d3 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-18 — spec trust-boundaries (F-49), challenged
Changed: .agent/specs/trust-boundaries.md (revision 2, stories 1–6, T01–T05): every spec carries a Trust boundaries section (each boundary the change creates or alters with its guard and a negative-test story, or none: with why); the challenger attacks a missed or unproven one as MAJOR; the sweep router passes Memory: trusted|untrusted from cobot-memory trust, and in trusted memory the auditor checks each declared guard at its site as inventory lines; two graders on medium-spec-then-challenge.
Why: F-49; the owner answered four questions on 2026-11-18, all recommended, and a fifth after the challenger pass: check declared guards, no found-not-declared lines.
Proof: the challenger's SOUND WITH CHANGES (3 MAJOR, 3 MINOR) checked by hand before folding: foreign mode's .agent is the owner's external memory (docs/02-design.md), a clone shipping .agent/ is the untrusted case, cobot-memory trust prints trusted:/untrusted:; spec 184 lines.
Open: none before the build.
Next: owner reviews; then T01.
verified: tree b878647bebb1cd48f5e41d3e1a34106ae1a5e4d3 · challenger pass

## 2026-11-18 — T01 trust-boundaries: the template and the spec skill ask for boundaries
Changed: skills/spec/template.md gains Trust boundaries after Stories and acceptance (the kinds, a row per boundary the change creates or alters as entry or crossing · guard · story, or one none: line); security-sweep/references/procedure.md inventories privilege lines, so both lists name the same kinds; spec SKILL.md step 2 notes the sites of each kind, step 3 fills the section with a guard and a negative-test story per boundary and a checkable reason for none:. New tests/test_spec_skill.py.
Why: F-49, spec trust-boundaries stories 1–2.
Proof: tests first (three failing for the right reason); the draft-step test then caught its phrase split across a line, rewrapped; full suite 3505 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Open: none.
Next: T02, the challenger's step.
verified: tree 43e94f746d16923e0a75616378ffa39643b26d32 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-19 — T02 trust-boundaries: the challenger attacks a change's boundaries
Changed: claude-agents/challenger.md method gains step 3: read the spec's Trust boundaries; from the stories and the lines the change touches, a boundary it creates or alters that the section misses, or one without a guard or a negative-test story, is MAJOR, as is a none: the stories contradict; a boundary the change does not touch is not an objection. agents/challenger.md regenerated by sync-agents. tests/test_spec_skill.py checks the step in both twins.
Why: F-49, spec trust-boundaries story 3.
Proof: test first (both twins failing, no such step); full suite 3507 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Open: none.
Next: T03, the sweep's Memory line and declared-guard check.
verified: tree 1a6ac48fb53ec1cc8db0b0c908eeda28cf105ce4 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-19 — T03 trust-boundaries: the sweep checks declared guards, in trusted memory only
Changed: security-sweep SKILL.md gains Memory trust: the router runs cobot-memory trust once and puts Memory: trusted or untrusted into every unit's prompt, untrusted when the check did not run or failed. procedure.md gains Declared boundaries under the inventory: with trusted memory, read the specs' Trust boundaries and check each declared guard at its site under the unit's paths (declared guard missing: <boundary> · <file>:<line>; declared, site gone: N); inventory lines, never findings; a spec without the section is skipped; untrusted memory reads no spec (declared: not read (untrusted memory)). Both report templates carry a declared: line so the lines reach the owner (not named in the spec; the inventory had no other place in the reports).
Why: F-49, spec trust-boundaries story 4.
Proof: tests first (two failing for the right reason); full suite 3509 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Open: none.
Next: T04, the eval graders.
verified: tree 6ce92470e62f790d55b1cb1e9b4166b4107586c0 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-19 — T04 trust-boundaries: an eval shows an agent writes the section
Changed: evals/medium-spec-then-challenge prompt names the spec's path, .agent/specs/config-loader.md; two file graders on it: boundary-section (a regex scoped to the section, wanting env, environment or config file; flags: i, which the spec did not name, so a capitalised table cell counts) and boundary-not-none (not_contains a none: line under the heading). tests/test_eval_graders.py: matches() on a row (passes) and on a none: line, the word only in another section, and no section (each fails a grader); a test that the prompt and both graders name the same path.
Why: F-49, spec trust-boundaries story 5.
Proof: tests first (five failing for the right reason); full suite 3514 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate; one local eval run (--runs 1, sonnet-5-5, judge haiku-5-5): score 1, all nine graders passed, the seven old ones unchanged. CI runs the case's three.
Open: none.
Next: T05, decision 33, design rows, CHANGELOG, F-49 closed.
verified: tree da5ab11d50f276edd1df3564947d95bfc0acb705 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, local eval medium-spec-then-challenge 9/9

## 2026-11-19 — T05 trust-boundaries: decision 33, design rows, F-49 closed
Changed: docs/01-decisions.md decision 33 (a spec names its trust boundaries; the challenger attacks a missed or unproven one; the sweep checks declared guards from trusted memory only, as inventory lines); docs/02-design.md the medium path row names the section and the medium-spec-then-challenge eval row its two graders; CHANGELOG Added entry; FINDINGS F-49 closed; the spec's Built note, with the two additions (declared: report lines, the case-insensitive grader).
Why: F-49, spec trust-boundaries story 6.
Proof: full suite 3514 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate; cobot-memory check: 1 open finding of 49 (F-39), brief 5818 of 6000 chars.
Open: cobot-memory check warns JOURNAL.md is over 400 lines (compact is the owner's call).
Next: the owner pushes feat/trust-boundaries and opens its PR.
verified: tree da5ab11d50f276edd1df3564947d95bfc0acb705 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate, cobot-memory check

## 2026-11-20 — spec session-grants (0.4.0), challenged
Changed: .agent/specs/session-grants.md revision 2 (299 lines): gcloud, kubectl and helm grants per kind (deletes separate) on one explicit target, recorded by a PostToolUse hook only against a pending entry the gate wrote when it asked, main thread and Claude Code only; the gate emits allow for a covered command only (ADR-0008, decision 34 planned); grant_scope as allow-lists of groups, verbs and options; Terraform apply and destroy move from never to a prompt-only ask, never granted; the never list grows (state surgery and -lock= false spellings, token and secret printers, kubeconfig writes, cluster wipes, rm -rf of / and home, owner rule files from config_dir(), shell writes to never paths denied). T01 probes P1-P7 first.
Why: 0.4.0 scope (owner, 2026-11-14), design input owner-ideas-03 §4; owner answers 2026-11-20: Claude Code only, deletes separate, gate tests plus apply-asks eval, no Terraform grants.
Proof: two cold reads of the gate and docs; challenger RETHINK (2 BLOCKER, 6 MAJOR, 1 MINOR) and a CLI consult against upstream docs, every claim re-checked by gate dry runs, all folded; Terraform answer asked after BLOCKER 2.
Open: the probe (T01) can still stop the design (P1, P2, P6).
Next: T01, the probe.
verified: tree da5ab11d50f276edd1df3564947d95bfc0acb705 · spec only, no code; gate dry runs of the challenged commands

## 2026-11-20 — T01 session-grants: the probe's findings
Changed: .agent/specs/session-grants.md Converge holds P1–P7; story 1 points there; story 5 records a grant on PostToolUse with CLAUDE_CODE_SESSION_ATTENDED=1 (no mode check, no exit-code field: PostToolUse fires only on success); trade-offs gain the session id in Bash, the SDK host, and a grant never beating a settings ask or deny.
Why: spec session-grants story 1: recording rests on P1, P2, P6.
Proof: Claude Code 2.1.326, a log-only probe plugin by --plugin-dir and rules by --settings (no settings file touched), scratchpad only. Six headless runs: hook ask never ran in any mode, bypassPermissions included, even with a settings allow; hook allow ran an unmatched command but lost to a settings ask and a settings deny; PostToolUse absent for a failed ls; subagents (general-purpose, Explore, background, context: fork) carry agent_type and agent_id, the main thread neither; resume keeps the session id; SessionEnd fires with reason; export does not persist; ATTENDED 0 headless, ENTRYPOINT inherited from the parent. The owner in the interactive CLI saw a prompt in auto, acceptEdits, plan and bypassPermissions; ATTENDED 1 there and in the desktop app.
Open: workflow agents not probed; default mode not run interactively (the owner's default is auto). A grep of this session's env printed CLAUDE_* values into the local transcript (a broken pattern); a stray sed -i on /dev/null failed and edited nothing.
Next: T02, the never additions and the prompt-only apply.
verified: tree da5ab11d50f276edd1df3564947d95bfc0acb705 · spec only; probe logs in the session scratchpad

## 2026-11-20 — T02 session-grants: the never list grows, apply and destroy prompt only
Changed: default.rules: never rows for Terraform, tofu and terragrunt state surgery (state rm|mv|push|replace-provider, force-unlock, import, taint, untaint, workspace delete -force, -lock= false spellings), state buckets, projects delete, set-iam-policy, keys create, the gcloud and kubectl credential printers (were asks), kubectl create token, kubectl config writes, Edit/Write of ~/.kube/*, cluster-wide deletes (-A or --all-namespaces, kube-system), rm -* of / ~ ~/ $HOME, Edit/Write of ~/.claude/cobot.rules and cobot/*, agent reads of ~/.kube; apply and destroy move from never to asks noted "prompt only". cobot-rules: resolve() puts a prompt-only default ask above every allow; read_layer adds a CLAUDE_CONFIG_DIR twin of each ~/.claude file row (moved root computed once per layer); protected_verdict denies a literal shell word on the sealed owner files, or a move, copy or delete into their folder, and keeps the ask for holes, globs and other protected files. New tests/test_session_grants.py (90); existing gate tests: apply rows ask, the bypass corpora retargeted from apply to import (still never), cloud credential printers split into a deny list, set-iam-policy deny, and the F-33 cases that reach home or root deny (REACHES_OWNER_FILES).
Why: spec session-grants stories 2 and 3 (challenger 3, 4, 7, 8).
Proof: tests first (71 failing for the right reason, neighbours passing); full suite 3605 passed, 98.46 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate. Gate timing: load_rules was 5x slower from a per-rule config_dir() call, fixed; judge_bash about 20 % slower from the extra rows.
Open: narrower than the spec text (now reworded): only cobot's owner files are sealed to shell, settings.json keeps its ask; kubectl delete -A is never even without --all (wider). The agents' Read tool on ~/.kube is not gated (the gate judges no Read).
Next: T03, grant_scope.
verified: tree 006a47d8c9b34168ceb415e7abad897f555870aa · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-20 — T03 session-grants: grant_scope, allow-lists only
Changed: cobot-rules gains a session-grants section: grant_scope(command) -> (kind, target) | None and valid_grant(kind, target). A command is covered only when its raw text is plain (a character allow-list: no quote, $, glob, operator or assignment; rtk the only wrapper), no word holds projects/, gs:// or ://, and its tool's allow-list matches: gcloud command paths (compute, run, pubsub, functions, artifacts, dns, container clusters and node-pools) with create, update, deploy (gcloud) or delete (gcloud-delete) and --project once, refusing --flags-file, --configuration, --impersonate-service-account, --account, --access-token-file and any abbreviation of them or of --project; kubectl apply/create -f, patch, label, annotate, set image (kubectl) and delete, scale, rollout restart (kubectl-delete) with --context once and only allow-listed options; helm install, upgrade, rollback (helm) and uninstall, del, delete, un (helm-uninstall) with --kube-context once. Files must stay inside the repository. Targets: project id or context format. The signature drops the spec's cwd: Terraform is out, and the path check is lexical.
Why: spec session-grants story 4 (challenger 1 and 7, the CLI consult).
Proof: tests first (101 failing for the right reason). A self-attack found a real bypass: kubectl --dry-run takes an optional value, so "--context lab --dry-run --context prod" read as lab while kubectl acts on prod; fixed by dropping --dry-run and refusing any option value that starts with "-", with tests for it and the gcloud abbreviation. 199 session-grant tests; full suite 3714 passed, 98.47 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Open: gcloud flag abbreviation is guarded without knowing whether gcloud accepts it (defensive). kubectl patch with an inline -p JSON is not covered (quotes), only --patch-file.
Next: T04, the grant verb, pending entries, the store and the hooks.
verified: tree 35d651bc3c2b15c012360dc4c2db45c46815f524 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-20 — T04 session-grants: the grant verb, pending entries, the store and the hooks
Changed: cobot-rules: grant_request parses the cobot-rules grant family (grant, revoke all or one, list; anything else starting like one is malformed); the gate answers it before any rule: malformed, a subagent, an unknown kind or target, or no valid session is denied; revoke and list are silent; a grant request asks with a rule-less reason after writing a pending entry {digest, kind, target, time}; under agy it is denied (Claude Code only). posttool (PostToolUse Bash, prefix check first) records a grant only for a fresh pending entry with the same digest, on the main thread (no agent_id, agent_type absent or null), with a valid session and CLAUDE_CODE_SESSION_ATTENDED=1; revoke narrows; sessionend removes the session file. The store is <config dir>/cobot/grants/<session>.json, read as empty on any defect, written under a lock with the report state's rename-and-prune. cobot-rules grant prints the request and writes nothing; --list reads the file via CLAUDE_CODE_SESSION_ID. hooks/grant.sh (exit 0 on every path) and hooks.json entries for PostToolUse ^Bash$ and SessionEnd. Spec: main thread is the strict reading (an empty agent_type is an agent, which the old wording contradicted), --list reads the file itself.
Why: spec session-grants story 5 (challenger 5, 6, 9; probe P1, P2, P4, P5, P6).
Proof: tests first (39 failing for the right reason, 6 passing for today's behaviour); 46 store tests; the real hook scripts run end to end in a scratch config dir (ask, record, list, SessionEnd removal); full suite 3760 passed, 98.42 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate.
Open: accepted residual: the gate killed by its timeout after writing the pending entry, with an owner settings allow on cobot-rules, could run the command without a prompt and record it (microseconds, needs the owner's own allow line). The log list is kept but not filled until T05.
Next: T05, the gate's allow for a granted command.
verified: tree d4c5e5c68b6aec1dafaa791f52f692631086217b · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-20 — T05 session-grants: the gate allows a granted command, and only one
Changed: cobot-rules gate(): granted_reason lifts a Bash verdict to allow only when it is an ask from a default row (not never, not prompt-only, not rule-less, no second ask), the call is from the main thread, grant_scope names a (kind, target) this session holds unexpired, and the owner and project layers alone neither ask nor deny on the command (a verdict names only its first rule, so an owner ask would hide behind the default one). Reason: cobot grant: <kind> on <target> (cobot-rules grant --revoke). posttool logs each command that ran under a grant (200 kept, 200 characters each); --list prints them as ran: lines. The module docstring's contract names the one allow. The allow pin becomes test_gate_neverEmitsAllow_withoutAGrant; agy unchanged (test_corpus_noAnswerEverAutoApproves stands). The unused GRANT_STATE_DAYS went.
Why: spec session-grants story 6.
Proof: tests first (the 3 positive cases failing, the 14 near-misses already asking or denying); 63 store tests; the real hook scripts end to end (grant, allow on lab, ask on prod and on another kind, the log listed); full suite 3777 passed, 98.43 %; ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate; gate timing unchanged.
Open: none.
Next: T06, the protocol and skill texts.
verified: tree a1ca27f7c1a768b6eeee8f6c6a40d66fdd384cd0 · pytest+cov, ruff, markdownlint, check-plugin, sync-agents --check, claude and agy plugin validate

## 2026-11-20 — session grants T06: protocol and skill texts
Changed: protocol.md gains a Grants paragraph (one AskUserQuestion with three answers, main thread only, plan -out then apply at the prompt, the lab log); apply leaves the outward list; lang-terraform, terraform-builder (synced), ship, expert-gcp, expert-kubernetes and README no longer say the gate denies apply, and the two expert skills document the grantable forms and the lab log; check-plugin's protocol cap is 3400.
Why: spec session-grants story 7; owner's answer 5 raised the cap (the protocol reached 3400 chars).
Proof: 3800 passed, coverage 98.43%; tests/test_grant_texts.py 23 passed (documented forms checked against grant_scope); ruff check and format, markdownlint, check-plugin (protocol 3400 chars), sync-agents --check, claude plugin validate --strict and agy validate (1 warning) all pass; documented verdicts dry-run with cobot-rules check.
Open: docs/02-design.md and docs/architecture.md still say a 3k protocol (T08).
Next: T07, the apply-asks eval.
verified: tree 7c479907b77193cbf4d55c446e328256210e014c · full suite, lint, contract and validate
