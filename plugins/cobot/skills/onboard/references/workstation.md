# Workstation: install routes, package names, helpers

Read by onboard step 3b and N3 (spec onboard-environment, decision 29). `cobot-env detect` says
what the machine has; this file says what to print when something is missing. cobot never runs
an install: it prints the command in the owner's route, and the gate asks on every route below.

## Install routes

The route is the owner's answer (`cobot-env prefer <route>`), asked only when a tool is missing
and `cobot-env show` has no route for this host.

| route | what onboarding prints | note |
|---|---|---|
| mise, the repository pins the version (`.mise.toml`, `mise.toml`, `.tool-versions`) | `mise install` | installs the pin; writes nothing |
| mise, no pin | `mise use -g <tool>@<version>` | an **owner-level change**: say so. The version comes from a `lang-*` line that is not stale; without one, `<tool>@latest` and say it is unpinned. Never `mise use` without `-g`: it writes the repository's mise.toml and overrides its pin |
| brew | `brew install <package>` | |
| apt | `sudo apt install <package>` | |
| dnf | `sudo dnf install <package>` | |
| pacman | `sudo pacman -S <package>` | |
| zypper | `sudo zypper install <package>` | |
| apk | `sudo apk add <package>` | |
| nix | `nix profile install nixpkgs#<package>` | |
| distrobox:`<box>` | `distrobox enter <box> -- <the box's own route>` | the box's package manager, from `cobot-env detect` run inside it, else ask |

## Package names

- [verified 2026-11-16 · src: apt-cache policy on Debian 13] apt: `ripgrep`, `fd-find` (installs `fdfind`, which `cobot-env` counts as fd), `jq`, `gh`; rtk has no Debian package.
- [verified 2026-11-16 · src: mise registry, mise 2026.11.4] mise: `ripgrep` (aqua:BurntSushi/ripgrep), `fd` (aqua:sharkdp/fd), `jq` (aqua:jqlang/jq), `gh` (aqua:cli/cli), `rtk` (aqua:rtk-ai/rtk).
- [reported 2026-11-16 · src: https://github.com/cli/cli/blob/trunk/docs/install_linux.md] gh: dnf and zypper `gh`, pacman and apk `github-cli`, brew `gh`; the program is always `gh`.
- [reported 2026-11-16 · src: https://pkgs.alpinelinux.org/package/v3.24/community/x86_64/fd] fd: dnf `fd-find`, pacman, zypper, apk and brew `fd`.
- [reported 2026-11-16 · src: https://github.com/BurntSushi/ripgrep#installation] ripgrep and jq keep their names on dnf, pacman, zypper, apk and brew (`ripgrep`, `jq`).

A name missing here is looked up (`apt-cache policy`, `dnf info`, `brew info`: reads, silent),
never guessed.

## Helpers cobot benefits from

Advised once, in one printed line naming the absent ones (`advise:` in the brief) and how to
decline: `cobot-env decline <helper>`. Never a question.

| helper | what it saves cobot | licence | repository |
|---|---|---|---|
| rtk | 60–90 % fewer tokens on dev commands (a hook rewrites Bash to `rtk <cmd>`); the gate unwraps it | Apache-2.0 for the `rtk-oss` edition; see below | `github.com/rtk-ai/rtk` |
| ripgrep (`rg`) | fast searches that respect `.gitignore` | MIT or Unlicense | `github.com/BurntSushi/ripgrep` |
| fd | fast file finding that respects `.gitignore` | MIT or Apache-2.0 | `github.com/sharkdp/fd` |
| jq | reading JSON from `gh`, `cobot-env detect --json`, package tools | MIT | `github.com/jqlang/jq` |
| gh | PRs, CI runs and API reads for the GitHub forge | MIT | `github.com/cli/cli` |

- [reported 2026-11-16 · src: https://github.com/rtk-ai/rtk] rtk installs with `brew install rtk`, `mise use -g rtk`, or `cargo install --git https://github.com/rtk-ai/rtk`; the 1.0 line ships a mixed-licence full build and an Apache-2.0 `rtk-oss` edition (`brew install rtk-ai/tap/rtk-oss`); the two install the same `rtk` program.
- [verified 2026-11-16 · src: rtk 0.50.0 on the owner's machine] the hook is installed with `rtk init -g`, an owner-level change the owner runs.

**rtk's identity.** Two programs are called `rtk`: the Rust Token Killer above, and the
"Rust Type Kit" (reachingforthejack/rtk), which is what plain `cargo install rtk` installs from
crates.io. Never print `cargo install rtk`. `cobot-env` cannot tell them apart (it runs
nothing); when `rtk` is present, the owner's own `rtk gain` proves it: the Type Kit has no such
command.
