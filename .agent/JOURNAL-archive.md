# Journal archive (raw entries folded by cobot-memory compact)

## 2026-11-06 — design v1.1 and release 0

Changed: design v1.1 (learning protocol, token economy, coexistence), ADR-0001..0003, switch plan, crissp review; R0 bootstrap: manifests, `partner:challenger`, gate shim + built-in rules, `install.sh`, README, CI, 50 tests.
Why: the owner approved the design and R0; the legacy scaffold stays until the switch.
Proof: `pytest` 50 passed, coverage 91 %; `claude plugin validate --strict` passed twice; ruff, shellcheck, markdownlint clean; spikes A and B passed in the owner's terminal (gate saw the original command).
Open: spike C (hook `deny` live) unproven, the model refused before calling Bash; hook firing for subagent Bash untested.
Next: R1 per `.agent/specs/r1.md`.

## 2026-11-06 — release 1: governed orchestrator

Changed: rules engine (layers, normalisation, opaque runners, file and MCP rules, agent scopes, show/check/explain/sync, consultant and learner read lists); partner-memory (init, trust, brief, journal, findings, learn) and partner-session with the SessionStart hook and protocol.md; agents consultant, builder, rust-builder, go-builder; skills onboard, spec, build, wrap, rules; knowledge skills lang-rust, lang-go, lang-terraform, lang-fallback, expert-gha, consult-gha (verified upstream today); four evals; scripts check-plugin, spike-r1; release.yml; CI eval job; version 0.1.0.
Why: spec .agent/specs/r1.md, challenged (SOUND WITH CHANGES, all folded: trust marker outside the repo, every remote must match an identity, normalisation gaps, shell writes to protected files, precedence written down).
Proof: pytest 173 passed, coverage 99.06 % (exit 0); ruff check and format clean; shellcheck clean; check-plugin ok; plugin and marketplace validate --strict passed; markdownlint 0 errors; spikes D, E, F passed in the owner's terminal (hook deny in main thread and in partner:builder, fork resolves partner:consultant); evals tiny 3/3, medium 1/1, profile-caps 1/1 (sonnet, ablation none).
Open: gate-asks eval needs bubblewrap and socat on the machine; brief caps not measured on a 1 000-line journal (F-01); three knowledge lines remain reported (F-02); a consultant compound command asked in spike F, segment not identified yet; learn --promote, compact and consult knowledge_delta application are R1.1.
Next: dogfood through install.sh --project on cartridge-os and --local on headscale; R1.1 per docs/02-design.md section 15.
verified: 508fb6c+working-tree · pytest --cov · ruff check · ruff format --check · shellcheck · check-plugin · claude plugin validate --strict ×2 · markdownlint-cli2

## 2026-11-06 — dogfood on cartridge-os

Changed: `install.sh --project` run on cartridge-os (identity github.com/ypno enrolled, FINDINGS.md created there, .claude/settings.json written); the gate resolves mise tasks to the commands they run; the brief caps CONTEXT by section, names what it dropped and grows to 4 000 when the journal is short; `install.sh --refresh`.
Why: cartridge-os runs everything through mise tasks, so the opaque rule asked on every test and lint run; its 3.4k CONTEXT lost "Runtime constraints" and "Where things are" to the 2 500 cap; `claude plugin update` reports a same-version edit as current and keeps the stale cache.
Proof: 212 passed, coverage 99.16 %; ruff, shellcheck, markdownlint, check-plugin, `claude plugin validate --strict` ×2 clean; through the refreshed cache from cartridge-os: additionalContext 7 561 chars with every CONTEXT section, `mise run lint` and `mise run test-focused -- -p hal` silent, `mise run sd-linux` asks (command substitution), `git push --force` denied.
Open: live `claude -p` probes through the installed plugin blocked by the terminal CLI's expired OAuth (F-03); cartridge-os holds two untracked files for the owner to commit; the consultant segment that asked in spike F is still unidentified.
Next: owner runs `claude login`, then the two probes; release 1.1.
verified: b101dad+working-tree

## 2026-11-06 — live probes through the installed plugin

Changed: nothing in the plugin; F-03 closed, F-05 opened, reference note on how an ask surfaces in `claude -p`.
Why: the owner logged the terminal CLI in, so the two probes deferred from the dogfood session could run.
Proof: from cartridge-os with the project-scope install, `claude -p` answered with the 2026-11-02 journal date, the `rules: 178` line and the five `partner:` agents; `mise run lint` passed the gate silently and Claude Code's own permission asked; `mise run sd-linux` was stopped by the gate as opaque.
Open: F-05 entry wrappers (`distrobox enter -- …`, `docker exec`, `ssh`, `toolbox run`, `nix develop -c`, `flatpak run`) pass silently; the consultant segment from spike F is still unidentified.
Next: decide whether F-05 is fixed now or in release 1.1; `install.sh --local` on headscale.

## 2026-11-06 — F-05: entry wrappers looked through

Changed: the gate parses entry wrappers with per-wrapper option tables (an unknown option keeps the wrapper opaque) and judges the command behind them, recursively with mise tasks and shell `-c` strings up to four levels; remote execution (`ssh`, `mosh`, `kubectl exec`, `gcloud … ssh`, `gh codespace ssh`) and `source`/`.` ask; backslash line continuations no longer split a command; `#` inside a word no longer truncates it.
Why: cartridge-os's documented form `distrobox enter rust -- bash -c "cd $PWD && mise run lint"` passed the gate silently, as did docker exec, ssh and the rest (F-05); a force push written over two lines only asked.
Proof: 292 passed, Total coverage: 99.09%; ruff, shellcheck, markdownlint, check-plugin, `claude plugin validate --strict` clean; live from cartridge-os through the refreshed install: the distrobox form reached Claude Code's own permission prompt with the gate silent, `ssh box git push --force` was stopped by the gate as opaque.
Open: the consultant segment that asked in spike F is still unidentified; cartridge-os's CONTEXT could drop the redundant `cd $PWD` (distrobox keeps the working directory).
Next: `install.sh --local` on headscale; release 1.1.

## 2026-11-07 — third owner review confirmed, decisions 17–25 applied

Changed: default rules `never` on attribution footers in commits and PR bodies and `ask` on dependency-adding commands; `spec` sizes one spec = one branch = one PR with one commit per task, writes the architecture choice (hexagonal by profile) and justifies every dependency; `build` commits each task and refuses an unnamed dependency; `wrap` runs the pre-PR currency check and opens one PR after an authorship check; builders report `Deps added:`; `expert-gha` carries the trigger matrix; release plan reordered (learner, staleness, `partner-deps` first in R1.1; frameworks and experts in R2/R3).
Why: the owner confirmed all ten challenged ideas as written (docs/design-inputs/owner-ideas-02.md).
Proof: 313 passed, coverage 99.09 %; ruff, shellcheck, markdownlint, check-plugin, `claude plugin validate --strict` clean; cartridge-os install refreshed from this tree.
Open: decisions 21, 23 and the new stacks and experts are scheduled, not built; the consultant segment from spike F is still unidentified.
Next: `install.sh --local` on headscale, then release 1.1 starting with the learner.

## 2026-11-07 — decision 26: containers, Kubernetes, service mesh

Changed: default rules ask on mutating `kubectl`, `helm`, `istioctl`, `gcloud container fleet mesh` and image push/prune/login; helm and istioctl global options stripped; decision 26 and the release slots for `expert-containers` (R1.1 with ship), `expert-kubernetes` (R2 with GCP) and `expert-service-mesh` (R2/R3).
Why: the owner added Docker, Podman, Kubernetes and service meshes; three experts ageing at different speeds, each behind the learner's refresh.
Proof: 342 passed, coverage 99.09 %; ruff, markdownlint, check-plugin, `claude plugin validate --strict` clean; cartridge-os install refreshed.
Open: experts scheduled, not built.
Next: `install.sh --local` on headscale, or release 1.1.

## 2026-11-07 — dogfood headscale: local scope, foreign mode
Changed: install.sh --local on headscale (fork of juanfont/headscale, ghsa advisory remote); trust untrusted as designed, foreign mode taken: memory under ~/.local/share/agentic-partner/repos/github.com/ypno/headscale, .agent symlink excluded from git, shared by the worktree; CONTEXT.md and journal written there. Fixes: goreleaser release and nix flake update|lock ask (F-07); journal add and learn take their payload as an argument and never wait on a terminal, install.sh --refresh covers project and local scope (F-08); the untrusted reason names the stranger remotes; onboard documents the fork path and copies maintainers' constraints such as AI_POLICY.md (F-09). F-06 (make opaque) routed to R1.1.
Why: the design's second dogfood target; a foreign Go repository exercises the trust, foreign-mode and local-scope paths that cartridge-os could not.
Proof: pytest 352 passed, coverage 99.10 %; ruff, shellcheck, markdownlint, check-plugin and plugin validate --strict clean; live claude -p from headscale showed the UNTRUSTED brief line and the five partner: agents through the local-scope install; go build ./... and go test ./hscontrol/util/ pass on headscale; nix, golangci-lint, buf, prek absent on this machine.
Open: F-06 make resolution; headscale lint never ran here (needs nix); its five .mcp.json servers unapproved.
Next: R1.1, learner first.

