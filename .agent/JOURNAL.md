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
