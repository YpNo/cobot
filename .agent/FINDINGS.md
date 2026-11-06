# Findings

Observations parked the moment they are seen. Wrap turns each into a task, an issue, or closes it with a reason.

| # | Seen | Observation | Goes to |
|---|---|---|---|
| F-01 |  spec r1 story 2  |  brief caps not yet measured on the 1 013-line cartridge-os journal  | measured on cartridge-os: brief 3.5k chars, additionalContext 6.6k on the 1 013-line journal; the 2 500 CONTEXT cap cut 'Runtime constraints' and 'Where things are', so the cap is now section-aware and grows to 4 000 when the journal is short |
| F-02 | lang skills | three knowledge lines remain reported (LuCI runtime, secret masking rule, Dependabot groups for actions) | /partner:learn R1.1 |
| F-03 |  dogfood cartridge-os  |  live probe through the installed plugin not run: the terminal CLI's OAuth session had expired (claude login), hook behaviour verified by feeding payloads to the cached hooks instead  | live probes passed through the installed plugin on 2026-11-06: the brief carried the 2026-11-02 journal entry, the rules line and five partner: agents; mise run lint went silent through the gate and Claude Code's own permission asked, mise run sd-linux was stopped by the gate as opaque |
| F-04 | dogfood cartridge-os | ~/.claude/CLAUDE.md is a plain file, not the symlink to ~/.agents/AGENTS.md the global instructions describe; install.sh --check reports it | switch plan (docs/03-switch-plan.md) |
| F-05 |  live probes  |  entry wrappers hide the command from the gate: distrobox enter <box> -- <cmd> (cartridge-os's documented form), docker/podman exec <c> <cmd>, ssh <host> <cmd>, toolbox run, nix develop -c, nix-shell --run, flatpak run all judge as silence; the inner command should be judged (remote/ssh as opaque)  | fixed 2026-11-06: entry wrappers (distrobox enter, toolbox run, docker/podman exec, docker compose exec/run, nix develop -c, nix-shell --run, flatpak run --command=, chroot) and shell -c strings are looked through up to four levels; ssh, mosh, kubectl exec, gcloud ssh, gh codespace ssh, source and . ask; verified live from cartridge-os |