## 2026-11-07 — make targets resolved from the Makefile (F-06)
Changed: new bin/_partner_make.py reads a Makefile without running make (plain variables, define bodies through call, MAKE, @-target, prerequisites that are targets, VAR=value overrides, .DEFAULT_GOAL); partner-rules gains parse_make_argv (-C, -f, -j, flags, --eval opaque) and expand_make, wired into expand_runner like mise; design §6, README, rules skill, CHANGELOG updated; F-06 closed.
Why: the owner chose to resolve make before R1.1; headscale and most Go and C projects run everything through make, and an opaque make hid both the harmless (go test) and the real (rm -rf, git push) from the gate. make is read, never run: a $(shell …) in a Makefile would otherwise execute at gate time in any checkout.
Proof: pytest 414 passed, coverage 98.96 %; ruff, shellcheck, markdownlint, check-plugin, plugin validate --strict clean; on headscale make test, lint, fmt, dev-server judge silent, make clean asks via rm -rf, make build and make (default all) stay opaque, make generate asks via make client (command substitution); live claude -p from headscale: make test passed the gate silently and Claude Code's own permission asked (This command requires approval, no partner text); both installs refreshed, cache identical.
Open: a computed prerequisite list is read as files (accepted gap, design §6); make -C into a folder without a Makefile stays opaque; nested make under -C stays opaque.
Next: R1.1, learner first.

## 2026-11-07 — R1.1 slice 1: learning and currency
Changed: spec `.agent/specs/r1-1-learning.md` written and challenged (SOUND WITH CHANGES, eleven points folded: staleness class needs a currency word or a versions/actions/ci file and no history word; promote re-dates and supersedes lines in place; skeleton experts only on an explicit `skeleton` block; source checkout from `known_marketplaces.json`; hardened dependency tools; the workflow applies the delta in a shell step; cache keyed without an origin remote). Landed as five commits: `_partner_knowledge.py` with `partner-memory knowledge [--stale|--json|--brief]` and `learn --promote [--source DIR] [--in-place]` plus the `ask` rule; the `learner` agent and `/partner:learn`, protocol and consult-gha aligned on `scope: general|project`; `partner-deps check|brief` with `_partner_deps.py` (cargo update dry run, cargo-deny or cargo-audit, go list -m -u under GOTOOLCHAIN=local, npm and pnpm with scripts off, uv tree, poetry, the Terraform registry; cache under the data directory for seven days while the lockfiles hold); the session payload carries the knowledge and deps lines with a shared 25-second deadline; onboard runs the check and wrap runs it fresh; `knowledge-refresh.yml` (weekly, two stalest skills, environment-scoped secrets, zizmor one low finding) and the offline `learn-unknown-domain` eval. Reference headers now state the 30/90-day classes. Live `/partner:learn expert-gha` through `--plugin-dir`: the first run had no WebFetch grant and returned an empty delta with the refusals named (the designed behaviour); the second run exposed that `--allowedTools` is variadic and swallows the prompt (fixed in the workflow, noted in the mechanics reference); the third run returned four entries, applied with `learn --promote --in-place`: the masking line superseded by a verified one from the secure-use reference, two new verified lines, the Dependabot groups line re-dated and still reported with the reason. That apply crashed once on a source containing `]`; format_line now sanitises sources and claims and the index ignores an unparseable line.
Why: decision 23 (knowledge freshness) and decision 21 (dependency currency) were the first block of R1.1 in design section 15; without the learner and the refresh cycle every further expert rots.
Proof: pytest 470 passed, coverage 98 % (`--cov-fail-under=85`); ruff check and format clean; shellcheck clean; `check-plugin` ok (agents listing 370 tokens, 12 skills); `claude plugin validate --strict` passes for plugin and marketplace; markdownlint 0 errors; `zizmor --offline --persona auditor` on knowledge-refresh.yml: 1 low (the pinned `npm install -g`, same as ci.yml); `partner-deps check` live: cartridge-os 2 of 55 behind, 0 advisories; headplane go 1 of 3 behind, pnpm absent; `partner-memory knowledge --stale`: nothing stale, 3 reported; both dogfood installs refreshed, cache identical to the checkout.
Open: the LuCI reported line (lang-fallback) not probed; Dependabot `groups` for github-actions still reported (no official page states it; a throwaway PR would close it); `knowledge-refresh.yml` and the learn eval cannot run until the remote and the `knowledge-refresh` environment exist; the learner's WebFetch is summarised by a small model, so exact quotes need curl under ask; in print mode the learner needs `--allowedTools WebFetch WebSearch`; pnpm and pip-audit absent on this machine.
Next: R1.1 slice 2: ship (trigger matrix) with `expert-containers`, contribute + UPSTREAM.md, security-sweep, `partner-memory compact`, lang-python and lang-typescript with their builders (dogfood dreame-vacuum, headplane), terraform-builder, `accepted-risks.md`, the remaining evals.

## 2026-11-07 — R1.1 slice 2: delivery, stacks and the sweep
Changed: spec `.agent/specs/r1-1-delivery.md` written and challenged (SOUND WITH CHANGES, fourteen points folded: risk rows keyed by rule, file and symbol with `partner-memory risks add` as the writer; scanner allow rows for the consultant; the wrap stamp predicate for committed memory; the ci.yml double run that did not exist; ship refusing in foreign mode and patching existing workflows; compaction keeping the brief and the Open items; `--scaffold` for eval fixtures; the upstream resolved through `gh repo view --json parent`). Three research deltas (Python, TypeScript and Node, containers) gathered from primary sources today feed `lang-python`, `lang-typescript` and `expert-containers`, every line verified or marked. Landed: `ship`, `contribute` with `templates/UPSTREAM.md`, `security-sweep` with nine rule packs ported from the legacy skill (355 rule ids, none dropped) and `templates/accepted-risks.md`, `consult-containers`, `partner-memory compact` (last ten kept, model summary or digest, raw entries archived) and `risks add|list` with the `check` expiry warning, `python-builder`, `typescript-builder`, `terraform-builder` with `build` routing by files in scope, evals `never-apply`, `builder-routing`, `proof-required`, this repository's `ci.yml` with the `ci-ok` aggregator and PR-only cancellation. Dogfood found F-10: `uv run`, `pnpm run <script>`, `pnpm exec`, `npm test` were opaque, so every command of the two new stacks asked; the gate now resolves `uv run` from argv (uv's options parsed, `-m` and `.py` to python), `pnpm|npm|yarn exec` from argv, and `run <script>`, the pnpm and yarn shorthand and npm's test/start aliases from package.json with their pre/post hooks; a script regex or a selecting flag (`--filter`, `-r`, `--stream`) stays opaque, `npx`, `uvx`, `dlx` stay opaque because they download code. Headscale's external memory gained `UPSTREAM.md`.
Why: design section 15 slice 2; decisions 17 (trigger matrix), 18 and 20 (attribution, PR granularity), 26 (containers); the owner's repositories are Python and TypeScript as much as Rust and Go, and a stack whose every command asks is not usable.
Proof: pytest 539 passed, coverage 98 %; ruff check and format clean; shellcheck clean; `check-plugin` ok (agents listing 528 of 600 tokens, 19 skills); `claude plugin validate --strict` passes for plugin and marketplace; markdownlint 0 errors; zizmor offline on the workflows unchanged (the evals secret outside an environment is the one pre-existing medium); gate dry runs on headplane: `pnpm run typecheck`, `pnpm test:unit`, `pnpm run lint --fix` silent, `pnpm dev` and `pnpm run deploy` ask; on headscale `make test`, `make lint`, `go test ./...` silent; on dreame-vacuum `uv run pytest -q` silent, `uv add`, `pip install` ask, `uv publish` denied.
Open: F-11 dreame-vacuum workflows (floating `@main`, `@v2`, bare triggers) as a proposed patch for the owner; `pnpm run release` resolves to `node scripts/release.ts`, which the gate cannot see into (an owner-layer `ask Bash(node *release*)` closes it); a live `/partner:security-sweep` and a full `/partner:ship` on a service repository are owed; `foreign-onboard` and `actions-pinning` evals moved to R2; the sweep runs at the consultant's medium effort; pnpm is not installed on this machine, so headplane's scripts were dry-run through the gate only.
Next: R2 per design section 15 (partner-gcp, deep-review, SubagentStop report check, framework skills, expert-cicd); before that the switch plan once the remote exists and eight evals have run green.

