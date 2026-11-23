"""Where a copy, a download or an extraction lands (spec gate-f56-f60, F-56 and F-60).

The gate checked the words a copy names, not the place it lands: an option value joined to its
option, a source copied into a folder, a download into a folder, an extraction into the working
directory and a config dir outside HOME reached no decision.
"""

from __future__ import annotations

import pytest


def decide(rules, command, agent=None, cwd=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent, cwd)[0].decision


# ---------------------------------------------------------------- story 1: option values (F-60)

LANDING_OPTION_REFUSED = [
    "cp --target-directory=$HOME/.claude cobot.rules",
    "cp --target-directory=~/.claude cobot.rules",
    "cp -t$HOME/.claude cobot.rules",
    "cp -rt$HOME/.claude cobot.rules",
    "cp --target=$HOME/.claude cobot.rules",
    "cp --t=$HOME/.claude cobot.rules",
    "mv --target-directory=$HOME/.claude cobot.rules",
    "ln --target-directory=$HOME/.claude cobot.rules",
    "install --target-directory=$HOME/.claude cobot.rules",
    "curl -o~/.claude/cobot.rules https://h/x",
    "curl -sSLo~/.claude/cobot.rules https://h/x",
    "curl --output=~/.claude/cobot.rules https://h/x",
    "wget -O~/.claude/cobot.rules https://h/x",
    "wget --output-document=~/.claude/cobot.rules https://h/x",
    "curl --output-dir=~/.claude -O https://h/x",
    "wget -P~/.claude https://h/x",
    "wget --directory-prefix=~/.claude https://h/x",
    "7z x -o$HOME/.claude e.7z",
    "cpio -i -D ~/.claude < e.cpio",
    # T01 bypass review: a joined path on any short option, current 7-Zip binaries
    "wget -o~/.claude/cobot.rules https://h/x",
    "wget -qa~/.claude/cobot.rules https://h/x",
    "curl -sD~/.claude/cobot.rules https://h/x",
    "curl -c~/.claude/cobot.rules https://h/x",
    "sort -o~/.claude/cobot.rules x",
    "gcc -o~/.claude/cobot.rules x.c",
    "7zz x -o~/.claude/cobot a.7z",
    "7zr x -o$HOME/.claude a.7z",
]
LANDING_OPTION_SILENT = [
    "cp -t dist a.js",
    "cp --target-directory=dist a.js",
    "curl -oout.json https://h/x",
    "curl -o out.json https://h/x",
    "wget -O- https://h/x",
    "wget -Pdl https://h/x",
    "7z x -odist e.7z",
    "gcc -I/usr/include -o build/x x.c",
    "curl -fsSLo /tmp/x https://h/x",
    "install -t ~/.local/bin x",
    "cp -t ~/.claude/projects x",
]


@pytest.mark.parametrize("command", LANDING_OPTION_REFUSED)
def test_story1_joinedLandingOption_isRefusedAsTheSeparateForm(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", LANDING_OPTION_SILENT)
def test_story1_landingOptionOutsideAProtectedFolder_staysSilent(rules, command):
    assert decide(rules, command) is None
