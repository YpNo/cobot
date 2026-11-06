# Journal

Append-only, newest at the bottom. One entry per working session or task group.

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