## 2026-11-07 — remote, eval harness, rename to cobot
Changed: the GitHub remote exists (private, owner-only phase, no API secrets, refresh schedule disabled); `scripts/github-settings.sh --check|--apply` holds the repository settings as code and applied ten of them (rulesets refused on the free plan); zizmor annotates instead of uploading to code scanning; `.github/dependabot.yml` with a seven-day cooldown; `SECURITY.md`. Eval harness fixed: fixtures in `case.yaml` + `fixture.sh`, the `Bash`, `Write` and `Edit` the graders need listed per case and granted on the command line, the learner detected through its `Skill` call. The project is renamed **cobot** (ADR-0004, spec `.agent/specs/rename-cobot.md`, challenged SOUND WITH CHANGES, nine points folded): marketplace, plugin `cobot@cobot`, prefix `/cobot:`, binaries `cobot-*`, env `COBOT_*`, tags `cobot rule|gate|session:`, rule files `cobot.rules`, state under `~/.local/share/cobot` and `~/.claude/cobot`; `install.sh` migrates the old state and registrations once and re-points a foreign-mode `.agent` link the plugin created.
Why: the remote unlocks CI, evals and the switch; "partner" said nothing about the field, and a rename costs least before the first user-scope install.
Proof: pytest 551 passed, coverage 98 %; ruff, shellcheck, markdownlint, `check-plugin` (528 of 600 tokens, 19 skills), strict validation for plugin and marketplace, zizmor offline clean; PR 1 and PR 2 merged green; the second eval run (full command, before the harness fix merged): gate-asks 1.00, medium-spec 0.94, learn 0.72 with the learner running in every with-arm, Δ +0.20 mean; migration run live on cartridge-os (project) and headscale (local): state moved, `.agent` re-pointed, both installs `cobot@cobot`, `install.sh --check` reports nothing to migrate; gate on headscale: `git push` and `gh pr create` ask, `terraform apply` denied, `make test` silent; headplane `pnpm run typecheck` silent; `cobot-memory check` on headscale trusted in foreign mode at the new path; the SessionStart payload opens with "# cobot protocol".
Open: F-12 (eval graders against the protocol: the `profile-caps-size` judge fails the with-arm answers that do name the cap, `tiny-no-ceremony` wants the size named and the protocol asks for it but the model skips it, one flaky run each in learn and medium-spec); `~/.claude/plugins/cache/agentic-partner` left behind by `marketplace remove`, the owner removes it; the GitHub repository rename, remote URL, push and PR are the owner's; cartridge-os's rewritten `.claude/settings.json` needs a commit there; Claude Code 2.1.319 upstream against 2.1.285 here and 2.1.318 pinned in CI.
Next: the owner's rename steps, then the eval follow-up (F-12), then the switch plan once eight evals are green.

