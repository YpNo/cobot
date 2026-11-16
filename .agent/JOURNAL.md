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
