"""Where a copy, a download or an extraction lands (spec gate-f56-f60, F-56 and F-60).

The gate checked the words a copy names, not the place it lands: an option value joined to its
option, a source copied into a folder, a download into a folder, an extraction into the working
directory and a config dir outside HOME reached no decision.
"""

from __future__ import annotations

import os

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


# ---------------------------------------------------------------- story 2: landing words per copier

LANDING_ASKED = [
    "cp e/.claude.json ~/",
    "cp e/.claude.json ~",
    "cp -t ~ e/.claude.json",
    "mv e/.claude.json ~",
    "ln -s e/.claude.json ~",
    "install e/.claude.json ~",
    "rsync e/.claude.json ~/",
    "rsync -rt e/.claude.json ~/",
    "scp h:/x/.claude.json ~/",
    "scp -P 22 h:/x/.claude.json ~",
    "cp e/.bashrc ~/",
    "cp -t ~ .bashrc",
    "cp x/.zshenv y/.profile ~/",
]
LANDING_REFUSED = [
    "scp h:/x/cobot.rules ~/.claude",
    "scp -r h:/x/cobot ~/.claude/",
    "docker cp c:/x/cobot.rules ~/.claude/",
    "podman cp c:/x/cobot.rules ~/.claude",
    "kubectl cp ns/pod:/x/cobot.rules ~/.claude/",
    "rclone copy r:x/cobot.rules ~/.claude/",
    "rclone copy r:x/cobot.rules ~/.claude/ --transfers 4",
    "cp --parents .claude/cobot.rules ~",
    "rsync -R .claude/cobot.rules ~/",
    "rsync --relative .claude/cobot.rules ~/",
    "cp e/cobot.rules ~/.claude/shell-snapshots/",
]
LANDING_SILENT = [
    "cp a ~",
    "cp README.md ~/",
    "cp report /tmp/",
    "cp a.txt ~/notes/",
    "mv build dist/",
    "cp -t dist a.js",
    "rsync -rt src/ dist/",
    "rsync -a src/ dist/",
    "scp h:/x/report.txt .",
    "docker cp c:/app/log.txt .",
    "rclone copy r:photos ~/Pictures",
    'cp "$f" dist/',
    "cp -T a.txt ~/b.txt",
]


LANDING_ASKED += [
    # T02 bypass review: verbs behind global options, git mv, rsync -R's /./ marker
    "docker --log-level debug --context x cp c:/.bashrc ~",
    "podman --remote --url x cp c:/.bashrc ~",
    "git mv e/.bashrc ~",
    "git mv -k e/.bashrc ~",
    "rsync -R e/./.bashrc ~/",
]
LANDING_REFUSED += [
    "rclone -v copy r:cobot.rules ~/.claude/",
    "rclone copy r:dir ~",
    "rsync -a --files-from=l h: ~/",
]
LANDING_SILENT += ["rclone copy . r:backup", "git mv a b", "docker cp ./x c:/root/", "scp file h:~/"]


@pytest.mark.parametrize("command", ["cp e/.bashrc x:/../..", "cp -t x:/../.. e/.bashrc", "cp e/.bashrc ../"])
def test_story2_colonIsALocalFolderForCp_landingIsJudged(rules, command):
    """For cp, ``x:`` is a folder: from ``~/proj`` the file lands at ``~/.bashrc`` (T02 review)."""
    assert decide(rules, command, cwd=os.path.expanduser("~/proj")) == "ask"


@pytest.mark.parametrize("command", LANDING_ASKED)
def test_story2_copyLandingOnAnAskRowFile_asks(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", LANDING_REFUSED)
def test_story2_copyLandingOnASealedFile_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", LANDING_SILENT)
def test_story2_copyLandingElsewhere_staysSilent(rules, command):
    assert decide(rules, command) is None