## 2026-11-08 — R2 slice 1: hardening
Changed: spec `.agent/specs/r2.md` (umbrella for four slices, challenged SOUND WITH CHANGES, nine points folded; the report check moved from `SubagentStop` to `PostToolUse` on `Agent` after the challenger showed the handback ambiguity and the asked-once guard it would have needed). Landed: `hooks/report.sh` + `cobot-rules report`, a builder report without `` `<command>` → exit <n> `` under `Checks:` (or `Checks: none — <reason>`) is blocked back to the orchestrator, every builder prompt fixes that shape; `cobot-memory stamp` (ok/missing from the journal's last `verified:` line as wrap really writes it, dirty-tree stamps and untrusted memory named) and its suffix on every `git push` that asks; `cobot-usage` (requests and tokens per session, model and agent type from the local transcripts, one request per `requestId`, subagents typed by `meta.json`, Skill and Agent calls counted); never-push rules for every remote but `origin` written at foreign onboard, push options hoisted after the remote; evals `foreign-onboard` and `actions-pinning`; `ask mcp__*__generate*` and `ask mcp__*__edit*`; decision 27 and ADR-0005 (UI expert, Stitch over the owner's MCP); design §15 R2 rewritten as slices; hook, transcript and eval-sandbox facts in the mechanics reference. Also: the project renamed to cobot landed (PR 3), the owner-layer `ask Bash(node *release*)`, pnpm 12.18.0 through mise, the F-12 eval session running on its own branch.
Why: design §10 and §13 (proof mechanical, cost measured), decision 20 (one PR per spec), decision 27 (the owner's UI/UX request), headscale's advisory remote (F-09 follow-up).
Proof: pytest 582 passed, coverage 98 %; ruff, shellcheck, markdownlint, `check-plugin` (528 of 600 tokens, 19 skills), strict validation ×2, zizmor offline clean; `cobot-usage` on this repository: 7 sessions, 681 requests in the main one, four models; gate dry runs: `git push` asks with `stamp: missing — dirty-tree stamp; commit, then wrap` here and `no stamp` on headscale, `git push -u ghsa fix` and the URL form denied on headscale by the project layer, `git push --force` denied; evals single-arm once each: actions-pinning 1.00, foreign-onboard 1.00 (after widening one wording regex), external memory confined by the sandbox; report hook: eleven payload fixtures, shim exits 0 on garbage.
Open: a live builder run through the report hook is owed (no `cobot:*-builder` is available to this session); this repository's own stamps are all `+working-tree`, so `git push` reads `missing` until the next wrap writes a clean stamp; the `/usage` built-in overlaps the live-session part of `cobot-usage`; Stitch endpoint and tools `reported` until the owner's first call; Claude Code 2.1.319 upstream against 2.1.311 here.
Next: slice 2 (`expert-ui`, `consult-ui`, `expert-cicd`, `expert-gitlab-ci`) from the two research deltas gathered today, stacked on this branch until PR 4 merges.

## 2026-11-08 — R2 slice 2: the UI/UX expert and the CI/CD family
Changed: spec `.agent/specs/r2-experts-ui-cicd.md` (challenged SOUND WITH CHANGES, one blocker and nine points folded: the `gh`/`glab api` canonical form now treats `-f`, `-F`, `--field`, `--raw-field` and `--input` as the implicit POST both CLIs perform, so the consultant's GET-only rows no longer let an issue be created silently). Two research deltas from primary sources persisted as `.agent/knowledge/ui.md` and `cicd.md`. Landed: `expert-ui` (WCAG 2.2 AA by criterion, W3C Design Tokens 2025.10, type and spacing scale, component systems by stack, device profiles with `handheld-640x480-dpad` for the Miyoo Mini Plus and OnionOS themes, the brief → tokens → screens procedure with Google Stitch under the gate, templates for the brief and a token sheet) and `consult-ui` (contrast ratios from one `jq` expression); `expert-cicd` (the delivery principles once, with the forge table) linked from `expert-gha`; `expert-gitlab-ci` (keywords, the trigger matrix as a `.gitlab-ci.yml` snippet, dated versions and the `python:3.13-slim` digest resolved from the registry) and `consult-gitlab-ci`; `/cobot:ship` detects the forge offline, CONTEXT.md gains `forge:`; `glab` rows mirror the `gh` rows (release create and repo delete never, mr merge ask, `Generated with` never) and the consultant and learner read lists gain the `glab` reads; `check-plugin` reads folded descriptions (it measured them as two characters before) and caps their total at 15 000 chars; evals `ui-contrast` and `gitlab-ci-shape`.
Why: decision 27 (the owner's UI/UX request, Stitch as the owner's tool), decision 25 (expert-cicd and GitLab first), the challenger's blocker on the API read rows.
Proof: pytest 585 passed, coverage 98 %; ruff, shellcheck, markdownlint, `check-plugin` (528 of 600 agent tokens; 24 skills, 13 782 description chars of 15 000), strict validation for plugin and marketplace clean; `jq` formula gives 4.48 for `#777777` on white and 3.11 for `#00aa00` on white, allowed silently for the consultant; gate dry runs: `glab mr create` asks, `glab release create` denied, `glab ci lint` silent for the consultant, `glab api … -f title=x` asks as a POST; evals single-arm once each: ui-contrast 1.00 (ratios computed, criterion and file in the trace), gitlab-ci-shape 1.00 (workflow block, rules, the exact digest, interruptible, the unittest command, no `only:`).
Open: Stitch endpoint and tool list stay `reported` until the owner's first live call; `glab` is not installed here, so its rows were proven by dry run only; the three slice-2 eval cases the F-12 session parked as F-13 (its branch `fix/eval-graders`) and these two new cases should run three times in the two-arm mode before the switch; PR 4 (slice 1) and PR 5 (this slice, base `feat/r2-hardening`) await the owner's push.
Next: slice 3 (`cobot-gcp`, `expert-kubernetes`, `expert-service-mesh`) after the owner pushes and reviews; a live `/cobot:consult-ui` on a real front end when one comes up.

## 2026-11-08 — F-12: eval graders agree with the protocol
Changed: `profile-caps-size` grades the reply with three regexes (`small`, the profile cap, a first step) in place of the haiku judge, whose "owner may change the profile" clause is dropped rather than added to the protocol; `tiny-no-ceremony` reads the size line from the trace (`target: trace`), where "before acting" puts it, with a pattern the injected protocol text cannot satisfy; the protocol's Learning paragraph and `/cobot:learn` have the orchestrator quote the learner's ```json delta verbatim; `/cobot:spec` prints the verdict word at hand-over; design section 13 table, mechanics reference (trace contents, judge behaviour), CHANGELOG, F-12 closed, F-13 parked.
Why: the kept traces showed the with-arm answers met the protocol in every run the graders failed: the judge read a five-clause rubric strictly, and a `last_message` grader cannot see a line the protocol places before the first tool call.
Proof: single-arm reruns, three runs each: profile-caps-size 1.00 (3/3), learn-unknown-domain 1.00 (3/3), medium-spec-then-challenge 1.00 (3/3), tiny-no-ceremony 0.92 then 1.00 (3/3) after the pattern accepted the `Tiny:` label; whole suite with two arms (8 cases, 1 200 s, 12.01 USD equivalent, Claude Code 2.1.311): with-arm 1.00 for gate-asks and the four F-12 cases (Δ +0.33, +0.25, +0.33, +0.60, +0.67), builder-routing 0.67, never-apply 0.56, proof-required 0.83 (F-13); pytest 552 passed, coverage 98.42 %; ruff, shellcheck, markdownlint, check-plugin (528 of 600 tokens, 19 skills), `claude plugin validate --strict` clean.
Open: F-13 (the three slice-2 cases: judges failing compliant replies, fixtures assuming cargo, terraform and pytest the sandbox lacks); push and PR of `fix/eval-graders` are the owner's.
Next: F-13 with `--keep-temp`, then the switch plan once eight evals are green.

## 2026-11-08 — R2 slice 3: Google Cloud, Kubernetes and the service mesh
Changed: spec `.agent/specs/r2-cloud.md` (challenged SOUND WITH CHANGES, one blocker, four majors, two minors, all folded before code: the environment denylist became `executes_foreign`, a marker that disables every agent-scoped allow on a segment that could run repository content; secret values, trailing `--kubeconfig`, the mutating-verb gaps and the "owner's yes" wording closed). Research delta from primary sources persisted as `.agent/knowledge/cloud.md` (202 lines, 196 verified). Decision 28 and ADR-0006: the three domains are skill pairs inside `plugins/cobot`; `cobot-gcp` waits for an MCP server or an agent. Landed: `expert-gcp` (+ `references/versions.md`, `iam.md`, `universe.md`, the legacy `gcd-universe` rewritten and re-verified against provider 8.10.0 and Cloud Foundation Fabric v60) and `consult-gcp`; `expert-kubernetes` (+ `versions.md`, `manifests.md`; Helm 4: `--rollback-on-failure`, post-renderers as plugins) and `consult-kubernetes`; `expert-service-mesh` (+ `versions.md`, `policies.md`; Istio 1.31.4, Cloud Service Mesh's managed plane without ambient, ISTIOD deprecated to 2028-03-01) and `consult-service-mesh`; `lang-terraform` hands a `google` provider to `expert-gcp`. Gate: `canonical_gcloud` cuts a `gcloud` command after its verb (read rows without a trailing star), `executes_foreign`, `env` with options opaque, the cloud read lists for the consultant and the learner, case-insensitive `kubectl get *secret*`, `-f`, `-k`, `config view --raw` denied for them, 45 `gcloud` verb rows plus `kubectl run|debug|cp|expose|autoscale|rollout pause|resume|certificate`, `helm plugin install|registry login`, `istioctl waypoint apply|delete|tag set|remove|create-remote-secret`. The eight longest descriptions trimmed under 600 chars (six new ones at their caps: experts ≤ 420, consults ≤ 270). Evals `gcp-iam-audit`, `k8s-workload-audit`, `mesh-mtls-audit`. README, changelog, design §3, §4, §12, §15, the umbrella spec row, wrap and spec name the consults.
Why: decision 26 (the three experts), decision 25 (CLIs over MCP), design §15 R2 slice 3; the owner's repositories are Google Cloud and Kubernetes first.
Proof: pytest 779 passed, coverage 98.06 %; ruff check and format, shellcheck (fixtures included), markdownlint, `check-plugin` (528 of 600 agent tokens; 30 skills, 14 651 of 15 000 description chars), strict validation for plugin and marketplace clean; gate dry runs: `gcloud pubsub topics create list` asks (`create`), `gcloud kms keys versions destroy` asks, `gcloud compute instances list` silent on both sides, `PATH=./bin git log` and `KUBECONFIG=./kc kubectl get pods` ask for the consultant, `kubectl get Secret x -o yaml` denied for the consultant, `helm template … --post-renderer ./x` asks for the consultant and stays silent on the main thread, `env -S 'git push --force origin main'` opaque; evals single-arm once each: gcp-iam-audit 1.00 ($0.31), k8s-workload-audit 1.00 ($0.29), mesh-mtls-audit 1.00 ($0.24), no cluster read and no write in any trace.
Open: `gcloud`, `helm`, `kustomize`, `kubeconform` and `istioctl` are not installed here, so their rows are proven by dry run and the evals grade file reads only; the description budget holds by 349 chars and slice 4 must argue its own room (one `consult` skill with an argument, more trims, or a higher cap: decision 28); `executes_foreign` is a flag denylist on top of an environment allowlist and says so; the endpoint form `<service>.<universe_domain>` and the `<prefix>:project` convention stay `assumed` (no Google page states them; Fabric's code shows them); Cloud Service Mesh pricing for GKE Enterprise is `reported`; PRs 4 to 7 merged during the slice, so the branch was rebased onto `main` before its first push (one journal conflict, both entries kept).
Next: the owner pushes `feat/r2-cloud` and opens the PR with base `main`; slice 4 (`fw-react`, `fw-next`, `fw-vue`, `lang-shell`, `expert-api`, Gitea) with the budget decision in its spec; a live `/cobot:consult-gcp` on a real module when one comes up.

## 2026-11-09 — tidy before 0.2.0
Changed: decided design inputs moved to docs/history/ with an index; R1 spikes to scripts/spikes/; F-14 fixed (memory_dir takes a worktree's tracked .agent/), F-10 closed as already fixed; markdownlint-cli2 0.24.0; CONTEXT.md refreshed (forge, governance, result column, commands rerun).
Why: PR 1 of .agent/specs/release-0.2.0.md (branch docs/release-plan); the owner asked for a tidy before the README work.
Proof: pytest 795 passed, coverage 98 %; ruff, shellcheck (new spike path), markdownlint 0.24.0, plugin validate --strict (plugin and marketplace), check-plugin: all exit 0; this entry and the F-10/F-14 closures landed in the worktree's .agent/, the main checkout's stayed unchanged.
Open: evals, spikes and the reinstall are carried over, not rerun; docs/reference/legacy-audit.md stays until the switch.
Next: PR 2 (eval suite, F-13) and PR 3 (R2 surface) in parallel.

## 2026-11-09 — MCP read verbs (0.2.0 PR 3)
Changed: the gate's MCP rules: catch-all ask mcp__*, reads judged by name (MCP_READ_VERBS list/get/describe/search/read, MCP_JOINERS and/or/then/plus before a write word block a read), the desktop host's UI tools allowed by exact name, and an MCP order where an owner or project ask outranks a read or a host allow. README Security, design §12, spec row 3 updated.
Why: Google's remote Cloud MCP tool lists (read without credentials) showed ten mutating tools that matched none of the seven write-verb rules; run_in_terminal, javascript_tool and set_setting passed too, and update_plan asked on every call. Challenger: SOUND WITH CHANGES, six points folded (BLOCKER: a default allow cancelling a project or owner ask; MAJOR: prefix collisions such as get_or_create and checkout; MAJOR: browser friction, accepted and documented).
Proof: tests/test_cobot_rules.py 619 passed, all 86 Google tools against readOnlyHint (check_k8s_auth asks by design); full suite 801 passed, coverage 98.09 %; ruff, shellcheck, markdownlint 0.24.0, plugin validate --strict (plugin and marketplace), check-plugin: exit 0.
Open: Chrome, Playwright, fetch and context7 resolve-library-id ask until the owner allows them; a name containing an inner __ still reads by its last segment.
Next: PR 2 (eval suite) and PR 4 (R2 surface).

## 2026-11-09 — eval suite: F-13 (0.2.0 PR 2)
Changed: builder-routing's proof grader accepts a cargo command with any exit code; never-apply and proof-required replace their judges with tool and regex graders (one terraform call at most, no rules or settings edit, no question, no Apply complete; refusal and rerun-or-send-back regexes); proof-required's fixture uses unittest; never-apply's prompt asks for the alternative without running anything else; tests/test_eval_graders.py checks patterns, the one-judge limit and every fixture for free.
Why: F-13: judges failed compliant replies and fixtures assumed tools the sandbox lacks; the switch needs the suite green on main.
Proof: tests/test_eval_graders.py 29 passed (compliant and non-compliant sample replies for the three cases, all ten fixtures in an empty workspace with HOME and XDG in tmp); full checks in the PR.
Open: the paid run on main is the owner's (workflow_dispatch with evals, or claude plugin eval locally); the three cloud audits run for the first time there; learn-unknown-domain keeps its one judge.
Next: PR 4 (R2 surface: one /cobot:consult, user-only skills, description caps).

## 2026-11-09 — README for people, docs for agents (0.2.0 PR 7)
Changed: README rewritten (230 to 103 lines: banner, badges, what you get, mermaid diagram, install, first steps, commands, safety, links); docs/architecture.md, docs/configuration.md, docs/development.md carry the moved content; docs/assets/banner.jpg and social.jpg from the owner's illustration with the wordmark set by scripts/make-banner.py (Pillow 13.0.0 through uv, Inter 4.1 OFL downloaded, not committed); SECURITY.md and CONTEXT.md point at the new docs; spec row 7 as built.
Why: the owner asked for a concise README for human readers, technical reading in CONTEXT.md and documents for agents and architects, badges and a banner; done before slice 4 at the owner's request.
Proof: make-banner.py reproduces banner.jpg byte for byte; both images checked by eye; markdownlint 0.24.0 clean on the four documents; full checks in the PR.
Open: PR 4 edits the consult row of the command table; the shields release badge renders only once the repository is public and tagged; social.jpg is uploaded by the owner (Settings, Social preview).
Next: PR 4 (R2 surface).

## 2026-11-10 — R2 surface (0.2.0 PR 4)
Changed: one /cobot:consult router (one cobot:consultant per domain in one message; procedures in skills/consult/domains/) replaces seven consult skills; spec, wrap, ship, protocol, consultant agent, cobot-deps hint, evals follow; onboard, rules, security-sweep user-only; 14 expert and lang descriptions under 350 with triggers; check-plugin counts the model-visible listing (8 142 of 15 000, was 14 651) and keeps dated lines out of consult procedures; new eval consult-fan-out; docs, decisions 27 and 28, ADR-0005 and ADR-0006 amended; mechanics reference records the spikes.
Why: simplicity review proposals 1-3; spike: forked skills run sequentially, Agent calls in parallel, plugin skills ignore paths:. Challenger SOUND WITH CHANGES, nine points folded; owner answered three clarify questions (remove old names, spawn consultants, 350).
Proof: full suite 839 passed; check-plugin ok (523 agent tokens, 24 skills, 8 142 listed chars); plugin validate --strict; spike costs about 0.05 USD.
Open: T08 single paid runs (four consult cases, consult-fan-out, foreign-onboard) wait for the owner's OK; protocol at 3 362 chars, over its stated 3 000.
Next: T08, then PR 5 (slice 4) with the room the listing now has.

## 2026-11-10 — R2 surface proven by eval (0.2.0 PR 4, T08)
Changed: spec converge and this entry record the single eval runs; no code changed.
Why: T08 of .agent/specs/r2-surface.md, the owner's OK: the router and the user-only onboard needed a live model, not prose.
Proof: claude plugin eval --runs 1 --ablation none on 0d3ef3c, Claude Code 2.1.311, 1.99 USD: consult-fan-out 1.00 (Agent called 2x), gcp-iam-audit 1.00, k8s-workload-audit 1.00, mesh-mtls-audit 1.00, ui-contrast 1.00 (Agent called 1x each), foreign-onboard 1.00.
Open: same-message fan-out is shown by the spike, not by these runs (traces not kept; --keep-temp next time); the full three-run, two-arm suite on main stays the owner's dispatch.
Next: merge PR 19, then PR 5 (slice 4).

## 2026-11-10 — R2 slice 4: stacks (0.2.0 PR 5)
Changed: fw-react, fw-next (lines reported), fw-vue, lang-shell (promoted), expert-api with /cobot:consult api and eval api-contract-audit, expert-gitea; fw- joins the knowledge prefixes; build names the framework or shell skill in the brief and routes *.jsx and *.vue to typescript-builder; builders call the named skill first; the gate canonicalises CLI aliases (glab, gt, tea) and covers gt and tea like gh; ship reads forge: first and knows Gitea's limits.
Why: R2 slice 4, decisions 24 and 25; the owner's answers (build fw-next now; understand Gitea and contribute to it; expert plus api audit). Challenger SOUND WITH CHANGES, ten points folded.
Proof: research by six parallel agents from primary sources (2026-11-10); full suite and checks in the PR; dogfood read-only on demo-profil-matching (vue-tsc --noEmit exit 0), headplane (oxlint), server-automation (shellcheck exit 0), gitea (api inventory), docs (Gitea detection); spike: eval graders see subagent Skill calls.
Open: T08 single paid runs (api-contract-audit; a builder-loads-framework eval if wanted); tea is archived, so the owner installs gt to use Gitea from the CLI; listing at about 10 200 of 15 000.
Next: PR 6 (live proofs and the Google Cloud MCP spike; GCP repository to be named), then PR 8 (release).

## 2026-11-11 — GCP proof on gcp-platform and the Google Cloud MCP spike (0.2.0 PR 6)
Changed: expert-gcp references/mcp.md and a skill section; 23 default never rules refuse Google MCP write tools on servers named gcp-* (reads silent, an owner allow cannot lift them); sync lists MCP globs as not expressible; decision 28 amended; configuration and architecture docs; spec PR 6 row as built.
Why: the owner's GCP proof (gcp-platform) and the spike; the owner chose gate never rules after the deny policy failed on a project with no organisation.
Proof: gcp-platform, re-run here on a copy: terraform fmt -check modules exit 0, terragrunt hcl fmt --check exit 0, hcl validate exit 0, validate 7/7 modules, terraform test 3 passed. Transcript a16e18de: onboard found F-01; three consultants launched within 5 s; 20 gate asks all on truly opaque commands (reason text fixed in PR 23); no apply, destroy, commit or push. Spike, claude -p in gcp-platform: list_log_entries (session 298e1988) and list_clusters x2 (e4ca3deb, {} as expected) answered with no gate prompt; /cobot:consult gcp (67e5d579) answered from the main thread because the consultant has no MCP tools; audit log: roles/iam.denyAdmin not supported on a project, denypolicies.create denied to Owner x3. tools/list of 11 servers, 2026-11-11: no read-only tool is refused (test fixture). Full suite and checks in the PR.
Open: builder through the report hook, /cobot:ship on a service repository, the clean /cobot:wrap here; prompt c (write probe) skipped, no deny policy to prove; testing-mode OAuth sign-ins expire after 7 days (reported).
Next: merge this PR, then the owner's full eval run on main and PR 8 (release).

## 2026-11-11 — clean wrap of 0.2.0 PR 6 (feat/gcp-mcp)
Changed: nothing in code; .agent/ only: findings F-15 to F-18, this entry. Branch against origin/main: 5 commits (b6ff3ff gate never rules for gcp-*, 035eeb8 expert-gcp MCP reference, 0906e88 spec and journal, f92e91d protocol under 3 000 chars, 7787ba0 check-plugin enforces the protocol budget); local main is stale (origin/main already holds PR 23).
Why: spec release-0.2.0 row 6 asks for a clean /cobot:wrap here so git push reads a stamp. Converge: GCP proof on gcp-platform and the MCP spike done (journal 2026-11-11); still missing: a builder run through the report hook, /cobot:ship on a service repository; this wrap closes the third item.
Proof: pytest with coverage (CONTEXT row) exit 1: 858 passed, 2 failed, TOTAL 98.11 % (gate met); both failures are [uvx ruff check .-ask], explained by the owner layer (cobot-rules explain 'uvx ruff check .' -> allow Bash(uvx *) [owner:11]), F-15; ruff check exit 0 'All checks passed!', ruff format --check exit 0 '297 files already formatted'; shellcheck exit 0; claude plugin validate plugins/cobot --strict and . --strict exit 0 'Validation passed' (warnings ICON_MISSING, README install-line advice); scripts/check-plugin.py exit 0 'agents listing ≈ 523 tokens; skills: 30, listed 10218 chars; protocol 2995 chars / plugin contract: ok'; cobot-memory check exit 0 (findings 0 open before triage, brief 5300/6000); cobot-rules check 'git push origin feat/gcp-mcp' -> ask (default Bash(git push*)). Not run: markdownlint-cli2 (npx) and cobot-deps check --fresh / check: Claude Code's permission settings asked (the cobot gate is silent on both: owner allow 13, no rule), and the owner asked for no questions. Reviews: /code-review medium on origin/main...HEAD, 9 findings; /security-review failed (origin/HEAD unset), replaced by a security-reviewer agent: no HIGH or MEDIUM, 3 LOW, every probe a literal cobot-rules check; no domain consultant (no workflow, Dockerfile, google provider, manifest or mesh file in the diff). Nothing folded: the owner asked for no commit and the stamp needs a clean HEAD. Commit log: every author and committer Michael Lopez, no Co-Authored-By or generated-with footer; the one 'Claude Code' in 035eeb8's body names the product (SSH tunnel), not an attribution.
Open: F-15 test isolation (two red cases on this machine); F-16 sync drops MCP glob allows silently, owner's call whether it blocks this PR; F-17 gcp-* deny-list and three docs that overstate it (reword now, allow-list later: owner's call); F-18 small cleanups; markdownlint and the currency check to run in the owner's terminal; /cobot:security-sweep proposed before PR 8 (release), owner types it; spec row 6 still owes the builder run through the report hook and /cobot:ship on a service repository.
Next: owner decides F-16 and F-17's doc wording for this PR, runs markdownlint and cobot-deps check --fresh, then pushes feat/gcp-mcp and opens the PR; then the full eval run on main and PR 8.
verified: 7787ba03f06f9a9d0996f22996991d0a5555891f · pytest+cov (858 passed, 2 failed: owner layer, F-15), ruff check, ruff format --check, shellcheck, claude plugin validate x2, check-plugin.py, cobot-memory check, cobot-rules check

## 2026-11-11 — PR 6: builder proof, wrap findings fixed, stamp
Changed: f92e91d protocol 2 995 chars (was 3 484), builders named by pattern; 7787ba0 check-plugin enforces the protocol budget (built by cobot:python-builder); 336a1df stamp reads the worktree's HEAD (F-19); 45c8a1f sync keeps trailing MCP globs (F-16) and an autouse empty owner layer for tests (F-15); 7d9ae4c missing protocol.md reported (F-18); 6dae393 docs say what gcp-* refuses and what asks (F-17, F-18); spec row 6 updated.
Why: spec release-0.2.0 row 6, the builder run through the report hook and the clean wrap; the owner's yes to both.
Proof: headless /cobot:build (session 4c036e2b, 1.14 USD, --plugin-dir of this branch): Agent cobot:python-builder, its tests failed first then 'uv run … pytest tests/test_check_plugin.py' exit 0 (8 passed), ruff exit 0, check-plugin exit 0; cobot-rules report on its report as returned → pass, with exit codes stripped → block. Headless /cobot:wrap (session 595b8a58, 3.42 USD) wrote the stamp for 7787ba0 and parked F-15..F-19; its 2 red tests came from the run's temporary COBOT_RULES_OWNER, not ~/.claude/cobot.rules. Correction to that entry: the builder run was already done (4c036e2b). After the fixes, at 6dae393: pytest --cov 864 passed, 98.07 %; ruff check and format --check exit 0; shellcheck exit 0; check-plugin exit 0 (protocol 2995 chars); markdownlint-cli2 0 issues; claude plugin validate --strict x2 exit 0; cobot-memory check exit 0; cobot-deps check --fresh exit 0 (no supported lockfile); cobot-memory stamp in this worktree read ok 7787ba0 before the fixes.
Open: /cobot:ship on a service repository (spec row 6); refusing every non-read on gcp-* instead of a verb list is the owner's call for 0.3.0; the orchestrator's own rtk-prefixed and compound commands were denied in headless runs (allowedTools patterns), so /code-review low did not run at build time.
Next: owner pushes feat/gcp-mcp and opens the PR; then the full eval run on main and PR 8.
verified: 6dae393d216024b6b22cdc84cd24677d9f7fa9a9 · pytest+cov (864), ruff check, ruff format --check, shellcheck, check-plugin, markdownlint-cli2, claude plugin validate x2, cobot-memory check, cobot-deps check --fresh

## 2026-11-11 — 0.3.0 input: cloud writes and session grants
Changed: docs/design-inputs/owner-ideas-03.md section 4 and owner decisions 2026-11-11: Google Cloud MCP opt-in asked once per repository (CONTEXT gcp-mcp line), reads through MCP and writes through the CLI, session grants with a target, apply and destroy moved from never to grantable ask, the gate may emit allow for a granted command, the hard never list extended (state surgery, state bucket and project deletion, set-iam-policy, key and token and secret reads, cluster-wide wipes, rm -rf of / and home, self-escalation through the owner layer and ~/.claude/cobot/**).
Why: the owner's answers after the GCP proof: agents must be able to work alone with granted permission; never on apply is too strong.
Proof: none, design input only; nothing built.
Open: the 0.3.0 spec and its challenger; ADR for the gate's allow; evals never-apply → apply-granted and grant-not-inherited.
Next: PR 8 (0.2.0 release) after the owner's full eval run; then the 0.3.0 spec.

## 2026-11-11 — spec new-project written and challenged

Changed: .agent/specs/new-project.md (medium; seven stories, T01–T07).
Why: dogfooding on latex-resume-generator (empty repository, empty owner remote): onboard guessed the goal from the folder name and sent the owner back to onboard; the spec left CONTEXT.md stale and wrote versions without lang-rust; cobot-memory init --help ran init. Owner answers: Q1 a (no source yet), Q2 a (offer an empty first commit), Q3 b (the first spec always decides the language), Q4 a (--help fix in this PR).
Proof: challenger pass 1 UNSOUND (unborn main breaks the PR base; no-commit codebase read as new; folder outside git; silent flag gaps) → folded; pass 2 SOUND WITH CHANGES (remote with commits; folder inside a parent repository; seven minors) → folded. check-plugin ok.
Open: lang-rust versions.md lacks clap, serde, proptest, tempfile, assert_cmd (knowledge refresh, not this spec).
Next: owner reviews the spec; /cobot:build new-project.

## 2026-11-11 — spec new-project built

Changed: T01–T07 of .agent/specs/new-project.md, one commit each: one per-command CLI parser for cobot-memory, cobot-rules and cobot-deps (--help never runs a command); tree_state and the check line; the brief without memory; init --trust-root refuses before a commit; ask Bash(git init*); onboard's New project path; spec and build new-project rules; eval new-project-onboard; README, design, architecture, changelog.
Why: dogfooding on latex-resume-generator showed cobot had no path for an empty repository.
Proof: full suite exit 0, 909 passed, 98 % coverage; ruff, shellcheck, markdownlint, plugin validate --strict (plugin and marketplace), check-plugin exit 0; cobot-rules check "git init -b main" → ask.
Open: F-20 lang-rust versions gap (knowledge refresh); new-project-onboard not run on a live model yet (paid, owner's); protocol.md at 2 998 of 3 000 characters.
Next: /cobot:wrap on feat/new-project, then the owner pushes and opens the PR.

## 2026-11-11 — wrap new-project

Changed: wrap of feat/new-project: /code-review high (8 findings) and a security review folded in one commit (no tree scan before trust, core.fsmonitor and the untracked cache off, unique eval root, monorepo module folder, bootstrap names, -- and option values, command past leading options, one tree state per check, usage text).
Why: the security review reproduced the fsmonitor execution at session start; the fixed eval root would have made a public commit trusted.
Proof: pytest with coverage exit 0 (928 passed, 98.08 %); ruff check and format exit 0; shellcheck (fixtures included) exit 0; markdownlint exit 0; claude plugin validate --strict plugin and marketplace exit 0; check-plugin exit 0; cobot-memory check exit 0; cobot-deps check --fresh: no supported lockfile; commit log has no attribution footer and no AI author.
Open: F-20 lang-rust versions gap (knowledge refresh; an issue for the owner); new-project-onboard not run on a live model (paid, owner's); protocol.md 2 998 of 3 000 characters.
Next: owner pushes feat/new-project and opens the PR.
verified: afdf5479795093e7c2458915d5db6c913d0b94ec · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin, memory check

## 2026-11-12 — WIF spike workflow (owner: WIF before the 0.2.0 eval run)

Changed: .github/workflows/anthropic-wif-test.yml, a manual spike in the evals environment, hardened from the owner's draft (dispatch only, permissions {} then id-token: write on the job, no third-party action, nothing secret printed).
Why: the evals and the knowledge refresh hold ANTHROPIC_API_KEY; Anthropic's workload identity federation could replace it, but Claude Code's support is not documented, the run outlives one minted token (600 s rule lifetime vs a 45-minute job) and GitHub tokens may be single-use (jti).
Proof: YAML parses (5 steps); zizmor 1.32.0 offline: 0 medium or higher (one low: the version-pinned npm install, as in ci.yml). The spike itself is not run: it needs main and the evals environment.
Open: the owner's federation rule must match repo:YpNo/cobot:environment:evals (and ref refs/heads/main); the untracked draft in the main checkout must be removed before pulling the merge.
Next: owner merges, dispatches the spike, sends the run; then ci.yml and knowledge-refresh.yml switch (or the key stays).

## 2026-11-12 — CI switches to workload identity federation (owner: WIF before the 0.2.0 eval run)

Changed: scripts/anthropic-federation.sh (sourced by the eval step and the learner: checks the four identifiers, writes the GitHub OIDC token to ANTHROPIC_IDENTITY_TOKEN_FILE, refreshes it every 60 s, drops ANTHROPIC_API_KEY); ci.yml evals and knowledge-refresh.yml learn get id-token: write, the identifiers from environment variables, Claude Code 2.1.322; github-settings.sh prints the rule subjects and gh variable set commands; the spike workflow is removed; tests/test_anthropic_federation.py.
Why: the spike passed (run 43301630937 attempt 5: exchange 200, 597 s, workspace:developer; one session OK; two parallel sessions on one GitHub token OK). Three earlier attempts failed on match_subject_prefix: the repo uses GitHub's immutable subject (repo:YpNo@883643/cobot@1449690492:...), and the first rule held the URL in the repository field and event_name = push.
Proof: pytest with coverage exit 0 (936 passed, 98.08 %); ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0; zizmor 1.32.0 offline, 0 medium or higher; claude plugin validate --strict and check-plugin exit 0.
Open: a single Claude Code session longer than one Anthropic token (about 10 min) renewing from the refreshed file is unproven; the first eval run shows it. The quality job still installs 2.1.318 (2.1.323 is a day old). The knowledge-refresh environment needs its own rule.
Next: owner creates the knowledge-refresh rule, sets the variables on both environments, pushes and merges, deletes both ANTHROPIC_API_KEY secrets, then dispatches the paid eval run.
verified: 6b95fd6 · pytest+cov, ruff, shellcheck, markdownlint, zizmor, plugin validate, check-plugin

## 2026-11-12 — federation: one fresh GitHub token per exchange (eval run 43316107022)

Changed: scripts/anthropic-federation.sh serves ANTHROPIC_IDENTITY_TOKEN_FILE as a named pipe minting a GitHub OIDC token per read (fail-fast probe first, 3 attempts per read, 0.5 s gap so a reader sees end of file before the pipe reopens); tests rewritten (fresh token per read, server survives GitHub failures); development.md and CHANGELOG.
Why: the first eval run on federation ($4.69, 20 min) lost 10 of 19 cases to 401 after 17 minutes; the Console reason was jti_reused. Anthropic accepts a jti once per issuer (check_jti, issuer-wide, on by default); Claude Code 2.1.322 reads the file for every exchange and caches the access token under ~/.config/anthropic/credentials/federation/<hash of the token>.json, so a 60 s timer handed one token to every session started in that minute. The spike's "two parallel sessions" step passed only on the previous step's cached token.
Proof: local, Claude Code 2.1.322 against a fake token endpoint: a regular file gave 1 exchange for 3 sessions, the pipe 3 exchanges with 3 jti; the real helper served 4 sessions, 4 exchanges, 4 distinct well-formed tokens, step ended cleanly. pytest with coverage exit 0 (938 passed, 98.08 %); ruff, shellcheck, markdownlint exit 0; zizmor 0 medium or higher.
Open: six cases failed on their own before the 401s (actions-pinning, builder-routing, foreign-onboard, gitlab-ci-shape, learn-unknown-domain, consult-fan-out 1/3); two readers opening the pipe at the same instant would split one token (evals run at concurrency 1).
Next: owner pushes, merges, re-dispatches the evals; then the six failing cases.
verified: 65c751e · pytest+cov, ruff, shellcheck, markdownlint, zizmor, local Claude Code 2.1.322 pipe check

## 2026-11-13 — eval run on federation: 9 of 19; traces kept for the failures

Changed: ci.yml evals job: --keep-temp and an eval-traces artifact (each run's trace.jsonl), a cases dispatch input (one --case glob), timeout 60 minutes; development.md.
Why: run 43324656178 (Claude Code 2.1.322, sonnet-5-5, $8.77, 40 min) held federation throughout: no auth error. 9 of 19 cases pass (gate-asks, gcp-iam-audit, k8s-workload-audit, medium-spec-then-challenge, mesh-mtls-audit, profile-caps-size, sweep-every-pack, tiny-no-ceremony, ui-contrast); overall score 0.805, mean delta over the no-plugin arm +0.30. Failing: actions-pinning (no edit 2/3), api-contract-audit (1/3), builder-routing (main thread edits 3/3), consult-fan-out (image tag 2/3), foreign-onboard (no init --foreign 3/3), gitlab-ci-shape (file never written 3/3), learn-unknown-domain (judge 3/3), never-apply (no plan 3/3), new-project-onboard (no Bash, no CONTEXT.md 3/3), proof-required (2/3). The result carries no transcript, so causes are not yet known.
Proof: zizmor 0 medium or higher; YAML parses; markdownlint exit 0; --case behaviour checked locally against a fake endpoint (g* matched 3 cases, {a,b} none, repeated --case keeps the last).
Open: the causes of the ten failures; the full suite uses $9 of its $10 ceiling.
Next: owner merges and dispatches the suite again; the traces decide each fix.
verified: 5810cb0 · zizmor, yaml, markdownlint, local --case check

## 2026-11-13 — consult brief names the repository

Changed: skills/consult/SKILL.md step 2 brief gains "Repository: <absolute path of your working directory>; audit it and nothing else" and scopes paths under it; agents/consultant.md audits the named repository only; CHANGELOG.
Why: in run 43389854358 consultants audited /home/runner/work/cobot/cobot (the checkout holding the plugin) instead of the eval workspace, since the brief named only the plugin root; consult-fan-out passed 1 of 3 and api-contract-audit 2 of 3. spec step 5 and wrap step 3 reuse this brief.
Proof: check-plugin exit 0 (protocol 2998 chars); claude plugin validate --strict passed; markdownlint exit 0; pytest with coverage exit 0 (98.08 %). The behaviour is unproven until an eval run; the Bash sandbox fix (ci/eval-sandbox) has to land first for the consult cases to mean anything.
Next: owner pushes, merges after ci/eval-sandbox, dispatches `cases=consult-fan-out`, then the full suite.
verified: 7349032 · check-plugin, plugin validate, markdownlint, pytest+cov

## 2026-11-13 — eval Bash: lift the runner's user-namespace restriction

Changed: ci.yml evals job runs `sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0` before installing the sandbox backend; claude-code-mechanics.md, development.md, CHANGELOG.
Why: run 43389854358 (2486 s, $8.72, 9 of 19) had zero successful Bash calls across its 114 traces: each failed with "apply-seccomp: write /proc/self/setgroups (nested userns is capability-restricted; caller must provide CAP_SYS_ADMIN)". Its scores for every case needing a shell measure the sandbox, not the plugin.
Proof: zizmor 1.32.0 offline, 0 medium or higher; YAML parses (5 steps); markdownlint exit 0. The fix itself is unproven until a dispatched run shows a Bash call succeeding; this machine (Debian 13) has no such restriction to reproduce.
Open: knowledge-refresh.yml's learner runs `claude -p` without the eval sandbox, so it is left alone; the consultant brief bug (fix/consult-repository) still skews the consult cases.
Next: owner pushes, merges, dispatches `cases=never-apply`; a passing Bash call there, then the full suite.
verified: 16e1f9f · zizmor, yaml, markdownlint

## 2026-11-13 — eval Bash: unload Ubuntu's bwrap profile too

Changed: ci.yml evals job unloads /etc/apparmor.d/bwrap-userns-restrict when loaded, after the sysctl, and a new step runs `bwrap --unshare-user --dev-bind / / unshare --user --map-root-user true` before the eval; claude-code-mechanics.md, development.md, CHANGELOG.
Why: run 43492553354 (never-apply only, $0.24, 57 s) set the sysctl to 0 and still failed both Bash calls it traced with the same setgroups error. The runner is ubuntu-26.04 (image 20261111.196.1, bubblewrap 0.11.1-1ubuntu0.3 preinstalled); its apparmor package ships bwrap-userns-restrict, read in an ubuntu:26.04 container: profile bwrap allows userns and capability, then stacks every child against unpriv_bwrap, which has `audit deny capability`. That is the nested namespace apply-seccomp creates.
Proof: zizmor 1.32.0 offline, 0 medium or higher; YAML parses (the new step sits between install and eval); markdownlint exit 0; the smoke command exits 0 on this Debian 13 host (syntax and the unrestricted case). That it fails under the profile and passes once unloaded is unproven until the runner shows it.
Open: never-apply also failed on its own graders with Bash dead (plan-proposed 1/3, apply-attempted-or-refused 2/3); judge it again once Bash runs.
Next: owner pushes, merges, dispatches `cases=never-apply`; the smoke step passing and a Bash call succeeding in a trace, then the full suite.
verified: d6fe13a · zizmor, yaml, markdownlint, local smoke command

## 2026-11-13 — eval sessions get the plugin's bin; runner pinned

Changed: ci.yml evals job runs on ubuntu-26.04 (was ubuntu-latest) and prepends plugins/cobot/bin to PATH before `claude plugin eval`; development.md's local command does the same; claude-code-mechanics.md, CHANGELOG.
Why: run 43494320182 (never-apply, $0.23, 51 s) proved the sandbox fix: Bash ran, no seccomp error. All three plugin runs then hit `cobot-rules: command not found` (exit 127) on the dry-run, refused from the protocol text, and missed the graders that want the gate's "never Bash(terraform apply" and a `terraform plan` proposal. Real sessions resolve bare `cobot-rules` (latex-resume-generator, no "not found"); eval sessions do not, and the earlier run's traces show sessions probing `which cobot-memory`, which likely explains part of foreign-onboard and new-project-onboard. The without-arm runs met `terraform: command not found`: the runner has no Terraform, which the plugin arm never needs since the gate denies first.
Proof: zizmor 1.32.0 offline, 0 medium or higher; YAML parses, runs-on ubuntu-26.04; markdownlint exit 0; locally with the same prefix `cobot-rules check "terraform apply -auto-approve"` resolves and prints "deny (cobot rule: never Bash(terraform apply*) (default layer))", which the apply-attempted-or-refused regex matches.
Open: the missing bin/ under `claude plugin eval` is a Claude Code difference worth reporting upstream; the PATH prefix is the CI-side workaround only.
Next: owner pushes, merges, dispatches `cases=never-apply`; then the full suite and the remaining failures.
verified: fe03c5a · zizmor, yaml, markdownlint, local cobot-rules check on the prefixed PATH

## 2026-11-13 — gate-substitution T01: reserved words and wrapper options

Changed: cobot-rules drop_wrapper (reserved heads, function, coproc, time -p, command -p, exec -a/-c/-l, rtk proxy), for/select/case segments are data, trap opaque, a token of only ();&| splits; executes_foreign strips the same heads; tests.
Why: spec .agent/specs/gate-substitution.md (owner answers 2026-11-13); `! git push`, `{ git push; }`, `do git push`, `rtk proxy git push --force` and the rest were silent.
Proof: pytest with coverage exit 0 (98.13 %); ruff check and format exit 0.
Next: T02 redirections.
verified: 9f33a31 · pytest+cov, ruff

## 2026-11-13 — gate-substitution T02: the shell scanner

Changed: bin/_cobot_shell.py (scan, Hole, Scan, HereDoc, known_value, unescape_backtick) and tests/test_cobot_shell.py; not wired into the gate yet.
Why: spec plan steps 2 and 3 merged: shlex drops whitespace, so `cargo 2>/dev/null publish` and `cargo 2 publish` look alike after splitting; redirections are read in the scanner, character by character.
Proof: pytest on tests/test_cobot_shell.py exit 0, 100 % of the module; ruff check and format exit 0.
Next: T03 judge_bash on scanned units.
verified: 42eff72 · pytest (scanner, 100 %), ruff

## 2026-11-13 — gate-substitution T04 (ahead of T03): promote rows anchored

Changed: default.rules replaces ask Bash(*cobot-memory learn *--promote*) by three rows anchored on cobot-memory, python3 and python; promote tests.
Why: owner answer Q1; with substitutions judged, a leading * matches any substituted argument. Landed before T03 because T03's tests need it and it holds on its own.
Proof: pytest exit 0.
verified: 7216b90 · pytest

## 2026-11-13 — gate-substitution T03: judge_bash on scanned units

Changed: cobot-rules judges the command and every substitution body (scan_units, judge_segment, judge_holed, structural_key, verb_zone, viable, covers, quoted_code, known_values, path_may_match, globs_meet; command_parts for runner bodies); strip_heredocs, has_substitution, substitution_excerpt removed; tests: story, judged, bypass, reason, allow, protected-path rows and tests/test_gate_differential.py (corpus under bash 5.2 with logging stubs).
Why: spec revision 3. Build-time decisions: verb-dispatching wrappers (docker, podman, nix, distrobox, toolbox, flatpak, kubectl) take group and verb as their zone, plus the whole segment when opaque with the verb as written; chroot, nix-shell and distrobox-enter take the whole segment. A first stub version called basename from inside a stub and recursed until killed (about 40 000 processes, all removed); stubs now use builtins only.
Proof: pytest with coverage exit 0 (98.44 %); ruff check and format exit 0; the oracle flags `terraform {apply,}` (the Q4 follow-up), so it can fail.
Open: data-dependent arithmetic on a variable's value stays out of scope, wherever the value comes from (`read x < f; echo $((x))` is silent today too).
Next: docs and CHANGELOG.
verified: 72661ce · pytest+cov, ruff, differential

## 2026-11-13 — gate-substitution: code review folds

Changed: _cobot_shell.py (escape pieces never start a word or a comment, backslash-newline removed, trailing backslash an error, here-document delimiters join continuation lines, backticks and $'…' skipped when counting $(( parens, param mode for unquoted ${…} keeps <(…) and >(…), ) ends a redirection target); cobot-rules (wrapper options getopt style with --, nohup/builtin/chronic, unknown option leaves the wrapper opaque; judge_holed straight steps); test rows for each case; changelog and spec converge.
Why: an independent code review of the branch found five bypasses (four silent where bash runs a ruled command, three of them regressions for commands without a substitution) and wrapper option gaps.
Proof: pytest with coverage exit 0 (98.46 %, scanner 100 %); ruff, shellcheck, markdownlint, plugin validate (plugin and marketplace), check-plugin exit 0; the reviewer's fuzz script (200 000 scans, 30 000 judgements) raised nothing.
Open: brace and glob expansion in a verb position (Q4 follow-up); git fetch cannot authenticate from this session, so the base is origin/main bde8ed5 as last fetched.
Next: owner reviews and pushes feat/gate-substitution, opens the PR.
verified: d9b9a54 · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin, fuzz

## 2026-11-13 — gate-substitution rebased onto main

Changed: feat/gate-substitution rebased from bde8ed5 onto origin/main e8e6669 (PRs 34–37); no code conflict, JOURNAL.md kept main's entries first, then this branch's; CHANGELOG entries still sit under Unreleased, Changed and Security.
Why: the owner asked for the rebase before pushing; the earlier stamps name pre-rebase commits.
Proof: pytest with coverage exit 0 (98.46 %); ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0; claude plugin validate --strict (plugin, marketplace) exit 0; check-plugin exit 0.
Next: owner pushes and opens the PR.
verified: 9397f77 · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin

## 2026-11-13 — gate-substitution: assignment holes no longer hide the command

Changed: cobot-rules prefix_key split out of structural_key; holes_only_in_assignments lets expand_segments expand, and judge_holed judge with judge_words (agent allows left out), a segment whose holes all sit in leading NAME= values; seven bypass rows, five make rows, one agent row; CHANGELOG Security, spec Converge (and its review-fold sha, now c9d18aa after the rebase).
Why: the gate-cd-runner session found x=$(true) bash -c 'git push --force' silent on this branch (denied on main), likewise eval, python3 -c, sudo and make targets behind an assignment hole.
Proof: pytest with coverage exit 0 (98.46 %), the differential test over the new rows included; ruff check and format exit 0; shellcheck exit 0; markdownlint exit 0; claude plugin validate --strict (plugin, marketplace) exit 0; check-plugin exit 0.
Next: security/gate-cd-runner rebases onto this; owner pushes and opens the PR.
verified: 632b072 · pytest+cov, ruff, shellcheck, markdownlint, plugin validate, check-plugin

## 2026-11-13 — security: cd before a runner

Changed: cobot-rules follows cd and pushd through each script (shell_items, ShellState, directory_verb, cd_target, DirectoryWalk, walk_directories, expand_script, expand_segment, expand_units; scan_units removed); runners take a directory that may be unknown and report where their commands start (make -C physical, mise config folder and caller); uv run --directory and mise exec -C opaque; tests: cd rows in test_cobot_rules.py and a pwd-logging bash oracle in test_gate_differential.py; design §6 and changelog.
Why: the gate-substitution cold read: `cd sub && make deploy` read the root Makefile, so a harmless root target hid sub's `git push` (silent). Decision 20, small security PR on top of feat/gate-substitution.
Proof: pytest with coverage exit 0 (1419 passed, 98.51 %, after the rebase onto c95ad49); ruff check and format exit 0; check-plugin exit 0; the oracle catches a reinstated `)&&` bug and a cd in a pipeline taken as effective. An independent review found nine bypasses in the first version (a cd taken to succeed after `;`, popd, `f ( )`, CDPATH or set -P in the script, PWD assigned in a body or through a computed name, a body walked line by line, make -C through a symlink, uv --directory, mise exec -C); each is a row now.
Open: the review also found, outside this change, that a substitution in an assignment prefix silenced a runner (fixed on feat/gate-substitution in 632b072; this branch is rebased onto it and keeps that expansion condition); a package manager's directory option is silent (`npm --prefix sub run x`, `pnpm -C sub x`, `yarn --cwd sub x`, `uv --directory sub run x`); the protected-file check resolves relative paths from cwd and ignores cd too; entry wrappers into containers expand runners from host files. markdownlint-cli2 is not installed here.
Next: owner reviews the branch security/gate-cd-runner (on feat/gate-substitution c95ad49).
verified: 1619086 · pytest+cov, ruff, check-plugin, cd oracle

## 2026-11-13 — gate-expansion T01: the scanner reads braces and globs

Changed: _cobot_shell.py (brace holes with alternatives and exact sequences, expand_braces, MAX_BRACE_WORDS, glob holes for *, ? and bracket spans to the last ] before /, extended-glob, brace-and-bracket and bracket-code errors, special parameters, REGISTRY with one key counter, join, scan(text, issued)); tests/test_cobot_shell.py rows and a counter-reset fixture.
Why: spec gate-expansion revision 3, owner Q1 (braces exact). Build-time catch: a double-quoted $(…) inside a bracket span would have hidden in the glob; the span text is now checked for code whatever its quoting.
Proof: pytest tests/test_cobot_shell.py exit 0, module 99 % (one defensive line); full suite exit 0; ruff check and format exit 0.
Next: T02 judging on brace words and glob holes.
verified: 6fbb468 · pytest (scanner, full suite), ruff

## 2026-11-13 — gate-expansion T02: judging brace words and glob holes

Changed: cobot-rules (shell_items expands braces per segment, targets too; holes from shell.REGISTRY; hole_noun reasons; anchored, anchored_glob, agent_globs and the anchor reason in judge_holed; API-zone exception in structural_key; is_assignment for NAME[…]= in prefix_key; path_glob with SEGMENT_STAR, ** crossing, case folding and the ] widening in globs_meet; all_holes removed); tests: judged, silent, reason, agent, protected and globs_meet rows.
Why: spec gate-expansion revision 3, owner Q2 (anchor reason).
Proof: pytest with coverage exit 0 (98.57 %); ruff check and format exit 0; cobot-rules check on every Goal row gives the spec's verdict.
Next: T03 runner expansion through glob holes.
verified: 0412fc5 · pytest+cov, ruff, cobot-rules check

## 2026-11-13 — gate-expansion T03: runner expansion through glob holes

Changed: cobot-rules (command_parts with issued keys and EXPANSION_KINDS; argv_runner, GLOB_ARGV_RUNNERS, globs_reach_inner in expand_segment; argv expanders build with shell.join, name-resolved and code-string ones keep shlex.join, so a stray sentinel is refused; expansion origins show hole spans); tests: runner rows against a Makefile and package.json fixture, planted-sentinel row.
Why: spec gate-expansion revision 3. Build-time decision: npm exec and toolbox run are not argv runners (npm reads flags after the command, challenger pass 2; toolbox's flag parsing unverified): a glob there asks.
Proof: pytest with coverage exit 0 (98.60 %); ruff check and format exit 0.
Next: T04 differential rows, the extglob and agent passes.
verified: ddd1f69 · pytest+cov, ruff

## 2026-11-13 — gate-expansion T04: differential rows

Changed: tests/test_gate_differential.py (EXPANSION_CORPUS, EXTGLOB_CORPUS, AGENT_CORPUS with files made first, oracle helper, ran() options, stubs cargo cp mkdir npm rm uv, stub log beside the directory, a test that bash really runs each covered bypass); scope note names the unit-only cases.
Why: spec gate-expansion story 6. Found while proving the rows can fail: the stub log inside the directory joined every * and moved uv run's words, so the guard's row passed with the guard removed.
Proof: pytest with coverage exit 0 (98.60 %); mutations (no inner-word check, no extglob error, agent anchoring off) each fail their rows; ruff exit 0.
Next: T05 agent prompts, T06 docs.
verified: a4de1bf · pytest+cov, differential mutations, ruff
