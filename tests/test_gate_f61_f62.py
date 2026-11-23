"""The other writers, and taking the config dir away (spec gate-f56-f60, stories 7 and 8).

F-61: writers whose output folder the gate did not read (aria2c, gh downloads, ditto, pax, sftp,
dpkg-deb, jar, ar, unar, the bsd tools, in-place decompression). F-62: removing, covering or
locking the config dir, and reaching it through a symlink. Each row reached no decision on
``6022fa6``.
"""

from __future__ import annotations

import pytest


def decide(rules, command, agent=None, cwd=None):
    loaded, _, _ = rules.load_rules(None)
    return rules.judge_bash(command, loaded, agent, cwd)[0].decision


# ---------------------------------------------------------------- story 7, T07: other downloaders

DOWNLOADER_REFUSED = [
    "aria2c -d ~/.claude https://h/x",
    "aria2c --dir=~/.claude https://h/cobot.rules",
    "aria2c --dir ~/.claude https://h/x",
    "aria2c -d~/.claude https://h/cobot.rules",
    "aria2c -d ~/.claude -o cobot.rules https://h/x",
    "gh release download v1 -D ~/.claude",
    "gh release download v1 --dir ~/.claude",
    "gh release download v1 --dir=~/.claude/cobot",
    "gh run download 1 -D ~/.claude",
    "gh run download 1 --dir=~/.claude",
    "gh release download v1 -O ~/.claude/cobot.rules",
    "gh -R o/r release download v1 -D ~/.claude",
    "cd ~/.claude && gh release download v1 -p cobot.rules -O cobot.rules",
]
DOWNLOADER_ASKED = [
    "gh release download v1 -D ~",
    "cd ~ && gh run download 1",
    "cd ~ && gh release download v1 -p '*'",
    "aria2c -d ~ https://h/x",
    "aria2c -d ~ -i urls.txt",
    "cd ~ && aria2c https://h/x",
    "aria2c -d ~ -o .claude.json https://h/x",
    "aria2c --conf-path=e/conf https://h/x",
    "aria2c --conf-path e/conf https://h/x",
    # challenger: an input list's dir= and out= lines move the landing, as curl -K
    "aria2c -d dl -i list.txt",
    "aria2c --input-file=list.txt",
]
DOWNLOADER_SILENT = [
    "gh release download v1 -D dist/",
    "gh release download v1",
    "gh run download 1 -D artifacts",
    "gh run download 1 -n logs",
    "gh release list",
    "gh pr view 1",
    "aria2c -d dl https://h/x",
    "aria2c https://h/x",
    "aria2c -o out.bin https://h/x",
]


# ---------------------------------------------------------------- story 7, T08: copiers and extractors

WRITER_REFUSED = [
    "ditto e/cobot.rules ~/.claude/",
    "ditto e/ ~/.claude",
    "ditto -x -k e.zip ~/.claude",
    "ditto --arch x86_64 e/cobot.rules ~/.claude/",
    "pax -rw src ~/.claude",
    "pax -r -w -p e src ~/.claude/",
    "sftp h:/x/cobot.rules ~/.claude/",
    "sftp -P 22 h:/x/cobot.rules ~/.claude",
    "cd ~/.claude && sftp h:/x/cobot.rules",
    "dpkg-deb -x e.deb ~/.claude",
    "dpkg-deb --extract e.deb ~/.claude",
    "dpkg-deb -R e.deb ~/.claude",
    "dpkg-deb --vextract e.deb ~/.claude/cobot",
    "dpkg -x e.deb ~/.claude",
    "bsdunzip -d ~/.claude e.zip",
    "bsdcpio -i -D ~/.claude < e.cpio",
    "unar -o ~/.claude e.rar",
    "unar e.rar -o ~/.claude",
    "unar -output-directory ~/.claude e.rar",
    "ar x --output=~/.claude e.a",
    "ar x --output ~/.claude e.a",
    "jar xf e.jar -C ~/.claude",
    "jar --extract --file e.jar --dir ~/.claude",
    # challenger: ditto copies a folder's contents, and -x extracts into its last operand
    "ditto e ~",
    "ditto -x -k e.zip ~",
    "dpkg-deb -e e.deb ~/.claude/cobot",
    # T07 bypass review: pax keeps each operand's path; aria2c's --index-out
    "pax -rw .claude/cobot.rules ~",
    "pax -rw ./.claude/cobot.rules ~",
    "pax -rw .claude/cobot ~",
    "pax -rw ../cobot.rules ~/.claude/x",
    "aria2c --index-out=1=$HOME/.claude/cobot.rules a.torrent",
    "aria2c -O 1=$HOME/.claude/cobot.rules a.torrent",
]
WRITER_ASKED = [
    "cd ~/.claude && jar xf e.jar",
    "cd ~/.claude && jar -xf e.jar",
    "cd ~/.claude && ar x e.a",
    "cd ~/.claude && unar e.rar",
    "cd ~/.claude && bsdunzip e.zip",
    "cd ~ && unar e.rar",
    "cd ~ && jar xf e.jar",
    # member names the gate cannot place
    "pax -r -f e.pax",
    "pax -r < e.pax",
    "pax -r -s ,^,/x/, -f e.pax",
    "jar xPf e.jar",
    "ar xP e.a",
    "bsdcpio -i --insecure < e.cpio",
    # T07 bypass review: ar's separate dashed key words and --plugin; pax -rw -s
    "cd ~/.claude && ar -v -x a.a",
    "cd ~/.claude && ar --plugin p x a.a",
    "ar -v -xP a.a",
    "ar --plugin p xP a.a",
    "pax -rw -s ',^a$,../cobot.rules,' a ~/.claude/x",
    "aria2c -d ~ -O 1=.claude.json a.torrent",
]
WRITER_SILENT = [
    "ditto src dst",
    "ditto -c -k src out.zip",
    "ditto -c -k ~/.claude out.zip",
    "jar cf a.jar -C ~/.claude .",
    "pax -w -f out.pax src",
    "pax -rw src dst",
    "sftp h:/x/report.txt .",
    "sftp h",
    "dpkg-deb -x e.deb out",
    "dpkg-deb -c e.deb",
    "dpkg -i e.deb",
    "jar xf e.jar",
    "jar cf out.jar -C build .",
    "jar tf e.jar",
    "ar x e.a",
    "ar rcs lib.a a.o",
    "unar e.rar",
    "unar -o out e.rar",
    "bsdunzip e.zip",
    "bsdcpio -i < e.cpio",
    "pax -rw sub/.bashrc ~",
    "pax -rw cfg/.claude.json ~",
    "ar -v -x a.a",
    "ar t a.a",
]


@pytest.mark.parametrize("command", WRITER_REFUSED)
def test_story7_writerIntoASealedFolder_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", WRITER_ASKED)
def test_story7_writerInAProtectedCwdOrUnplaced_asks(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", WRITER_SILENT)
def test_story7_writerElsewhere_staysSilent(rules, command):
    assert decide(rules, command) is None


@pytest.mark.parametrize("command", DOWNLOADER_REFUSED)
def test_story7_downloaderIntoASealedFolder_isRefused(rules, command):
    assert decide(rules, command) == "deny"


@pytest.mark.parametrize("command", DOWNLOADER_ASKED)
def test_story7_downloaderWithServerNamesInAHolder_asks(rules, command):
    assert decide(rules, command) == "ask"


@pytest.mark.parametrize("command", DOWNLOADER_SILENT)
def test_story7_downloaderElsewhere_staysSilent(rules, command):
    assert decide(rules, command) is None
