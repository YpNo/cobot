# Findings

Observations parked the moment they are seen. Wrap turns each into a task, an issue, or closes it with a reason.

| # | Seen | Observation | Goes to |
|---|---|---|---|
| F-01 |  spec r1 story 2  |  brief caps not yet measured on the 1 013-line cartridge-os journal  | measured on cartridge-os: brief 3.5k chars, additionalContext 6.6k on the 1 013-line journal; the 2 500 CONTEXT cap cut 'Runtime constraints' and 'Where things are', so the cap is now section-aware and grows to 4 000 when the journal is short |
| F-02 | lang skills | three knowledge lines remain reported (LuCI runtime, secret masking rule, Dependabot groups for actions) | /partner:learn R1.1 |
| F-03 | dogfood cartridge-os | live probe through the installed plugin not run: the terminal CLI's OAuth session had expired (claude login), hook behaviour verified by feeding payloads to the cached hooks instead | owner: claude login, then rerun the two probes |
| F-04 | dogfood cartridge-os | ~/.claude/CLAUDE.md is a plain file, not the symlink to ~/.agents/AGENTS.md the global instructions describe; install.sh --check reports it | switch plan (docs/03-switch-plan.md) |
