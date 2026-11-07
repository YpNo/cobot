# lang-fallback — versions and dated facts

Format: `- [status date · src] claim`. Version lines are flagged after 30 days, idiom after 90; re-check with
`curl -s https://api.github.com/repos/<owner>/<repo>/releases/latest | jq -r .tag_name`.
Maintenance is judged on the last commit, not the last release.

## Shell

| Tool | Current | Released | Last commit |
|---|---|---|---|
| shellcheck | 0.11.0 | 2025-08-04 | 2026-11-05 |
| shfmt (mvdan/sh) | 3.14.1 | 2026-09-06 | — |
| bats-core | 1.14.0 | 2026-07-21 | — |
| bats-assert | 2.2.4 | 2025-10-14 | — |
| bats-support | 0.3.0 | 2022-03-04 | — |

- [verified 2026-11-06 · src: https://github.com/koalaman/shellcheck/releases] shellcheck 0.11.0 is the latest release; master is active (commit 2026-11-05).
- [verified 2026-11-06 · src: https://github.com/koalaman/shellcheck/wiki/SC1071] shellcheck supports sh, bash, dash and ksh only; no zsh.
- [verified 2026-11-06 · src: https://github.com/mvdan/sh/releases] shfmt 3.14.1; parses POSIX sh, bash, zsh and mksh; building from source needs Go 1.26+.
- [verified 2026-11-06 · src: https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd] shfmt applies `.editorconfig` only when no parser or printer flag is given.
- [verified 2026-11-06 · src: https://github.com/bats-core/bats-core/releases] bats-core 1.14.0.
- [verified 2026-11-06 · src: https://github.com/bats-core/bats-assert/releases] bats-assert 2.2.4; bats-support 0.3.0 is old but still the dependency bats-assert expects.
- [verified 2026-11-06 · src: https://www.shellcheck.net/wiki/SC3040] `set -o pipefail` entered POSIX in POSIX.1-2024; older `/bin/sh` implementations reject it.

## Lua

| Tool / runtime | Current | Released | Last commit |
|---|---|---|---|
| Lua (PUC) | 5.5.1 (5.4.9 on the 5.4 line) | 2026-08-03 | — |
| LuaJIT | rolling, no tags | — | — |
| luacheck | 1.2.0 | 2024-05-24 | 2026-07-31 |
| StyLua | 2.6.0 | 2026-10-10 | — |
| busted | 2.3.0 | 2026-01-07 | — |
| Neovim | 0.12.6 | 2026-10-09 | 2026-11-06 |
| NodeMCU firmware | 3.0.0-release_20240225 | 2024-02-25 | 2025-08-28 |

- [verified 2026-11-06 · src: https://www.lua.org/versions.html] Lua 5.5 released 2025-12-22; 5.5.1 on 2026-08-03; 5.4.9 is the latest 5.4 tarball (<https://www.lua.org/ftp/>).
- [verified 2026-11-06 · src: https://www.lua.org/manual/5.5/readme.html] Lua 5.5 adds declarations for global variables.
- [verified 2026-11-06 · src: https://luajit.org/download.html] LuaJIT uses rolling releases; no release tarballs or binaries.
- [verified 2026-11-06 · src: https://github.com/lunarmodules/luacheck] luacheck 1.2.0 checks Lua 5.1 to 5.4 and LuaJIT; `--std` values include `lua54`, `luajit`, `max`; no 5.5 listed. Release is old, commits continue: maintained, slow.
- [verified 2026-11-06 · src: https://github.com/JohnnyMorganz/StyLua] StyLua 2.6.0; `syntax` options `All`, `Lua51`–`Lua54`, `LuaJIT`, `Luau`, `CfxLua`; no 5.5 listed.
- [verified 2026-11-06 · src: https://github.com/lunarmodules/busted/releases] busted 2.3.0.

## Lua hosts the owner meets

- [verified 2026-11-06 · src: https://github.com/neovim/neovim/blob/master/runtime/doc/lua.txt] Lua 5.1 is Neovim's permanent interface; builds should use LuaJIT; plugins target 5.1.
- [verified 2026-11-06 · src: https://github.com/nodemcu/nodemcu-firmware] NodeMCU: Lua 5.1.4 or 5.3 without `debug`, `io`, `os` and most of `math`; `release`/`dev` target ESP8266, `dev-esp32` the ESP32. Last release 2024, last commit 2025-08: low activity.
- [verified 2026-11-06 · src: https://github.com/domoticz/domoticz] Domoticz event scripting through dzVents (Lua).
- [verified 2026-11-06 · src: https://github.com/openwrt/luci] OpenWrt LuCI repository is active (commit 2026-11-05).
- [reported 2026-11-06] Newer LuCI views are client-side JavaScript and OpenWrt is moving system scripting to ucode; Lua remains in older LuCI apps. Check the target release before writing Lua for it.
- [verified 2026-11-06 · src: https://github.com/AppDaemon/appdaemon] Home Assistant automations (AppDaemon, Pyscript) are Python, not Lua; route them to the Python skill.
