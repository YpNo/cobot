"""Workflow skill texts that name cobot-memory commands keep naming the commands that exist
(spec memory-and-ship)."""

from __future__ import annotations

from conftest import PLUGIN

SKILLS = PLUGIN / "skills"


def text(skill: str) -> str:
    return (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")


def test_wrap_namesTheOneCommitFlow():
    # story 1: stage, key the tree, journal with the key, one commit; foreign mode skips the add
    wrap = text("wrap")
    steps = ("cobot-memory stamp --tree", "verified: tree <key>", "journal add --check", "one `git commit`")
    for step in steps:
        assert step in wrap, step
    assert "foreign mode" in wrap and "+working-tree" in wrap


def test_build_journalsWithTheTreeStamp():
    assert "cobot-memory stamp --tree" in text("build")


def test_onboard_untrustedAfterInit_namesInitWithTheConfigDir():
    # story 6 (F-47): both paths, the prefixed init command, never `cobot-memory trust`
    onboard = text("onboard")
    assert "run `cobot-memory check` again" in onboard and "trust file:" in onboard
    assert "CLAUDE_CONFIG_DIR=<path>" in onboard and "Never send the owner to `cobot-memory trust`" in onboard


def test_ship_groundChecksToolchainsRemoteAndTools():
    # story 8 (F-37, F-43, F-48)
    ship = text("ship")
    for rule in (
        "`cobot-deps check`",
        "pin Dependabot cannot see",
        "git remote get-url origin",
        "GIT_TERMINAL_PROMPT=0",
        "timeout 20 git",
        "ls-remote --symref origin HEAD",
        "**empty** remote",
        "**unreachable**, never empty",
        "Name the base branch",
        "never run",
        "REMOTE",
        "PINS",
    ):
        assert rule in ship, rule


def test_wrapAndBuild_clearTheParkedNotices():
    # story 3: wrap files or drops each parked item, build parks an async hand-back's itself
    wrap = text("wrap")
    assert "cobot-memory noticed list" in wrap and "cobot-memory noticed clear" in wrap
    build = text("build")
    assert "hand-back" in build and "cobot-memory noticed add" in build


AGENT_SKILLS = ("build", "consult", "ship", "security-sweep", "wrap", "spec")


def test_agentSkills_carryBothHostStrings():
    # builder-proof-hosts story 6: the parameter where the host has it, and the wait everywhere
    for name in AGENT_SKILLS:
        body = text(name)
        assert "`run_in_background: false` where the host offers it" in body, name
        assert "wait for every hand-back" in body, name


def test_build_neverTicksAnUnprovenReport():
    # builder-proof-hosts story 4: the hook's mark stops the tick; re-run or ask
    build = text("build")
    assert "`UNPROVEN:`" in build and "never ticked" in build and "ask the owner" in build
